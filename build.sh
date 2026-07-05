#!/usr/bin/env bash
# build.sh — Render build script
# Executed automatically during each deploy.

set -o errexit  # exit on error

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
