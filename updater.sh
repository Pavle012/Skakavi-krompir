#!/bin/bash
# An updater script for Linux systems
# works by downloading the latest version from github and replacing the current one
# should only work for compiled version of the game

# This script takes one argument: the path to the game executable to update.

set -e # exit on error

# --- Configuration ---
# GitHub repository in the format OWNER/REPO
REPO="Pavle012/Skakavi-krompir"
# ---------------------

API_URL="https://api.github.com/repos/$REPO/releases/latest"

# Check for game path argument
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <path_to_game_executable>"
    exit 1
fi

GAME_PATH=$1
GAME_FILENAME=$(basename "$GAME_PATH")

if [ ! -f "$GAME_PATH" ]; then
    echo "Error: Game executable not found at '$GAME_PATH'"
    exit 1
fi

ARCH=$(uname -m)
case "$ARCH" in
    x86_64|amd64)
        ARCH_TAG="amd64"
        ;;
    aarch64|arm64)
        ARCH_TAG="arm64"
        ;;
    *)
        echo "Unsupported architecture: $ARCH"
        exit 1
        ;;
esac
ASSET_NAME="Skakavi-Krompir-Linux-${ARCH_TAG}"

echo "Fetching latest release information from $REPO..."

echo "Looking for Linux release asset: $ASSET_NAME"

# Resolve the exact asset URL from the release JSON rather than using an
# ambiguous grep prefix match. This avoids picking up the .flatpak bundle.
DOWNLOAD_URL=$(curl -fsSL "$API_URL" | python3 -c 'import json,sys; data=json.load(sys.stdin); assets=data.get("assets",[]); matches=[a.get("browser_download_url") for a in assets if a.get("name") == sys.argv[1]]; print(matches[0] if matches else "")' "$ASSET_NAME")

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

echo "Update complete! '$GAME_FILENAME' has been updated to the latest version."
echo "Running the game now..."
# Run the updated game
"$GAME_PATH"