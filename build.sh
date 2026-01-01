#!/bin/bash

# 1. Install dependencies (if needed)
pip install pygame nuitka requests Pillow PyQt6 breeze-style-sheets

# 2. Cleanup old builds
rm -rf dist
mkdir -p dist

# 3. Build it
python3 -m nuitka --onefile \
    --jobs=4 \
    --include-data-dir=assets=assets \
    --include-package-data=breeze_style_sheets \
    --enable-plugin=pyqt6 \
    --output-dir=dist \
    -o game \
    main.py
