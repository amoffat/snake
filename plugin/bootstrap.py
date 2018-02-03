import sys
import vim
sys.path.insert(0, vim.eval("s:current_path"))

if "snake" in sys.modules:
    snake = reload(snake)
else:
    import snake
