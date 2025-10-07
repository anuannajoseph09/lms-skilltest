from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.roles import instructor_required
from .models import Course, Category
from .forms import CourseForm, CategoryForm
from django.db.models import Count, Q, Max


# optional imports — only if these apps exist (they do in your milestones)
try:
    from enrollments.models import Enrollment
except Exception:
    Enrollment = None
try:
    from quizzes.models import Submission
except Exception:
    Submission = None
try:
    from learning.models import LiveSession
except Exception:
    LiveSession = None
try:
    from forum.models import Thread
except Exception:
    Thread = None


@login_required
def dashboard(request):
    if not getattr(request.user, "is_instructor", lambda: False)():
        return render(request, "instructor/not_allowed.html", status=403)

    # All courses owned by this instructor with useful counters
    courses = (
        Course.objects.filter(instructor=request.user)
        .annotate(
            lessons_count=Count("lessons", distinct=True),
            quizzes_count=Count("quizzes", distinct=True),
            students_approved=Count("enrollments", filter=Q(enrollments__status="approved"), distinct=True),
            students_pending=Count("enrollments", filter=Q(enrollments__status="pending"), distinct=True),
        )
        .order_by("-id")
    )

    # Top-level KPIs
    kpi = {
        "total_courses": courses.count(),
        "total_lessons": sum(c.lessons_count for c in courses),
        "total_quizzes": sum(c.quizzes_count for c in courses),
        "total_students": sum(c.students_approved for c in courses),
        "pending_approvals": sum(c.students_pending for c in courses),
    }

    # Recent activity widgets (each limited to 5)
    recent_enrolls = []
    recent_threads = []
    upcoming_live = []

    if Enrollment:
        recent_enrolls = (
            Enrollment.objects
            .filter(course__instructor=request.user)
            .select_related("user", "course")
            .order_by("-created_at")[:5]
        )

    if Thread:
        recent_threads = (
            Thread.objects
            .filter(course__instructor=request.user)
            .select_related("author", "course")
            .order_by("-created_at")[:5]
        )

    if LiveSession:
        upcoming_live = (
            LiveSession.objects
            .filter(course__instructor=request.user)
            .order_by("start_time")[:5]
        )

    # Latest quiz result per course (optional)
    latest_results = []
    if Submission:
        latest_results = (
        Submission.objects
        .filter(quiz__course__instructor=request.user)
        .select_related("user", "quiz", "quiz__course")
        .order_by("-submitted_at")[:5]
    )
    

    return render(request, "instructor/dashboard.html", {
        "kpi": kpi,
        "courses": courses,
        "recent_enrolls": recent_enrolls,
        "recent_threads": recent_threads,
        "upcoming_live": upcoming_live,
        "latest_results": latest_results,
    })

@login_required
@instructor_required
def my_courses(request):
    qs = Course.objects.filter(instructor=request.user).order_by("-id")
    return render(request, "instructor/my_courses.html", {"courses": qs})

@login_required
@instructor_required
def course_create(request):
    form = CourseForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.instructor = request.user
        obj.save()
        messages.success(request, "Course created.")
        return redirect("my_courses")
    return render(request, "instructor/course_form.html", {"form": form, "title": "New Course"})

@login_required
@instructor_required
def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk, instructor=request.user)
    form = CourseForm(request.POST or None, request.FILES or None, instance=course)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Course updated.")
        return redirect("my_courses")
    return render(request, "instructor/course_form.html", {"form": form, "title": f"Edit: {course.title}"})

@login_required
@instructor_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk, instructor=request.user)
    if request.method == "POST":
        course.delete()
        messages.success(request, "Course deleted.")
        return redirect("my_courses")
    return render(request, "instructor/confirm_delete.html", {"what": course.title})

# ---- Categories (simple) ----
@login_required
@instructor_required
def category_list(request):
    return render(request, "instructor/categories.html",
                  {"items": Category.objects.order_by("name")})

@login_required
@instructor_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save(); messages.success(request, "Category added.")
        return redirect("category_list")
    return render(request, "instructor/category_form.html", {"form": form})
