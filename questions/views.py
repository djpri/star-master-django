from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Question


def question_list(request):
    """Display paginated list of questions visible to the user."""
    questions = Question.objects.visible_to_user(request.user)

    # Paginate questions (12 per page)
    paginator = Paginator(questions, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'questions': page_obj,
        'page_obj': page_obj,
    }

    return render(request, 'questions/list.html', context)
