from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.views.decorators.http import require_POST
from questions.models import Question
from .models import Answer
from .forms import AnswerTypeChoiceForm, StarAnswerForm, BasicAnswerForm


@login_required
def create_answer(request, question_id):
    """Create a new answer for a specific question"""
    # Get the question, ensuring it's visible to the user
    try:
        question = Question.objects.visible_to_user(request.user).get(
            id=question_id
        )
    except Question.DoesNotExist:
        # Question doesn't exist or user doesn't have permission to see it
        context = {
            "error_title": "Question Not Found",
            "error_message": (
                "The question you're trying to answer doesn't exist or "
                "you don't have permission to view it."
            ),
            "back_url": "questions:list",
            "back_text": "Back to Questions",
        }
        return render(request, "answers/pages/error.html", context, status=404)

    # Business rule: Public questions (approved public questions) should not
    # have answers linked to them
    if question.is_visible_publicly:
        context = {
            "error_title": "Cannot Create Answer",
            "error_message": (
                "You cannot create answers for public questions. "
                "Public questions are designed to be used as "
                "read-only examples."
            ),
            "back_url": "questions:list",
            "back_text": "Back to Questions",
        }
        return render(request, "answers/pages/error.html", context, status=404)

    # Handle form submission
    if request.method == "POST":
        answer_type = request.POST.get("answer_type", "STAR")

        if answer_type == "STAR":
            form = StarAnswerForm(request.POST)
            if form.is_valid():
                answer = form.save(commit=False)
                answer.question = question
                answer.user = request.user
                # Default to private since they can only answer private
                # questions
                answer.is_public = False
                answer.save()
                messages.success(
                    request, "Your STAR answer has been created successfully!"
                )
                return redirect("questions:detail", pk=question.pk)
        else:  # BASIC
            form = BasicAnswerForm(request.POST)
            if form.is_valid():
                answer = form.save(commit=False)
                answer.question = question
                answer.user = request.user
                # Default to private since they can only answer private
                # questions
                answer.is_public = False
                answer.save()
                messages.success(
                    request, "Your answer has been created successfully!"
                )
                return redirect("questions:detail", pk=question.pk)
    else:
        # GET request - show the form
        answer_type = request.GET.get("type", "STAR")
        if answer_type == "STAR":
            form = StarAnswerForm()
        else:
            form = BasicAnswerForm()

    # Prepare context
    type_choice_form = AnswerTypeChoiceForm(
        initial={"answer_type": answer_type}
    )

    context = {
        "question": question,
        "form": form,
        "type_choice_form": type_choice_form,
        "answer_type": answer_type,
    }

    return render(request, "answers/pages/create.html", context)


def answer_detail(request, pk):
    """Display a single answer with full details"""
    answer = get_object_or_404(
        Answer.objects.visible_to_user(request.user), pk=pk
    )

    # Get the specific answer type (StarAnswer or BasicAnswer)
    if hasattr(answer, "staranswer"):
        specific_answer = answer.staranswer
    elif hasattr(answer, "basicanswer"):
        specific_answer = answer.basicanswer
    else:
        specific_answer = answer

    context = {
        "answer": answer,
        "specific_answer": specific_answer,
        "question": answer.question,
    }

    return render(request, "answers/pages/detail.html", context)


@login_required
def answer_edit(request, pk):
    """Edit an existing answer - only owner can edit their own answers"""
    answer = get_object_or_404(Answer, pk=pk, user=request.user)

    # Get the specific answer type instance
    if hasattr(answer, "staranswer"):
        specific_answer = answer.staranswer
        form_class = StarAnswerForm
        answer_type = "STAR"
    elif hasattr(answer, "basicanswer"):
        specific_answer = answer.basicanswer
        form_class = BasicAnswerForm
        answer_type = "BASIC"
    else:
        # Fallback - shouldn't happen in normal use
        raise Http404("Answer type not found")

    if request.method == "POST":
        form = form_class(request.POST, instance=specific_answer)
        if form.is_valid():
            answer_instance = form.save(commit=False)
            # Ensure ownership and privacy settings remain unchanged
            answer_instance.user = request.user
            answer_instance.is_public = False  # Keep answers private
            answer_instance.save()

            messages.success(
                request,
                f"Your {answer_type} answer has been updated successfully!",
            )
            return redirect("answers:detail", pk=answer.pk)
    else:
        form = form_class(instance=specific_answer)

    context = {
        "form": form,
        "answer": answer,
        "specific_answer": specific_answer,
        "question": answer.question,
        "answer_type": answer_type,
        "is_edit_mode": True,
    }

    return render(request, "answers/pages/edit.html", context)


@login_required
@require_POST
def answer_delete(request, pk):
    """Delete an answer - only owner can delete their own answers"""
    answer = get_object_or_404(Answer, pk=pk, user=request.user)

    # Store answer details for success message before deletion
    answer_type = answer.answer_type
    question_title = answer.question.title
    question_pk = answer.question.pk

    answer.delete()

    messages.success(
        request,
        f'Your {answer_type} answer for "{question_title}" has been deleted.',
    )

    return redirect("questions:detail", pk=question_pk)
