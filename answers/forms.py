from django import forms
from .models import StarAnswer, BasicAnswer


class AnswerTypeChoiceForm(forms.Form):
    """Form to let user choose between STAR or Basic answer type"""
    ANSWER_TYPE_CHOICES = [
        ('STAR', 'STAR Method'),
        ('BASIC', 'Basic Text Answer'),
    ]

    answer_type = forms.ChoiceField(
        choices=ANSWER_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'radio radio-primary'
        }),
        initial='STAR',
        label='Answer Type'
    )


class StarAnswerForm(forms.ModelForm):
    """Form for creating STAR method answers"""

    class Meta:
        model = StarAnswer
        fields = ['situation', 'task', 'action', 'result', 'is_public']
        widgets = {
            'situation': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 4,
                'placeholder': 'Describe the situation or context...'
            }),
            'task': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 4,
                'placeholder': 'Explain the task or challenge you faced...'
            }),
            'action': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 4,
                'placeholder': 'Detail the actions you took...'
            }),
            'result': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 4,
                'placeholder': 'Share the results and outcomes...'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-primary'
            })
        }
        labels = {
            'situation': 'Situation',
            'task': 'Task',
            'action': 'Action',
            'result': 'Result',
            'is_public': 'Make this answer publicly visible'
        }
        help_texts = {
            'situation': 'Set the scene - describe the context and background',
            'task': 'What needed to be done? What was your responsibility?',
            'action': 'What specific steps did you take to address the situation?',
            'result': 'What was the outcome? What did you learn or achieve?',
            'is_public': 'Other users will be able to see your answer if you make it public'
        }


class BasicAnswerForm(forms.ModelForm):
    """Form for creating basic text answers"""

    class Meta:
        model = BasicAnswer
        fields = ['text', 'is_public']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 8,
                'placeholder': 'Write your answer here...'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-primary'
            })
        }
        labels = {
            'text': 'Your Answer',
            'is_public': 'Make this answer publicly visible'
        }
        help_texts = {
            'text': 'Provide a comprehensive answer to the interview question',
            'is_public': 'Other users will be able to see your answer if you make it public'
        }
