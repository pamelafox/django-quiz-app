from django.contrib.postgres import fields
from django.db import models


class Quiz(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    prompt = models.CharField(max_length=200)

    def __str__(self):
        return self.prompt


class Answer(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE)
    correct_answer = models.CharField(max_length=200)

    class Meta:
        abstract = True


class FreeTextAnswer(Answer):
    case_sensitive = models.BooleanField(default=False)

    def __str__(self):
        return self.correct_answer

    def is_correct(self, user_answer):
        if not self.case_sensitive:
            return user_answer.lower() == self.correct_answer.lower()
        return user_answer == self.correct_answer


class MultipleChoiceAnswer(Answer):
    choices = fields.ArrayField(models.CharField(max_length=200, blank=True))

    def __str__(self):
        return f"{self.correct_answer} from {self.choices}"

    def is_correct(self, user_answer):
        return user_answer == self.correct_answer
