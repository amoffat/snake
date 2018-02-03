" contains custom vimscript stuff sourced by snake and the tests
exec "source " . expand("<sfile>:p:h") . "/snake/prelude.vim"

let bootstrap=expand("<sfile>:p:h") . "/snake/bootstrap.py"

if has("python")
    exec "pyfile " . bootstrap
elseif has("python3")
    exec "py3file " . bootstrap
else
    echo "No Python available!"
endif
