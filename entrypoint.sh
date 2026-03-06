#!/bin/sh
set -e

echo "=> migrating schemas"
python manage.py makemigrations accounts public_app tenant_app --noinput
python manage.py migrate_schemas --noinput

echo "=> setting up public tenant"
python manage.py setup_public_tenant

exec "$@"