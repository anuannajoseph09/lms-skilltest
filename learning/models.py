from django.db import models
from courses.models import Course
from django.utils import timezone
from django.conf import settings 

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

class LiveSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="live_sessions")
    title = models.CharField(max_length=200)
    meet_link = models.URLField()
    start_time = models.DateTimeField()
    end_time   = models.DateTimeField()

    def is_active(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time


class LessonProgress(models.Model):
    """Marks a single student's completion for a lesson."""
    user   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lesson_progress")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="progress_marks")
    is_completed = models.BooleanField(default=True)  # simple flag
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "lesson")
        indexes = [models.Index(fields=["user", "lesson"])]

    def save(self, *args, **kwargs):
        if self.is_completed and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)