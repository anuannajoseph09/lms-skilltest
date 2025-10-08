from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django import forms
from .models import Lesson, Material
from courses.models import Course

class LessonForm(forms.ModelForm):
    class Meta: model = Lesson; fields = ["title","description","order"]

class MaterialForm(forms.ModelForm):
    class Meta: model = Material; fields = ["type","file"]

@login_required
def manage_lessons(request, course_id):
    course = get_object_or_404(Course, pk=course_id, instructor=request.user)
    lessons = course.lessons.order_by("order","id")
    return render(request, "instructor/lessons.html", {"course":course, "lessons":lessons})

@login_required
def lesson_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id, instructor=request.user)
    form = LessonForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False); obj.course=course; obj.save()
        messages.success(request,"Lesson added.")
        return redirect("learning:manage_lessons", course_id=course.id)
    return render(request,"instructor/lesson_form.html",{"form":form,"course":course})

@login_required
def lesson_edit(request, pk):
    l = get_object_or_404(Lesson, pk=pk, course__instructor=request.user)
    form = LessonForm(request.POST or None, instance=l)
    if request.method == "POST" and form.is_valid():
        form.save(); messages.success(request,"Lesson updated.")
        return redirect("learning:manage_lessons", course_id=l.course.id)
    return render(request,"instructor/lesson_form.html",{"form":form,"course":l.course})

@login_required
def lesson_delete(request, pk):
    l = get_object_or_404(Lesson, pk=pk, course__instructor=request.user)
    if request.method=="POST":
        cid=l.course.id; l.delete(); messages.success(request,"Lesson deleted.")
        return redirect("learning:manage_lessons", course_id=cid)
    return render(request,"instructor/confirm_delete.html",{"what":l.title})

@login_required
def material_create(request, lesson_id):
    l = get_object_or_404(Lesson, pk=lesson_id, course__instructor=request.user)
    form = MaterialForm(request.POST or None, request.FILES or None)
    if request.method=="POST" and form.is_valid():
        m = form.save(commit=False); m.lesson=l; m.save()
        messages.success(request,"Material uploaded.")
        return redirect("learning:manage_lessons", course_id=l.course.id)
    return render(request,"instructor/material_form.html",{"form":form,"lesson":l})

@login_required
def material_delete(request, pk):
    m = get_object_or_404(Material, pk=pk, lesson__course__instructor=request.user)
    if request.method=="POST":
        cid=m.lesson.course.id; m.delete(); messages.success(request,"Material deleted.")
        return redirect("learning:manage_lessons", course_id=cid)
    return render(request,"instructor/confirm_delete.html",{"what":str(m)})
