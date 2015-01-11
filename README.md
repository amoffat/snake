Snake
=====

Snake lets you use Python to its fullest extent to write powerful vim plugins:

```python
from snake import *

def toggle_boolean():
    """ takes the current boolean value and inverts it """
    word = get_word()
    mapping = {
        "True": "False",
        "true": "false",
        "False": "True",
        "false": "true",
        "0": "1",
        "1": "0",
    }
    opp = mapping.get(word)
    if opp:
        replace_word(opp)

key_map("<leader>b", toggle_boolean)
```

Why do you want this?
=====================

Because the learning curve and pain of vimscript is discouraging.

How do I write a plugin?
========================

Simple:

* Create a folder for your plugin in `~/.vim/snake` or symlink it there.
* Add an `__init__.py` package containing your plugin code.
* Add `from snake.plugins import <your_package>` to `~/.vimrc.py`

Can I use a virtualenv for my plugin?
=====================================

Yes!

Just include a `requirements.txt` file in your package directory that contains
the `pip freeze` output of all the dependencies you wish to include.  When your
module is imported from `.vimrc.py`, a virtualenv will be automatically created
for your plugin, and your plugin dependencies automatically installed.

Show me another example
=======================
