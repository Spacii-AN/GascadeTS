@echo off
REM Cascade Tile Scanner Launch Script
REM This script will check dependencies and launch the web scanner

echo ========================================
echo   Cascade Tile Scanner Launcher
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python found
python --version

REM Check if requirements are installed
echo.
echo Checking dependencies...
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing dependencies...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed
) else (
    echo [OK] Dependencies already installed
)

REM Launch the scanner
echo.
echo ========================================
echo   Starting Web Scanner...
echo ========================================
echo.
echo The scanner will be available at:
echo   - Local: http://localhost:9000
echo   - Network: http://<your-ip>:9000
echo.
echo Press Ctrl+C to stop the scanner
echo.

python web_scanner.py

pause

