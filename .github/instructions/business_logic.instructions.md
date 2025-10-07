---
applyTo: "**"
---

# Business Logic Instructions

This file contains critical instructions for understanding and implementing business logic in this project. Please read and follow these guidelines carefully.

## Questions

- Questions are split up into two categories: **Public** and **Private**.
- **Public** questions are designed to be used as read-only examples that users can copy to their own list of private questions. Even users who are not logged in can view public questions, but cannot perform any actions on them.
- **Public** questions are not designed to have answers linked to them, and this will be made clear in the user interface. This rule should be enforced on the backend as well.
- **Public** questions can only be edited by admins or the user who created them, after the question has been approved. If a non-admin user edits their own public question, it will go back to being marked as "pending approval" until an admin reviews and approves the changes.
- **Private** questions are only visible to the user. The user can create, edit, and delete their own private questions. These questions should always have approved status. Admins can also view and manage private questions from the admin panel, but even admins will only see their own private questions in the user interface.

## Question Tags

- Questions can be tagged with multiple tags to help with organization and searching.
- Public tags are predefined and can only be created or edited by admins. They are accessible to all users for tagging their private questions.
- Private tags can be created, edited, and deleted by users for their own private questions. This allows users to extend the tagging system to suit their personal organization needs, without affecting other users.
- Tags are case-insensitive. For example, "Leadership", "leadership", and "LEADERSHIP" are considered the same tag.

## Answers

- Answers are always linked to a specific question.
- Answers can only be created, edited, or deleted by the user who owns the private question they are linked to.
- Answers can be created in two formats: STAR and Basic
  - STAR answers must follow the STAR format (Situation, Task, Action, Result) and should be validated to ensure they contain all four components.
  - Basic answers are free-form text and do not require specific formatting.