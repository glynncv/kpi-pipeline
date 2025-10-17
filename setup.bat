@echo off
REM Setup script for KPI Pipeline (Windows)

echo ==================================================
echo KPI Pipeline - Setup Script
echo ==================================================
echo.

REM Check Python version
echo [1/4] Checking Python version...
python --version
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.9 or higher.
    pause
    exit /b 1
)
echo [OK] Python found

REM Create virtual environment
echo.
echo [2/4] Creating virtual environment...
if exist .venv (
    echo [INFO] Virtual environment already exists
) else (
    python -m venv .venv
    echo [OK] Virtual environment created
)

REM Activate virtual environment
echo.
echo [3/4] Activating virtual environment...
call .venv\Scripts\activate.bat
echo [OK] Virtual environment activated

REM Install requirements
echo.
echo [4/4] Installing requirements...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo [OK] Requirements installed

echo.
echo ==================================================
echo [SUCCESS] Setup completed successfully!
echo ==================================================
echo.
echo To activate the virtual environment, run:
echo   .venv\Scripts\activate
echo.
echo To run the pipeline:
echo   python main.py
echo.
echo For more information, see README.md
echo ==================================================
pause



