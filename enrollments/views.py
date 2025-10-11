from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from courses.models import Course
from .models import Enrollment

User = get_user_model()

@login_required
@transaction.atomic
def instructor_manage_enrollments(request, course_id):
    # Only the owner instructor can manage enrollments for this course
    course = get_object_or_404(Course, pk=course_id, instructor=request.user)

    # POST: Add a student to the course
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        if not user_id:
            messages.error(request, "Please choose a student to add.")
            return redirect("enrollments:manage_course_enrollments", course_id=course.id)

        user = get_object_or_404(User, pk=user_id)

        enroll, created = Enrollment.objects.get_or_create(
            user=user,
            course=course,
            defaults={"status": Enrollment.APPROVED},  # or Enrollment.PENDING
        )
        if created:
            messages.success(request, f"{user.get_username()} added to {course.title}.")
        else:
            messages.info(request, f"{user.get_username()} is already enrolled (status: {enroll.status}).")

        return redirect("enrollments:manage_course_enrollments", course_id=course.id)

    # ------- GET: List all students with search + pagination, mark who’s enrolled
    q = (request.GET.get("q") or "").strip()

    # ✅ Use your role field. Show only real students, exclude superusers (and staff if you want).
    students_qs = User.objects.filter(role='student').exclude(is_superuser=True).order_by("username")
    # Optionally: .exclude(is_staff=True)

    if q:
        students_qs = students_qs.filter(
            Q(username__icontains=q) |
            Q(email__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q)
        )

    # Set of enrolled user IDs for THIS course (used to show “Enrolled ✓” vs “Add” button)
    enrolled_ids = set(
        Enrollment.objects.filter(course=course).values_list("user_id", flat=True)
    )

    paginator = Paginator(students_qs, 15)  # 15 per page
    page_obj = paginator.get_page(request.GET.get("page"))

    # Current enrollments list (right-side table)
    enrollments = (
        Enrollment.objects
        .filter(course=course)
        .select_related("user")
        .order_by("user__username")
    )

    return render(
        request,
        "instructor/enrollments/manage.html",
        {
            "course": course,
            "page_obj": page_obj,      # ← use this in template to loop all students
            "q": q,
            "enrolled_ids": enrolled_ids,
            "enrollments": enrollments # ← defined now
        },
    )
