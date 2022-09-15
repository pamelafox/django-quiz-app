from django.shortcuts import get_object_or_404,render

from .models import Quiz

def index(request):
    quiz_list = Quiz.objects.all()
    context = {'quiz_list': quiz_list}
    return render(request, 'quizzes/index.html', context)


def display(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    return render(request, 'quizzes/display.html', {'quiz': quiz})


def grade(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    return render(request, 'quizzes/display.html', {'quiz': quiz})
