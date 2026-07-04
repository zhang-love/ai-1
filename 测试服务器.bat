@echo off
echo ========================================
echo   Test Server
echo ========================================
echo.

cd /d "%~dp0"

python src/test_server.py

pause
