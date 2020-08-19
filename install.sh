#!/bin/sh
# Lyrebird installer script. If running as root then will install at /usr/local/{bin,share},
# otherwise will install at ~/.local/{bin,share}.

VERSION="1.1"

VERBOSE=${VERBOSE:-1}
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

if [ "$(id -u)" -eq 0 ]; then
    INSTALL_PREFIX="${INSTALL_PREFIX:-/usr/local}"
else
    INSTALL_PREFIX="${INSTALL_PREFIX:-$HOME/.local}"
fi
verbose_echo "Installing Lyrebird to prefix: ${INSTALL_PREFIX}"

BIN_PATH="$INSTALL_PREFIX/bin"
SHARE_PATH="$INSTALL_PREFIX/share/lyrebird"
DESKTOP_PATH="$INSTALL_PREFIX/share/applications"

python_version_check() {
    PYTHON_VERSION=$(python3 --version | grep -Po '3\.\d')

    PYTHON_MIN_MAJOR=3
    PYTHON_MIN_MINOR=7

    PYTHON_MAJOR=${PYTHON_VERSION%.*}
    PYTHON_MINOR=${PYTHON_VERSION#*.}

    invalid_python() {
        info_echo "Lyrebird requires Python version 3.7 or higher"
    }

    if [ "$PYTHON_MAJOR" -lt "$PYTHON_MIN_MAJOR" ]; then
        invalid_python
        exit 1
    elif [ "$PYTHON_MAJOR" -eq "$PYTHON_MIN_MAJOR" ] && [ "$PYTHON_MINOR" -lt "$PYTHON_MIN_MINOR" ]; then
        invalid_python
        exit 1
    fi
}
python_version_check

# Removing previous versions
remove_deprecated_install() {
    if [ -d "$1" ] || [ -f "$1" ] ; then
        if [ $2 -eq 1 ] && [ "$(id -u)" -ne 0 ]; then
            warning_echo "Deprecated install location found, cannot remove without root access: $1"
            return
        fi

        info_echo "Removing old install location: $1"
        if [ $DRYRUN != 1 ]; then rm -rf $1; fi
    fi
}
remove_deprecated_install "/usr/local/bin/lyrebird/" 1
if [ "$(id -u)" -ne 0 ]; then
    remove_deprecated_install "/usr/local/share/applications/Lyrebird.desktop" 1
fi

if [ -d "/etc/lyrebird/" ]; then
    warning_echo "/etc/lyrebird/ is now deprecated, please relocate contents to ~/.config/lyrebird/ and delete"
fi

# Required pip3 modules space separated
REQUIRED_PIP_MODULES="toml"

# Create all of the directories if they don't exist
if [ ! -d "$BIN_PATH" ]; then
    verbose_echo "Creating binary path: $BIN_PATH"
    if [ $DRYRUN != 1 ]; then
        mkdir -p "$BIN_PATH"
        chmod -R 755 "$BIN_PATH"
    fi
fi

if [ ! -d "$SHARE_PATH" ]; then
    verbose_echo "Creating share path: $SHARE_PATH"
    if [ $DRYRUN != 1 ]; then
        mkdir -p "$SHARE_PATH"
        chmod -R 755 "$SHARE_PATH"
    fi
fi

if [ ! -d "$DESKTOP_PATH" ]; then
    verbose_echo "Creating desktop path: $DESKTOP_PATH"
    if [ $DRYRUN != 1 ]; then
        mkdir -p "$DESKTOP_PATH"
    fi
fi

install_python_modules() {
    verbose_echo "Installing Python modules: $REQUIRED_PIP_MODULES"
    if [ $DRYRUN != 1 ]; then
        # Var not included in quotes so it installs each module
        pip3 install --prefix $INSTALL_PREFIX $REQUIRED_PIP_MODULES
    fi
}

install_binary_source() {
    verbose_echo "Copying lyrebird/ to: $SHARE_PATH"
    if [ $DRYRUN != 1 ]; then cp -rf lyrebird "$SHARE_PATH"; fi

    verbose_echo "Copying icon.png to: $SHARE_PATH"
    if [ $DRYRUN != 1 ]; then cp icon.png "$SHARE_PATH"; fi

    verbose_echo "Copying app.py to: $SHARE_PATH"
    if [ $DRYRUN != 1 ]; then cp app.py "$SHARE_PATH"; fi

    verbose_echo "Copying entrypoint.sh (lyrebird) to: $BIN_PATH"
    if [ $DRYRUN != 1 ]; then cp entrypoint.sh "$BIN_PATH/lyrebird"; fi

    verbose_echo "Setting permissions 755 recursively for: $SHARE_PATH"
    if [ $DRYRUN != 1 ]; then chmod -R 755 "$SHARE_PATH"; fi
}

install_desktop() {
    verbose_echo "Copying Lyrebird.desktop to: $DESKTOP_PATH"
    if [ $DRYRUN != 1 ]; then BIN_PATH=$BIN_PATH SHARE_PATH=$SHARE_PATH envsubst < Lyrebird.desktop > $DESKTOP_PATH/Lyrebird.desktop; fi

    verbose_echo "Setting permission 644 for: $DESKTOP_PATH/Lyrebird.desktop"
    if [ $DRYRUN != 1 ]; then chmod -R 644 "$DESKTOP_PATH/Lyrebird.desktop"; fi
}

verbose_space() { if [ $VERBOSE = 1 ]; then echo; fi }

install_python_modules
verbose_space

install_binary_source
verbose_space

install_desktop
verbose_space

info_echo "Installed Lyrebird v$VERSION"
