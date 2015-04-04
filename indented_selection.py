import sublime
import sublime_plugin
import re

from .selection import get as get_selection

def get(view, sel, _):
  value = get_selection(view, sel, _)
  if value == None:
    return value

  tab_size = view.settings().get('tab_size')
  spaces = view.settings().get('translate_tabs_to_spaces')

  if spaces:
    tab = " " * tab_size
  else:
    tab = "\n"

  return re.sub(r'(^|\n)(.)', '\\1' + tab + '\\2', value)