# STAR Master

## 📝 Contents
- [STAR Master](#-star-master)
  - [🎯 Project Overview](#-project-overview)
  - [🎨 UX Design](#-ux-design)
  - [📋 Project Planning](#-project-planning)
  - [🗄️ Database Design](#️-database-design)
  - [✨ Features](#-features)
  - [🚀 Future Features](#-future-features)
  - [💻 Technologies Used](#-technologies-used)
  - [🤖 AI Implementation](#-ai-implementation)
  - [🧪 Testing](#-testing)
  - [🔒 Security](#-security)
  - [🌐 Deployment](#-deployment)
  - [🐛 Known Issues \& Bugs](#-known-issues--bugs)
  - [🙏 Credits](#-credits)

## 🎯 Project Overview

STAR Master is a full-stack web application designed to allow users to manage a library of interview questions, and keep a history of responses to these questions. This application focuses on STAR (Situation, Task, Action, Result) method questions in particular, allowing users to keep a history of stories and situations that may have otherwise been forgotten.

### Purpose

It is a common experience for people to go into an interview and feel that their mind has gone completely blank. The goal of this website is to help people prepare properly and also have stories to talk about in interviews for future roles.

### Target Audience

The main target audience for this application includes job seekers and students preparing for interviews, but also current professionals looking to enhance their interview skills.

## 🎨 UX Design

### Design Inspiration

### Colour Scheme

### Typography

I chose to use Monterrat for headings and Alan Sans for body text. Both fonts are available from Google Fonts. I chose these fonts as they are modern, clean and easy to read.

To further enhance readability, I made small adjustments to the letter spacing and line height of the body text. These small details can make a big difference to the overall look and feel of a website.

### Imagery

### Wireframes

## 📋 Project Planning

### Strategy Plane

### Site Goals

### Agile Methodology

### User Stories

### MoSCoW Prioritization

### Project Board / Kanban Board

### Sprints

## 🗄️ Database Design

### Database Structure

### Entity Relationship Diagram (ERD)

### Models

## ✨ Features

### Existing Features

### Key Features

### CRUD Functionality

### User Authentication & Authorization

The authentication system is provided by the Django Allauth package, allowing for ready made system with little configuration. Users can register, login, logout and reset their password.

### Navigation

### Responsive Design

## 🚀 Future Features

## 💻 Technologies Used

### Languages

### Frameworks & Libraries

### Tools & Programs

### Database

The database is a postgres database hosted on a server provided by Code Institute.

### Deployment & Hosting

This website is hosted on [Heroku](https://www.heroku.com/), a cloud platform that allows developers to build, run, and operate applications entirely in the cloud. 

## 🤖 AI Implementation

AI played a critical role in the development of this project, assisting in various aspects from code generation to debugging, testing and optimization. I used a variety of premium models within GitHub Copilot, and found that different models were better suited to different tasks.

### Use of AI in Code Creation

### Use of AI in Debugging

### Use of AI in Code Optimization

### Use of AI in Creating Unit Tests

### Reflection on AI's Role in Development

## 🧪 Testing

### Manual Testing

### Automated Testing

### Validation

#### HTML Validation

#### CSS Validation

#### Python Validation

#### JavaScript Validation

### Lighthouse Testing

### Responsiveness Testing

### Browser Compatibility

### User Story Testing

## 🔒 Security

## 🌐 Deployment

### Pre-Deployment

### Deployment Process

### Cloning and Forking

### Environment Variables

## 🐛 Known Issues & Bugs

## 🙏 Credits

### Code

### Media

### Content

### Acknowledgements
### Use of AI in Code Optimization

### Use of AI in Creating Unit Tests

### Reflection on AI's Role in Development

## 🧪 Testing

### Manual Testing

### Automated Testing

### Validation

#### HTML Validation

#### CSS Validation

#### Python Validation

#### JavaScript Validation

### Lighthouse Testing

### Responsiveness Testing

### Browser Compatibility

### User Story Testing

## 🔒 Security

An essential step in the deployment process is ensuring the security of sensitive information. This project uses environment variables to manage sensitive data such as database credentials and secret keys. By using environment variables, we can keep this information out of the codebase, reducing the risk of accidental exposure.

Early on in the development process, I made a mistake of committing sensitive information to the repository. To fix this problem, I used a tool called **bfg-repo-cleaner** to remove the sensitive data from the entire git history. I then updated the django secret key, and any other credentials that may have been exposed.

## 🌐 Deployment

Below are the steps taken to deploy this project to Heroku.

### Environment variables

- `DATABASE_URL`: The URL for the database connection.
- `DJANGO_SECRET_KEY`: The secret key for the Django application.
- `ENVIRONMENT`: Set to "development" for development environment. If not set, the app will assume it is in production and not run in debug mode.

### Deployment Process

1. Set up the Heroku app and configure the buildpacks. We are using the nodejs and python buildpacks. The order of the buildpacks is important, as the nodejs buildpack must be first.
2. Set the environment variables in the Heroku dashboard.
3. Deploy the application using Git or the Heroku CLI.
4. Run database migrations and collect static files.

### Cloning and Forking

## 🐛 Known Issues & Bugs

## 🙏 Credits

### Code

### Media

### Content

### Acknowledgements
