import sublime
import sublime_plugin
import re

def get(view, sel, values):
  if sel.empty():
    return None

  region = sublime.Region(view.line(sel.begin()).a, sel.end())
  wide_text = view.substr(region)

  original_text = view.substr(sel)
  ignore_first_line = False
  if wide_text.strip() != original_text.strip():
    text = re.search(r'^(\s*)', wide_text).group(1) + original_text
  else:
    text = wide_text

  match, min, source_indentation = None, None, ''
  for index, line in enumerate(text.split("\n")):
    if ignore_first_line and index == 0:
      continue

    match = re.search(r'^(\s*)\S', line)

    if match == None:
      continue

    if min == None or min > len(match.group(1)):
      min = len(match.group(1))
      source_indentation = match.group(1)

  if match == None:
    return original_text

  text = re.sub(r'(^|\n)' + source_indentation, '\\1', text)

  return text