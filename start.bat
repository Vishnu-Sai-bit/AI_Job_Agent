@echo off
title AI Job Copilot & Career Intelligence Platform
echo ===================================================
echo     Starting AI Job Copilot & Career Platform       
echo     Local Server: http://127.0.0.1:5000
echo ===================================================
echo.

:: Check if virtual environment exists and activate it
if exist venv\Scripts\activate.bat (
    echo [System] Activating virtual environment...
    call venv\Scripts\activate.bat
)

:: Run local Flask application
echo [System] Launching application on port 5000...
python run.py

pause
