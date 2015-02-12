import sublime
import sublime_plugin
import re
import importlib

class SnippetInfo():
  def __init__(self):
    settings = self._get_settings()

    self.variables = settings.get('variables', {})

  def _call(self, handler, *args):
    module_name, method_name = handler.rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, method_name)(*args)

  def _get_settings(self):
    result = {'variables': {}}
    for resource in sublime.find_resources('SnippetCaller.sublime-settings'):
      settings = sublime.decode_value(sublime.load_resource(resource))
      if 'variables' in settings:
        result['variables'].update(settings['variables'])

    return result

  def get(self, view, sel, snippet = None, contents = None, **values):
    eval_code, commands, values = self._get_info(snippet, values, contents)
    values.update(self._extract_content_values(view, sel, values))
    values.update(self._eval(view, sel, eval_code, values))
    content = self._get_content_with_values(values)
    return commands, content

  def _get_info(self, snippet, values, contents):
    commands, eval_code = ['RUN'], None
    if contents == None:
      contents = snippet['content']
      commands = snippet.get('commands', None) or ['RUN']
      eval_code = snippet.get('eval', None) or None

    values['contents'] = contents
    return eval_code, commands, values

  def _extract_content_values(self, view, sel, values):
    keys = []
    for match in re.finditer(r'(\\*)\$(\w+)', values['contents']):
      if len(match.group(1)) % 2 != 0:
        continue

      keys.append(match.group(2))

    result = values.copy()
    for key in keys:
      for subkey in key.split('__or__'):
        if subkey not in self.variables:
          continue

        value = self._call(self.variables[subkey], view, sel, result)
        if value == None:
          continue

        value = self._escape(value)
        if value != None:
          result[key] = value
          break

    return result

  def _eval(self, view, sel, eval_code, values):
    if eval_code == None:
      return values

    parameters = {'view': view, 'sel': sel, 'values': values}
    eval_result = eval(eval_code.strip(), parameters)

    if not isinstance(eval_result, dict):
      raise Exception("variables should be python code that returns dict")

    return eval_result

  def _get_content_with_values(self, values):
    content = values['contents']
    for match in reversed(list(re.finditer(r'(\\*)\$(\{?(\w+)\}?)', content))):
      key = match.group(2)
      if key != match.group(3):
        key = match.group(3)

      if len(match.group(1)) % 2 != 0 or key not in values:
        continue

      value = values[key]

      preceding = content[:match.start(2) - 1]
      spacing = re.finditer(r'(^|\n)(\s*)', preceding)
      indentation = list(reversed(list(spacing)))[0].group(2).replace("\n", "")

      value = re.sub(r'\n', '\n' + indentation, value)
      content = preceding + value + content[match.end(2):]

    return content

  def _escape(self, value):
    return (
      value.
        replace('\\', '\\\\').
        replace('$', '\\$').
        replace('{', '\\{').
        replace('}', '\\}')
    )

  def _get_region(self, view, values):
    sel = self.view.sel()
    match = re.search(r'(\n|^)(\s*)\S*\$indented_selection', values['contents'])
    if len(sel) == 1 and sel[0].size() > 0 and match != None:
      indented_selection = self._get_indented_region(sel[0], match.group(2))
      values['contents'] = values['contents'].replace('$indented_selection',
        indented_selection)
    return values

__info = None
def get(view, sel, snippet = None, contents = None, **values):
  global __info
  if __info == None:
    __info = SnippetInfo()

  return __info.get(view, sel, snippet, contents, **values)