@echo off
title Suvarna Nadi - Estuarine Mouth Dynamics Web Application
cd /d "%~dp0"

echo ======================================================================
echo   SUVRNA NADI - ESTUARINE MOUTH DYNAMICS PREDICTION SYSTEM (WEB APP)
echo   National Institute of Technology Karnataka (NITK Surathkal)
echo ======================================================================
echo.

IF EXIST ".venv\Scripts\python.exe" (
    echo [*] Detected virtual environment at .venv\Scripts\python.exe
    ".venv\Scripts\python.exe" run_web.py
) ELSE (
    echo [*] Using global Python interpreter
    python run_web.py
)

pause
