@echo off
echo Starting Customer Service Training Bot...
echo.

cd /d "%~dp0"

echo Checking Python...
py --version >nul 2>&1
if errorlevel 1 (
    echo Python not found!
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Remember to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo Python found!
py --version
echo.

echo Installing dependencies...
py -m pip install -r requirements.txt
echo.

echo Starting server...
echo Open browser at http://localhost:8000
echo.

py src/main.py

pause
