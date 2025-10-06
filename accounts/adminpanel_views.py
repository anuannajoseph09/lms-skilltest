from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django import forms
from django.http import HttpResponse
from django.apps import apps
from django.db.models import Q

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

@staff_member_required
def dashboard(request):
    User = apps.get_model("accounts", "User")
    Course = apps.get_model("courses", "Course")

    Enrollment = apps.get_model("enrollments", "Enrollment") if apps.is_installed("enrollments") else None
    Quiz = apps.get_model("quizzes", "Quiz") if apps.is_installed("quizzes") else None
    Submission = apps.get_model("quizzes", "Submission") if apps.is_installed("quizzes") else None

    stats = {
        "total_users": User.objects.count(),
        "total_students": User.objects.filter(role="student").count(),
        "total_instructors": User.objects.filter(role="instructor").count(),
        "total_courses": Course.objects.count(),
        "total_quizzes": Quiz.objects.count() if Quiz else 0,
    }

    # Determine the relation name from Enrollment to Course (defaults to "enrollment_set")
    popular_courses = []
    if Enrollment:
        course_field = Enrollment._meta.get_field("course")
        rel_name = course_field.remote_field.related_name or "enrollment_set"

        # annotate using the relation name we discovered
        popular_courses = (
            Course.objects.annotate(enrolls=Count(rel_name))
            .order_by("-enrolls", "-id")[:5]
        )

    top_students = []
    if Submission:
        top_students = (
            Submission.objects.values("user__username")
            .annotate(avg_score=Avg("score"), attempts=Count("id"))
            .order_by("-avg_score")[:5]
        )

    return render(
        request,
        "adminpanel/dashboard.html",
        {"stats": stats, "popular_courses": popular_courses, "top_students": top_students},
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
        return redirect("ap_user_list")
    return render(request, "adminpanel/user_form.html", {"form": form, "title": "Create Student"})


@staff_member_required
def create_instructor(request):
    form = AdminCreateUserForm(request.POST or None, initial={"role": "instructor"})
    if request.method == "POST" and form.is_valid():
        u = form.save(commit=False)
        u.password = make_password(form.cleaned_data["password"])
        u.save()
        messages.success(request, "Instructor created.")
        return redirect("ap_user_list")
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
        return redirect("ap_user_list")
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
        return redirect("ap_user_list")
    return render(request, "adminpanel/user_form.html", {"form": form, "title": f"Reset password for {u.username}"})


# ✅ APPROVE / REJECT INSTRUCTOR
@staff_member_required
def approve_instructor(request, pk):
    u = get_object_or_404(User, pk=pk)
    u.role = "instructor"
    u.is_instructor_approved = True
    u.save()
    messages.success(request, f"{u.username} approved as Instructor.")
    return redirect("ap_user_list")


@staff_member_required
def reject_instructor(request, pk):
    u = get_object_or_404(User, pk=pk)
    if u.role == "instructor":
        u.is_instructor_approved = False
        u.save()
    messages.info(request, f"{u.username} instructor status rejected.")
    return redirect("ap_user_list")

# -------------------------------------------------
# ✅ COURSE OVERSIGHT
# -------------------------------------------------
@staff_member_required
def course_list(request):
    Course = apps.get_model("courses", "Course")
    q = request.GET.get("q", "")
    courses = Course.objects.select_related("instructor", "category").order_by("-id")
    if q:
        courses = courses.filter(title__icontains=q)
    return render(request, "adminpanel/course_list.html", {"courses": courses, "q": q})


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
        return redirect("ap_category_list")
    return render(request, "adminpanel/user_form.html", {"form": form, "title": "Create Category"})


@staff_member_required
def category_delete(request, pk):
    Category = apps.get_model("courses", "Category")
    c = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        c.delete()
        messages.success(request, "Category deleted.")
        return redirect("ap_category_list")
    return render(request, "adminpanel/confirm_delete.html", {"what": f"category {c.name}"})
