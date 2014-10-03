# Sublime SnippetCaller plugin

Snippet system on top of default sublime snippets. That glorious plugin provides
invaluable features if you use snippets much.

Please refer section "Right way to use snippets" if you are not snippet user
yet.


### Demo

![Demo](https://raw.github.com/shagabutdinov/sublime-snippet-caller/master/demo/demo.gif "Demo")


### Installation

This plugin is part of [sublime-enhanced](http://github.com/shagabutdinov/sublime-enhanced)
plugin set. You can install sublime-enhanced and this plugin will be installed
automatically.

If you would like to install this package separately check "Installing packages
separately" section of [sublime-enhanced](http://github.com/shagabutdinov/sublime-enhanced)
package.


### WARNING

This plugin will not works with multicursors properly: all work will be done
only for the first cursor and then reused for others; it works like this because
sublime's snippet system does not provide way to specify different snippet
values for different cursors and workaround requires complete rewriting of
sublime's internal snippet system.


### Features

- Better scope detection; e.g. you can write snippets for string that sits under
ruby code

- Avoiding scope collisions; if you are writing snippets for both php and html,
html snippets will be expanded in php code; it's shame that default sublime
snippets work so badly; but this plugin allows you to avoid such unexpected
behavior

- Checking snippet context before execution; is valuable feature allows you to
execute snippets only under specific circumstances (e.g. if file is located
under "tests" folder or project contains specific framework or selection is
not empty and etc.); this allows to overload tab-triggers and use same triggers
for different snippets.

- Executing sublime-commands before and after snippet execution; it is very
handy when your snippets require some external library included (e.g. for python
"re.search()" you can setup adding "import re" automatically to the header)

- Evaluating custom python code when executing snippet and insert it results as
to snippet placeholders

- Custom extensible $-placeholders; by default there is $indented_selection
(replacement sublime's $selection that works shitty when wrapping code blocks in
it) and $last_assigned_variable

- Obvious snippet execution through quick search panel without typing tab
trigger in file

- Snippets nesting - executing snippet when another snippet is already running

- Backward compatibility for ".sublime-snippet" files


### Usage

Snippets should have ".sublime-snippet-enhanced" or ".sublime-snippet" extension
in order to work with this plugin. All default snippets should work without
changes.

Snippet is xml-file somewhere in packages path. Xml file keys description:

- "snippet" - root key for snippet

- "snippets" - root key for several snippets; "snippets" should contain several
"snippet" xml-elements and allows you to group snippets in one file

- "content" - snippet content; allows placeholders ${1:text} or $1 and $text.
Numeric placeholders is for cursor navigation, symbol placeholders is for
inserting extra values; there is default symbol placeholders
($indented_selection and $last_assigned_variable); symbol placeholders can be
used together using __or__ keyword ($indented_selection__or__last_assigned_variable)
in order to insert first non-empty variable. Note that dollar "$" and backslash
"\" should be escaped with backslash.

- "tabTrigger" - text that triggers a snippet; works slightly different than
default sublime's implementation (allowing to tab-triggering after any non-word
character)

- "scope" - a regular expression that will check the scope under cursor before
snippet execution; note that if you want to avoid scope collision you should
specify negative lookahead for next scope (e.g. "text.html(?!.*source)" for
html that will works only in html but not in embedded languages); note that
for html and css snippet-enhanced will fallback to default sublime snippets
("insert_best_completion") if no snippet will be found it is better to keep
html-snippets with ".sublime-snippet-enhanced" extension in order to avoid
hitting it with sublime default snippet system

- "description" - description of snippet that will be displayed in quick search
panel

- "context" - (json) additional context that will be checked prior to snippet
execution; check [sublime-context](http://github.com/shagabutdinov/sublime-context)
plugin to find out how to use context

- "commands" - (json) list of sublime commands (same commands used for
keymap-files) that will be executed along with snippet; snippet will be executed
in "RUN" value; commands can have "context" key to check will this command be
executed or not

- "eval" - evaluate some code through python's eval and insert result to snippet;
note that python's eval works like a shit and does not allow you to write more
than one statement (so no variables or multiline ifs can be used); I didn't
found better way to evaluate python code and get result; if you are python
expert and know one please tell me I'll be really thankful.



Example  snippet (php yii):

  ```
  <snippet>
    <content><![CDATA[
  <?= Html::encode(${1:$indented_selection}) ?>
  ]]></content>
    <tabTrigger>p</tabTrigger>
    <scope>text.html(?!.*source)</scope> <!-- allow only in html but not in source code -->
    <description>Html::encode</description>
    <context>
      [
        // file name should contain .php at the end; does not allow snippet to
        // be executed in .erb and other similar files that have html code
        {"key": "filename", "operator": "regex_contains", "operand": "\\.php(\\.\\w+)?$"},

        // 'yii' should be listed in settings.frameworks (defined in project settings)
        {"key": "settings.frameworks", "operator": "regex_contains", "operand": "'yii'"},
      ]
    </context>
    <commands>
      [
        // ensure "use yii\\helpers\\Html;" is in beginning of file
        {
          "command": "create_keyword",
          "args": {"keyword_type": "php.use", "keyword": "yii\\helpers\\Html"},
        },
        "RUN",
      ]
    </commands>
  </snippet>
  ```

Example class snippet (ruby):

  ```
  <snippet>
    <content><![CDATA[
  class $class

  end
  ]]></content>
    <tabTrigger>C</tabTrigger> <!-- note that "C" is in capital case -->
    <scope>source.ruby(?!.*source)</scope>
    <description>class</description>
    <eval><![CDATA[
  {'class': view.file_name() and __import__('re').sub(r'^.*/(.*)\.\w+$', '\\1', view.file_name()).title() or ''}
    ]]></eval>
  </snippet>
  ```

Extremely helpful for debugging print-snippet (php):

  ```
  <snippet>
    <content><![CDATA[
  var_dump($last_assigned_variable);
  ]]></content>
    <tabTrigger>v</tabTrigger>
    <scope>source.php(?!.*source)</scope>
    <description>var_dump</description>
  </snippet>
  ```

### Right way to use snippets

Snippets it is one of the most powerful instruments of developer that reduce
plain typing drastically and allows developer to concentrate on solving current
task but not typing.

I think most of people are using snippets in wrong way. It is common to type a
"while" than hit "tab" and receive "while($1) { $2 }". There is no profit to
type whole "while" even if it makes snippet unambiguous. If you use "while"
enough often, the right way to run snippet will be to type "w" then hit "tab".
And there is real profit will begin.

If you'll look over your code you'll find that some words are appears
everywhere and there is no reason to type it everywhere again and again
manually. Let's your editor to care about typing non-unique content (or common
tasks automation). Man should care about what he has to tell editor to do but
not doing editor's job instead of it. Along with
[sublime-autocompletion](http://github.com/shagabutdinov/sublime-autocompletion)
plugin typing can be reduced to typing unique content of program. Non-unique
content can be done by editor.

Snippets should be easy to use but not necessary unambiguous. It is like
shorthand of journalists for developers. You type two characters and receive
thirty. Or receive some valuable execution like inserting most probable name of
class or doing some useful job. When used over time snippets became used
automatically so there is no discomfort with strange tab triggers.

It's shame that even snippets systems creators puts large unusable tab triggers
to example snippets.

So my advise: map your snippets to 1-3 characters of tab-trigger and make it
intellectual. I'll try to help you to do it by providing useful stuff like
"last_assigned_variable".


### Commands

| Description                       | Keyboard shortcut |
|-----------------------------------|-------------------|
| Insert snippet or goto next field | tab               |
| Show snippet caller panel         | ctrl+\            |


### Dependencies

- https://github.com/shagabutdinov/sublime-context
- https://github.com/shagabutdinov/sublime-quick-search-enhanced

For "last assigned variable" snippet variable:

- https://github.com/shagabutdinov/sublime-local-variable
- https://github.com/shagabutdinov/sublime-expression
- https://github.com/shagabutdinov/sublime-statement