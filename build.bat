@echo off
echo Starting build process...

echo Cleaning up previous builds...
if exist "build" ( rd /s /q build )
if exist "dist" ( rd /s /q dist )
if exist "*.spec" ( del "*.spec" )

set /p version=<VERSION
echo Building version %version%...

echo Running PyInstaller...
.venv\Scripts\pyinstaller.exe --onefile --windowed --name Mp4ToMp3Converter-v%version% --copy-metadata imageio --copy-metadata moviepy main.py

echo Build complete!
echo The executable can be found in the 'dist' folder.
pause
