#!/bin/bash

echo "Starting build process..."

echo "Cleaning up previous builds..."
rm -rf build
rm -rf dist
rm -f *.spec

version=$(cat VERSION)
echo "Building version $version..."

echo "Running PyInstaller..."
# Note: The path might need to be adjusted depending on the shell environment.
# This path is tailored for Git Bash on Windows.
./.venv/Scripts/pyinstaller --onefile --windowed --name "Mp4ToMp3Converter-v$version" --copy-metadata imageio --copy-metadata moviepy main.py

echo "Build complete!"
echo "The executable can be found in the 'dist' folder."

# Keep the window open until a key is pressed
read -p "Press any key to continue..."
