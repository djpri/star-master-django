# Design Document

## Overview

This design document outlines the technical approach for enhancing the interview question and answer tracker application. The enhancements focus on completing CRUD operations for questions and answers, fixing the single question view performance issues, and implementing responsive design improvements. The design leverages the existing Django architecture with models, views, forms, and templates already in place.

## Architecture

### Current Architecture Analysis

The application follows Django's MVT (Model-View-Template) pattern with:

- **Models**: Well-structured with `Question`, `Answer`, `StarAnswer`, `BasicAnswer` using multi-table inheritance
- **Views**: Function-based views with proper authentication and permission handling
- **Templates**: DaisyUI/Tailwind CSS framework for styling
- **URL Routing**: Organized with app-level URL configurations

### Enhancement Strategy

The enhancements will extend the existing architecture by:

- Adding missing CRUD views for questions and answers
- Implementing proper form handling and validation
- Optimizing database queries in the question detail view
- Enhancing responsive design with mobile-first approach

## Components and Interfaces

### 1. Question Management Components

#### Question Create View (`questions/views.py`)

```python
@login_required
def create_question(request):
    # Handle GET: Display empty form
    # Handle POST: Validate and create question
    # Redirect to question detail on success
```

#### Question Update View (`questions/views.py`)

```python
@login_required
def update_question(request, pk):
    # Verify ownership
    # Handle GET: Display pre-populated form
    # Handle POST: Validate and update question
    # Redirect to question detail on success
```

#### Question Delete View (`questions/views.py`)

```python
@login_required
def delete_question(request, pk):
    # Verify ownership
    # Handle GET: Display confirmation page
    # Handle POST: Delete question and associated answers
    # Redirect to questions list on success
```

#### Question Form (`questions/forms.py`)

```python
class QuestionForm(forms.ModelForm):
    # Fields: title, body, tags, is_public
    # Custom validation for title uniqueness per user
    # Tag handling with autocomplete functionality
```

### 2. Answer Management Components

#### Answer Update View (`answers/views.py`)

```python
@login_required
def update_answer(request, pk):
    # Verify ownership
    # Handle answer type switching
    # Pre-populate appropriate form (STAR or Basic)
    # Handle form submission and validation
```

#### Answer Delete View (`answers/views.py`)

```python
@login_required
def delete_answer(request, pk):
    # Verify ownership
    # Handle GET: Display confirmation
    # Handle POST: Delete answer
    # Redirect to question detail
```

#### Enhanced Answer Forms (`answers/forms.py`)

```python
class AnswerUpdateForm:
    # Dynamic form that handles both STAR and Basic types
    # Includes answer type switching functionality
    # Removes is_public field (per requirements)
```

### 3. Enhanced Question Detail View

#### Optimized Question Detail (`questions/views.py`)

```python
def question_detail(request, pk):
    # Optimized query with select_related and prefetch_related
    # Proper answer type handling for STAR vs Basic rendering
    # Efficient permission checking
    # Pagination for large answer sets
```

### 4. Responsive Design Components

#### Mobile Navigation Enhancement

- Collapsible hamburger menu for mobile
- Touch-friendly button sizes (minimum 44px)
- Proper spacing for mobile interaction

#### Form Responsiveness

- Stack form fields vertically on mobile
- Appropriate input field sizing
- Mobile-optimized keyboard types

#### Card Layout Optimization

- Single column layout on mobile
- Proper spacing and padding adjustments
- Readable typography scaling

## Data Models

### Existing Models (No Changes Required)

The current model structure is well-designed and supports all requirements:

- `Question`: Handles ownership, visibility, status, and search functionality
- `Answer`: Base model with proper inheritance structure
- `StarAnswer`: Extends Answer with STAR-specific fields
- `BasicAnswer`: Extends Answer with text field

### Model Relationships

```
User (1) -----> (*) Question
Question (1) -> (*) Answer
Answer (1) ----> (1) StarAnswer | BasicAnswer
```

## Error Handling

### Permission-Based Error Handling

```python
# Consistent error handling pattern
def verify_ownership(obj, user):
    if obj.owner != user:
        raise PermissionDenied("You don't have permission to modify this resource")
```

### Form Validation Errors

- Client-side validation for immediate feedback
- Server-side validation with clear error messages
- Field-level error display in templates

### 404 Error Handling

- Custom error pages for missing questions/answers
- Proper HTTP status codes
- User-friendly error messages with navigation options

## Testing Strategy

### Unit Tests

```python
# Test cases for each CRUD operation
class QuestionCRUDTests(TestCase):
    def test_create_question_authenticated_user()
    def test_update_own_question()
    def test_delete_own_question()
    def test_permission_denied_other_user_question()

class AnswerCRUDTests(TestCase):
    def test_create_star_answer()
    def test_create_basic_answer()
    def test_update_answer_type_switching()
    def test_delete_answer()
```

### Integration Tests

```python
# End-to-end workflow tests
class QuestionAnswerWorkflowTests(TestCase):
    def test_complete_question_answer_cycle()
    def test_question_detail_view_performance()
    def test_responsive_design_elements()
```

### Performance Tests

- Database query optimization verification
- Page load time measurements
- Mobile device testing

## Implementation Details

### URL Patterns

```python
# questions/urls.py additions
path('create/', views.create_question, name='create'),
path('<int:pk>/edit/', views.update_question, name='update'),
path('<int:pk>/delete/', views.delete_question, name='delete'),

# answers/urls.py additions
path('<int:pk>/edit/', views.update_answer, name='update'),
path('<int:pk>/delete/', views.delete_answer, name='delete'),
```

### Template Structure

```
templates/
├── questions/
│   ├── create.html
│   ├── update.html
│   ├── delete_confirm.html
│   └── detail.html (enhanced)
├── answers/
│   ├── update.html
│   ├── delete_confirm.html
│   └── create.html (remove is_public field)
└── base.html (responsive enhancements)
```

### Database Query Optimization

```python
# Optimized question detail query
question = Question.objects.select_related('owner')\
    .prefetch_related('tags', 'answers__user')\
    .get(pk=pk)

# Efficient answer filtering
answers = question.answers.visible_to_user(request.user)\
    .select_related('user')\
    .order_by('-created_at')
```

### Responsive Design Implementation with Tailwind CSS & DaisyUI

```html
<!-- Mobile-first responsive classes using Tailwind -->
<div class="card bg-base-100 shadow-xl p-4 lg:p-8">
  <!-- Card content with responsive padding -->
</div>

<!-- Responsive grid layouts -->
<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
  <!-- Auto-responsive grid -->
</div>

<!-- Navigation with DaisyUI components -->
<div class="navbar bg-primary">
  <div class="navbar-start">
    <!-- Desktop menu -->
    <div class="hidden lg:flex">
      <ul class="menu menu-horizontal px-1">
        <!-- Menu items -->
      </ul>
    </div>
  </div>
  <div class="navbar-end">
    <!-- Mobile dropdown -->
    <div class="dropdown dropdown-end lg:hidden">
      <div tabindex="0" role="button" class="btn btn-ghost">
        <i class="fas fa-bars"></i>
      </div>
      <ul class="dropdown-content menu bg-base-100 rounded-box">
        <!-- Mobile menu items -->
      </ul>
    </div>
  </div>
</div>

<!-- Responsive form layouts using DaisyUI form components -->
<div class="form-control w-full">
  <label class="label">
    <span class="label-text">Field Label</span>
  </label>
  <input class="input input-bordered w-full" />
</div>

<!-- Mobile-optimized buttons -->
<button class="btn btn-primary w-full sm:w-auto">Action Button</button>

<!-- Responsive card stacking -->
<div class="flex flex-col lg:flex-row gap-4">
  <div class="card flex-1"><!-- Content --></div>
  <div class="card flex-1"><!-- Content --></div>
</div>
```

#### Key Tailwind/DaisyUI Responsive Patterns:

- Use `hidden lg:flex` and `lg:hidden` for show/hide on different screen sizes
- Apply `w-full sm:w-auto` for mobile-full, desktop-auto width buttons
- Use `p-4 lg:p-8` for responsive padding
- Apply `grid-cols-1 md:grid-cols-2` for responsive grid layouts
- Use `flex-col lg:flex-row` for responsive flex direction
- Apply DaisyUI component classes: `card`, `btn`, `input`, `navbar`, `dropdown`

### Security Considerations

- CSRF protection on all forms
- User ownership verification on all CRUD operations
- Proper permission decorators (@login_required)
- Input sanitization and validation
- SQL injection prevention through Django ORM

### Performance Optimizations

- Database query optimization with select_related/prefetch_related
- Template fragment caching for static content
- Efficient pagination for large datasets
- Lazy loading for non-critical content
- Optimized CSS/JS delivery
