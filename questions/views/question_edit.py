from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from questions.models import Question, Tag
from questions.forms import QuestionForm


@login_required
def question_edit(request, pk):
    """
    Edit an existing question - only for private questions owned by the user.
    """
    question = get_object_or_404(Question, pk=pk, owner=request.user)

    # Only allow editing of private questions
    if question.is_public:
        messages.error(
            request, "Public questions cannot be edited once submitted.")
        return redirect('questions:detail', pk=question.pk)

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question, user=request.user)
        if form.is_valid():
            question = form.save(commit=False)
            question.owner = request.user

            # Private questions always remain private when edited
            question.is_public = False
            question.status = Question.STATUS_PENDING

            question.save()
            form.save_m2m()  # Save many-to-many relationships (tags)

            messages.success(
                request, f'Question "{question.title}" has been updated successfully!')
            return redirect('questions:detail', pk=question.pk)
    else:
        form = QuestionForm(instance=question, user=request.user)

    # Get available tags for the user (public tags + user's personal tags)
    available_tags = Tag.objects.filter(
        models.Q(is_public=True) | models.Q(owner=request.user)
    ).order_by('name')

    context = {
        'form': form,
        'question': question,
        'available_tags': available_tags,
        'is_edit_mode': True,
    }
    return render(request, 'edit.html', context)
