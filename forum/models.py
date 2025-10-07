from django.db import models
from django.conf import settings
from courses.models import Course

class Thread(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="threads")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    body  = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Reply(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="replies")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body   = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
