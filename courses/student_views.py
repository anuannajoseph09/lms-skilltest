# courses/student_views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q
from django.contrib.auth import get_user_model

from .models import Course, Category
from enrollments.models import Enrollment

User = get_user_model()

@login_required
def catalog(request):
    qs = Course.objects.filter(is_active=True).select_related("category", "instructor")

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

    category = request.GET.get("category", "").strip()
    if category:
        qs = qs.filter(category__slug=category)

    instructor = request.GET.get("instructor", "").strip()
    if instructor:
        qs = qs.filter(instructor__username__iexact=instructor)

    sort = request.GET.get("sort", "popular")
    if sort == "newest":
        qs = qs.order_by("-created_at")
    elif sort == "title":
        qs = qs.order_by("title")
    else:  # popular
        qs = qs.annotate(e_count=Count("enrollments")).order_by("-e_count", "-created_at")

    categories = Category.objects.order_by("name")
    instructors = User.objects.filter(role="instructor", is_instructor_approved=True).order_by("username")

        # Map of my enrollments by course_id
    my_enrolls = {}
    if request.user.is_authenticated:
        my_enrolls = {
            e.course_id: e
            for e in Enrollment.objects
                .filter(user=request.user)
                .select_related("course")
        }

    # Convert queryset to list so we can add attrs
    courses = list(qs)
    for c in courses:
        # None or Enrollment instance
        c.enroll = my_enrolls.get(c.id)

    return render(request, "student/courses/catalog.html", {
        "courses": courses,
        "categories": categories,
        "instructors": instructors,
        "q": q, "category": category, "instructor": instructor, "sort": sort,
    })


@login_required
def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id, is_active=True)
    e, created = Enrollment.objects.get_or_create(user=request.user, course=course)
    if not created:
        messages.info(request, f"You are already enrolled ({e.status}).")
        return redirect("courses:learn", course_id=course.id)

    if course.enrollment_type == Course.FREE:
        e.status = Enrollment.APPROVED
        e.save()
        messages.success(request, "Enrolled successfully! You can start learning now.")
        return redirect("courses:learn", course_id=course.id)
    else:
        e.status = Enrollment.PENDING
        e.save()
        messages.info(request, "Enrollment request sent. Please wait for approval.")
        return redirect("courses:catalog")

@login_required
def my_courses(request):
    enrolls = (Enrollment.objects
               .filter(user=request.user, status=Enrollment.APPROVED)
               .select_related("course", "course__category", "course__instructor")
               .order_by("-created_at"))
    return render(request, "student/courses/my_courses.html", {"enrollments": enrolls})

@login_required
def course_learn(request, course_id):
    course = get_object_or_404(Course, pk=course_id, is_active=True)
    e = Enrollment.objects.filter(user=request.user, course=course, status=Enrollment.APPROVED).first()
    if not e:
        messages.error(request, "You must be enrolled (approved) to access this course.")
        return redirect("courses:catalog")

    lessons = course.lessons.all().prefetch_related("materials").order_by("order", "id")
    quizzes = course.quizzes.all().order_by("id")

    return render(request, "student/courses/learn.html", {
        "course": course,
        "lessons": lessons,
        "quizzes": quizzes,
    })
