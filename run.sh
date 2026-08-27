#!/usr/bin/env bash
# ONDA — one-command run for macOS/Linux. Requires: Python 3.11+, Node 18+, ffmpeg.
set -e
cd "$(dirname "$0")"

if [ ! -f .env ]; then
    echo "[!] Falta el fichero .env — copia .env.example a .env y pon tus API keys."
    exit 1
fi

echo "[1/3] Backend: entorno e instalación de dependencias..."
[ -d backend/.venv ] || python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -q -r backend/requirements.txt

echo "[2/3] Frontend: build de producción..."
(cd frontend && npm install --silent && npm run build)

echo "[3/3] Arrancando ONDA en http://localhost:8000 (la edición diaria se genera sola)..."
(sleep 2 && (open http://localhost:8000 || xdg-open http://localhost:8000) 2>/dev/null) &
cd backend
.venv/bin/python -m uvicorn app.main:app --port 8000
