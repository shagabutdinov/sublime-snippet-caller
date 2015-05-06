import sublime
import sublime_plugin
import re

from . import snippet_caller

class Listener(sublime_plugin.EventListener):

  def __init__(self):
    self._modificating = False
    self._last_command = None

  def on_text_command(self, view, command_name, args):
    self._last_command = command_name

  def on_modified(self, view):
    ignore = (
      self._last_command != None and (
        "delete" in self._last_command or
        "undo" in self._last_command or
        "redo" in self._last_command or
        "insert" in self._last_command or
        "ensure" in self._last_command or
        "snippet" in self._last_command or
        "completion" in self._last_command or
        "extract" in self._last_command
      )
    )

    if ignore:
      self._last_command = None
      return

    # prevent modification cycle
    if self._modificating:
      return

    self._modificating = True
    try:
      snippets = snippet_caller.get_snippets(view, trigger_type = 'trigger')
      if len(snippets) == 0:
        return

      view.run_command('insert_best_completion_enhanced', {
        'trigger_type': 'trigger',
      })
    finally:
      self._modificating = False