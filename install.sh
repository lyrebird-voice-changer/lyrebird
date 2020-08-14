#!/bin/sh
# Lyrebird installer script. Copies the source code to /usr/local/bin
# and copies the desktop file to /usr/local/share/applications.

[ "$(id -u)" != 0 ] && { echo "The installer must be run as root." ; exit 1 ; }

BIN_PATH="/usr/local/bin/lyrebird/"
DESKTOP_PATH="/usr/local/share/applications/"
CONFIG_PATH="/etc/lyrebird"

# Required pip3 modules space separated
REQUIRED_PIP_MODULES="toml"

# Create all of the directories if they don't exist
if [ ! -d "$BIN_PATH" ]; then
    mkdir -p "$BIN_PATH"
    echo "$BIN_PATH didn't exist before, just created it"
fi

if [ ! -d "/usr/local/share/applications/" ]; then
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
    pip3 install $REQUIRED_PIP_MODULES
}

create_config() {
    sudo tee "$CONFIG_PATH/config.toml" <<-EOF
# Configuration file for Lyrebird
# The following parameters are configurable

# buffer_size = The buffer size to use for sox. Higher = better quality, at
# the cost of higher latency. Default value is 1024

[[config]]
buffer_size = 1024
EOF
}

install_binary_source() {
    cp -rf lyrebird "$BIN_PATH"
    cp icon.png "$BIN_PATH"
    cp app.py "$BIN_PATH"

    # Copy presets.toml to .config/lyrebird
    cp presets.toml "$CONFIG_PATH"

    # Create the config file if it doesn't exist already
    if [ ! -f "$CONFIG_PATH/config.toml" ]; then
        create_config
    fi

    chmod -R 755 "$BIN_PATH"
    chmod -R 755 "$CONFIG_PATH"
}

install_desktop() {
    # Copy the desktop file to
    cp Lyrebird.desktop "$DESKTOP_PATH"
    chmod -R 644 "$DESKTOP_PATH/Lyrebird.desktop"
}

install_python_modules
install_binary_source
install_desktop

echo "Installed Lyrebird to $BIN_PATH"
echo "Installed Lyrebird.desktop to $DESKTOP_PATH"
