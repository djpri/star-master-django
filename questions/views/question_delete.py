from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from questions.models import Question


@login_required
@require_POST
def question_delete(request, pk):
    """
    Delete a question.
    - Admins can delete any question
    - Non-admins can only delete their own questions
    """
    # Admins can delete any question, non-admins only their own
    if request.user.is_superuser:
        question = get_object_or_404(Question, pk=pk)
    else:
        question = get_object_or_404(Question, pk=pk, owner=request.user)

    # Store question title for success message before deletion
    question_title = question.title

    # Check if question has answers - warn user but allow deletion
    answer_count = question.answers.count()

    question.delete()

    if answer_count > 0:
        answer_suffix = "s" if answer_count != 1 else ""
        messages.success(
            request,
            f'Question "{question_title}" and its {answer_count} '
            f'answer{answer_suffix} have been deleted.',
        )
    else:
        messages.success(
            request, f'Question "{question_title}" has been deleted.'
        )

    return redirect("questions:list")
