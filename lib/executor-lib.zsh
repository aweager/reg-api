#!/bin/zsh

# Usage:
#   Implement the following helper functions, then source this file:
#     - .get
#     - .list
#     - .set-no-sync
#     - .delete-no-sync
#     - .set-link-list
#     - .populate-links
#
# Then reg-impl is ready for use with posix-executor-loop.sh

# TODO validation

typeset -A RegLinks

function reg-impl() {
    local cmd="$1"
    shift

    case "$cmd" in
        get)
            reg-get "$@"
            ;;
        set)
            reg-set "$@"
            ;;
        has)
            reg-has "$@"
            ;;
        delete)
            reg-delete "$@"
            ;;
        list)
            reg-list "$@"
            ;;
        link)
            reg-link "$@"
            ;;
        unlink)
            reg-unlink "$@"
            ;;
        list-links)
            reg-list-links "$@"
            ;;
        sync)
            reg-sync "$@"
            ;;
        publish)
            reg-publish "$@"
            ;;
        *)
            printf 'Unknown reg command %s\n' "$cmd"
            reg-print-usage
            ;;
    esac <&0 >&1 2>&2 &
}

function reg-print-usage() {
    # TODO
    echo "usage not implemented"
    return 1
}

function reg-get() {
    if ! .get "$1"; then
        printf 'Register "%s" not found\n' "$1" >&2
        return 1
    fi
}

function reg-set() {
    .set-no-sync "$1"
    .publish-except "" "$1"
}

function reg-has() {
    .list | grep "^$1\$" > /dev/null
    return $?
}

function reg-delete() {
    if .delete-no-sync "$1"; then
        .publish-except "" "$1"
    fi
}

function reg-list() {
    local REG_LIST="$(.list)"
    if [[ -z "$REG_LIST" ]]; then
        return
    fi

    local -a reg_list=("${(f)REG_LIST}")
    unnamed_index="$reg_list[(Ie)unnamed]"
    if [[ $unnamed_index != 0 ]]; then
        echo unnamed
        reg_list=("${(@)reg_list[1,$unnamed_index - 1]}" "${(@)reg_list[$unnamed_index + 1,-1]}")
    fi

    if [[ -z $reg_list ]]; then
        return
    fi

    printf '%s\n' "$reg_list[@]" | sort
}

function reg-link() {
    .populate-links
    RegLinks[$1]=1
    .sanitize-links
    .set-link-list
}

function reg-list-links() {
    .populate-links
    .sanitize-links
    if [[ -n $RegLinks ]]; then
        printf '%s\n' "${(@k)RegLinks}"
    fi
}

function reg-unlink() {
    .populate-links
    unset "RegLinks[$1]"
    .sanitize-links
    .set-link-list
}

function reg-sync() {
    local from_socket="$1"
    local specific_reg="$2"

    if [[ -n "$specific_reg" ]]; then
        if reg -I "$from_socket" has "$specific_reg"; then
            reg -I "$from_socket" get "$specific_reg" | .set-no-sync "$specific_reg"
        else
            .delete-no-sync "$specific_reg"
        fi
    else
        local THEIRS="$(reg -I "$from_socket" list)"
        local MINE="$(.list)"

        local -a theirs=("${(f)THEIRS}")
        local -a mine=("${(f)MINE}")

        local -a pids

        local reg
        for reg in "$theirs[@]"; do
            if [[ -n "$reg" ]]; then
                reg -I "$from_socket" get "$reg" | .set-no-sync "$reg" &
                pids+=($!)
            fi
        done

        local -T THEIRS theirs "\n"
        for reg in "$mine[@]"; do
            if [[ -n "$reg" && $theirs[(Ie)$reg] -eq 0 ]]; then
                .delete-no-sync "$reg" &
                pids+=($!)
            fi
        done

        wait "$pids[@]"
    fi

    .publish-except "$from_socket" "$specific_reg"
}

function reg-publish() {
    .publish-except "" "$1"
}

function .publish-except() {
    local exclude_link="$1"
    local specific_reg="$2"
    .populate-links
    .sanitize-links

    local link
    local -a pids
    for link in "${(@k)RegLinks}"; do
        if [[ "$link" != "$exclude_link" ]]; then
            reg -I "$link" sync "$REG_SOCKET" "$specific_reg" &
            pids+=($!)
        fi
    done

    wait "$pids[@]"
}

function .sanitize-links() {
    local link
    for link in "${(@k)RegLinks}"; do
        if [[ ! -S "$link" ]]; then
            unset "RegLinks[$link]"
        fi
    done
}
