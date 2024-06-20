#!/bin/zsh

zmodload zsh/zutil

function start-tmux-reg() {
    setopt local_options err_return

    local -x TMUX="$1"
    export REG_SOCKET="$2"

    command-server-start ~/projects/reg-api/implementations/tmux/server.conf --socket "$2" --log-file "$3"
}
