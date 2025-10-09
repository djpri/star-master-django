from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Count, Q
from django.contrib.postgres.search import SearchQuery
from django.db import connection

from questions.models import Question, Tag


def public_question_list(request):
    """Display paginated list of public questions that users can save to their own collection."""
    # Get filter and search parameters
    tag_filter = request.GET.get('tag', '').strip()
    search_query = request.GET.get('search', '').strip()

    # Only show public approved questions with optimized queries
    questions = Question.objects.filter(
        is_public=True, status=Question.STATUS_APPROVED
    ).select_related('owner').prefetch_related('tags')

    # Apply tag filter if provided
    selected_tag = None
    selected_tag_name = None
    if tag_filter:
        # Filter questions that have the specified tag (case-insensitive by slug)
        questions = questions.filter(tags__slug__iexact=tag_filter)
        # Get the actual tag object for display
        try:
            tag_obj = Tag.objects.filter(
                is_public=True, slug__iexact=tag_filter
            ).first()
            if tag_obj:
                selected_tag = tag_obj.slug
                selected_tag_name = tag_obj.name
            else:
                selected_tag = tag_filter
                selected_tag_name = tag_filter
        except AttributeError:
            selected_tag = tag_filter
            selected_tag_name = tag_filter

    # Apply search filter if provided
    # Search across question title (partial match), body, and answer content (full-text search)
    if search_query:
        if connection.vendor == 'postgresql':
            # Use PostgreSQL full-text search for body
            search = SearchQuery(search_query, search_type='websearch')

            # Partial match on title + full-text search on body
            questions = questions.filter(
                Q(title__icontains=search_query) |
                Q(search_vector=search)
            ).distinct()
        else:
            # Fallback to basic search for non-Postgres databases (e.g., SQLite in tests)
            questions = questions.filter(
                Q(title__icontains=search_query) |
                Q(body__icontains=search_query)
            ).distinct()

    # Order by most recent and make distinct to avoid duplicates from tag filter
    questions = questions.distinct().order_by('-created_at')

    # Paginate questions (12 per page)
    paginator = Paginator(questions, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Force evaluation and get the actual list of questions for this page
    # This prevents re-evaluation of the queryset later
    questions_list = list(page_obj.object_list)

    if questions_list:
        question_ids = [q.id for q in questions_list]

        # Get answer counts for questions on this page - single query
        from answers.models import Answer
        answer_counts = dict(
            Answer.objects.filter(
                question_id__in=question_ids,
                is_public=True  # Only count public answers
            )
            .values('question_id')
            .annotate(count=Count('id'))
            .values_list('question_id', 'count')
        )

        # Attach counts to questions as attributes
        for question in questions_list:
            question.answer_count = answer_counts.get(question.id, 0)

    # Replace the queryset with our evaluated list to prevent re-querying
    page_obj.object_list = questions_list

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

    # Get all public tags for the filter dropdown
    available_tags = Tag.objects.filter(
        is_public=True
    ).distinct().order_by('name')

    context = {
        'questions': page_obj,
        'page_obj': page_obj,
        'is_public_view': True,
        'saved_question_titles': saved_question_titles,
        'pending_questions': pending_questions,
        'available_tags': available_tags,
        'selected_tag': selected_tag,
        'selected_tag_name': selected_tag_name,
        'search_query': search_query,
    }

    return render(request, 'questions/pages/public_list.html', context)
