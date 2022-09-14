from django.http import HttpResponse

def index(request):
    return HttpResponse("Here are all the quizzes")

def display(request, quiz_id):
    return HttpResponse("You're looking at quiz %s." % quiz_id)
