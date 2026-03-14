# MP4 to MP3 Converter

A simple desktop application to convert video files (e.g., MP4) into audio files (MP3). It features a user-friendly graphical interface and supports drag-and-drop functionality.

## Features

-   **Easy to Use**: Simple and intuitive graphical user interface.
-   **File Selection**: Supports both clicking a button to select a file or dragging and dropping a file onto the application window.
-   **Cross-Platform**: Built with Python, making it compatible with Windows, macOS, and Linux.
-   **Standalone Executable**: Can be packaged into a single executable file for easy distribution and use without a Python installation.

## Requirements

### For End-Users (Using the Executable)

-   A compatible operating system (e.g., Windows 10/11). No other dependencies are needed.

### For Developers

-   Python 3.8+
-   A virtual environment tool (recommended)

## How to Use

### For End-Users

1.  Download the `Mp4ToMp3Converter-vX.X.X.exe` file from the `dist` folder (where `X.X.X` is the version number).
2.  Double-click `Mp4ToMp3Converter-vX.X.X.exe` to run the application.
3.  Click the "Select MP4 File" button and choose your video file, or simply drag and drop your file onto the window.
4.  The conversion will start automatically, and the resulting MP3 file will be saved in the same directory as the original video file.

### For Developers

#### 1. Setup

First, clone the repository and set up a virtual environment:

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate

# Install the required packages
pip install -r requirements.txt
```

#### 2. Running the Application

To run the application from the source code, execute the following command:

```bash
python main.py
```

## How to Build from Source

If you want to create the standalone executable from the source code, you can use the provided build scripts.

**On Windows:**

Simply double-click the `build.bat` file.

**On macOS/Linux (using Git Bash on Windows):**

Run the following command in your terminal:

```bash
./build.sh
```

The generated executable will be located in the `dist/` directory.

## Versioning

This project uses a `VERSION` file to manage the release version. To create a new release, update the version number in this file before running the build script. The build script will automatically append the version number to the executable name.

## License

This project is licensed under the Apache-2.0 License - see the [LICENSE](LICENSE) file for details.
