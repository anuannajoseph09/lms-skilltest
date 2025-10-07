from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from .models import Thread, Reply
from courses.models import Course

class ReplyForm(forms.ModelForm):
    class Meta: model = Reply; fields = ["body"]

@login_required
def thread_list(request, course_id):
    c = get_object_or_404(Course, pk=course_id, instructor=request.user)
    threads = Thread.objects.filter(course=c).select_related("author").order_by("-id")
    return render(request, "instructor/forum_threads.html", {"course": c, "threads": threads})

@login_required
def reply_create(request, thread_id):
    t = get_object_or_404(Thread, pk=thread_id, course__instructor=request.user)
    form = ReplyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        r = form.save(commit=False); r.thread=t; r.author=request.user; r.save()
        return redirect("forum_threads", course_id=t.course.id)
    return render(request, "instructor/reply_form.html", {"form": form, "thread": t})
