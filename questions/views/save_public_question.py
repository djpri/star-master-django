from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.http import url_has_allowed_host_and_scheme

from questions.models import Question


@login_required
def save_public_question(request, question_id):
    """Save a public question to the user's personal collection."""
    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST requests allowed"}, status=405
        )

    redirect_target = request.POST.get("next") or request.GET.get("next")
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
        status=Question.STATUS_APPROVED,
    )

    # Check if user already has this exact question saved
    # We check for title AND that it's not public
    # (indicating it's a saved copy)
    # AND that it has an empty body
    # (indicating it was copied from public, not user-created)
    existing_question = Question.objects.filter(
        owner=request.user,
        title=public_question.title,
        is_public=False,
    ).first()

    if existing_question:
        if request.headers.get("Accept") == "application/json":
            return JsonResponse(
                {"error": "You already have this question saved"}, status=400
            )
        messages.warning(
            request, "You already have this question saved to your collection."
        )
        return redirect(redirect_target or "questions:public_list")

    # Create a copy for the user (title only, no description)
    user_question = Question.objects.create(
        owner=request.user,
        title=public_question.title,
        body="",  # Don't copy the description
        is_public=False,  # User's personal copy
        status=Question.STATUS_APPROVED,  # Auto-approve user's own questions
    )

    # Copy tags if any
    user_question.tags.set(public_question.tags.all())

    if request.headers.get("Accept") == "application/json":
        return JsonResponse(
            {
                "success": True,
                "message": "Question saved to your collection!",
                "question_id": user_question.id,
            }
        )

    messages.success(
        request,
        f'Question "{public_question.title}" saved to your collection!',
    )
    return redirect(redirect_target or "questions:public_list")
