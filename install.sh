#!/bin/bash
# Lyrebird installer script. Copies the source code to /usr/local/bin
# and copies the desktop file to /usr/local/share/applications.

BIN_PATH="/usr/local/bin/lyrebird/"
DESKTOP_PATH="/usr/local/share/applications/"
CONFIG_PATH="/home/$USER/.config/lyrebird/"

# Create all of the directories if they don't exist
if [ ! -d "$BIN_PATH" ]; then
    sudo mkdir -p "$BIN_PATH"
    echo "$BIN_PATH didn't exist before, just created it"
fi

if [ ! -d "/usr/local/share/applications/" ]; then
    sudo mkdir -p "$DESKTOP_PATH"
    echo "$DESKTOP_PATH didn't exist before, just created it"
fi

if [ ! -d "$CONFIG_PATH" ]; then
    sudo mkdir -p "$CONFIG_PATH"
    echo "$CONFIG_PATH didn't exist before, just created it"
fi

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
    sudo cp -rf src "$BIN_PATH"
    sudo cp icon.png "$BIN_PATH"
    sudo cp app.py "$BIN_PATH"

    # Copy presets.toml to .config/lyrebird
    sudo cp presets.toml "$CONFIG_PATH"

    # Create the config file if it doesn't exist already
    if [ ! -f "$CONFIG_PATH/config.toml" ]; then
        create_config
    fi
}

install_desktop() {
    # Copy the desktop file to
    sudo cp Lyrebird.desktop "$DESKTOP_PATH"
}

install_binary_source
install_desktop

echo "Installed Lyrebird to $BIN_PATH"
echo "Installed Lyrebird.desktop to $DESKTOP_PATH"