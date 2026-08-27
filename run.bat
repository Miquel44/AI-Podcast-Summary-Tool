@echo off
REM ONDA — one-command run for Windows. Requires: Python 3.11+, Node 18+, ffmpeg.
cd /d "%~dp0"

if not exist .env (
    echo [!] Falta el fichero .env — copia .env.example a .env y pon tus API keys.
    pause
    exit /b 1
)

echo [1/3] Backend: entorno e instalacion de dependencias...
if not exist backend\ProsperVenv python -m venv backend\ProsperVenv
backend\ProsperVenv\Scripts\python -m pip install -q --trusted-host pypi.org --trusted-host files.pythonhosted.org -r backend\requirements.txt

echo [2/3] Frontend: build de produccion...
cd frontend
call npm install --silent
call npm run build
cd ..

echo [3/3] Arrancando ONDA en http://localhost:8000 (la edicion diaria se genera sola)...
start "" http://localhost:8000
cd backend
ProsperVenv\Scripts\python -m uvicorn app.main:app --port 8000
