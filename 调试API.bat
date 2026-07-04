@echo off
chcp 65001 >nul
echo ========================================
echo   API 调试工具
echo ========================================
echo.

cd /d "%~dp0"

python test_api.py

if errorlevel 1 (
    py test_api.py
)

pause
