from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from .models import LiveSession
from courses.models import Course

class LiveForm(forms.ModelForm):
    class Meta:
        model = LiveSession
        fields = ["title","meet_link","start_time","end_time"]
        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type":"datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"type":"datetime-local"}),
        }

@login_required
def live_list(request, course_id):
    c = get_object_or_404(Course, pk=course_id, instructor=request.user)
    items = c.live_sessions.order_by("-start_time")
    return render(request, "instructor/live_list.html", {"course": c, "items": items})

@login_required
def live_create(request, course_id):
    c = get_object_or_404(Course, pk=course_id, instructor=request.user)
    form = LiveForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.course = c
        obj.save()
        return redirect("learning:live_list", course_id=c.id)   # <-- namespaced
    return render(request, "instructor/live_form.html", {"form": form, "course": c})

@login_required
def live_edit(request, pk):
    s = get_object_or_404(LiveSession, pk=pk, course__instructor=request.user)
    form = LiveForm(request.POST or None, instance=s)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("learning:live_list", course_id=s.course.id)  # <-- namespaced
    return render(request, "instructor/live_form.html", {"form": form, "course": s.course})
