#!/bin/bash

function check_installed() {
    ## Function will return a 1 if not installed, or 0 if installed
    #    Check exit status with "$?""

    command -v $1 &>/dev/null

}

function fetch_prune() {

    echo "[INFO] Running $ git fetch -p, remove deleted remotes from local branches."
    git fetch -p

}

function remove_local_deleted_from_remote() {
    ## Delete extant local branches

    echo "[INFO] Deleting local branches that have a deleted remote branch."

    git fetch -p

    ## Find deleted origin branches, delete existing local versions
    #  If you want to review branches before deleting, change "xargs git branch -D" to "... branch -d"
    git branch -r | awk '{print $1}' | egrep -v -f /dev/fd/0 <(git branch -vv | grep origin) | awk '{print $1}' | xargs git branch -D || return 1

}

function main() {

    check_installed git
    if [[ ! $? == 0 ]]; then
        echo "[ERROR] git is not installed. Exiting"

        exit 1
    fi

    fetch_prune || 1

    if [[ ! $? == 0 ]]; then
        echo "[ERROR] Running git prune command. Review before continuing."
        read -p "          Press CTRL+C to exit if error is critical."
    fi

    remove_local_deleted_from_remote

    if [[ ! $? == 0 ]]; then
        echo "[ERROR] Error removing extant local branches."

        exit 1
    fi

    exit 0

}

main
