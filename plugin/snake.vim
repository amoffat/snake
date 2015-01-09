python << EOF
import sys
from os.path import expanduser
sys.path.insert(0, "~/.vim/bundle/snake")
import snake
snake = reload(snake)
EOF
