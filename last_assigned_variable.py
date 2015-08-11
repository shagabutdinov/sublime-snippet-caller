import sublime
import sublime_plugin

import re

try:
  from LocalVariable import local_variable
  from Method import method as method_parser
  from Expression import expression
  from Statement import statement
except ImportError:
  sublime.error_message("Dependency import failed; please read readme for " +
   "SnippetCaller plugin for installation instructions; to disable this " +
   "message remove this plugin")


def get(view, sel, values):
  scope = None
  method = method_parser.extract_method(view, sel.b)
  if method != None:
    scope = [method['start'], method['end']]
  else:
    scope = [0, view.size()]

  match = expression.find_match(view, sel.b, r'[^=][\*\/+\-]?=(?!=)\s*',
    {'backward': True, 'range': [scope[0], sel.b]})

  if match == None:
    return None

  container = statement.get_statement(view, scope[0] + match.start(0))
  if container == None:
    return None

  variables = local_variable.find_variables(view, container[0], False,
    container)

  if variables == None or len(variables) == 0:
    return

  return view.substr(sublime.Region(*variables[0]))