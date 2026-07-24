@echo off
title AI JobAgent Server
echo ===================================================
echo             Starting AI JobAgent System            
echo ===================================================
echo.

:: Check if virtual environment exists and activate it
if exist venv\Scripts\activate.bat (
    echo [System] Activating virtual environment...
    call venv\Scripts\activate.bat
)

:: Start FastAPI Backend in the background
echo [System] Starting FastAPI Backend on port 8000...
start "FastAPI Backend" /b python app.py

:: Wait a moment for FastAPI to initialize
timeout /t 3 /nobreak >nul

:: Start Streamlit Frontend
echo [System] Starting Streamlit Frontend on port 8501...
streamlit run frontend.py --server.port 8501

pause
