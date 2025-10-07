import os
import django
from django.utils.text import slugify
from django.contrib.auth import get_user_model

# --------------- Setup Django ---------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lms.settings")
django.setup()

from courses.models import Category, Course
from learning.models import Lesson, Material
from quizzes.models import Quiz, Question, Option, Submission
from enrollments.models import Enrollment

User = get_user_model()

# -------------------------------------------------
# USERS
# -------------------------------------------------
admin, _ = User.objects.get_or_create(
    username="admin",
    defaults={"email": "admin@example.com", "is_staff": True, "is_superuser": True},
)
admin.set_password("admin123")
admin.save()

instructor1, _ = User.objects.get_or_create(
    username="instructor1",
    defaults={
        "email": "instructor1@example.com",
        "role": "instructor",
        "is_instructor_approved": True,
    },
)
instructor1.set_password("test1234")
instructor1.save()

instructor2, _ = User.objects.get_or_create(
    username="instructor2",
    defaults={
        "email": "instructor2@example.com",
        "role": "instructor",
        "is_instructor_approved": True,
    },
)
instructor2.set_password("test1234")
instructor2.save()

student1, _ = User.objects.get_or_create(
    username="student1",
    defaults={"email": "student1@example.com", "role": "student"},
)
student1.set_password("test1234")
student1.save()

student2, _ = User.objects.get_or_create(
    username="student2",
    defaults={"email": "student2@example.com", "role": "student"},
)
student2.set_password("test1234")
student2.save()

print("✅ Users created")

# -------------------------------------------------
# CATEGORIES
# -------------------------------------------------
categories = ["Python", "Web Development", "Data Science"]
for name in categories:
    Category.objects.get_or_create(name=name, slug=slugify(name))
print("✅ Categories created")

# -------------------------------------------------
# COURSES
# -------------------------------------------------
cat_python = Category.objects.get(name="Python")
cat_web = Category.objects.get(name="Web Development")

course1, _ = Course.objects.get_or_create(
    title="Python for Beginners",
    category=cat_python,
    instructor=instructor1,
    defaults={
        "description": "A complete introduction to Python.",
        "enrollment_type": Course.FREE,
        "is_active": True,
    },
)

course2, _ = Course.objects.get_or_create(
    title="Advanced Django Development",
    category=cat_web,
    instructor=instructor2,
    defaults={
        "description": "Master Django and build full-stack web apps.",
        "enrollment_type": Course.APPROVAL,
        "is_active": True,
    },
)

print("✅ Courses created")

# -------------------------------------------------
# LESSONS & MATERIALS
# -------------------------------------------------
l1, _ = Lesson.objects.get_or_create(
    course=course1,
    title="Intro to Python",
    order=1,
    description="Learn what Python is and how it works.",
)
l2, _ = Lesson.objects.get_or_create(
    course=course1,
    title="Data Types & Variables",
    order=2,
    description="Understand basic data types and variables in Python.",
)
Material.objects.get_or_create(lesson=l1, type="PDF", file="materials/python_intro.pdf")
Material.objects.get_or_create(lesson=l2, type="VIDEO", file="materials/datatypes.mp4")

l3, _ = Lesson.objects.get_or_create(
    course=course2,
    title="Setting up Django",
    order=1,
    description="Learn Django setup and environment configuration.",
)
Material.objects.get_or_create(lesson=l3, type="PDF", file="materials/django_setup.pdf")

print("✅ Lessons & materials created")

# -------------------------------------------------
# QUIZZES
# -------------------------------------------------
quiz1, _ = Quiz.objects.get_or_create(course=course1, title="Python Basics Quiz")
q1, _ = Question.objects.get_or_create(quiz=quiz1, text="Python is a ___ language?", type="MCQ")
Option.objects.get_or_create(question=q1, text="Programming", is_correct=True)
Option.objects.get_or_create(question=q1, text="Markup", is_correct=False)

q2, _ = Question.objects.get_or_create(quiz=quiz1, text="Files in Python end with .py?", type="TF")
Option.objects.get_or_create(question=q2, text="True", is_correct=True)
Option.objects.get_or_create(question=q2, text="False", is_correct=False)

quiz2, _ = Quiz.objects.get_or_create(course=course2, title="Django Setup Quiz")
q3, _ = Question.objects.get_or_create(quiz=quiz2, text="Django uses which language?", type="MCQ")
Option.objects.get_or_create(question=q3, text="Python", is_correct=True)
Option.objects.get_or_create(question=q3, text="Java", is_correct=False)

print("✅ Quizzes, questions, and options created")

# -------------------------------------------------
# ENROLLMENTS & SUBMISSIONS
# -------------------------------------------------
enr1, _ = Enrollment.objects.get_or_create(user=student1, course=course1, status="approved")
enr2, _ = Enrollment.objects.get_or_create(user=student2, course=course2, status="pending")

Submission.objects.get_or_create(quiz=quiz1, user=student1, score=90)
Submission.objects.get_or_create(quiz=quiz1, user=student2, score=70)
Submission.objects.get_or_create(quiz=quiz2, user=student1, score=80)

print("✅ Enrollments and quiz submissions created")

print("\n🎉 All sample data successfully seeded!")
