#!/bin/sh
# Lyrebird installer script. If running as root then will install at /usr/local/{bin,share},
# otherwise will install at ~/.local/{bin,share}.

VERBOSE=${VERBOSE:-0}
DRYRUN=${DRYRUN:-0}

# Initial setup

if [ $DRYRUN = 1 ]; then DRYRUN_INFO=" (dryrun)"; fi
ECHO_PREFIX="[lyrebird]$DRYRUN_INFO"

info_echo() {
    echo "$ECHO_PREFIX $1"
}

warning_echo() {
    echo "[warning]$DRYRUN_INFO $1"
}

verbose_echo() {
    if [ $VERBOSE = 1 ]; then
        echo "$ECHO_PREFIX $1"
    fi
}

delete_file() {
    if [ -f "$1" ]; then
        if [ $2 -eq 1 ] && [ "$(id -u)" -ne 0 ]; then
            warning_echo "Cannot delete without root access: $1"
            return
        fi
        info_echo "Deleting: $1"
        if [ $DRYRUN != 1 ]; then rm "$1"; fi
    else
        verbose_echo "File not present, skipping: $1"
    fi
}

delete_dir() {
    if [ -d "$1" ]; then
        if [ $2 -eq 1 ] && [ "$(id -u)" -ne 0 ]; then
            warning_echo "Cannot delete without root access: $1"
            return
        fi
        info_echo "Deleting: $1"
        if [ $DRYRUN != 1 ]; then rm -rf "$1"; fi
    else
        verbose_echo "Directory not present, skipping: $1"
    fi
}

delete_dir "/usr/local/bin/lyrebird/" 1
delete_dir "/usr/local/share/lyrebird/" 1
delete_file "/usr/local/bin/lyrebird" 1

delete_dir "/etc/lyrebird/" 1

delete_dir "$HOME/.local/share/lyrebird/" 0
delete_file "$HOME/.local/bin/lyrebird" 0

delete_dir "$HOME/.config/lyrebird/" 0

delete_file "/usr/local/share/applications/Lyrebird.desktop" 1
delete_file "$HOME/.local/share/applications/Lyrebird.desktop" 0