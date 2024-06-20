#!/bin/zsh

source "${0:h}/tmux-lib.zsh"

set -- reg-impl "$@"
source "${COMMAND_SERVER_LIB}/posix-executor-loop.sh"
