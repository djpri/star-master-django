from django.urls import path

from .views.approve_public_question import approve_public_question
from .views.deny_public_question import deny_public_question
from .views.public_question_list import public_question_list
from .views.question_create import question_create
from .views.question_delete import question_delete
from .views.question_detail import question_detail
from .views.question_list import question_list
from .views.save_public_question import save_public_question


app_name = 'questions'

urlpatterns = [
    path('', question_list, name='list'),
    path('public/', public_question_list, name='public_list'),
    path('save/<int:question_id>/', save_public_question, name='save_public'),
    path('approve/<int:question_id>/',
         approve_public_question, name='approve_public'),
    path('deny/<int:question_id>/', deny_public_question, name='deny_public'),
    path('create/', question_create, name='create'),
    path('<int:pk>/', question_detail, name='detail'),
    path('<int:pk>/delete/', question_delete, name='delete'),
]
