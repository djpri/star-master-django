# Project Structure

## Root Directory
```
├── .env                    # Environment variables for local development
├── .python-version         # Python version specification
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── Procfile              # Heroku process definitions
├── Procfile.windows      # Windows-specific Heroku processes
├── gunicorn.conf.py      # Gunicorn WSGI server configuration
├── app.json              # Heroku app metadata
└── README.md             # Project documentation
```

## Django Configuration (`config/`)
- **settings.py**: Main Django settings with Heroku-specific configurations
- **urls.py**: Root URL configuration
- **wsgi.py**: WSGI application entry point
- **asgi.py**: ASGI application entry point (for async support)

## Django Apps
- **chords/**: Main application for chord sheet management
- **music/**: Application for song management

## Key Conventions

### Settings Configuration
- Environment-based configuration using `os.environ.get()`
- Separate behavior for Heroku (`IS_HEROKU_APP` flag)
- Debug mode controlled by `ENVIRONMENT` variable
- Database URL parsing with `dj-database-url`

### Static Files
- Static files collected to `staticfiles/` directory
- WhiteNoise handles static file serving
- Compressed and hashed static files in production

### Security
- Secret key from environment variable or auto-generated
- HTTPS redirect enabled on Heroku
- Proper ALLOWED_HOSTS configuration

### Database
- SQLite for local development
- PostgreSQL for production via DATABASE_URL
- Migrations should be run via Heroku release phase

### Logging
- Structured logging configuration
- Console output for both development and production
- Request logging suppressed for 4xx responses