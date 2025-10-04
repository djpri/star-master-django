from questions.models import Question


from django.core.paginator import Paginator
from django.shortcuts import redirect, render


def question_list(request):
    """Display paginated list of user's personal questions (both private and public)."""
    if not request.user.is_authenticated:
        # Redirect unauthenticated users to public questions
        return redirect('questions:public_list')

    # Show user's own questions (both private and public) with optimized queries
    questions = Question.objects.filter(
        owner=request.user
    ).select_related('owner').prefetch_related('tags', 'votes').order_by('-created_at')

    # Paginate questions (12 per page)
    paginator = Paginator(questions, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'questions': page_obj,
        'page_obj': page_obj,
    }

    return render(request, 'list.html', context)
