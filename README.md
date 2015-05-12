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

```python
from snake import *
from os import getcwd

abbrev("cwd", getcwd)
```

Have a function run for a file type
-----------------------------------

```python
from snake import *

@when_buffer_is("python")
def setup_python_folding(buf):
    buf.set_option("foldmethod", "indent")
    buf.set_option("foldnestmax", 2)
    buf.key_map("<space>", "za")
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

Now instead of your plugin containing `execute normal! yiw`, it can contain
`word = get_word()`


How do I write a plugin?
========================

* Add a directory in your vim runtime path.  For many of you, this will be
  `~/.vim/bundle`
* In your plugin directory, create a python file or package named your plugin
  name.  Do not turn your plugin folder into a package with an `__init__.py`
* Add `from snake.plugins import <your_package>` to `~/.vimrc.py`
* Re-source your `~/.vimrc`

For plugin API reference, check out [api_reference.md](docs/api_reference.md).

What is .vimrc.py?
==================

`.vimrc.py` is intended to be the python equivalent of `.vimrc`.  If you were so
inclined, you could move all of your vim settings and options into `.vimrc.py`:

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

set_global("mapleader", ",")

...
```

Can I use a virtualenv for my plugin?
=====================================

Yes!

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

Read [development.md](docs/development.md) for development info.

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

Automated testing
-----------------

There is no testing right now.  I'm not totally sure how to do it, but it might
involve running vim in a subprocess in some kind of headless mode, applying
snake functions, then checking the output of the vim buffer for correctness.

More functions
--------------

Common actions, like `get_word()` already have functions, but there are plenty
more common actions that I haven't thought of yet.  Please write functions for
them!
