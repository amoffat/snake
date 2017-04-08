" contains custom vimscript stuff sourced by snake and the tests
exec "source " . expand("<sfile>:p:h") . "/snake/prelude.vim"

python << EOF
import sys
import vim
sys.path.insert(0, vim.eval("expand('<sfile>:p:h')"))

if "snake" in sys.modules:
    snake = reload(snake)
else:
    import snake
EOF
