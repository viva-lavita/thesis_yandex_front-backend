#!/usr/bin/env bash

set -e

HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}

uv sync  # догрузка dev зависимостей
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

exec python manage.py runserver "${HOST}:${PORT}"
