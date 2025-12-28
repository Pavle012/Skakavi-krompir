#!/bin/bash
# An updater script for Linux systems
# works by downloading the latest version from github and replacing the current one
# should only work for compiled version of the game

# This script assumes the game executable is named "Skakavi Krompir-Linux"
# and is located in the same directory as this script.

set -e # exit on error

# --- Configuration ---
# GitHub repository in the format OWNER/REPO
REPO="Pavle012/Skakavi-krompir"
# The name of the release asset to download
ASSET_NAME="Skakavi Krompir-Linux"
# The name of the game executable to be replaced
GAME_EXECUTABLE="Skakavi Krompir-Linux"
# ---------------------

API_URL="https://api.github.com/repos/$REPO/releases/latest"

# Get the directory where the script is located
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
GAME_PATH="$SCRIPT_DIR/$GAME_EXECUTABLE"

if [ ! -f "$GAME_PATH" ]; then
    echo "Error: Game executable not found at '$GAME_PATH'"
    echo "Please make sure the updater is in the same directory as the game executable ('$GAME_EXECUTABLE')."
    exit 1
fi

echo "Fetching latest release information from $REPO..."

# Get the download URL for the linux asset using curl and grep
# This is a bit fragile; using jq would be more robust, but this avoids a dependency.
DOWNLOAD_URL=$(curl -s $API_URL | grep "browser_download_url.*$ASSET_NAME" | cut -d '"' -f 4)

if [ -z "$DOWNLOAD_URL" ]; then
    echo "Could not find a download URL for the asset '$ASSET_NAME'."
    echo "There might be no new release, or the asset name has changed."
    echo "Please check the releases page: https://github.com/$REPO/releases"
    exit 1
fi

echo "Found download URL: $DOWNLOAD_URL"
echo "Downloading latest version..."

# Download to a temporary file to avoid corruption
TEMP_FILE=$(mktemp)
wget -q --show-progress -O "$TEMP_FILE" "$DOWNLOAD_URL"

echo "Download complete. Replacing the old version..."

# Make the downloaded file executable
chmod +x "$TEMP_FILE"

# Replace the old game executable with the new one
mv "$TEMP_FILE" "$GAME_PATH"

echo "Update complete! '$GAME_EXECUTABLE' has been updated to the latest version."
echo "You can now run the game."