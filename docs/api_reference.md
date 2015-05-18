TODO please help document this stuff

# Core

## keys(k)

`k` is a string of valid key presses to send to Vim.  These key presses can
include navigation, yanking, deleting, etc.  This is a core function to much of
the functionality Snake provides.

## command(cmd, capture=False)

Runs `cmd` as a Vim command, as if you typed `:cmd`.  If `capture` is `True`,
also return the output of the command.

## expand(stuff)

Expands Vim wildcards and keywords.  For example, `expand("%:p")` will return
the current file as an absolute path.  See also:
http://vimdoc.sourceforge.net/htmldoc/eval.html#expand()

# Cursor

## get_cursor_position()

Returns the current cursor position as a tuple, `(row, column)`.

## set_cursor_position(pos)

Sets the cursor position, where `pos` is a tuple `(row, column)`.

# State Management

These context managers and decorators help keep your functions from messing
around with your current state.  For example, if you had a function that
searched for and counted the number of times "bananas" was said in your buffer,
you would want to use the context manager `with preserve_cursor():` in order to
keep your cursor in the same location before and after your function runs.

* preserve_state()
* preserve_cursor()
* preserve_buffer()
* preserve_mode()
* preserve_registers(\*regs)

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

* get_visual_selection()
* replace_visual_selection(rep)
* get_visual_range()

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

* get(name, namespace=None, scope=NS_GLOBAL)
* let(name, value, namespace=None, scope=NS_GLOBAL)
* multi_let(namespace, **name_values)

# Options

* toggle_option(name)
* set_option(name, value=None)
* multi_set_option(*names)
* set_option_default(name)
* unset_option(name)
* set_local_option(name, value=None)

# Registers

* get_register(name)
* set_regsiter(name, value)
* clear_register(name)


# Key Mapping

* key_map(key, fn_or_command, mode=NORMAL_MODE, recursive=False)
* visual_key_map(key, fn, recursive=False)

# Searching

* search(s, wrap=True, backwards=False, move=True)

# Misc

* redraw()
