from django.shortcuts import get_object_or_404, render

from questions.models import Question


def question_detail(request, pk):
    """Display a single question with its answers"""
    if request.user.is_authenticated and request.user.is_superuser:
        queryset = Question.objects.all()
    else:
        queryset = Question.objects.visible_to_user(request.user)

    question = get_object_or_404(queryset, pk=pk)

    # Get answers visible to the user with related answer content
    answers = question.answers.visible_to_user(
        request.user).select_related('user', 'staranswer', 'basicanswer')

    # Check if current user has an answer for this question
    user_answer = None
    if request.user.is_authenticated:
        user_answer = answers.filter(user=request.user).first()

    already_saved = False
    if question.is_public and request.user.is_authenticated:
        already_saved = Question.objects.filter(
            owner=request.user,
            title=question.title,
            is_public=False,
        ).exists()

    context = {
        'question': question,
        'answers': answers,
        'user_answer': user_answer,
        'already_saved': already_saved,
    }

    return render(request, 'detail.html', context)
