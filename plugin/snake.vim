let s:current_path=expand("<sfile>:p:h")

function! LoadSnake()
    " contains custom vimscript stuff sourced by snake and the tests
    exec "source " . s:current_path . "/prelude.vim"

    let bootstrap=s:current_path . "/bootstrap.py"

    if has("python")
        exec "pyfile " . bootstrap
    elseif has("python3")
        exec "py3file " . bootstrap
    else
        echo "No Python available!"
    endif
endfunction

call LoadSnake()

" Load snake once again so that it invalidates the function mappings
" from the session file.
autocmd SessionLoadPost * call LoadSnake()
