# quizzes/models.py
from django.db import models
from django.conf import settings
from courses.models import Course


class Quiz(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="quizzes"
    )
    title = models.CharField(max_length=200)

    def __str__(self) -> str:
        return f"{self.course.title} / {self.title}"


class Question(models.Model):
    MCQ = "MCQ"
    TF = "TF"
    SHORT = "SHORT"
    TYPES = [
        (MCQ, "Multiple Choice"),
        (TF, "True/False"),
        (SHORT, "Short Answer"),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    type = models.CharField(max_length=10, choices=TYPES, default=MCQ)

    def __str__(self) -> str:
        return f"{self.quiz.title} – {self.text[:40]}"


class Option(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="options"
    )
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.text[:30]} ({'✓' if self.is_correct else '✗'})"


class Submission(models.Model):
    """Tracks student quiz attempts"""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="submissions")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quiz_submissions"
    )
    score = models.FloatField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.quiz.title} ({self.score})"
