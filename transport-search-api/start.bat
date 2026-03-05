@echo off
cd /d "%~dp0"
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting Transport Search API on http://localhost:8001
echo Swagger UI: http://localhost:8001/docs
echo.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
