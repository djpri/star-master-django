# Technology Stack

## Framework & Core Dependencies

- **Django 5.2**: Web framework
- **Python**: Runtime (version specified in `.python-version`)
- **Gunicorn**: WSGI HTTP Server for production
- **WhiteNoise**: Static file serving middleware
- **dj-database-url**: Database URL parsing for Heroku
- **psycopg[binary]**: PostgreSQL adapter
- **django-allauth**: Authentication
- **django-crispy-forms**: Form rendering
- **django-summernote**: Rich text editor for admin interface

## UI

- **Tailwind CSS**: Utility-first CSS framework
- **Font Awesome**: Icon library

## Database

- **PostgreSQL**: Same database for development and production

## Deployment

- **Heroku**: Primary deployment platform
- **Docker**: Not used in this setup

## Common Commands

### Development

```bash
# Setup virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Unix

# Install dependencies
pip install -r requirements.txt

# Run migrations (with .env loaded)
heroku local:run python manage.py migrate

# Start development server (with .env loaded)
heroku local:run python manage.py runserver

# Alternative: Run with Heroku local web process
heroku local
```

### Testing

```bash
# Run tests (with .env loaded)
heroku local:run python manage.py test

# Run tests with debug mode (with .env loaded)
heroku local:run python manage.py test --debug-mode
```

### Production

```bash
# Collect static files (with .env loaded)
heroku local:run python manage.py collectstatic --no-input

# Run with Gunicorn
gunicorn --config gunicorn.conf.py config.wsgi
```

### Heroku Deployment

```bash
# Deploy to Heroku
git push heroku main

# Run migrations on Heroku
heroku run python manage.py migrate

# View logs
heroku logs --tail
```
