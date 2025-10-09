from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import redirect, render

from questions.forms import QuestionForm
from questions.models import Question, Tag


@login_required
def question_create(request):
    """Allow users to create a new interview question."""

    public_param = (request.GET.get('public') or '').lower()
    force_public = public_param == 'true'
    force_private = public_param == 'false'

    initial_data = {}
    if force_public:
        initial_data['is_public'] = True
    elif force_private:
        initial_data['is_public'] = False

    if request.method == 'POST':
        post_data = request.POST.copy()
        if force_public:
            post_data['is_public'] = 'true'

        form = QuestionForm(post_data, user=request.user)
        if form.is_valid():
            question = form.save(commit=False)
            question.owner = request.user

            is_public = form.cleaned_data.get('is_public', False)
            question.is_public = is_public

            if request.user.is_superuser:
                question.status = Question.STATUS_APPROVED
                approval_message = 'Your question has been created successfully!'
            elif is_public:
                question.status = Question.STATUS_PENDING
                approval_message = 'Your question is pending review by a moderator.'
            else:
                question.status = Question.STATUS_APPROVED
                approval_message = 'Your question has been created successfully!'

            question.save()
            form.save()  # This will handle tags via the custom save method

            messages.success(request, approval_message)
            return redirect('questions:detail', pk=question.pk)
    else:
        form = QuestionForm(initial=initial_data, user=request.user)

    truthy_values = {'true', '1', 'on', 'yes'}
    form_data_public = str(form.data.get('is_public', '')).lower()
    is_public_question = force_public or form_data_public in truthy_values or form.initial.get(
        'is_public') is True

    # Get available tags for the user (public tags + user's personal tags)
    available_tags = Tag.objects.filter(
        models.Q(is_public=True) | models.Q(owner=request.user)
    ).order_by('name')

    context = {
        'form': form,
        'is_public_question': is_public_question,
        'available_tags': available_tags,
    }
    return render(request, 'questions/pages/create.html', context)
