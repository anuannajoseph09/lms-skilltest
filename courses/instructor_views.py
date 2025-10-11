from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.roles import instructor_required
from .models import Course, Category
from .forms import CourseForm, CategoryForm
from django.db.models import Count, Q, Max, Avg
from forum.models import Thread, Reply
from django.views.decorators.cache import never_cache
from learning.models import Lesson, LessonProgress


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

@never_cache
@login_required
def dashboard(request):
    

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
          .select_related("course")
          .annotate(replies_count=Count("replies"))
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
        return redirect("courses:instructor_my_courses")
    return render(request, "instructor/course_form.html", {"form": form, "title": "New Course"})

@login_required
@instructor_required
def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk, instructor=request.user)
    form = CourseForm(request.POST or None, request.FILES or None, instance=course)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Course updated.")
        return redirect("courses:instructor_my_courses")
    return render(request, "instructor/course_form.html", {"form": form, "title": f"Edit: {course.title}"})

@login_required
@instructor_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk, instructor=request.user)
    if request.method == "POST":
        course.delete()
        messages.success(request, "Course deleted.")
        return redirect("courses:instructor_my_courses")
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
        return redirect("courses:category_list")
    return render(request, "instructor/category_form.html", {"form": form})

@login_required
def course_students(request, course_id):
    """
    For an instructor's course: show all enrolled students with
    lesson-completion % (via LessonProgress) and quiz summary.
    """
    course = get_object_or_404(Course, pk=course_id, instructor=request.user)

    # Total lessons in this course (avoid divide-by-zero)
    lessons_total = course.lessons.count()

    # Enrolled & approved students for this course
    enrolls = (
        Enrollment.objects
        .filter(course=course, status=Enrollment.APPROVED)
        .select_related("user")
        .order_by("user__username")
    )

    # Completed lesson counts per user (uses your exact fields)
    done_map = {
        row["user_id"]: row["c"]
        for row in (
            LessonProgress.objects
            .filter(lesson__course=course, is_completed=True)
            .values("user_id")
            .annotate(c=Count("id"))
        )
    }

    # Quiz rollup per user (attempts, avg, last submission time)
    quiz_map = {
        row["user_id"]: row
        for row in (
            Submission.objects
            .filter(quiz__course=course)
            .values("user_id")
            .annotate(
                attempts=Count("id"),
                avg_score=Avg("score"),
                last_time=Max("submitted_at"),
            )
        )
    }

    # Build rows for template
    rows = []
    for e in enrolls:
        uid = e.user_id
        lessons_done = done_map.get(uid, 0)
        pct = round((lessons_done / lessons_total) * 100) if lessons_total else 0
        qm = quiz_map.get(uid)
        rows.append({
            "user": e.user,
            "lessons_done": lessons_done,
            "lessons_total": lessons_total,
            "progress_pct": pct,
            "quiz_attempts": qm["attempts"] if qm else 0,
            "avg_score": round(qm["avg_score"], 1) if (qm and qm["avg_score"] is not None) else None,
            "last_time": qm["last_time"] if qm else None,
        })

    return render(request, "instructor/progress/course_students.html", {
        "course": course,
        "rows": rows,
    })


@login_required
def student_progress_detail(request, course_id, user_id):
    """
    For a single student in an instructor's course:
    show which lessons are completed and their quiz submissions.
    """
    course = get_object_or_404(Course, pk=course_id, instructor=request.user)

    lessons = (
        Lesson.objects
        .filter(course=course)
        .order_by("order", "id")
        .prefetch_related("materials")
    )

    # Set of completed lesson IDs for this student
    done_ids = set(
        LessonProgress.objects
        .filter(lesson__course=course, user_id=user_id, is_completed=True)
        .values_list("lesson_id", flat=True)
    )

    # Student’s quiz submissions for this course
    subs = (
        Submission.objects
        .filter(quiz__course=course, user_id=user_id)
        .select_related("quiz")
        .order_by("-submitted_at")
    )

    # Progress %
    total = lessons.count()
    pct = round((len(done_ids) / total) * 100) if total else 0

    return render(request, "instructor/progress/student_detail.html", {
        "course": course,
        "student_id": user_id,
        "lessons": lessons,
        "done_ids": done_ids,
        "submissions": subs,
        "progress_pct": pct,
    })


