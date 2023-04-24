from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import generic

from .models import Question, Quiz


class IndexView(generic.ListView):
    model = Quiz
    template_name = "quizzes/index.html"


def display_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    question = quiz.question_set.first()
    return redirect(reverse("quizzes:display_question", kwargs={"quiz_id": quiz_id, "question_id": question.pk}))


def display_question(request, quiz_id, question_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    # fetch ALL of the questions to find current and next question
    questions = quiz.question_set.all()
    current_question, next_question = None, None
    for ind, question in enumerate(questions):
        if question.pk == question_id:
            current_question = question
            if ind != len(questions) - 1:
                next_question = questions[ind + 1]

    return render(
        request,
        "quizzes/display.html",
        {"quiz": quiz, "question": current_question, "next_question": next_question},
    )


def grade_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    answer = question.get_answer()
    if answer is None:
        return render(request, "quizzes/partial.html", {"error": "Question must have an answer"}, status=422)
    is_correct = answer.is_correct(request.POST.get("answer"))
    return render(
        request,
        "quizzes/partial.html",
        {"is_correct": is_correct, "correct_answer": answer.correct_answer},
    )
