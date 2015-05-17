Snake (SNAAAAAAAAKKKE)
======================

Snake lets you use Python to its fullest extent to write vim plugins:

```python
from snake import *

@key_map("<leader>c")
def toggle_snake_case_camel_case():
    """ toggles a word between snake case (some_function) and camelcase
    (someFunction) """
    word = get_word()

    # it's snake case
    if "_" in word:
        chunks = word.split("_")
        camel_case = chunks[0] + "".join([chunk.capitalize() for chunk in
            chunks[1:]])
        replace_word(camel_case)

    # it's camel case
    else:
        # split our word on capital letters followed by non-capital letters
        chunks = filter(None, re.split("([A-Z][^A-Z]*)", word))
        snake_case = "_".join([chunk.lower() for chunk in chunks])
        replace_word(snake_case)
```

Pressing "&lt;leader&gt;c" will then toggle between snake and camel case for the
current word!

![Metal Gear Solid Snake Success](http://i.imgur.com/ZFr3vXG.gif)

Why do you want this?
=====================

Vim is great, but vimscript is painful as a programming language.  Let's use
Python instead.  Here's some cool things you can do:

Bind a function to a key
------------------------

```python
from snake import *

@key_map("<leader>r")
def reverse():
    word = list(get_word())
    word.reverse()
    replace_word("".join(word))
```

Use a function for an abbreviation
----------------------------------

A Python function can be expanded dynamically as you type an abbreviation in
insert mode.

```python
from snake import *
import time

abbrev("curtime", time.ctime)
```

Have a function run for a file type
-----------------------------------

Sometimes it is convenient to run some code when the buffer you open is of a
specific file type.

```python
from snake import *

@when_buffer_is("python")
def setup_python_folding(ctx):
    ctx.set_option("foldmethod", "indent")
    ctx.set_option("foldnestmax", 2)
    ctx.key_map("<space>", "za")
```

A context object is passed into the function you wrap.  This context allows you
to set options, let variables, and create abbreviations and keymaps that apply
only to the buffer you just opened, not globally.

Press arbitrary keys as if you typed them
-----------------------------------------

```python
from snake import *

def uppercase_second_word():
    keys("gg") # go to top of file, first character
    keys("w") # next word
    keys("viw") # select inner word
    keys("~") # uppercase it
```

How do I get it?
================

Vundle
------

Add the following line to your Vundle plugin block:

```
Plugin 'amoffat/snake'
```

Pathogen
--------

TODO

Where do I write my Snake code?
===============================

`.vimrc.py` is intended to be the python equivalent of `.vimrc`.  Snake.vim will
load it on startup.  It should contain all of your Snake initialization code and
do any imports of other Snake plugins.  If were so inclined, you could move all
of your vim settings and options into `.vimrc.py` as well:

```python
from snake import *

multi_set_option(
    "nocompatible",
    "exrc",
    "secure",

    ("background", "dark"),
    ("textwidth", 80),

    ("shiftwidth", tab),
    ("softtabstop", tab),
    ("tabstop", tab),
    "expandtab",
)

let("mapleader", ",")

multi_command(
    "nohlsearch",
    "syntax on",
)

from snake.plugins import my_rad_plugin
```

Design Philosophy
=================

Vim is powerful, but its commands and key-bindings are built for seemingly every
use case imaginable.  It doesn't distinguish between commonly-used and
rarely-used.  Snake should use that existing foundation of functionality to add
structure for commonly-needed operations.  For example, many vim users know that
`yiw` yanks the word you're on into a register.  This is a common operation, and
so it should be mapped to a simple function:

```python
@preserve_state()
def get_word():
    keys("yiw")
    return get_register("0")
```

Now instead of your plugin containing `execute "normal! yiw"`, it can contain
`word = get_word()`


How do I write a plugin?
========================

* Create a directory in your vim runtime path.  For many of you, this directory
  will be `~/.vim/bundle`.  The directory you create should be the name of your
  plugin.
* Inside this new plugin directory, create a python file or package (meaning, a
  new directory) named your plugin name.  *Do not* turn your plugin directory
  into a package itself by adding an `__init__.py`.  It won't go well.
* Add `from snake.plugins import <your_package>` to `~/.vimrc.py`
* Re-source your `~/.vimrc`

For plugin API reference, check out [api_reference.md](docs/api_reference.md).

Can I use a virtualenv for my plugin?
=====================================

Yes!  But it's crazy!

Just include a `requirements.txt` file in your package directory that contains
the `pip freeze` output of all the dependencies you wish to include.  When your
module is imported from `.vimrc.py`, a virtualenv will be automatically created
for your plugin if it does not exist, and your plugin dependencies automatically
installed.

Virtualenvs that are created automatically will use your virtualenv\_wrapper
`WORKON_HOME` environment variable, if one exists, otherwise `~/.virtualenvs`.
And virtualenvs take the name `snake_plugin_<your_plugin_name>`.

Gotchas
-------

You may be wondering how snake can allow for different virtualenvs for different
plugins within a single Python process.  There's a little magic going on, and as
such, there are some gotchas.

When a plugin with a virtualenv is imported, it is imported automatically within
that plugin's virtualenv.  Then the virtualenv is exited.  This process is
repeated for each plugin with a virtualenv.

What this means is that all of your plugin's imports *must* occur at your
plugin's import time:

GOOD:
```python
from snake import *
import requests

def stuff():
    return requests.get("http://google.com").text
```

BAD:
```python
from snake import *

def stuff():
    import requests
    return requests.get("http://google.com").text
```

The difference here is that in the first example, your plugin will have a
reference to the correct `requests` module, because it was imported while your
plugin was being imported inside its virtualenv.  In the second example, when
`stuff()` runs, it is no longer inside of your plugin's virtualenv, so when it
imports `requests`, it will not get the correct module or any module at all.

All of this obviously isn't great, and I'm not super pleased with the solution,
but I don't have a better one at the moment.  Just be careful with your modules.

Contributing
============

Read [development.md](docs/development.md) for technical info.

Pull requests
-------------

Although Snake is meant to make Vim more scriptable in Python, it is *not* meant
to provide all the nuanced functionality of Vim.  PRs for new features will be
screened by the value-add of the feature weighed against the complexity added to
the api, with favor towards keeping the api simple.


Snake needs a vundle equivalent
-------------------------------

I would like to see an import hook that allows this in your `.vimrc.py`:

```python
from snake import *

something_awesome = __import__("snake.plugins.tpope/something_awesome")
```

Where the import hook checks if the plugin exists in `~/.vim/snake`, and if it
doesn't, looks for a repo to clone at
`https://github.com/tpope/something_awesome`
