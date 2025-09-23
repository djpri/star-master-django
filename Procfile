web: gunicorn --config gunicorn.conf.py config.wsgi

# Release phase: build assets and run migrations
release: npm run build && python manage.py collectstatic --no-input && python manage.py migrate --no-input