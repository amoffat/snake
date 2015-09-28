TODO please help document this stuff

# Core

### keys(k)

`k` is a string of valid key presses to send to Vim.  These key presses can
include navigation, yanking, deleting, etc.  This is a core function to much of
the functionality Snake provides.

### command(cmd, capture=False)

Runs `cmd` as a Vim command, as if you typed `:cmd`.  If `capture` is `True`,
also return the output of the command.

### expand(stuff)

Expands Vim wildcards and keywords.  For example, `expand("%:p")` will return
the current file as an absolute path.  See also:
http://vimdoc.sourceforge.net/htmldoc/eval.html#expand()

# Cursor

### get_cursor_position()

Returns the current cursor position as a tuple, `(row, column)`.

### set_cursor_position(pos)

Sets the cursor position, where `pos` is a tuple `(row, column)`.

# State Management

These context managers and decorators help keep your functions from messing
around with your current state.  For example, if you had a function that
searched for and counted the number of times "bananas" was said in your buffer,
you would want to use the context manager `with preserve_cursor():` in order to
keep your cursor in the same location before and after your function runs.

### preserve_state()

A convenience decorator that preserves common states.  For example:

```python
@preserve_state
def do_something():
    pass
```

Calling `do_something()` would be as if you called it like this:

```python
with preserve_cursor(), preserve_mode(), preserve_registers():
    do_something()
```

### preserve_cursor()

A with-context manager that preserves the cursor location

### preserve_buffer()

A with-context manager that preserves the current buffer contents.

### preserve_mode()

A with-context manager that doesn't do anything because apparently it's
ridiculously difficult/impossible to get the current mode (visual mode, normal
mode, etc).  Feel free to grind mind against this one if you want to get it
working.

### preserve_registers(\*regs)

A with-context manager that preserves the registers listed in `\*regs`, along
with the special delete register and default yank register.  Use it like this:

```python
with preserve_registers("a"):
    keys('"ayy')
    yanked_line = get_register("a")
```

# Convenience

* get_word()
* delete_word()
* replace_word(rep)
* get_in_quotes()
* get_leader()
* get_runtime_path()
* set_runtime_path(paths)
* multi_command(\*cmds)

# Visual

### get_visual_selection()

Returns the content currently selected in visual mode.

### replace_visual_selection(rep)

Replaces the content currently selected in visual mode with `rep`.

### get_visual_range()

Gets the `((start_row, start_col), (end_row, end_col))` of the visual selection.

# Input

* raw_input(prompt="")

# Buffers

* new_buffer(name, type=BUFFER_SCRATCH)
* get_buffers()
* set_buffer(buf)
* get_current_buffer()
* get_buffer_in_window(win)
* get_num_buffers()
* set_buffer_contents(buf, s)
* set_buffer_lines(buf, lines)
* get_buffer_contents(buf)
* get_current_buffer_contents()
* get_buffer_lines(buf)
* when_buffer_is(filetype)

# Windows

* get_current_window()
* get_num_windows()
* get_window_of_buffer(buf)
* new_window(size=None, vertical=False)


# Variables

### let(name, value, namespace=None, scope=NS_GLOBAL)

Sets a variable.  You typically only need the `name` and `value`.  You can use
different scopes for the variable, like `NS_GLOBAL` ("g") or buffer-local scope.
`namespace` follows the convention of many Vim plugins by prefixing a Vim
variable name with the plugin name.  So something like:

```python
let("switch_buffer", "0", namespace="ctrlp")
```

Seems not super useful now, but it comes in handy with `multi_let`, where you
can define many plugin variables at once.

### get(name, namespace=None, scope=NS_GLOBAL)

Gets a variable's value.

### multi_let(namespace, **name_values)

Let's you batch-define a bunch of variables related to some namespace.  It's
essentially a sequence of `let`s, where the namespace of all of them is the
same.  For example, in my `.vimrc.py`:

```python
multi_let(
    "ctrlp",
    match_window="bottom,order:tbb",
    switch_buffer=0, 
    user_command='ag %s -l --nocolor -U --hidden -g ""',
    working_path_mode="r",
    map="<c-p>",
    cmd="CtrlPBuffer",
)
```

This sets all of my `ctrlp` settings in one go.

# Options

### set_option(name, value=None)

Sets a Vim option, like:

```python
set_option("expandtab")
set_option("textwidth", 80)
```

### get_option(name)

Gets an option's value.

### toggle_option(name)

Toggles an option on and off.

### multi_set_option(\*names)

A convenience function for batch setting options in your `.vimrc.py`:

```python
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

    "incsearch",
    "hlsearch",
)
```

### set_option_default(name)
### unset_option(name)
### set_local_option(name, value=None)

Sets a buffer-local option.

# Registers

* get_register(name)
* set_regsiter(name, value)
* clear_register(name)


# Key Mapping

### key_map(keys, fn_or_command, mode=NORMAL_MODE, recursive=False)

Maps the key-sequence `keys` to a Vim key-sequence or a Python function.  To use
it like you would in regular Vim:

```python
key_map("<leader>sv", ":source $MYVIMRC<CR>")
```

Or to use it with a Python function:

```python
key_map("<leader>t", sync_to_network)
```

`key_map` can also optionally be used as a decorator:

```python
@key_map("<leader>t")
def sync_to_network():
    """ sync this buffer to a remote machine """
```
  
### visual_key_map(key, fn, recursive=False)

Creates a key mapping for visual mode.  What's cool about this function is that
if you attach a Python function to the key-sequence, that function will be
passed the contents of the current visual selection.  And if your function
returns anything other than `None`, it will be used to replace the contents of
the visual selection:

```python
@visual_key_map("<leader>b")
def reverse_everything(selected):
    s = list(selected)
    s.reverse()
    return "".join(s)
```

# Searching

### search(s, wrap=True, backwards=False, move=True)

Returns the `(row, col)` of the string `s`.  By default, it will move the cursor
there.

# Misc

* redraw()
