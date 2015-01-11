Snake
=====

Snake lets you use Python to its fullest extent to write powerful vim plugins:

```python
from snake import *

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

key_map("<leader>c", toggle_snake_case_camel_case)
```

![Metal Gear Solid Snake Success](http://i.imgur.com/ZFr3vXG.gif)

Why do you want this?
=====================

Vim is great, but vimscript is painful as a programming language.  Let's use
Python instead.

How do I get it?
================

Vundle
------

Pathogen
--------

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

* Create a folder for your plugin in `~/.vim/snake` or symlink it there.
* In your plugin directory, add a `__init__.py` file containing your plugin
  code.
* Add `from snake.plugins import <your_package>` to `~/.vimrc.py`
* Re-source your `~/.vimrc`

What is .vimrc.py?
==================

`.vimrc.py` is intended to be the python equivalent of `.vimrc`.  If you were so
inclined, you could move all of your vim settings and options into `.vimrc.py`:

```python
from snake import *

set("exrc")
set("nocompatible")
set("secure")
set("textwidth", 80)
set("number")

tab = 4
set("shiftwidth", tab)
set("softtabstop", tab)
set("tabstop", tab)

set_global("ctrlp_map", "<c-p>")
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

Contributing
============

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

There is no testing right now.  I'm not sure how to do it right now, but it
might involve running vim in a subprocess in some kind of headless mode,
applying snake functions, then checking the output of the vim buffer for
correctness.

More functions
--------------

Common actions, like `get_word()` already have functions, but there are plenty
more common actions that I haven't thought of yet.  Please write functions for
them!
