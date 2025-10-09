from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from questions.models import Question, Tag
from questions.forms import QuestionForm


@login_required
def question_edit(request, pk):
    """
    Edit an existing question.
    - Admins can edit any question
    - Non-admins can only edit their own questions
    - When non-admins edit public questions, status reverts to PENDING
    """
    # Admins can edit any question, non-admins only their own
    if request.user.is_superuser:
        question = get_object_or_404(Question, pk=pk)
    else:
        question = get_object_or_404(Question, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question, user=request.user)
        if form.is_valid():
            question = form.save(commit=False)

            # Preserve original owner (important for admin edits)
            # question.owner is already set from the instance

            # Handle status based on user role and question visibility
            is_public = form.cleaned_data.get('is_public', False)

            if is_public:
                # Public questions: non-admins editing reverts to PENDING
                if not request.user.is_superuser and question.owner != request.user:
                    # This shouldn't happen due to queryset filtering, but just in case
                    messages.error(
                        request, "You don't have permission to edit this question.")
                    return redirect('questions:detail', pk=question.pk)
                elif not request.user.is_superuser:
                    # Non-admin owner editing their own public question
                    question.status = Question.STATUS_PENDING
                    question.is_public = True
                    messages.info(
                        request,
                        "Your question has been updated and submitted for review again."
                    )
                else:
                    # Admin editing - preserve existing status
                    question.is_public = True
            else:
                # Private questions always remain private with APPROVED status
                question.is_public = False
                question.status = Question.STATUS_APPROVED

            question.save()

            # Handle tags using the form's custom logic
            tags_str = form.cleaned_data.get('tags_input', '')
            tag_names = [name.strip()
                         for name in tags_str.split(',') if name.strip()]

            tags_to_add = []
            for tag_name in tag_names:
                tag = form._get_or_create_tag(tag_name)
                if tag:
                    tags_to_add.append(tag)

            question.tags.set(tags_to_add)

            if not is_public or request.user.is_superuser:
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
    return render(request, 'questions/pages/edit.html', context)
