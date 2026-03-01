@echo off
REM Orchestrator Agent Setup Script for Windows

echo ==================================================
echo Orchestrator Agent - Setup Script (Windows)
echo ==================================================

REM Check Python version
echo.
echo [1/5] Checking Python version...
python --version >nul 2>&1 || (echo Python not found. Please install Python 3.11+& exit /b 1)

REM Create virtual environment
echo.
echo [2/5] Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo [3/5] Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Setup environment file
echo.
echo [4/5] Setting up environment file...
if not exist .env (
    copy .env.example .env
    echo. Created .env file (fill in your configuration)
) else (
    echo. .env file already exists
)

REM Create directories
echo.
echo [5/5] Creating necessary directories...
if not exist app\__pycache__ mkdir app\__pycache__
if not exist app\ml\__pycache__ mkdir app\ml\__pycache__
if not exist app\integrations\__pycache__ mkdir app\integrations\__pycache__

echo.
echo ==================================================
echo Setup Complete!
echo ==================================================
echo.
echo Next steps:
echo 1. Update .env with your configuration
echo 2. Ensure Ollama is running: ollama serve
echo 3. Pull required models:
echo    - ollama pull phi4
echo    - ollama pull llama2
echo 4. Start the application:
echo    python -m uvicorn app.main:app --reload --port 8000
echo.
echo API Documentation: http://localhost:8000/docs
echo ==================================================
pause
