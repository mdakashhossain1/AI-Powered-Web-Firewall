@echo off
echo ========================================
echo AI-Powered Web Firewall Setup Script
echo Author: Akash Hossain
echo Website: arknox.in
echo License: MIT
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [1/6] Python detected successfully
python --version

:: Check if pip is available
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip is not available
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

echo [2/6] pip detected successfully
echo.

:: Create virtual environment
echo [3/6] Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists, skipping creation
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
)
echo.

:: Activate virtual environment
echo [4/6] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo Virtual environment activated
echo.

:: Install dependencies from packages folder if available
echo [5/6] Installing dependencies...
if exist "packages" (
    echo Installing from local packages folder...
    for %%f in (packages\*.whl) do (
        echo Installing %%f...
        pip install "%%f" --force-reinstall --no-deps
    )
    echo Local packages installed
) else (
    echo Local packages folder not found, installing from requirements.txt...
)

:: Install from requirements.txt
if exist "requirements.txt" (
    echo Installing from requirements.txt...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo WARNING: Some packages from requirements.txt failed to install
        echo This might be normal if local packages were already installed
    )
) else (
    echo requirements.txt not found, installing essential packages...
    pip install flask scikit-learn pandas numpy joblib requests opencv-python pillow
)
echo.

:: Check if model file exists
echo [6/6] Checking project files...
if exist "model\firewall_model.pkl" (
    echo Machine learning model found: model\firewall_model.pkl
) else (
    echo WARNING: Machine learning model not found at model\firewall_model.pkl
    echo You may need to train the model first using train_model.py
)

if exist "dataset\nsl_kdd.csv" (
    echo Dataset found: dataset\nsl_kdd.csv
) else (
    echo WARNING: Dataset not found at dataset\nsl_kdd.csv
    echo Please download NSL-KDD dataset and place it in the dataset folder
)

if exist "app\main.py" (
    echo Main application found: app\main.py
) else (
    echo ERROR: Main application file not found at app\main.py
    pause
    exit /b 1
)
echo.

:: Setup complete
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. To run the AI Firewall:
echo    cd app
echo    python main.py
echo.
echo 2. To run the Hacker Portal (for testing):
echo    cd hacker_portal
echo    python app.py
echo.
echo 3. To train the model (if needed):
echo    python train_model.py
echo.
echo 4. The virtual environment is now active
echo    To deactivate it later, run: deactivate
echo.
echo For more information, visit: https://arknox.in
echo Repository: https://github.com/mdakashhossain1/AI-Powered-Web-Firewall
echo ========================================
echo.
pause
