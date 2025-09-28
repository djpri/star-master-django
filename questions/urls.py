from django.urls import path
from . import views

app_name = 'questions'

urlpatterns = [
    path('', views.question_list, name='list'),
    path('public/', views.public_question_list, name='public_list'),
    path('save/<int:question_id>/', views.save_public_question, name='save_public'),
    path('<int:pk>/', views.question_detail, name='detail'),
]
