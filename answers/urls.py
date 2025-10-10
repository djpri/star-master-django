from django.urls import path
from . import views

app_name = "answers"

urlpatterns = [
    path("create/<int:question_id>/", views.create_answer, name="create"),
    path("<int:pk>/", views.answer_detail, name="detail"),
    path("<int:pk>/edit/", views.answer_edit, name="edit"),
    path("<int:pk>/delete/", views.answer_delete, name="delete"),
]
