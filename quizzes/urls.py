from django.urls import path

from . import views

app_name = 'quizzes'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:quiz_id>/', views.display_quiz, name='display_quiz'),
    path('<int:quiz_id>/questions/<int:question_id>', views.display_question, name='display_question'),
    path('questions/<int:question_id>/grade/', views.grade_question, name='grade_question'),
]