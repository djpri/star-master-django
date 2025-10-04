---
applyTo: "**"
---
# Full-Stack Django Web Application - Learning Outcomes and Assessment Criteria

## LO1: Agile Methodology and Full-Stack Design

**Objective**: Apply Agile methodology to effectively plan and design a Full-Stack Web application using Django Web framework and related contemporary technologies.

### 1.1 Front-End Design
**Assessment Criteria**: Design a front-end that meets accessibility guidelines and follows UX design principles. Create a responsive full-stack application that meets its given purpose, provides a set of user interactions, and uses custom HTML and CSS/CSS frameworks.

**Expected Performance**:
- Semantic use of HTML
- No Web Content Accessibility Guideline (WCAG) errors
- User-friendly interface with consistent styles, clear navigation, and adherence to wireframes/mockups
- Responsive layout that adapts to different screen sizes using CSS media queries, Flexbox, Grid, and/or Bootstrap without major errors/loss of functionality

### 1.2 Database
**Assessment Criteria**: Build a database-backed Django web application to manage data records. Design a database structure with at least one custom model.

**Expected Performance**:
- Configured Django web application with connected database
- At least one custom model that fits project requirements
- Correct implementation of Django models with appropriate fields, relationships, and constraints
- Use of Django's ORM for data management ensuring efficient and secure database operations

### 1.3 Agile Methodology
**Assessment Criteria**: Use an Agile tool to plan and track all major functionality. Document and implement all user stories linking them to project goals within an agile tool.

**Expected Performance**:
- Use of an Agile tool to plan and track project tasks and progress
- Documentation of user stories clearly linked to project goals and deliverables within the tool

### 1.4 Code Quality
**Assessment Criteria**: Include custom Python logic demonstrating proficiency, including compound statements like if-else conditions and loops. Write code with proper readability, indentation, and meaningful naming conventions. Name files consistently and descriptively, avoiding spaces and capitalization for cross-platform compatibility.

**Expected Performance**:
- Inclusion of custom Python logic with clear, well-structured if-else conditions and loops
- Code that follows readability standards with proper indentation and meaningful naming conventions
- Consistent and descriptive file naming avoiding spaces and capital letters for compatibility
- Use of comments and docstrings to explain complex logic and functions within the code
- Adherence to PEP 8 guidelines for Python code style and conventions

### 1.5 Documentation
**Assessment Criteria**: Document the UX design process, including wireframes, mockups, and diagrams. Ensure documentation demonstrates that the design process has been followed through to implementation.

**Expected Performance**:
- Concise documentation of the UX design process, including wireframes, mockups, diagrams, as well as reasoning for changes throughout the development process
- Well-organized README file detailing the UX process, design rationale, and final implementation

## LO2: Data Model and Business Logic Implementation

**Objective**: Develop and implement a data model, application features, and business logic to manage, query, and manipulate data to meet specific needs in a real-world domain.

### 2.1 Database Development
**Assessment Criteria**: Develop a well-organised and consistent database model.

**Expected Performance**:
- Well-organised database schema with clearly defined tables and relationships
- Consistent use of data types and constraints to ensure data integrity
- Use of migrations to manage schema changes and version control for the database

### 2.2 CRUD Functionality
**Assessment Criteria**: Implement functionality for users to create, read, update, and delete (CRUD) records.

**Expected Performance**:
- Implementation of user-friendly interfaces for creating, reading, updating, and deleting (CRUD) records
- Secure access controls to ensure only authorised users can perform CRUD operations

### 2.3 User Notifications
**Assessment Criteria**: Ensure that all changes to the data are notified to the relevant user.

**Expected Performance**:
- Implementation of real-time or near-real-time notifications for relevant data changes
- Clear and concise notification messages that inform users of data changes

### 2.4 Forms and Validation
**Assessment Criteria**: Implement at least one form with validation for creating and editing models in the backend.

**Expected Performance**:
- Implementation of forms for creating and editing models with proper field validation
- User-friendly and accessible form design with clear labels and input fields
- Clear and informative error messages for invalid form submissions

## LO3: Authentication and Authorization

**Objective**: Implement and configure authorization, authentication, and permission features in a Full-Stack web application.

### 3.1 Role-Based Login and Registration
**Assessment Criteria**: Implement role-based login (user/admin/etc.) and registration functionality.

**Expected Performance**:
- Implementation of a secure role-based login and registration system
- Clear differentiation between user roles (e.g., user, admin) with appropriate permissions
- Secure handling of user credentials and sensitive information
- User-friendly registration and login interfaces with validation and error handling

### 3.2 Reflect Login State
**Assessment Criteria**: Ensure the current login state is accurately reflected to the user.

**Expected Performance**:
- Accurate reflection of the current login state across all pages of the application
- Clear visual indicators of login status (e.g., user avatar, logout button)
- Conditional rendering of content based on user's login state and role

### 3.3 Access Control
**Assessment Criteria**: Prevent users from accessing restricted content or functionality before logging in with the appropriate role.

**Expected Performance**:
- Proper implementation of access control to restrict content and functionality based on user roles
- Clear error messages or redirects for unauthorised access attempts

## LO4: Testing Implementation

**Objective**: Design, create, and execute manual or automated tests for a Full-Stack Web application using Django Web framework and related contemporary technologies.

### 4.1 Python Test Procedures
**Assessment Criteria**: Design and implement manual or automated Python test procedures to evaluate the functionality, usability, responsiveness, and data management of the web application.

**Expected Performance**:
- Clear and organized test cases for different application components (if automated tests are not implemented)
- Detailed test results showing pass/fail status and, if applicable, coverage metrics

### 4.2 JavaScript Test Procedures (if applicable)
**Assessment Criteria**: Design and implement manual or automated JavaScript test procedures to evaluate the functionality, usability, responsiveness, and data management of the web application, if JavaScript is being utilised.

**Expected Performance**:
- Clear and organized test cases for different application components (if automated tests are not implemented)
- Detailed test results showing pass/fail status and, if applicable, coverage metrics

### 4.3 Testing Documentation
**Assessment Criteria**: Document all testing procedures and results in the README file.

**Expected Performance**:
- Detailed documentation of all testing procedures, including manual and/or automated tests
- Clear explanations of test cases, expected outcomes, and actual results
- Well-organised README file summarising the testing approach and results

## LO5: Version Control and Code Management

**Objective**: Utilise a distributed version control system and a repository hosting service to document, develop, and maintain a Full-Stack Web application using Django Web framework and related contemporary technologies.

### 5.1 Version Control with Git & GitHub
**Assessment Criteria**: Use Git for version control and GitHub (or a similar repository hosting service) to document the development process, including meaningful commit messages.

**Expected Performance**:
- Use of Git for version control with meaningful and descriptive commit messages
- Regular commits reflecting incremental development and progress
- Comprehensive commit history documenting the development process

### 5.2 Secure Code Management
**Assessment Criteria**: Ensure the final committed code is free of passwords or security-sensitive information before deployment to the repository and hosting platform.

**Expected Performance**:
- Ensuring no passwords or sensitive information are committed to the repository
- Use of environment variables and .gitignore for managing secret keys and configurations

## LO6: Cloud Deployment

**Objective**: Deploy a Full-Stack Web application using Django Web framework and related contemporary technologies to a cloud-based platform, ensuring proper functionality and security.

### 6.1 Deploy Application to Cloud Platform
**Assessment Criteria**: Successfully deploy the final version of the Full-Stack application to a cloud-based hosting platform and verify that it matches the development version.

**Expected Performance**:
- Successful deployment of the application to a cloud-based platform
- Verification that the deployed version matches the development version in functionality
- Proper configuration of the hosting environment to support the application

### 6.2 Document Deployment Process
**Assessment Criteria**: Clearly document the deployment process in a README file.

**Expected Performance**:
- Clear and detailed documentation of the deployment process in the README file
- Step-by-step instructions for setting up and deploying the application

### 6.3 Ensure Security in Deployment
**Assessment Criteria**: Secure the deployed application by: Not including passwords or sensitive information in the git repository, using environment variables or .gitignore for secret keys, and ensuring DEBUG mode is turned off.

**Expected Performance**:
- No inclusion of passwords or sensitive information in the git repository
- Use of environment variables or .gitignore to manage secret keys and configurations
- Ensuring DEBUG mode is turned off in the deployed application

## LO7: Object-Based Software Concepts

**Objective**: Demonstrate the use of object-based software concepts by designing and implementing custom data models in their Full-Stack Web application development.

### 7.1 Design and Implement a Custom Data Model
**Assessment Criteria**: Design and implement a custom data model that fits the specific purpose and requirements of the project.

**Expected Performance**:
- Design of a custom data model that fits the project's specific requirements
- Proper implementation of the data model using Django's ORM

## LO8: AI-Assisted Development

**Objective**: Leverage AI tools to orchestrate the software development process.

### 8.1 Use AI tools to assist in code creation
**Assessment Criteria**: Demonstrates strategic use of AI for generating code aligned with project objectives.

**Expected Performance**:
- Brief reflection in README.md on key decisions where AI was used to generate code, focusing on the outcomes rather than detailed prompts or manual interventions

### 8.2 Use AI tools to assist in debugging code
**Assessment Criteria**: Efficient use of AI tools to identify and resolve code issues.

**Expected Performance**:
- Brief reflection in README.md summarizing AI's role in identifying and resolving bugs, noting key interventions

### 8.3 Use AI tools to optimize code for performance and user experience
**Assessment Criteria**: AI-driven optimisation for improved performance and user experience.

**Expected Performance**:
- Short reflection on how AI contributed to performance and UX improvements
- Minimal documentation of AI use

### 8.4 Use AI tools to create automated unit tests
**Assessment Criteria**: Use GitHub Copilot to generate Django unit tests for application features, ensuring code coverage for key functionalities.

**Expected Performance**:
- README.md notes Copilot's role in creating unit tests, with brief mention of adjustments made to improve test accuracy or completeness
- Demonstrates basic understanding of test logic generated by Copilot

### 8.5 Reflect on AI's role in the development process and its impact on workflow
**Assessment Criteria**: High-level reflection on how AI tools affected the development process, with focus on outcomes rather than detailed steps.

**Expected Performance**:
- README.md includes concise insights into how AI influenced workflow, focusing on efficiency and outcomes without in-depth prompt documentation

---

## Summary for AI Agents

This document outlines the comprehensive assessment criteria for a Full-Stack Django Web application project. Key requirements include:

1. **Technical Implementation**: Django framework, responsive design, database modeling, CRUD operations
2. **Development Practices**: Agile methodology, version control, testing, code quality
3. **Security & Deployment**: Authentication/authorization, secure deployment, environment configuration
4. **Documentation**: Comprehensive README, UX process documentation, testing documentation
5. **AI Integration**: Strategic use of AI tools for development, debugging, optimization, and testing

All deliverables should demonstrate professional-level implementation with proper security practices, comprehensive documentation, and evidence of AI-assisted development workflow.