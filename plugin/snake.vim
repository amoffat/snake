let s:current_path=expand("<sfile>:p:h")
function! LoadSnake()
" contains custom vimscript stuff sourced by snake and the tests
exec "source " . s:current_path . "/snake/prelude.vim"

python << EOF
import sys
import vim
sys.path.insert(0, vim.eval('s:current_path'))

if "snake" in sys.modules:
    snake = reload(snake)
else:
    import snake
EOF
endfunction

call LoadSnake()

" Load snake once again so that it invalidates the function mappings
" from the session file.
autocmd SessionLoadPost * call LoadSnake()
