from questions.models import Question
from django.db.models import Count

from django.core.paginator import Paginator
from django.shortcuts import redirect, render


def question_list(request):
    """Display paginated list of user's personal questions (both private and public)."""
    if not request.user.is_authenticated:
        # Redirect unauthenticated users to public questions
        return redirect('questions:public_list')

    # Show user's own questions (both private and public) with optimized queries
    # Annotate with answer count to avoid N+1 queries in the template
    questions = Question.objects.filter(
        owner=request.user
    ).select_related('owner').prefetch_related('tags', 'votes').annotate(
        answer_count=Count('answers')
    ).order_by('-created_at')

    # Paginate questions (12 per page)
    paginator = Paginator(questions, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get user's answer count to avoid N+1 query in stats section
    from answers.models import Answer
    user_answer_count = Answer.objects.filter(user=request.user).count()

    context = {
        'questions': page_obj,
        'page_obj': page_obj,
        'user_answer_count': user_answer_count,
    }

    return render(request, 'list.html', context)
