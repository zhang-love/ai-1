@echo off
chcp 65001 >nul
echo ========================================
echo   🤖 客服培训机器人 - 流式版本
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] 检查 Python...
py --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 未找到！
    pause
    exit /b 1
)
echo ✅ Python 就绪
py --version
echo.

echo [2/3] 检查依赖...
py -c "import fastapi, uvicorn, requests, dotenv" 2>nul
if errorlevel 1 (
    echo ⚠️  正在安装依赖...
    py -m pip install -r requirements.txt
) else (
    echo ✅ 依赖就绪
)
echo.

echo [3/3] 启动服务器...
echo.
echo 🌐 访问地址: http://localhost:8000
echo 📚 知识库已加载
echo ✨ 支持流式响应
echo.
echo 按 Ctrl+C 停止服务器
echo ========================================
echo.

py src/main.py

pause
