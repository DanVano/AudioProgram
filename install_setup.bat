@echo off
echo === AudioProgram Setup ===

:: Optional: check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python 3.8 or newer.
    pause
    exit /b
)

:: Install required packages
echo Installing dependencies...
pip install -r requirements.txt

:: Run the program
echo Launching AudioProgram...
python main.py

pause
