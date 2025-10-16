@echo off
echo Building main.py with PyInstaller...
pyinstaller --onefile "%~dp0main.py"
echo Done! Check the "dist" folder.
pause
