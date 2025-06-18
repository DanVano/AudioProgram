@echo off
echo Starting Audio Program...
cd ..
if not exist "Core\main.py" (
    echo Error: Core\main.py not found!
    pause
    exit /b 1
)
python Core/main.py
pause
