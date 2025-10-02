from django.urls import path
from . import views

app_name = 'questions'

urlpatterns = [
    path('', views.question_list, name='list'),
    path('public/', views.public_question_list, name='public_list'),
    path('save/<int:question_id>/', views.save_public_question, name='save_public'),
    path('approve/<int:question_id>/',
         views.approve_public_question, name='approve_public'),
    path('deny/<int:question_id>/',
         views.deny_public_question, name='deny_public'),
    path('create/', views.question_create, name='create'),
    path('<int:pk>/', views.question_detail, name='detail'),
]
