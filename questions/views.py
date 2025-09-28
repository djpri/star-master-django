from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Question


def question_list(request):
    """Display paginated list of user's personal questions (private collection)."""
    if not request.user.is_authenticated:
        # Redirect unauthenticated users to public questions
        return redirect('questions:public_list')

    # Only show user's own private questions with optimized queries
    questions = Question.objects.filter(
        owner=request.user,
        is_public=False
    ).select_related('owner').prefetch_related('tags', 'votes').order_by('-created_at')

    # Paginate questions (12 per page)
    paginator = Paginator(questions, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'questions': page_obj,
        'page_obj': page_obj,
    }

    return render(request, 'questions/list.html', context)


def public_question_list(request):
    """Display paginated list of public questions that users can save to their own collection."""
    # Only show public approved questions with optimized queries
    questions = Question.objects.filter(
        is_public=True, status=Question.STATUS_APPROVED
    ).select_related('owner').prefetch_related('tags', 'votes').order_by('-created_at')

    # Paginate questions (12 per page)
    paginator = Paginator(questions, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get saved question titles for the current user (if authenticated)
    saved_question_titles = set()
    if request.user.is_authenticated:
        saved_question_titles = set(
            Question.objects.filter(
                owner=request.user,
                is_public=False
            ).values_list('title', flat=True)
        )

    context = {
        'questions': page_obj,
        'page_obj': page_obj,
        'is_public_view': True,
        'saved_question_titles': saved_question_titles,
    }

    return render(request, 'questions/public_list.html', context)


@login_required
def save_public_question(request, question_id):
    """Save a public question to the user's personal collection."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests allowed'}, status=405)

    # Get the public question
    public_question = get_object_or_404(
        Question,
        id=question_id,
        is_public=True,
        status=Question.STATUS_APPROVED
    )

    # Check if user already has this exact question saved
    # We check for title AND that it's not public (indicating it's a saved copy)
    # AND that it has an empty body (indicating it was copied from public, not user-created)
    existing_question = Question.objects.filter(
        owner=request.user,
        title=public_question.title,
        is_public=False,
    ).first()

    if existing_question:
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({'error': 'You already have this question saved'}, status=400)
        messages.warning(
            request, 'You already have this question saved to your collection.')
        return redirect('questions:public_list')

    # Create a copy for the user (title only, no description)
    user_question = Question.objects.create(
        owner=request.user,
        title=public_question.title,
        body='',  # Don't copy the description
        is_public=False,  # User's personal copy
        status=Question.STATUS_APPROVED  # Auto-approve user's own questions
    )

    # Copy tags if any
    user_question.tags.set(public_question.tags.all())

    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            'success': True,
            'message': 'Question saved to your collection!',
            'question_id': user_question.id
        })

    messages.success(
        request, f'Question "{public_question.title}" saved to your collection!')
    return redirect('questions:public_list')
