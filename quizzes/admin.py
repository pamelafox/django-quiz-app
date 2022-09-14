from django.contrib import admin
from .models import Quiz, Question, FreeTextAnswer, MultipleChoiceAnswer

admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(FreeTextAnswer)
admin.site.register(MultipleChoiceAnswer)
