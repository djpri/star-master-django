from questions.models import Question, Tag
from django.db.models import Count, Q
from django.contrib.postgres.search import SearchQuery
from django.db import connection

from django.core.paginator import Paginator
from django.shortcuts import redirect, render

# Sorting options for private questions (value, label)
SORT_OPTIONS = (
    ("-created_at", "Newest First"),
    ("created_at", "Oldest First"),
    ("title", "Title (A-Z)"),
    ("-title", "Title (Z-A)"),
    ("-answer_count", "Most Answers"),
    ("answer_count", "Fewest Answers"),
)

# Visibility filter options (value, label)
VIEW_OPTIONS = (
    ("personal", "Personal Questions Only"),
    ("public", "Your Public Questions"),
    ("all", "All Your Questions"),
)


def question_list(request):
    """
    Display paginated list of user's personal questions
    (both private and public).
    """
    if not request.user.is_authenticated:
        # Redirect unauthenticated users to public questions
        return redirect("questions:public_list")

    # Get filter, search, sort, and view parameters
    tag_filter = request.GET.get("tag", "").strip()
    search_query = request.GET.get("search", "").strip()
    sort_by = request.GET.get("sort", "-created_at").strip()
    view_mode = request.GET.get("view", "personal").strip()

    # Validate view mode
    valid_view_values = [option[0] for option in VIEW_OPTIONS]
    if view_mode not in valid_view_values:
        view_mode = "personal"  # Default to personal

    # Start with user's own questions with optimized queries
    questions = (
        Question.objects.filter(owner=request.user)
        .select_related("owner")
        .prefetch_related("tags")
    )

    # Apply visibility filter based on view mode
    if view_mode == "personal":
        # Only show private questions
        questions = questions.filter(is_public=False)
    elif view_mode == "public":
        # Only show public questions (regardless of status)
        questions = questions.filter(is_public=True)

    # Apply tag filter if provided
    selected_tag = None
    selected_tag_name = None
    if tag_filter:
        # Filter questions that have the specified tag (case-insensitive by
        # slug)
        questions = questions.filter(tags__slug__iexact=tag_filter)
        # Get the actual tag object for display
        try:
            tag_obj = Tag.objects.filter(
                Q(owner=request.user, slug__iexact=tag_filter)
                | Q(is_public=True, slug__iexact=tag_filter)
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
    # Search across question title (partial match), body, and answer content
    # (full-text search)
    if search_query:
        if connection.vendor == "postgresql":
            # Use PostgreSQL full-text search for body and answers
            search = SearchQuery(search_query, search_type="websearch")

            # Partial match on title + full-text search on body
            questions_with_search = questions.filter(
                Q(title__icontains=search_query) | Q(search_vector=search)
            )

            # Also find questions that have answers matching the search query
            from answers.models import Answer

            matching_answer_question_ids = (
                Answer.objects.filter(user=request.user, search_vector=search)
                .values_list("question_id", flat=True)
                .distinct()
            )

            # Combine both querysets (questions matching OR having matching
            # answers)
            questions = questions.filter(
                Q(id__in=questions_with_search.values_list("id", flat=True))
                | Q(id__in=matching_answer_question_ids)
            ).distinct()
        else:
            # Fallback to basic search for non-Postgres databases
            # (e.g., SQLite in tests)
            # Only search question title and body for simplicity
            questions = questions.filter(
                Q(title__icontains=search_query)
                | Q(body__icontains=search_query)
            ).distinct()

    # Validate and apply sorting
    valid_sort_values = [option[0] for option in SORT_OPTIONS]
    if sort_by not in valid_sort_values:
        sort_by = "-created_at"  # Default to newest first

    # If sorting by answer count, annotate the queryset
    # Otherwise, apply simple ordering
    if "answer_count" in sort_by:
        from answers.models import Answer

        questions = (
            questions.annotate(
                answer_count=Count("answers", distinct=True)
            )
            .distinct()
            .order_by(sort_by, "-created_at")
        )
    else:
        # Order by selected sort option and make distinct to avoid
        # duplicates from tag filter
        questions = questions.distinct().order_by(sort_by)

    # Paginate questions (12 per page)
    paginator = Paginator(questions, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Force evaluation and get the actual list of questions for this page
    # This prevents re-evaluation of the queryset later
    questions_list = list(page_obj.object_list)

    # If answer counts were not already annotated (i.e., not sorting by
    # answer_count), fetch them separately for the current page
    if "answer_count" not in sort_by and questions_list:
        question_ids = [q.id for q in questions_list]

        # Get answer counts for questions on this page - single query
        from answers.models import Answer

        answer_counts = dict(
            Answer.objects.filter(question_id__in=question_ids)
            .values("question_id")
            .annotate(count=Count("id"))
            .values_list("question_id", "count")
        )

        # Attach counts to questions as attributes
        for question in questions_list:
            question.answer_count = answer_counts.get(question.id, 0)

    # Replace the queryset with our evaluated list to prevent re-querying
    page_obj.object_list = questions_list

    # Get all available tags for the filter dropdown
    # Include both public tags and user's private tags
    available_tags = (
        Tag.objects.filter(Q(is_public=True) | Q(owner=request.user))
        .distinct()
        .order_by("name")
    )

    # Get sort option label for display
    sort_label = next(
        (label for value, label in SORT_OPTIONS if value == sort_by),
        "Newest First",
    )

    # Get view mode label for display
    view_label = next(
        (label for value, label in VIEW_OPTIONS if value == view_mode),
        "Personal Questions Only",
    )

    context = {
        "questions": page_obj,
        "page_obj": page_obj,
        "available_tags": available_tags,
        "selected_tag": selected_tag,
        "selected_tag_name": selected_tag_name,
        "search_query": search_query,
        "sort_options": SORT_OPTIONS,
        "selected_sort": sort_by,
        "selected_sort_label": sort_label,
        "view_options": VIEW_OPTIONS,
        "selected_view": view_mode,
        "selected_view_label": view_label,
    }

    return render(request, "questions/pages/list.html", context)
