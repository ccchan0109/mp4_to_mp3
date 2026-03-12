@echo off
echo Starting build process...

echo Cleaning up previous builds...
if exist "build" ( rd /s /q build )
if exist "dist" ( rd /s /q dist )
if exist "main.spec" ( del main.spec )

echo Running PyInstaller...
.venv\Scripts\pyinstaller.exe --onefile --windowed --copy-metadata imageio --copy-metadata moviepy main.py

echo Build complete!
echo The executable can be found in the 'dist' folder.
pause
