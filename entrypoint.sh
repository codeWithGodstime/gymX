#!/bin/sh
set -e

echo "=> migrating schemas"
python manage.py makemigrations --noinput
python manage.py migrate_schemas --noinput

exec "$@"