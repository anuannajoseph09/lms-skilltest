from django.db import models
from courses.models import Course

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)
    def __str__(self): return f"{self.course.title} / {self.title}"

class Material(models.Model):
    VIDEO='VIDEO'; PDF='PDF'; SLIDE='SLIDE'
    TYPES=[(VIDEO,'Video'),(PDF,'PDF/Notes'),(SLIDE,'Slides')]

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="materials")
    type = models.CharField(max_length=10, choices=TYPES)
    file = models.FileField(upload_to="materials/")
    def __str__(self): return f"{self.lesson} [{self.type}]"
