@echo off
REM ==========================================================
REM  M&A AI Toolkit Launcher
REM  This batch file activates your virtual environment
REM  and starts Streamlit automatically.
REM ==========================================================

REM --- Change directory to this script’s folder ---
cd /d "%~dp0"

REM --- Activate virtual environment (adjust folder if needed) ---
call venv\Scripts\activate

REM --- Launch Streamlit app ---
python -m streamlit run main.py

REM --- Optional: keep window open after app closes ---
pause
