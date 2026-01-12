@echo off
REM Quick Start Script for Dash Dashboard (Windows)

cls
echo.
echo ============================================================
echo Dash Dashboard - Quick Start (Windows)
echo ============================================================
echo.

REM Check if in right directory
if not exist "requirements.txt" (
    echo Error: requirements.txt not found
    echo Please run this script from the dashboard directory
    exit /b 1
)

REM Check if .venv exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    echo Virtual environment created
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install/update dependencies
echo Installing dependencies...
pip install -q -r requirements.txt

if %errorlevel% neq 0 (
    echo Failed to install dependencies
    exit /b 1
)

echo Dependencies installed
echo.
echo ============================================================
echo Ready to start!
echo ============================================================
echo.
echo Starting Dash Dashboard...
echo.

REM Start the app
python app.py

pause
