#!/usr/bin/env bash
# Xatolik yuz berganda to'xtatish
set -o errexit

# Bog'liqliklarni o'rnatish
pip install -r requirements.txt

# Statik fayllarni bitta papkaga yig'ish (WhiteNoise uchun)
python manage.py collectstatic --no-input

# Baza jadvallarini yangilash
python manage.py migrate
