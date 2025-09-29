# Commands

Prioritise the use of these commands when looking to execute anything in the terminal.

Note: Any command that requires the .env file to be loaded should be prefixed with `heroku local:run` to ensure that the environment variables are loaded correctly. This is true for most manage.py tasks.

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

# Note: separate command is needed to be ran at the same time for reloading tailwind styles in development
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
