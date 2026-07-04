@echo off
echo ========================================
echo   Full Version with Claude API
echo ========================================
echo.

cd /d "%~dp0"

echo Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo.
echo Starting server...
echo.
echo ========================================
echo   Open browser at: http://127.0.0.1:8000
echo ========================================
echo.

python src/full_main.py

echo.
echo Server stopped.
pause
