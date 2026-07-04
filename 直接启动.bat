@echo off
echo ========================================
echo   Customer Service Training Bot
echo ========================================
echo.

cd /d "%~dp0"

echo [1/2] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo.
echo [2/2] Starting server...
echo.
echo ========================================
echo   Open your browser at:
echo   http://localhost:8000
echo   (or http://127.0.0.1:8000)
echo ========================================
echo.

python src/main.py

echo.
echo Server stopped.
pause
