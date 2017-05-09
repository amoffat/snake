![snake logo](https://github.com/amoffat/snake/blob/master/logo.gif)

[![Build
Status](https://travis-ci.org/amoffat/snake.svg?branch=master)](https://travis-ci.org/amoffat/snake)

Snake (SNAAAAAAAAAKKKE) lets you use Python to its fullest extent to write Vim plugins:

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

## [API Reference](docs/api_reference.md)

# Why do you want this?

Vim is great, but vimscript is painful as a programming language.  Let's use
Python instead.  Here's some cool things you can do:

## Bind a function to a key

```python
from snake import *

@key_map("<leader>r")
def reverse():
    replace_word(get_word()[::-1])
```

## Use a function for an abbreviation

A Python function can be expanded dynamically as you type an abbreviation in
insert mode.

```python
from snake import *
import time

abbrev("curtime", time.ctime)
```

## Have a function run for a file type

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

## Press arbitrary keys as if you typed them

```python
from snake import *

def uppercase_second_word():
    keys("gg") # go to top of file, first character
    keys("w") # next word
    keys("viw") # select inner word
    keys("~") # uppercase it
```

# How do I get it?

Your Vim version must include [`+python`](http://vimdoc.sourceforge.net/htmldoc/various.html#+python) to use Snake. You can check with `:version`.

## Vundle

Add the following line to your Vundle plugin block of your `.vimrc`:

```
Plugin 'amoffat/snake'
```

Re-source your `.vimrc`.  Then `:PluginInstall`

## Pathogen

TODO

## Neobundle

Add the following line to your Neobundle plugin block of your `.vimrc`:

```
NeoBundle 'amoffat/snake'
```

Re-source your `.vimrc`. Then `NeoBundleInstall`

# Where do I write my Snake code?

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

# Design Philosophy

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


# How do I write a plugin?

If your plugin is a package, create (or symlink) a directory inside
`~/.vim/bundle` for your plugin.  Make this directory a Python package by
creating a `__init__.py`

If your plugin is a simple one-file module, just create or symlink that file
into your `~/.vim/bundle` directory.

Next Add `from snake.plugins import <your_plugin>` to `~/.vimrc.py`.  Finally,
Re-source your `~/.vimrc`

For plugin API reference, check out [api\_reference.md](docs/api_reference.md).

# Can I use a virtualenv for my plugin?

Yes!  But it's crazy!

Just include a `requirements.txt` file in your package directory that contains
the `pip freeze` output of all the dependencies you wish to include.  When your
module is imported from `.vimrc.py`, a virtualenv will be automatically created
for your plugin if it does not exist, and your plugin dependencies automatically
installed.

Virtualenvs that are created automatically will use your virtualenv\_wrapper
`WORKON_HOME` environment variable, if one exists, otherwise `~/.virtualenvs`.
And virtualenvs take the name `snake_plugin_<your_plugin_name>`.

## Gotchas

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

There is also the problem of different plugins having different dependency
versions.  For example, if Snake plugin `A` depends on `sh==1.10` and plugin `B`
depends on `sh==1.11`, whichever plugin gets loaded first in `.vimrc.py` will
put *their* `sh` module into `sys.modules`.  Then, when the other plugin loads,
it will attempt to load `sh`, see it is in `sys.modules`, and use that instead,
instead of looking in its virtualenv.

All of this obviously isn't great, and something better needs to be built to
more thoroughly separate virtualenvs from under a single Python process.  I
think what can happen is, for the `SnakePluginHook`, if a `fullname` has more
than 3 paths, drop into the virtualenv for the plugin and run `imp.find_module`.
If the module exists, return `self` as the loader.  Repeat the process in
`load_module` except actually `imp.load_module`.  This way, the dependency
should be loaded into `sys.modules` prefixed by the full plugin name
`snake.plugins.whatever.sh`.


# Contributing

Read [development.md](docs/development.md) for technical info.

## Pull requests

Although Snake is meant to make Vim more scriptable in Python, it is *not* meant
to provide all the nuanced functionality of Vim.  PRs for new features will be
screened by the value-add of the feature weighed against the complexity added to
the api, with favor towards keeping the api simple.


## Snake needs a vundle equivalent

I would like to see an import hook that allows this in your `.vimrc.py`:

```python
from snake import *

something_awesome = __import__("snake.plugins.tpope/something_awesome")
```

Where the import hook checks if the plugin exists in `~/.vim/snake`, and if it
doesn't, looks for a repo to clone at
`https://github.com/tpope/something_awesome`
