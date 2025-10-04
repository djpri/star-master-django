from django.core.paginator import Paginator
from django.shortcuts import render

from questions.models import Question


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

    pending_questions = Question.objects.none()
    if request.user.is_authenticated and request.user.is_superuser:
        pending_questions = Question.objects.filter(
            is_public=True,
            status=Question.STATUS_PENDING
        ).select_related('owner').prefetch_related('tags').order_by('-created_at')

    context = {
        'questions': page_obj,
        'page_obj': page_obj,
        'is_public_view': True,
        'saved_question_titles': saved_question_titles,
        'pending_questions': pending_questions,
    }

    return render(request, 'public_list.html', context)
