import sublime
import sublime_plugin

import re
import os
from xml.dom import minidom

try:
  from Context import context
except ImportError:
  sublime.error_message("Dependency import failed; please read readme for " +
   "SnippetCaller plugin for installation instructions; to disable this " +
   "message remove this plugin")

class Snippet():
  def __init__(self):
    self.load_snippets()

  def load_snippets(self):
    snippets = []
    maximal_trigger_length = 0
    is_error_reported = False
    resources = (sublime.find_resources("*.sublime-snippet") +
      sublime.find_resources("*.sublime-snippet-enhanced"))

    for resource in resources:
      try:
        for snippet in self._parse_snippets(resource):
          if snippet == None:
            continue

          snippets.append(snippet)
          maximal_trigger_length_exceeded = ('tabTrigger' in snippet and
            len(snippet['tabTrigger']) > maximal_trigger_length)

          if maximal_trigger_length_exceeded:
            maximal_trigger_length = len(snippet['tabTrigger'])

      except Exception as error:
        if not is_error_reported:
          message = ('Failed to load snippet ' + resource + ': {0}').format(error)
          sublime.error_message(message)
        is_error_reported = True

    self.snippets = snippets
    self.maximal_trigger_length = maximal_trigger_length

  def _parse_snippets(self, name):
    xml_string = sublime.load_resource(name)
    if xml_string == '':
      return []

    xml = minidom.parseString(xml_string).firstChild
    if xml == None:
      return []

    if xml.nodeType == xml.ELEMENT_NODE and xml.tagName == 'snippets':
      snippets = []
      for node in xml.childNodes:
        if not isinstance(node, minidom.Element):
          continue
        snippets.append(self._parse_snippet_xml(name, node))
    else:
      snippets = [self._parse_snippet_xml(name, xml)]

    return snippets

  def _parse_snippet_xml(self, name, xml):
    snippet = {}

    for node in xml.childNodes:
      if node.nodeType == node.ELEMENT_NODE:
        value_node = node.firstChild
        if value_node == None:
          continue
        snippet[node.tagName] = value_node.data

    if len(snippet) == 0:
      return None

    if 'content' not in snippet:
      return None

    if 'context' in snippet:
      snippet['context'] = sublime.decode_value(snippet['context'])

    if 'commands' in snippet:
      snippet['commands'] = sublime.decode_value(snippet['commands'])

    snippet['content'] = snippet['content'].strip()
    if len(snippet['content']) == 0:
      return None

    if 'scope' in snippet:
      # load old snippets
      snippet['_scope'] = snippet['scope']

      if re.search(r'^([\w\+]+\.[\w\+]+,?\s*)*$', snippet['scope']) != None:
        snippet['scope'] = (
          '((?:\W|^)' + snippet['scope'].
            replace(', ', '(?:\W|$)|(?:\W|^)').
            replace('+', '\\+').replace('.', '\\.') + '(?:\W|$))'
        )

      snippet['scope'] = re.compile(snippet['scope'])

    snippet['name'], _ = os.path.splitext(os.path.basename(name))
    snippet['path'] = name

    return snippet

  def get_snippets(self, view, sel, trigger = None):
    found = []
    maximal_trigger_length = 0
    scope = view.scope_name(sel.b)
    for snippet in self.snippets:
      if trigger != None and not 'tabTrigger' in snippet:
        continue

      triggered = (trigger == None or ('tabTrigger' in snippet and
        trigger == snippet['tabTrigger']))

      if not triggered:
        continue

      if 'scope' in snippet and re.search(snippet['scope'], scope) == None:
        continue

      if 'context' in snippet and not context.check(view, snippet['context']):
        continue

      found.append(snippet)

      maximal_trigger_length_exceeded = ('tabTrigger' in snippet and
        len(snippet['tabTrigger']) > maximal_trigger_length)
      if maximal_trigger_length_exceeded:
        maximal_trigger_length = len(snippet['tabTrigger'])

    filtered = []
    if trigger != None:
      for snippet in found:
        has_maximal_length = ('tabTrigger' in snippet and
          len(snippet['tabTrigger']) == maximal_trigger_length)
        if has_maximal_length:
          filtered.append(snippet)
    else:
      filtered = found

    for index, snippet in enumerate(filtered):
      snippet = snippet.copy()
      if 'scope' in snippet:
        snippet.pop('scope')
      filtered[index] = snippet

    return filtered

  def get_maximal_trigger_length(self):
    return self.maximal_trigger_length

__snippet = None
__cache = [None, None]

def clear_cache():
  global __snippet, __cache
  __cache = [None, None]
  __snippet = None

def get_snippet_helper():
  global __snippet, __cache

  if __snippet == None:
    __snippet = Snippet()
    __cache = [None, None]

  return __snippet

def get_snippets(view, regexps = [r'(\S?(?:\w+)\S?|\S)$', r'((?:\w+)\S?|\S)$']):
  maximal_trigger_length = get_snippet_helper().get_maximal_trigger_length()
  sel = view.sel()[0]
  if sel.a != sel.b and regexps != None:
    return []

  # __cache last get_snippets
  __cache_key = '-'.join([
    str(view.id()),
    str(view.change_count()),
    str(sel.b),
    str(regexps)
  ])

  global __cache
  if __cache != None and __cache[0] == __cache_key:
    return __cache[1]

  start = sel.a - maximal_trigger_length
  if start < 0:
    start = 0

  scope = view.scope_name(sel.a)

  line = view.substr(sublime.Region(start, sel.a))
  helper = get_snippet_helper()

  file_extension = None
  file_name = view.file_name()
  if file_name != None:
    _, file_extension = os.path.splitext(file_name)

  result = []
  if regexps == None:
    result = helper.get_snippets(view, sel)
  else:
    for regexp in regexps:
      trigger = re.search(regexp, line)
      trigger = trigger and trigger.group(1)
      if trigger == None:
        continue

      snippets = helper.get_snippets(view, sel, trigger)
      if len(snippets) != 0:
        result = snippets

  __cache = [__cache_key, result]
  return result