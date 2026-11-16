@echo off
cd /d "%~dp0"
echo Starting River Path Deviation Prediction System...
"%~dp0.venv\Scripts\python.exe" "%~dp0main.py"
if %errorlevel% neq 0 (
    echo.
    echo Application exited with error code %errorlevel%
    pause
)
