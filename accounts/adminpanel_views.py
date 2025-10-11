from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django import forms
from django.http import HttpResponse
from django.apps import apps
from django.db.models import Q
from django.views.decorators.cache import never_cache
from django.utils import timezone
from datetime import timedelta


User = get_user_model()

# -------------------------------------------------
# ✅ HEALTH CHECK
# -------------------------------------------------
@staff_member_required
def ping(request):
    return HttpResponse("adminpanel ok")

# -------------------------------------------------
# ✅ USER MANAGEMENT
# -------------------------------------------------

# accounts/adminpanel_views.py
from django.db.models import Count, Avg


@never_cache
@staff_member_required
def dashboard(request):
    User = apps.get_model("accounts", "User")
    Course = apps.get_model("courses", "Course")
    Enrollment = apps.get_model("enrollments", "Enrollment") if apps.is_installed("enrollments") else None
    Quiz = apps.get_model("quizzes", "Quiz") if apps.is_installed("quizzes") else None
    Submission = apps.get_model("quizzes", "Submission") if apps.is_installed("quizzes") else None

    # --------- Totals
    stats = {
        "total_users": User.objects.count(),
        "total_students": User.objects.filter(role="student").count(),
        "total_instructors": User.objects.filter(role="instructor").count(),
        "total_courses": Course.objects.count(),
        "total_quizzes": Quiz.objects.count() if Quiz else 0,
    }

    # --------- New last 7 days
    now = timezone.now()
    stats["new_users_7d"] = User.objects.filter(date_joined__gte=now - timedelta(days=7)).count()
    stats["new_courses_7d"] = (
        Course.objects.filter(created_at__gte=now - timedelta(days=7)).count()
        if hasattr(Course, "created_at") else 0
    )

    # --------- Popular courses (by total enrollments)
    popular_courses = []
    if Enrollment:
        # related_name-safe annotation
        course_field = Enrollment._meta.get_field("course")
        rel_name = course_field.remote_field.related_name or "enrollment_set"
        popular_courses = (
            Course.objects.annotate(enrolls=Count(rel_name))
            .order_by("-enrolls", "-id")[:5]
        )

    # --------- Top students
    top_students = []
    if Submission:
        top_students = (
            Submission.objects.values("user__username")
            .annotate(avg_score=Avg("score"), attempts=Count("id"))
            .order_by("-avg_score")[:5]
        )
    # Fallback if quizzes app not present or no data
    if Enrollment and not top_students:
        top_students = (
            Enrollment.objects.values("user__username")
            .annotate(attempts=Count("id"))
            .order_by("-attempts")[:5]
        )

    return render(
        request,
        "adminpanel/dashboard.html",
        {
            "stats": stats,
            "popular_courses": popular_courses,
            "top_students": top_students,
        },
    )


@staff_member_required
def user_list(request):
    q = request.GET.get("q", "")
    role = request.GET.get("role", "")
    users = User.objects.all().order_by("-date_joined")

    if role in ("student", "instructor"):
        users = users.filter(role=role)
    if q:
        users = users.filter(Q(username__icontains=q) | Q(email__icontains=q))

    return render(request, "adminpanel/user_list.html", {"users": users, "q": q, "role": role})


class AdminCreateUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=6)

    class Meta:
        model = User
        fields = ["username", "email", "password", "role"]


@staff_member_required
def create_student(request):
    form = AdminCreateUserForm(request.POST or None, initial={"role": "student"})
    if request.method == "POST" and form.is_valid():
        u = form.save(commit=False)
        u.password = make_password(form.cleaned_data["password"])
        u.save()
        messages.success(request, "Student created.")
        return redirect("adminpanel:ap_user_list")
    return render(request, "adminpanel/user_form.html", {"form": form, "title": "Create Student"})


@staff_member_required
def create_instructor(request):
    form = AdminCreateUserForm(request.POST or None, initial={"role": "instructor"})
    if request.method == "POST" and form.is_valid():
        u = form.save(commit=False)
        u.password = make_password(form.cleaned_data["password"])
        u.save()
        messages.success(request, "Instructor created.")
        return redirect("adminpanel:ap_user_list")
    return render(request, "adminpanel/user_form.html", {"form": form, "title": "Create Instructor"})


class AdminEditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "role", "is_active", "is_staff"]


@staff_member_required
def user_edit(request, pk):
    u = get_object_or_404(User, pk=pk)
    form = AdminEditUserForm(request.POST or None, instance=u)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "User updated.")
        return redirect("adminpanel:ap_user_list")
    return render(request, "adminpanel/user_form.html", {"form": form, "title": f"Edit {u.username}"})


@staff_member_required
def user_delete(request, pk):
    u = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        u.delete()
        messages.success(request, "User deleted.")
        return redirect("ap_user_list")
    return render(request, "adminpanel/confirm_delete.html", {"what": f"user {u.username}"})


class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput, min_length=6)


@staff_member_required
def reset_password(request, pk):
    u = get_object_or_404(User, pk=pk)
    form = ResetPasswordForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        u.set_password(form.cleaned_data["new_password"])
        u.save()
        messages.success(request, "Password reset.")
        return redirect("adminpanel:ap_user_list")
    return render(request, "adminpanel/user_form.html", {"form": form, "title": f"Reset password for {u.username}"})


# ✅ APPROVE / REJECT INSTRUCTOR
@staff_member_required
def approve_instructor(request, pk):
    u = get_object_or_404(User, pk=pk)
    u.role = "instructor"
    u.is_instructor_approved = True
    u.save()
    messages.success(request, f"{u.username} approved as Instructor.")
    return redirect("adminpanel:ap_user_list")


@staff_member_required
def reject_instructor(request, pk):
    u = get_object_or_404(User, pk=pk)
    if u.role == "instructor":
        u.is_instructor_approved = False
        u.save()
    messages.info(request, f"{u.username} instructor status rejected.")
    return redirect("adminpanel:ap_user_list")

# -------------------------------------------------
# ✅ COURSE OVERSIGHT
# -------------------------------------------------


@staff_member_required
def course_toggle_active(request, pk):
    Course = apps.get_model("courses", "Course")
    c = get_object_or_404(Course, pk=pk)
    c.is_active = not c.is_active
    c.save()
    messages.info(request, f"'{c.title}' active = {c.is_active}")
    return redirect("ap_course_list")


# -------------------------------------------------
# ✅ CATEGORY MANAGEMENT
# -------------------------------------------------
from django.utils.text import slugify

@staff_member_required
def category_list(request):
    Category = apps.get_model("courses", "Category")
    q = request.GET.get("q", "")
    cats = Category.objects.all().order_by("name")
    if q:
        cats = cats.filter(name__icontains=q)
    return render(request, "adminpanel/category_list.html", {"categories": cats, "q": q})


class CategoryForm(forms.Form):
    name = forms.CharField(max_length=120)


@staff_member_required
def category_create(request):
    Category = apps.get_model("courses", "Category")
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        name = form.cleaned_data["name"].strip()
        Category.objects.create(name=name, slug=slugify(name))
        messages.success(request, "Category added.")
        return redirect("adminpanel:ap_category_list")
    return render(request, "adminpanel/user_form.html", {"form": form, "title": "Create Category"})


@staff_member_required
def category_delete(request, pk):
    Category = apps.get_model("courses", "Category")
    c = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        c.delete()
        messages.success(request, "Category deleted.")
        return redirect("adminpanel:ap_category_list")
    return render(request, "adminpanel/confirm_delete.html", {"what": f"category {c.name}"})



from django.core.paginator import Paginator

@staff_member_required
def course_list(request):
    Course = apps.get_model("courses", "Course")
    q = request.GET.get("q", "")
    qs = Course.objects.select_related("instructor", "category").order_by("-id")
    if q:
        qs = qs.filter(title__icontains=q)

    p = Paginator(qs, 15)
    page = p.get_page(request.GET.get("page"))
    return render(request, "adminpanel/course_list.html", {"page": page, "q": q})


@staff_member_required
def course_toggle_active(request, pk):
    Course = apps.get_model("courses", "Course")
    c = get_object_or_404(Course, pk=pk)
    c.is_active = not getattr(c, "is_active", True)
    c.save(update_fields=["is_active"])
    messages.info(request, f"Toggled active → {c.is_active} for '{c.title}'")
    return redirect("adminpanel:ap_course_list")

@staff_member_required
def course_delete(request, pk):
    Course = apps.get_model("courses", "Course")
    c = get_object_or_404(Course, pk=pk)
    if request.method == "POST":
        c.delete()
        messages.success(request, "Course deleted.")
        return redirect("adminpanel:ap_course_list")
    return render(request, "adminpanel/confirm_delete.html", {"what": f"course '{c.title}'"})

# -------- CONTENT MANAGEMENT --------
@staff_member_required
def contents_overview(request):
    Material = apps.get_model("learning", "Material") if apps.is_installed("learning") else None
    Quiz = apps.get_model("quizzes", "Quiz") if apps.is_installed("quizzes") else None
    Thread = apps.get_model("forum", "Thread") if apps.is_installed("forum") else None

    materials = Material.objects.select_related("lesson__course")[:50] if Material else []
    quizzes   = Quiz.objects.select_related("course")[:50] if Quiz else []
    # 🔧 use author instead of user
    threads   = Thread.objects.select_related("course", "author")[:50] if Thread else []

    return render(request, "adminpanel/contents_overview.html", {
        "materials": materials, "quizzes": quizzes, "threads": threads
    })


@staff_member_required
def material_delete(request, pk):
    Material = apps.get_model("learning", "Material")
    m = get_object_or_404(Material, pk=pk)
    title = f"{m.get_type_display()} — {m.lesson.title}"
    if request.method == "POST":
        m.delete()
        messages.success(request, "Material removed.")
        return redirect("adminpanel:ap_contents")
    return render(request, "adminpanel/confirm_delete.html", {"what": f"material '{title}'"})

# accounts/adminpanel_views.py
from django.views.decorators.http import require_POST

@staff_member_required
@require_POST
def quiz_toggle_active(request, pk):
    Quiz = apps.get_model("quizzes", "Quiz")
    qz = get_object_or_404(Quiz, pk=pk)

    if not hasattr(qz, "is_active"):
        messages.error(request, "Quiz model has no 'is_active' field.")
        return redirect("adminpanel:ap_contents")

    qz.is_active = not qz.is_active
    # If your Quiz has updated_at, include it; otherwise just is_active
    try:
        qz.save(update_fields=["is_active", "updated_at"])
    except Exception:
        qz.save(update_fields=["is_active"])

    messages.info(request, f"Toggled '{qz.title}' → {'Active' if qz.is_active else 'Inactive'}.")
    return redirect("adminpanel:ap_contents")


@staff_member_required
def quiz_delete(request, pk):
    Quiz = apps.get_model("quizzes", "Quiz")
    qz = get_object_or_404(Quiz, pk=pk)
    if request.method == "POST":
        qz.delete()
        messages.success(request, "Quiz deleted.")
        return redirect("adminpanel:ap_contents")
    return render(request, "adminpanel/confirm_delete.html", {"what": f"quiz '{qz.title}'"})

@staff_member_required
def thread_delete(request, pk):
    Thread = apps.get_model("forum", "Thread")
    t = get_object_or_404(Thread, pk=pk)
    if request.method == "POST":
        t.delete()
        messages.success(request, "Thread removed.")
        return redirect("adminpanel:ap_contents")
    return render(request, "adminpanel/confirm_delete.html", {"what": f"thread '{t.title}'"})
