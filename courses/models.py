from django.db import models
from django.conf import settings


class Category(models.Model):
    """Simple category for grouping courses (e.g., Python, Web Dev)"""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    """Course model for instructors to create and manage"""
    FREE = 'free'
    APPROVAL = 'approval'

    ENROLL_CHOICES = [
        (FREE, 'Free'),
        (APPROVAL, 'Approval required'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    thumbnail = models.ImageField(
        upload_to='course_thumbs/',
        blank=True,
        null=True
    )
    enrollment_type = models.CharField(
        max_length=20,
        choices=ENROLL_CHOICES,
        default=FREE
    )
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
