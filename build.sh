#!/bin/bash

# 1. Install dependencies (if needed)
pip install pygame nuitka requests Pillow customtkinter

# 2. Cleanup old builds
rm -rf dist
mkdir -p dist

# 3. Build it
# Note: Added --jobs=4 for your i5 and --standalone for easier debugging if onefile fails
python3 -m nuitka --onefile \
    --jobs=4 \
    --include-data-dir=assets=assets \
    --enable-plugin=tk-inter \
    --output-dir=dist \
    -o game \
    main.py

echo "Build complete! Running the game..."

# 4. Auto-run to check for those Nuitka bugs
./dist/game