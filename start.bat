@echo off
chcp 65001 >nul
echo ==========================================
echo    Customer Service Training Bot
echo ==========================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)
echo OK: Python found
python --version
echo.

echo [2/3] Checking dependencies...
python -c "import fastapi, uvicorn, requests, dotenv" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    echo OK: Dependencies are installed
)
echo.

echo [3/3] Starting server...
echo.
echo Open your browser and visit: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo ==========================================
echo.

python src/main.py

pause
