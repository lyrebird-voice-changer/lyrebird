#!/bin/sh
# Lyrebird installer script. Copies the source code to Python path
# and copies the desktop file to $PREFIX/share/applications.

[ "$(id -u)" != 0 ] && { echo "The installer must be run as root." ; exit 1 ; }

INSTALL_PREFIX="${INSTALL_PREFIX:-/usr/local}"
CONFIG_PATH="/etc/lyrebird"

if [[ $EUID -ne 0 ]]; then
    INSTALL_PREFIX="$HOME/.local"
    CONFIG_PATH="$HOME/.config/lyrebird"
fi

BIN_PATH="$INSTALL_PREFIX/bin"
SHARE_PATH="$INSTALL_PREFIX/share/lyrebird"
DESKTOP_PATH="$INSTALL_PREFIX/share/applications/"
PYTHON_VERSION=$(python3 --version | grep -Po '3\.\d')
PYTHON_PATH="$INSTALL_PREFIX/lib/python$PYTHON_VERSION/site-packages"

# Required pip3 modules space separated
REQUIRED_PIP_MODULES="toml"

# Create all of the directories if they don't exist
if [ ! -d "$BIN_PATH" ]; then
    mkdir -p "$BIN_PATH"
    chmod -R 755 "$BIN_PATH"
    echo "$BIN_PATH didn't exist before, just created it"
fi

if [ ! -d "$SHARE_PATH" ]; then
    mkdir -p "$SHARE_PATH"
    chmod -R 755 "$SHARE_PATH"
    echo "$SHARE_PATH didn't exist before, just created it"
fi

if [ ! -d "$PYTHON_PATH" ]; then
    mkdir -p "$PYTHON_PATH"
    chmod -R 755 "$PYTHON_PATH"
    echo "$PYTHON_PATH didn't exist before, just created it"
fi

if [ ! -d "$DESKTOP_PATH" ]; then
    mkdir -p "$DESKTOP_PATH"
    echo "$DESKTOP_PATH didn't exist before, just created it"
fi

if [ ! -d "$CONFIG_PATH" ]; then
    mkdir -p "$CONFIG_PATH"
    echo "$CONFIG_PATH didn't exist before, just created it"
fi

install_python_modules() {
    echo "Installing required pip3 modules"
    # Var not included in quotes so it installs each module
    pip3 install --prefix $INSTALL_PREFIX $REQUIRED_PIP_MODULES
}

create_config() {
    tee "$CONFIG_PATH/config.toml" <<-EOF
# Configuration file for Lyrebird
# The following parameters are configurable

# buffer_size = The buffer size to use for sox. Higher = better quality, at
# the cost of higher latency. Default value is 1024

[[config]]
buffer_size = 1024
EOF
}

install_binary_source() {
    cp -rf lyrebird "$PYTHON_PATH"
    cp icon.png "$SHARE_PATH"
    cp app.py "$SHARE_PATH"
    cp entrypoint.sh "$BIN_PATH/lyrebird"
    chmod +x "$BIN_PATH/lyrebird"

    # Copy presets.toml to .config/lyrebird
    cp presets.toml "$CONFIG_PATH"

    # Create the config file if it doesn't exist already
    if [ ! -f "$CONFIG_PATH/config.toml" ]; then
        create_config
    fi
}

install_desktop() {
    # Copy the desktop file to
    BIN_PATH=$BIN_PATH SHARE_PATH=$SHARE_PATH envsubst < Lyrebird.desktop > $DESKTOP_PATH/Lyrebird.desktop
    chmod -R 644 "$DESKTOP_PATH/Lyrebird.desktop"
}

install_python_modules
install_binary_source
install_desktop

echo "Installed Lyrebird to $SHARE_PATH"
echo "Installed Lyrebird.desktop to $DESKTOP_PATH"
