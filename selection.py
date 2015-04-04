import sublime
import sublime_plugin
import re

def get(view, sel, _):
  if sel.empty():
    return None

  selection = view.substr(sel)
  region = sublime.Region(view.line(sel.begin()).a, view.line(sel.end()).b)
  text = view.substr(region)

  lines = text.split("\n")
  while len(lines) > 0 and lines[0].strip() == '':
    lines.pop(0)

  if len(lines) == 0:
    return text

  tab1 = re.search(r'^(\s*)', lines[0])
  tab2 = re.search(r'^(\s*)', lines[len(lines) - 1])
  expr = r'(^|\n)(' + tab1.group(0) + r'|' + tab2.group(0) + r')'
  result = re.sub(expr, '\\1', selection)

  return result