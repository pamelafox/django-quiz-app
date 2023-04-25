from django.test import TestCase
from django.urls import reverse

from .models import FreeTextAnswer, MultipleChoiceAnswer, Question, Quiz


def create_quiz():
    quiz = Quiz.objects.create(name="Butterflies")
    question = Question.objects.create(quiz=quiz, prompt="What plant do Swallowtail caterpillars eat?")
    answer = MultipleChoiceAnswer.objects.create(
        question=question, correct_answer="Dill", choices=["Thistle", "Milkweed", "Dill"]
    )
    return quiz, question, answer


class FreeTextAnswerModelTests(TestCase):
    def test_case_insensitive(self):
        ans = FreeTextAnswer(correct_answer="Milkweed", case_sensitive=False)
        self.assertTrue(ans.is_correct("Milkweed"))
        self.assertTrue(ans.is_correct("milkweed"))
        self.assertFalse(ans.is_correct("thistle"))

    def test_case_sensitive(self):
        ans = FreeTextAnswer(correct_answer="Armeria Maritima", case_sensitive=True)
        self.assertFalse(ans.is_correct("armeria maritima"))
        self.assertTrue(ans.is_correct("Armeria Maritima"))


class MultipleChoiceAnswerModelTests(TestCase):
    def test_choices(self):
        ans = MultipleChoiceAnswer(correct_answer="Dill", choices=["Milkweed", "Dill", "Thistle"])
        self.assertTrue(ans.is_correct("Dill"))
        self.assertFalse(ans.is_correct("dill"))
        self.assertFalse(ans.is_correct("Milkweed"))


class QuizModelTests(TestCase):
    def test_quiz_relations(self):
        quiz = Quiz.objects.create(name="Butterflies")
        q1 = Question.objects.create(quiz=quiz, prompt="What plant do Swallowtail caterpillars eat?")
        a1 = MultipleChoiceAnswer.objects.create(
            question=q1, correct_answer="Dill", choices=["Thistle", "Milkweed", "Dill"]
        )
        q2 = Question.objects.create(quiz=quiz, prompt="What plant do Monarch caterpillars eat?")
        a2 = FreeTextAnswer.objects.create(question=q2, correct_answer="Milkweed", case_sensitive=False)
        self.assertEqual(len(quiz.question_set.all()), 2)
        self.assertEqual(q1.multiplechoiceanswer, a1)
        self.assertEqual(q2.freetextanswer, a2)


class IndexViewTests(TestCase):
    def test_no_quizzes(self):
        response = self.client.get(reverse("quizzes:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No quizzes are available.")
        self.assertQuerySetEqual(response.context["quiz_list"], [])

    def test_one_quiz(self):
        quiz, _, _ = create_quiz()
        response = self.client.get(reverse("quizzes:index"))
        self.assertQuerySetEqual(
            response.context["quiz_list"],
            [quiz],
        )


class DisplayQuizViewTests(TestCase):
    def test_quiz_404(self):
        url = reverse("quizzes:display_quiz", args=(12,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_quiz_redirects(self):
        quiz, question, _ = create_quiz()
        url = reverse("quizzes:display_quiz", args=(quiz.pk,))
        response = self.client.get(url)
        self.assertRedirects(response, reverse("quizzes:display_question", args=(quiz.pk, question.pk)))


class DisplayQuestionViewTests(TestCase):
    def test_quiz_404(self):
        url = reverse("quizzes:display_question", args=(12, 1))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_question_404(self):
        quiz, question, _ = create_quiz()
        url = reverse("quizzes:display_question", args=(quiz.pk, question.pk + 100))
        response = self.client.get(url)
        self.assertContains(response, "that question doesn't exist")

    def test_quiz_question_exists(self):
        quiz, question, answer = create_quiz()

        url = reverse("quizzes:display_question", args=(quiz.pk, question.pk))
        response = self.client.get(url)
        self.assertContains(response, quiz.name)
        self.assertContains(response, question.prompt)
        self.assertContains(response, answer.choices[0])


class GradeQuestionViewTests(TestCase):
    def test_question_404(self):
        url = reverse("quizzes:grade_question", args=(12,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_question_correct(self):
        _, question, answer = create_quiz()

        url = reverse("quizzes:grade_question", args=(question.pk,))
        response = self.client.post(url, {"answer": answer.correct_answer})
        self.assertTrue(response.context["is_correct"])
        self.assertEqual(response.context["correct_answer"], answer.correct_answer)
