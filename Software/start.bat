@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Create the virtual environment first:
  echo python -m venv .venv
  echo .venv\Scripts\pip install -r backend\requirements.txt
  pause
  exit /b 1
)
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
