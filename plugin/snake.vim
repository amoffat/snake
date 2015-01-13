python << EOF
import sys
from os.path import expanduser
sys.path.insert(0, expanduser("~/.vim/bundle/snake/plugin"))

if "snake" in sys.modules:
    snake = reload(snake)
else:
    import snake
EOF
