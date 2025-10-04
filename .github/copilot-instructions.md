# STAR Master

## Description of website

STAR Master is a web application designed to help users keep a history of personalised answers to common interview questions and learn and practice the STAR (Situation, Task, Action, Result) method.

The platform provides a structured approach to crafting responses, allowing users to create, edit, and review their STAR stories. Users can also craft basic text responses without the STAR structure if they prefer.

## Apps

theme - django-tailwind app for styling
questions - main app for handling question urls and models
answers - main app for handling answer urls and models

## Agent Mode

Commands will be run in powershell. When the agent opens up a new terminal, the venv is not activated. You will need to run the activate command before a python command will work. We also need to use heroku local:run to run pyton commands so that the environment variables are loaded from the .env file. Be pessimistc about whether the env will be needed or not, so assume it will be needed and use heroku local:run for all python commands.

### Example

```powershell
.\.venv\Scripts\Activate.ps1; heroku local:run python manage.py runserver
```

### Additional Notes

- Django's ORM cannot use property methods in database lookups - it expects actual database fields.