@echo off
echo Starting Simple Test Server...
echo.
cd /d "%~dp0"

echo Checking files...
if not exist "src\templates\index.html" (
    echo ERROR: index.html not found!
    pause
    exit /b 1
)

echo Starting server...
echo.
echo ==================================================
echo   Open your browser and go to:
echo   http://localhost:8000
echo.
echo   Or try:
echo   http://127.0.0.1:8000
echo ==================================================
echo.

py src/main_simple.py

echo.
echo Server stopped.
pause
