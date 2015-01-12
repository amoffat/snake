TODO document this stuff

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

Windows
=======
* get_current_window()
* get_num_windows()
* new_window(size=None, vertical=False)

Movement
========
* to_top()

Variables
=========
* get_global(name, namespace=None)
* set_global(name, value, namespace=None)
* multi_set_global(namespace, **name_values)

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

Modes
=====
* set_normal_mode()
* set_visual_mode()

Searching
=========
* search(s, wrap=True, backwards=False, move=True)

Misc
====
* keys(k)
* redraw()
