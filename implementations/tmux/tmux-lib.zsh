#!/bin/zsh

# TODO validation

typeset REG_LINKS
typeset -a reg_links
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
    tmux save-buffer -b "reg_$1" -
}

function reg-set() {
    .set-no-sync "$1"
    .publish "" "$1"
}

function reg-has() {
    reg-list | grep "^$1\$" > /dev/null
    return $?
}

function reg-delete() {
    .delete-no-sync "$1"
    .publish "" "$1"
}

function reg-list() {
    tmux list-buffers -f '#{?#{m:reg_*,#{buffer_name}},yes,}' -F '#{s|reg_||:buffer_name}' | sort
}

function reg-link() {
    .add-link "$1"
}

function reg-list-links() {
    .populate-links
    printf '%s\n' "$reg_links[@]"
}

function reg-unlink() {
    .populate-links
    unset RegLinks[$link]

    tmux set-option @reg_links ":${(kj|:|)RegLinks}"
}

function reg-sync() {
    .add-link "$1"
    reg -I "$1" link "$REG_SOCKET"

    if [[ -n "$2" ]]; then
        if reg -I "$1" has "$2"; then
            reg -I "$1" get "$2" | .set-no-sync "$2"
        else
            .delete-no-sync "$2"
        fi

        .publish "$1" "$2"
    else
        local THEIRS="$(reg -I "$1" list)"
        local MINE="$(reg-list)"

        local -a theirs=("${(f)THEIRS}")
        local -a mine=("${(f)MINE}")

        local -a pids

        local reg
        for reg in "$theirs[@]"; do
            reg -I "$1" get "$reg" | .set-no-sync "$reg" &
            pids+=($!)
        done

        local -T THEIRS theirs "\n"
        for reg in "$mine[@]"; do
            if [[ $theirs[(Ie)$reg] -eq 0 ]]; then
                .delete-no-sync "$reg" &
                pids+=($!)
            fi
        done

        wait "$pids[@]"

        .publish "$1" ""
    fi
}

function .populate-links() {
    REG_LINKS="$(tmux display-message -p '#{@reg_links}')"
    REG_LINKS="${REG_LINKS#:}"

    if [[ -z $REG_LINKS ]]; then
        reg_links=()
        RegLinks=()
        return
    fi

    reg_links=("${(ps|:|)REG_LINKS}")
    typeset -U reg_links

    RegLinks=()
    local link
    for link in "$reg_links[@]"; do
        RegLinks[$link]=1
    done
}

function .publish() {
    local exclude_link="$1"

    .populate-links

    local link
    local -a pids
    for link in "$reg_links[@]"; do
        if [[ "$link" != "$exclude_link" ]]; then
            if [[ -n "$2" ]]; then
                reg -I "$link" sync "$REG_SOCKET" "$2" &
            else
                reg -I "$link" sync "$REG_SOCKET" &
            fi
            pids+=($!)
        fi
    done

    wait "$pids[@]"
}

function .set-no-sync() {
    tmux load-buffer -b "reg_$1" -
}

function .delete-no-sync() {
    tmux delete-buffer -b "reg_$1"
}

function .add-link() {
    .populate-links
    RegLinks[$1]=1
    tmux set-option @reg_links "${(kpj|:|)RegLinks}"
}
