# STAR Master

## Description of website

STAR Master is a web application designed to help users keep a history of personalised answers to common interview questions and learn and practice the STAR (Situation, Task, Action, Result) method.

The platform provides a structured approach to crafting responses, allowing users to create, edit, and review their STAR stories. Users can also craft basic text responses without the STAR structure if they prefer.

## Apps

theme - django-tailwind app for styling
questions - main app for handling question urls and models
answers - main app for handling answer urls and models

## Site structure

- home
- accounts (handled by django-allauth)
- questions (paginated list of questions)
-- question id (shows question details and list of answers)
-- answer id (shows answer details)
-- answer id ?=edit (edit answer details)
- create answer ?=<question_id> (create a new answer for a specific question)