web: gunicorn --config gunicorn.conf.py config.wsgi

# Release phase: build assets and run migrations
release: python manage.py migrate --noinput