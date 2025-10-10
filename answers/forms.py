from django import forms
from .models import StarAnswer, BasicAnswer


class AnswerTypeChoiceForm(forms.Form):
    """Form to let user choose between STAR or Basic answer type"""

    ANSWER_TYPE_CHOICES = [
        ("STAR", "STAR Method"),
        ("BASIC", "Basic Text Answer"),
    ]

    answer_type = forms.ChoiceField(
        choices=ANSWER_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "radio radio-primary"}),
        initial="STAR",
        label="Answer Type",
    )


class StarAnswerForm(forms.ModelForm):
    """Form for creating STAR method answers"""

    class Meta:
        model = StarAnswer
        fields = ["situation", "task", "action", "result"]
        widgets = {
            "situation": forms.Textarea(
                attrs={
                    "class": "textarea textarea-bordered w-full",
                    "rows": 4,
                    "placeholder": "Describe the situation or context...",
                }
            ),
            "task": forms.Textarea(
                attrs={
                    "class": "textarea textarea-bordered w-full",
                    "rows": 4,
                    "placeholder": (
                        "Explain the task or challenge you faced..."
                    ),
                }
            ),
            "action": forms.Textarea(
                attrs={
                    "class": "textarea textarea-bordered w-full",
                    "rows": 4,
                    "placeholder": "Detail the actions you took...",
                }
            ),
            "result": forms.Textarea(
                attrs={
                    "class": "textarea textarea-bordered w-full",
                    "rows": 4,
                    "placeholder": "Share the results and outcomes...",
                }
            ),
        }
        labels = {
            "situation": "Situation",
            "task": "Task",
            "action": "Action",
            "result": "Result",
        }
        help_texts = {
            "situation": (
                "Set the scene - describe the context and background"
            ),
            "task": (
                "What needed to be done? What was your responsibility?"
            ),
            "action": (
                "What specific steps did you take to address "
                "the situation?"
            ),
            "result": (
                "What was the outcome? What did you learn or achieve?"
            ),
        }


class BasicAnswerForm(forms.ModelForm):
    """Form for creating basic text answers"""

    class Meta:
        model = BasicAnswer
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "class": "textarea textarea-bordered w-full",
                    "rows": 8,
                    "placeholder": "Write your answer here...",
                }
            )
        }
        labels = {"text": "Your Answer"}
        help_texts = {
            "text": "Provide a comprehensive answer to the interview question"
        }
