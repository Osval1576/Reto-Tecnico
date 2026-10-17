#!/usr/bin/env bash
# Build del backend en Render (Root Directory: backend).
# Build Command: bash build.sh
# Start Command: gunicorn config.wsgi:application
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate --no-input
