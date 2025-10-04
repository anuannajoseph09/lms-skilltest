from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django import forms
from django.http import HttpResponse
from django.apps import apps   # <-- new



User = get_user_model()

# ---------- health check ----------
@staff_member_required
def ping(request):
    return HttpResponse("adminpanel ok")

# ---------- User Management ----------

@staff_member_required
def user_list(request):
    q = request.GET.get("q", "")
    role = request.GET.get("role", "")
    users = User.objects.all().order_by("-date_joined")
    if role in ("student", "instructor"):
        users = users.filter(role=role)
    if q:
        users = users.filter(username__icontains=q) | users.filter(email__icontains=q)
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

@staff_member_required
def approve_instructor(request, pk):
    u = get_object_or_404(User, pk=pk)
    u.role = "instructor"
    u.save()
    messages.success(request, f"{u.username} is now an Instructor.")
    return redirect("ap_user_list")


# ---------- Course Oversight ----------
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


