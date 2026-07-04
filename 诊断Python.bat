@echo off
echo ========================================
echo   Python Diagnostic Tool
echo ========================================
echo.

cd /d "%~dp0"

echo [1] Checking Python...
py --version
if errorlevel 1 (
    echo Python not found with 'py' command
    echo.
    echo Trying 'python'...
    python --version
    if errorlevel 1 (
        echo.
        echo ERROR: Python not found properly!
        echo.
        echo Please reinstall Python:
        echo 1. Download from https://www.python.org/downloads/
        echo 2. During installation, CHECK THE BOX: "Add Python to PATH"
        echo 3. Also check "Install pip" if available
        echo.
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=python
    )
) else (
    set PYTHON_CMD=py
)

echo.
echo [2] Checking pip...
%PYTHON_CMD% -m pip --version
if errorlevel 1 (
    echo.
    echo pip not found!
    echo.
    echo Trying to install pip...
    %PYTHON_CMD% -m ensurepip --default-pip
    if errorlevel 1 (
        echo.
        echo Failed to install pip automatically.
        echo.
        echo Please reinstall Python and make sure to:
        echo - Check "Add Python to PATH"
        echo - Check "Install pip"
        echo.
        pause
        exit /b 1
    )
)

echo.
echo [3] Checking Python location...
%PYTHON_CMD% -c "import sys; print(sys.executable)"

echo.
echo ========================================
echo   Python looks good! Now install dependencies.
echo ========================================
echo.
echo Installing dependencies...
%PYTHON_CMD% -m pip install fastapi uvicorn jinja2 python-multipart anthropic python-dotenv markdown

echo.
echo ========================================
echo   Done! Now you can run the server!
echo ========================================
echo.
pause
