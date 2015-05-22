python << EOF
import sys
import vim
sys.path.insert(0, vim.eval("expand('<sfile>:p:h')"))

if "snake" in sys.modules:
    snake = reload(snake)
else:
    import snake
EOF
