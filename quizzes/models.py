from django.db import models
from django.contrib.postgres import fields


class Quiz(models.Model):
  name = models.CharField(max_length=100)

  def __str__(self):
    return f"<Quiz: {self.name}>"

  def display(self):
    # Display the quiz name
    print(f"Welcome to the quiz on {self.name}!")
    # Initialize the correct counter to 0
    correct_count = 0
    # Iterate through the questions
    #  Display each question
    #  Increment the correct counter accordingly
    for question in self.questions:
      question.display()
      if question.answer_status == 'correct':
        correct_count += 1
    # Print the ratio of correct/total
    print(f"You got {correct_count}/{len(self.questions)} correct.")



class Question(models.Model):
  quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
  prompt = models.CharField(max_length=200)

  def __str__(self):
    return self.prompt

  def display(self):
    print(self.prompt)
    self.answer.display()
    user_answer = input()
    if self.answer.is_correct(user_answer):
      print("You got it!")
      self.answer_status = 'correct'
    else:
      print(f"Sorry, it was: {self.answer.correct_answer}")
      self.answer_status = 'incorrect'

class Answer(models.Model):
  question = models.OneToOneField(
        Question,
        on_delete=models.CASCADE
    )
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

  def display(self):
    if self.case_sensitive:
      print("Type your answer in (capitalization matters!):")
    else:
      print("Type your answer in (don't worry about capitalization):")

class MultipleChoiceAnswer(Answer):
  choices = fields.ArrayField(models.CharField(max_length=200, blank=True))

  def __str__(self):
    return f"{self.correct_answer} from {self.choices}"

  def is_correct(self, user_answer):
    """Assumes user answer is number corresponding to answer."""
    return self.choices[int(user_answer) - 1] == self.correct_answer

  def is_correct(self, user_answer):
    self.user_answer = int(user_answer)
    self.user_answer -= 1
    correct_index = self.choices.index(self.correct_answer)
    if self.user_answer == correct_index:
      return True
    else:
      return False

  def display(self):
    print("Type the number corresponding to the correct answer.")
    for i in range(0, len(self.choices)):
      print(f"{i + 1}. {self.choices[i]}")
