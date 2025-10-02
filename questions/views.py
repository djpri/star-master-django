from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import models
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import QuestionForm
from .models import Question, Tag


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

    redirect_target = request.POST.get('next') or request.GET.get('next')
    if redirect_target and not url_has_allowed_host_and_scheme(
        redirect_target,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        redirect_target = None

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
        return redirect(redirect_target or 'questions:public_list')

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
    return redirect(redirect_target or 'questions:public_list')


@login_required
def question_create(request):
    """Allow users to create a new interview question."""

    if request.method == 'POST':
        form = QuestionForm(request.POST, user=request.user)
        if form.is_valid():
            question = form.save(commit=False)
            question.owner = request.user

            is_public = question.is_public
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
        # Pre-fill the form based on query parameter
        initial_data = {}
        public_param = request.GET.get('public', '').lower()
        if public_param == 'true':
            initial_data['is_public'] = True
        elif public_param == 'false':
            initial_data['is_public'] = False

        form = QuestionForm(initial=initial_data, user=request.user)

        # Pass context about whether this is a public question
        is_public_question = public_param == 'true'

    # Get available tags for the user (public tags + user's personal tags)
    available_tags = Tag.objects.filter(
        models.Q(is_public=True) | models.Q(owner=request.user)
    ).order_by('name')

    context = {
        'form': form,
        'is_public_question': is_public_question,
        'available_tags': available_tags,
    }
    return render(request, 'questions/create.html', context)


def question_detail(request, pk):
    """Display a single question with its answers"""
    question = get_object_or_404(
        Question.objects.visible_to_user(request.user), pk=pk)

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

    return render(request, 'questions/detail.html', context)
