from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [('instructor', 'Instructor'), ('student', 'Student')]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    qualifications = models.TextField(blank=True)

    def is_instructor(self): return self.role == 'instructor'
    def is_student(self): return self.role == 'student'

