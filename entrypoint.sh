#!/bin/sh
set -e

echo "⏳ Waiting for database..."
until python -c "
import psycopg, os, sys
try:
    db_url = os.environ['DATABASE_URL'].replace('postgresql+psycopg://', 'postgresql://')
    psycopg.connect(db_url)
    print('✅ DB ready')
except Exception as e:
    print(f'not ready: {e}')
    sys.exit(1)
" 2>/dev/null; do
  sleep 1
done

echo "🔄 Running migrations..."
flask --app run.py db upgrade heads

echo "🌱 Seeding roles..."
python -m scripts.seed_roles || true

echo "🌱 Seeding categories..."
python -m scripts.seed_categories || true

echo "🚀 Starting app..."
exec gunicorn --bind 0.0.0.0:8000 --workers 2 --timeout 120 "run:app"
