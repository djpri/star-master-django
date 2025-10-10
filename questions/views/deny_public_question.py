from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from questions.models import Question


@login_required
def deny_public_question(request, question_id):
    """Allow admins to deny pending public questions."""
    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST requests allowed"}, status=405
        )

    if not request.user.is_superuser:
        return JsonResponse(
            {"error": "Only admins can deny questions"}, status=403
        )

    redirect_target = request.POST.get("next") or request.GET.get("next")
    if redirect_target and not url_has_allowed_host_and_scheme(
        redirect_target,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        redirect_target = None

    redirect_target = redirect_target or reverse("questions:public_list")

    question = get_object_or_404(
        Question,
        id=question_id,
        is_public=True,
    )

    if question.status == Question.STATUS_DENIED:
        if request.headers.get("Accept") == "application/json":
            return JsonResponse(
                {"success": True, "message": "Question already denied."}
            )
        messages.info(request, "Question is already denied.")
        return redirect(redirect_target)

    question.status = Question.STATUS_DENIED
    question.save(update_fields=["status"])

    if request.headers.get("Accept") == "application/json":
        return JsonResponse(
            {"success": True, "message": "Question denied successfully."}
        )

    messages.success(
        request, f'Question "{question.title}" denied successfully.'
    )
    return redirect(redirect_target)
