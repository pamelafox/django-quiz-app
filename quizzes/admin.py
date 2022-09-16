from django.contrib import admin
from .models import Quiz, Question, FreeTextAnswer, MultipleChoiceAnswer

admin.site.register(Quiz)


class FreeTextAnswerInline(admin.StackedInline):
    model = FreeTextAnswer


class MultipleChoiceAnswerInline(admin.StackedInline):
    model = MultipleChoiceAnswer


class QuestionAdmin(admin.ModelAdmin):
    inlines = [FreeTextAnswerInline, MultipleChoiceAnswerInline]


admin.site.register(Question, QuestionAdmin)
