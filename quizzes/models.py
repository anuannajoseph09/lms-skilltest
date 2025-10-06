# Create your models here.
from django.db import models
from django.conf import settings
from courses.models import Course

class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="quizzes")
    title = models.CharField(max_length=200)
    def __str__(self): return f"{self.course.title} / {self.title}"

class Question(models.Model):
    MCQ='MCQ'; TF='TF'; SHORT='SHORT'
    TYPES=[(MCQ,'Multiple Choice'),(TF,'True/False'),(SHORT,'Short Answer')]
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    text = models.TextField()
    type = models.CharField(max_length=10, choices=TYPES, default=MCQ)

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

# students will create Attempt in student milestone
