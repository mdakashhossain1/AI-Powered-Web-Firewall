@echo off
echo ========================================
echo   AI-Powered Web Firewall - GitHub Upload
echo   Author: Akash Hossain (arknox.in)
echo   Repository: AI-Powered-Web-Firewall
echo ========================================
echo.

REM Check if git is installed
echo [Step 1] Checking Git installation...
git --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Git is not installed!
    echo.
    echo Please install Git first:
    echo 1. Go to: https://git-scm.com/download/windows
    echo 2. Download and install Git
    echo 3. Restart command prompt
    echo 4. Run this script again
    echo.
    pause
    start https://git-scm.com/download/windows
    exit /b 1
)
echo Git is ready!
echo.

echo [Step 2] Initializing Git repository...
git init
if errorlevel 1 (
    echo ERROR: Failed to initialize repository
    pause
    exit /b 1
)

echo [Step 3] Adding all files...
git add .
if errorlevel 1 (
    echo ERROR: Failed to add files
    pause
    exit /b 1
)

echo [Step 4] Creating initial commit...
git commit -m "Initial commit: AI-Powered Web Firewall

Complete AI security system with:
- Machine Learning threat detection
- Real-time blocking capabilities
- User verification system
- Comprehensive documentation with screenshots
- Hacker portal for testing
- MIT License by Akash Hossain (arknox.in)"

if errorlevel 1 (
    echo ERROR: Failed to commit files
    pause
    exit /b 1
)

echo [Step 5] Setting main branch...
git branch -M main
if errorlevel 1 (
    echo ERROR: Failed to set main branch
    pause
    exit /b 1
)

echo [Step 6] Adding remote repository...
git remote add origin https://github.com/mdakashhossain1/AI-Powered-Web-Firewall.git
if errorlevel 1 (
    echo Remote already exists, updating...
    git remote set-url origin https://github.com/mdakashhossain1/AI-Powered-Web-Firewall.git
)

echo [Step 7] Pushing to GitHub...
echo.
echo NOTE: GitHub may ask for your username and password/token
echo.
git push -u origin main
if errorlevel 1 (
    echo.
    echo ERROR: Push failed!
    echo.
    echo Common solutions:
    echo 1. Make sure you're logged into GitHub
    echo 2. Check your internet connection
    echo 3. Verify repository permissions
    echo.
    echo Try using GitHub Desktop as alternative:
    echo https://desktop.github.com/
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo           SUCCESS!
echo ========================================
echo.
echo Your AI-Powered Web Firewall is now on GitHub!
echo Repository: https://github.com/mdakashhossain1/AI-Powered-Web-Firewall
echo.
echo The README.md will show all your screenshots and documentation.
echo.
echo Author: Akash Hossain
echo Website: arknox.in
echo License: MIT
echo.
pause


