Reloading snake
===============

If you've installed snake with vundle, the first thing you might notice is that
re-sourcing your `.vimrc` does not reload snake, so changes you've made will not
be visible in your current vim session.  To get around this, add the following
line to your `.vimrc`:

```
source ~/.vim/bundle/snake/plugin/snake.vim
```

Now when you re-source `.vimrc`, snake will be reloaded, and your `.vimrc.py`
will be re-evaluated.

Punching buttons
================

The first and foremost thing you probably want to do is take some of the vim key
bindings that you know already and put them into functions.  This is
accomplished with `keys(k)`.  The string of keys to press are passed into vim as
if you pressed them yourself.  Often, this is the most basic "unit" of snake
functions, in that all the real work happens through specific key bindings
specified in the function:

```python
@preserve_state()
def delete_word():
    keys("diw")
```


Preserving state
================

Common state
------------

It's important that when your snake function runs, it doesn't steamroll over the
user's current state, unless you're doing it intensionally.  Use the
`preserve_state` context manager to prevent this.  By default, it preserves
cursor position, and yank (0) and delete (") special registers:

```python
@preserve_state()
def do_something():
    keys("BByw")
    return get_register("0")
```

The function above will appear to do nothing to the user's cursor or registers,
when in reality, it jumped back 2 words and yanked a word.

Register state
--------------

The `preserve_state` context manager is nice for general functions, but
sometimes your function will do something very complex with registers, and you
wish to preserve those individual registers.  In those instances, use the
`preserve_registers(*regs)` with-context around your critical section:

```python
def replace_visual_selection(rep):
    with preserve_registers("a"):
        set_register("a", rep)
        keys("gvd")
        keys('"aP')
```

All of the registers passed into `preserve_registers(*regs)` will be restored
after the context completes.

Cursor state
------------


When all else fails
===================

When you can't achieve your goals with existing snake functions, you should
resort to using the [vim](http://vimdoc.sourceforge.net/htmldoc/if_pyth.html)
module that vim's embedded python provides for you.  You can use it to eval
functions/variables/registers:

```python
def get_current_window():
    return int(vim.eval("winnr()"))
```

Or to execute commands:

```python
def set_register(name, val):
    val = escape_string_dq(val)
    vim.command('let @%s = "%s"' % (name, val))
```

If you find yourself using `vim.eval` and `vim.command` directly, ask yourself
if what you're righting can be abstracted further to a more reusable function.

Escaping
========

Two helper functions are provided to escape strings you wish to pass into vim.
These are `escape_string_dq` and `escape_string_sq` for escaping strings to be
surrounded by double quotes and single quotes, respectively.
