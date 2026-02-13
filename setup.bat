@echo off
REM Locivox Setup Script for Windows

echo ======================================
echo     Locivox Setup Script v0.1.0
echo ======================================
echo.

REM Check Python
echo Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.9 or higher from python.org
    pause
    exit /b 1
)

echo Python detected
echo.

REM Check FFmpeg
echo Checking for FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo WARNING: FFmpeg is not installed.
    echo Install it with: choco install ffmpeg
    echo.
    set /p continue="Continue without FFmpeg? (not recommended) [y/N]: "
    if /i not "%continue%"=="y" exit /b 1
)

echo FFmpeg detected
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Skipping...
) else (
    python -m venv venv
    echo Virtual environment created
)
echo.

REM Activate and install
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Upgrading pip and installing setuptools...
python -m pip install --upgrade pip setuptools wheel --quiet

echo.
echo Installing dependencies (this may take a few minutes)...
python -m pip install -r requirements-windows.txt

echo.
echo ======================================
echo        Setup Successful!
echo ======================================
echo.
echo To get started:
echo.
echo   1. Activate the virtual environment:
echo      venv\Scripts\activate
echo.
echo   2. Run Locivox:
echo      python src\cli.py
echo.
echo   3. Check the README for more options
echo.
echo Happy transcribing!
echo.
pause
