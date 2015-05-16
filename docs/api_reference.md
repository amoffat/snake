TODO please help document this stuff

Cursor
======
* get_cursor_position()
* set_cursor_position(pos)

Convenience
===========
* get_word()
* delete_word()
* replace_word(rep)
* get_in_quotes()

Visual
======
* get_visual_selection()
* replace_visual_selection(rep)
* get_visual_range()

Input
=====
* raw_input(prompt="")

Buffers
=======
* new_buffer()
* set_buffer(buf)
* get_current_buffer()
* get_buffer_in_window()
* get_window_of_buffer(buf)
* set_buffer_contents(buf, s)
* set_buffer_lines(buf, lines)
* get_buffer_contents(buf)
* get_buffer_lines(buf)
* when_buffer_is(filetype)

Windows
=======
* get_current_window()
* get_num_windows()
* new_window(size=None, vertical=False)


Variables
=========
* get(name, namespace=None, scope=NS_GLOBAL)
* let(name, value, namespace=None, scope=NS_GLOBAL)
* multi_let(namespace, **name_values)

Options
=======
* toggle_option(name)
* set_option(name, value=None)
* multi_set_option(*names)
* set_option_default(name)
* unset_option(name)
* set_local_option(name, value=None)

Registers
=========
* get_register(name)
* set_regsiter(name, value)
* clear_register(name)

Key Mapping
===========
* key_map(key, fn_or_command, mode=NORMAL_MODE, recursive=False)
* visual_key_map(key, fn, recursive=False)

Searching
=========
* search(s, wrap=True, backwards=False, move=True)

Misc
====
* keys(k)
* redraw()
