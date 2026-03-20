@echo off
title MI Logistics - Brand Review App
color 0A
echo.
echo  ============================================
echo   MI LOGISTICS - Brand Review App
echo  ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  ERROR: Python not found.
    echo.
    echo  Please install Python from: https://www.python.org/downloads/
    echo  Make sure to tick "Add Python to PATH" during install.
    echo.
    pause
    exit /b
)

REM Install Flask silently if not present
echo  Checking Flask...
pip show flask >nul 2>&1
if %errorlevel% neq 0 (
    echo  Installing Flask - please wait...
    pip install flask --quiet
)

echo  Flask ready.
echo.
echo  ============================================
echo   Opening in browser: http://localhost:5000
echo  ============================================
echo.

REM Open browser after 2 seconds
start /b cmd /c "timeout /t 2 >nul && start http://localhost:5000"

REM Start Flask
python app.py

echo.
echo  App stopped. Press any key to close.
pause
