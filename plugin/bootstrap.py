import sys
import vim
sys.path.insert(0, vim.eval("s:current_path"))

def purge(mod_name):
    for check in list(sys.modules.keys()):
        if check.startswith(mod_name + ".") or check == mod_name:
            del sys.modules[check]

purge("snake")
import snake
