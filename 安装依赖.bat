@echo off
chcp 65001 >nul
echo ========================================
echo   安装 Python 依赖
echo ========================================
echo.

cd /d "%~dp0"

echo 正在安装依赖...
echo.

python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo 尝试使用 py 命令...
    py -m pip install -r requirements.txt
)

echo.
echo ========================================
echo   安装完成！
echo ========================================
echo.
pause
