@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo        ResumeRank AI - Startup
echo ========================================
echo.

if not exist venv\Scripts\python.exe (
    echo Creating Python virtual environment...
    py -3 -m venv venv
    if errorlevel 1 (
        echo.
        echo ERROR: Python 3 was not found or the virtual environment could not be created.
        echo Install Python 3.9+ and run this file again.
        pause
        exit /b 1
    )
)

echo Installing/verifying required packages...
venv\Scripts\python.exe -m pip install --prefer-binary -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Package installation failed.
    echo Check your internet connection and run START_PROJECT.bat again.
    pause
    exit /b 1
)

echo.
echo Starting ResumeRank AI...
echo Open http://127.0.0.1:5000 in your browser.
echo Press Ctrl+C to stop the server.
echo.
venv\Scripts\python.exe run.py
pause
