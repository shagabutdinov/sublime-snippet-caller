import sublime
import sublime_plugin
import re

from SnippetCaller import snippet_caller
from SnippetCaller import snippet_info

try:
  from QuickSearchEnhanced import quick_search
  from Context import context
except ImportError:
  sublime.error_message("Dependency import failed; please read readme for " +
   "SnippetCaller plugin for installation instructions; to disable this " +
   "message remove this plugin")


class InsertSnippetEnhanced(sublime_plugin.TextCommand):
  def run(self, edit, snippet = None, contents = None, **args):
    commands, _ = snippet_info.get(self.view, self.view.sel()[0],
      snippet, contents, **args)

    for command in commands:
      if command == 'RUN':
        _, contents = snippet_info.get(self.view, self.view.sel()[0],
          snippet, contents, **args)
        self.view.run_command('insert_snippet', {'contents': contents})
      else:
        if not context.check(self.view, command.get('context', [])):
          continue

        self.view.run_command(command['command'], command.get('args', {}))

class InsertBestCompletionEnhanced(sublime_plugin.TextCommand):
  def run(self, edit, index = None, default = '', exact = False):
    self.found_snippets = snippet_caller.get_snippets(self.view)
    found_snippet = None
    if len(self.found_snippets) == 1:
      found_snippet = self.found_snippets[0]
    elif len(self.found_snippets) > 1 and index != None:
      found_snippet = self.found_snippets[index]
    else:
      descriptions = []
      for current_snippet in self.found_snippets:
        descriptions.append([
          current_snippet.get('tabTrigger', '') + ' ' +
            current_snippet.get('description', '') + ' ' +
            '<' + str(current_snippet.get('_scope', None)) + '>',
            current_snippet['path']
        ])

      self.view.window().show_quick_panel(descriptions, self._done)

    if found_snippet == None:
      return

    self._insert_snippet(edit, found_snippet)

  def _done(self, index):
    if index == -1:
      return None

    self.view.run_command('insert_best_completion_enhanced', {'index': index})

  def _insert_snippet(self, edit, snippet):
    for sel in self.view.sel():
      if sel.a != sel.b:
        return

      start = sel.a - len(snippet['tabTrigger'])
      if start < 0:
        return

      region = sublime.Region(start, sel.a)

      if self.view.substr(region) != snippet['tabTrigger']:
        return

    for sel in self.view.sel():
      start = sel.a - len(snippet['tabTrigger'])
      region = sublime.Region(start, sel.a)
      self.view.replace(edit, region, '')

    self.view.run_command('insert_snippet_enhanced', {'snippet': snippet})

class ReloadSnippets(sublime_plugin.WindowCommand):
  def run(self):
    snippet_caller.get_snippet_helper().load_snippets()
    snippet_caller.clear_cache()

class SnippetReloader(sublime_plugin.EventListener):
  def on_post_save_async(self, view):
    file = view.file_name()

    is_snippet_file = file != None and (file.endswith('.sublime-snippet') or
      file.endswith('.sublime-snippet-enhanced'))

    if not is_snippet_file:
      return

    snippet_caller.get_snippet_helper().load_snippets()
    snippet_caller.clear_cache()

class SnippetSelecter():
  def __init__(self, view):
    self.view = view

  def show(self):
    snippets = []
    found_snippets = snippet_caller.get_snippets(self.view, None)

    for snippet in found_snippets:
      description = snippet['name']
      if 'description' in snippet:
        trigger = 'tabTrigger' in snippet and snippet['tabTrigger'] + ' ' or ''
        description = trigger + snippet['description']

      snippets.append([snippet, description])

    self.panel = quick_search.panels.create(snippets, self._insert_snippet,
      callers = [['snippet_selecter', self]])
    self.panel.show()

  def _insert_snippet(self, panel):
    snippet = panel.get_current_value()
    if snippet == None:
      return

    self.view.run_command('insert_snippet_enhanced', {'snippet': snippet})

  def insert_exact_snippet(self):
    trigger = self.panel.get_current_text()
    for (snippet, _) in self.panel.get_values():
      if 'tabTrigger' in snippet and trigger == snippet['tabTrigger']:
        self.view.run_command('insert_snippet_enhanced', {'snippet': snippet})
        self.panel.close(False, None)
        break

class ShowSnippetSelecter(sublime_plugin.TextCommand):
  def run(self, edit):
    SnippetSelecter(self.view).show()

class InsertExactSnippetFromSelecter(sublime_plugin.TextCommand):
  def run(self, edit):
    panel = quick_search.panels.get_current()
    selecter = panel and panel.get_caller('snippet_selecter')
    selecter and selecter.insert_exact_snippet()

class Context(sublime_plugin.EventListener):
  def on_query_context(self, view, key, operator, operand, match_all):
    if key != 'matched_snippets_count':
      return None

    snippets_length = str(len(snippet_caller.get_snippets(view)))

    if operator == sublime.OP_EQUAL:
      return snippets_length == operand
    elif operator == sublime.OP_NOT_EQUAL:
      return snippets_length != operand
    elif operator == sublime.OP_REGEX_MATCH:
      return re.match(operand, snippets_length) != None
    elif operator == sublime.OP_NOT_REGEX_MATCH:
      return re.match(operand, snippets_length) == None
    elif operator == sublime.OP_REGEX_CONTAINS:
      return re.search(operand, snippets_length) != None
    elif operator == sublime.OP_NOT_REGEX_CONTAINS:
      return re.search(operand, snippets_length) == None

    raise Exception('Unsupported operator: ' +str(operator))