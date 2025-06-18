@echo off
echo ========================================
echo   AI-Powered Web Firewall - Setup
echo   Author: Akash Hossain (arknox.in)
echo   License: MIT
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org/
    pause
    exit /b 1
)

echo [1/4] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [4/4] Setup completed successfully!
echo.
echo ========================================
echo   SETUP COMPLETE!
echo ========================================
echo.
echo To run the AI Firewall:
echo 1. Activate virtual environment: venv\Scripts\activate.bat
echo 2. Run the application: python app\main.py
echo 3. Open browser: http://localhost:5000
echo.
echo To run the Hacker Portal (for testing):
echo 1. Navigate to hacker_portal folder: cd hacker_portal
echo 2. Run: python app.py
echo 3. Open browser: http://localhost:5001
echo.
pause
