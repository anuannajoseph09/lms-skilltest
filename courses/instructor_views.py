from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.roles import instructor_required
from .models import Course, Category
from .forms import CourseForm, CategoryForm

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
