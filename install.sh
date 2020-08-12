#!/bin/bash
# Lyrebird installer script. Copies the source code to /usr/local/bin
# and copies the desktop file to /usr/local/share/applications.

BIN_PATH="/usr/local/bin/lyrebird/"
DESKTOP_PATH="/usr/local/share/applications/"

# Create both of the directories if they don't exist
if [ ! -d "$BIN_PATH" ]; then
    mkdir -p "$BIN_PATH"
    echo "$BIN_PATH didn't exist before, just created it"
fi

if [ ! -d "/usr/local/share/applications/" ]; then
    mkdir -p "/usr/local/share/applications/"
    echo "/usr/local/share/applications/ didn't exist before, just created it"
fi

install_binary_source() {
    cp -rf src "$BIN_PATH"
    cp icon.png "$BIN_PATH"
    cp presets.toml "$BIN_PATH"
    cp app.py "$BIN_PATH"
}

install_desktop() {
    # Copy the desktop file to
    cp Lyrebird.desktop "$DESKTOP_PATH"
}

install_binary_source
install_desktop

echo "Installed Lyrebird to $BIN_PATH"
echo "Installed Lyrebird.desktop to $DESKTOP_PATH"