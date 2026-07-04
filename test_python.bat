@echo off
echo Testing Python...
py --version
if errorlevel 1 (
    echo Python not found!
    echo.
    echo Trying python...
    python --version
    if errorlevel 1 (
        echo.
        echo ERROR: Python is not installed or not in PATH!
        echo.
        pause
    ) else (
        echo.
        echo Python works!
        pause
    )
) else (
    echo.
    echo Python works!
    pause
)
