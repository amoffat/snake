# Changelog

## 0.15.4 - 3/3/18
* bugfix with old pip version creating virtualenvs
* bugfix with python3 not having execfile when installing virtualenvs

## 0.15.3 - 3/1/18
* add `set_filetype` for easily associating extensions to file types

## 0.15.2 - 2/14/18
* `delete_word` shouldn't preserve cursor, and it should return word

## 0.15.1 - 2/4/18
* bugfix in escaping strings containing single quotes
* support for `search` only searching current line
* bugfix where snake and plugins were not being reloaded on resourcing vimrc

## 0.15.0 - 2/3/18
* python3 support

## 0.14.3 - 5/16/17
* make visual selection callback argument optional
* bugfix where mode preserving context can yield annoying errors

## 0.14.2 - 5/16/17
* bugfix in restore order of state preservation contexts

## 0.14.1 - 5/13/17
* `preserve_mode` actually does something now
* added `debug(msg, persistent=False)` helper for scripts
* bugfix where a fn decorated with `key_map` wasn't propagating additional options.

## 0.14.0 - 4/8/17
* Fixed `vim.buffers` indexing inconsistency between vim versions
* Added polyfill for missing pyeval in older vim versions
