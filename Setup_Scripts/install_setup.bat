@echo off
echo === AudioProgram Setup ===

:: Go up one directory to the project root
cd ..

:: Optional: check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python 3.8 or newer.
    pause
    exit /b
)

:: Install FFmpeg (required for MP3 conversion via yt-dlp)
echo Installing FFmpeg...
winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements
IF %ERRORLEVEL% NEQ 0 (
    echo Warning: FFmpeg install may have failed or is already installed. Continuing...
)

:: Install required packages
echo Installing Python dependencies...
pip install -r requirements.txt

:: Run the program
echo Launching AudioProgram...
python core/main.py

pause
