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

# Note: separate command is needed for reloading tailwind styles in development
npm run dev

### Testing

```bash
# Run tests (with .env loaded)
heroku local:run python manage.py test

# Run tests with debug mode (with .env loaded)
heroku local:run python manage.py test --debug-mode
```

### Migrations


### Heroku Deployment

```bash
# Deploy to Heroku
git push heroku main

# Run migrations on Heroku
heroku run python manage.py migrate

# View logs
heroku logs --tail
```
