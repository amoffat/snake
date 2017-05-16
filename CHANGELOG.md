# Changelog

## 0.14.2 - 5/16/17
* bugfix in restore order of state preservation contexts

## 0.14.1 - 5/13/17
* `preserve_mode` actually does something now
* added `debug(msg, persistent=False)` helper for scripts
* bugfix where a fn decorated with `key_map` wasn't propagating additional options.

## 0.14.0 - 4/8/17
* Fixed `vim.buffers` indexing inconsistency between vim versions
* Added polyfill for missing pyeval in older vim versions
