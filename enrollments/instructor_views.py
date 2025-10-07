# enrollments/instructor_views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import Enrollment
from courses.models import Course

User = get_user_model()

def _instructor_only(request):
    return request.user.is_authenticated and getattr(request.user, "is_instructor", lambda: False)()

@login_required
def enrolled_students(request, course_id):
    if not _instructor_only(request):
        messages.error(request, "Instructor access only.")
        return redirect("/")

    course = get_object_or_404(Course, pk=course_id, instructor=request.user)

    # NOTE: model uses 'user', not 'student'
    items = (Enrollment.objects
             .filter(course=course)
             .select_related("user", "course")
             .order_by("-created_at"))

    # Add/Register a student by email (POST)
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        if not email:
            messages.error(request, "Enter a student email.")
            return redirect("enrolled_students", course_id=course.id)

        try:
            student = User.objects.get(email=email, role="student")
        except User.DoesNotExist:
            messages.error(request, "No student with that email.")
            return redirect("enrolled_students", course_id=course.id)

        obj, created = Enrollment.objects.get_or_create(user=student, course=course)
        if created:
            messages.success(request, f"{student.get_full_name() or student.username} added.")
        else:
            messages.info(request, "Student is already enrolled.")
        return redirect("enrolled_students", course_id=course.id)

    return render(request, "instructor/enrolled.html", {"course": course, "items": items})

@login_required
def approve_enrollment(request, pk):
    if not _instructor_only(request):
        messages.error(request, "Instructor access only.")
        return redirect("/")

    e = get_object_or_404(Enrollment, pk=pk, course__instructor=request.user)
    e.status = Enrollment.APPROVED
    e.save(update_fields=["status"])
    messages.success(request, "Enrollment approved.")
    return redirect("enrolled_students", course_id=e.course.id)
