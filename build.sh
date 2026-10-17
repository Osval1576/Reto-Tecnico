#!/usr/bin/env bash
# Build para desplegar en una plataforma tipo Render o Railway.
# Se ejecuta desde la raíz del repositorio: bash build.sh
set -o errexit

# 1. Frontend: genera frontend/dist, que Django sirve con WhiteNoise
npm ci --prefix frontend
npm run build --prefix frontend

# 2. Backend
pip install -r backend/requirements.txt
python backend/manage.py collectstatic --no-input
python backend/manage.py migrate --no-input
