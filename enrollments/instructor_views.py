# enrollments/instructor_views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model

from .models import Enrollment
from courses.models import Course

User = get_user_model()


def _is_instructor(user) -> bool:
    """
    Use your project’s rule: role='instructor' AND approved.
    (If you prefer user.is_instructor(), swap this to: return user.is_instructor())
    """
    return getattr(user, "role", "") == "instructor" and getattr(user, "is_instructor_approved", False)


# ---------- Roster for a course (and quick add by email) ----------
@login_required
def enrolled_students(request, course_id):
    if not _is_instructor(request.user):
        messages.error(request, "Instructor access only.")
        return redirect("/")

    course = get_object_or_404(Course, pk=course_id, instructor=request.user)

    items = (
        Enrollment.objects
        .filter(course=course)
        .select_related("user", "course")
        .order_by("-created_at")
    )

    # Add/Register a student by email (POST)
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        if not email:
            messages.error(request, "Enter a student email.")
            return redirect("enrollments:enrolled_students", course_id=course.id)

        try:
            student = User.objects.get(email=email, role="student")
        except User.DoesNotExist:
            messages.error(request, "No student with that email.")
            return redirect("enrollments:enrolled_students", course_id=course.id)

        obj, created = Enrollment.objects.get_or_create(user=student, course=course)
        if created:
            messages.success(request, f"{student.get_full_name() or student.username} added.")
        else:
            messages.info(request, "Student is already enrolled (status: %s)." % obj.status)
        return redirect("enrollments:enrolled_students", course_id=course.id)

    return render(request, "instructor/enrolled.html", {
        "course": course,
        "items": items,
    })


# Quick approve from the course roster
@login_required
def approve_enrollment(request, pk):
    if not _is_instructor(request.user):
        messages.error(request, "Instructor access only.")
        return redirect("/")

    e = get_object_or_404(Enrollment, pk=pk, course__instructor=request.user)
    e.status = Enrollment.APPROVED
    e.save(update_fields=["status"])
    messages.success(request, "Enrollment approved.")
    return redirect("enrollments:enrolled_students", course_id=e.course.id)


# ---------- Pending queue across all my courses ----------
@login_required
def pending_for_my_courses(request):
    if not _is_instructor(request.user):
        messages.error(request, "Instructor access only.")
        return redirect("/")

    enrolls = (
        Enrollment.objects
        .filter(course__instructor=request.user, status=Enrollment.PENDING)
        .select_related("user", "course")
        .order_by("-created_at")
    )
    return render(request, "instructor/enrollments_pending.html", {"enrollments": enrolls})


@login_required
def approve(request, enrollment_id):
    if not _is_instructor(request.user):
        messages.error(request, "Instructor access only.")
        return redirect("/")
    e = get_object_or_404(Enrollment, id=enrollment_id, course__instructor=request.user)
    e.status = Enrollment.APPROVED
    e.save(update_fields=["status"])
    messages.success(request, f"Approved {e.user.username} for {e.course.title}.")
    return redirect("enrollments:pending")


@login_required
def reject(request, enrollment_id):
    if not _is_instructor(request.user):
        messages.error(request, "Instructor access only.")
        return redirect("/")
    e = get_object_or_404(Enrollment, id=enrollment_id, course__instructor=request.user)
    e.status = Enrollment.REJECTED
    e.save(update_fields=["status"])
    messages.info(request, f"Rejected {e.user.username} for {e.course.title}.")
    return redirect("enrollments:pending")