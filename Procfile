web: gunicorn --config gunicorn.conf.py config.wsgi

# Release phase: build assets and run migrations
release: python manage.py migrate --noinput && \
         python manage.py tailwind build --no-input && \
         python manage.py collectstatic --noinput