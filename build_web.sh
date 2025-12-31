#!/bin/bash

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Install pygbag
echo "Installing/Checking pygbag..."
pip install pygbag

# Build and run
echo "Building and serving web version..."
# Kill anything on port 8000
echo "Stopping any process on port 8000..."
fuser -k 8000/tcp || true

# pygbag main.py builds to build/web and serves at localhost:8000
python3 -m pygbag main.py
