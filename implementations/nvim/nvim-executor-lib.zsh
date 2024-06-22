#!/bin/zsh

source "$(dirname "$(whence -p reg)")/../lib/executor-lib.zsh"

zmodload zsh/net/socket

function .get() {
    printf '%s\n%s' get "$1" | .nvim-comm
}

function .list() {
    echo list | .nvim-comm
}

function .set-no-sync() {
    { printf '%s\n%s\n' set "$1"; cat } | .nvim-comm
}

function .delete-no-sync() {
    printf '%s\n%s' delete "$1" | .nvim-comm
}

function .set-link-list() {
    printf '%s\n%s' set_link_list "${(kpj|:|)RegLinks}" | .nvim-comm
}

function .populate-links() {
    local REG_LINKS="$(echo list_links | .nvim-comm)"

    if [[ -z $REG_LINKS ]]; then
        RegLinks=()
        return
    fi

    RegLinks=()
    local link
    for link in "${(ps|:|)REG_LINKS}"; do
        RegLinks[$link]=1
    done
}

function .nvim-comm() {
    zsocket "$NVIM_REG_SOCKET"
    local conn_fd="$REPLY"

    {
        cat >&$conn_fd
        printf '\0' >&$conn_fd

        local status_code
        read -u $conn_fd status_code

        if [[ "$status_code" == 0 ]]; then
            cat <&$conn_fd || true
        else
            cat <&$conn_fd >&2 || true
        fi

        return $status_code
    } always {
        exec {conn_fd}>&-
    }
}
