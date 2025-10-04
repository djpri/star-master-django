---
applyTo: "**"
---

# Business Logic Instructions

This file contains critical instructions for understanding and implementing business logic in this project. Please read and follow these guidelines carefully.

## Questions

- Questions are split up into two categories: **Public** and **Private**.
- **Public** questions are designed to be used as read-only examples that users can copy to their own list of private questions. Even users who are not logged in can view public questions, but cannot perform any actions on them.
- **Public** questions are not designed to have answers linked to them, and this will be made clear in the user interface. This rule should be enforced on the backend as well.
- **Public** questions
- **Private** questions are only visible to the user. The user can create, edit, and delete their own private questions. Admins can also view and manage private questions from the admin panel, but even admins will only see their own private questions in the user interface.

## Answers

- Answers are always linked to a specific question.
- Answers can only be created, edited, or deleted by the user who owns the private question they are linked to.
- Answers can be created in two formats: STAR and Basic
  - STAR answers must follow the STAR format (Situation, Task, Action, Result) and should be validated to ensure they contain all four components.
  - Basic answers are free-form text and do not require specific formatting.