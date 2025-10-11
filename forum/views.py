from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count
from .models import Thread, Reply
from .permissions import is_student, student_is_enrolled
from courses.models import Course

@login_required
def thread_list(request, course_id):
    course = get_object_or_404(Course, pk=course_id, is_active=True)
    # Students must be enrolled/approved to see the forum
    if not is_student(request.user) or not student_is_enrolled(request.user, course):
        messages.error(request, "You must be enrolled in this course to view its forum.")
        return redirect("courses:catalog")

    threads = (course.threads
               .select_related('author')
               .annotate(replies_count=Count("replies"))
               .order_by("-created_at"))
    return render(request, 'forum/thread_list.html', {'course': course, 'threads': threads})

@login_required
def thread_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id, is_active=True)
    if not is_student(request.user) or not student_is_enrolled(request.user, course):
        messages.error(request, "You must be enrolled in this course to create a thread.")
        return redirect("forum:thread_list", course_id=course.id)

    if request.method == 'POST':
        title = (request.POST.get('title') or '').strip()
        body  = (request.POST.get('body') or '').strip()
        if not title or not body:
            messages.error(request, 'Please provide a title and content.')
        else:
            Thread.objects.create(course=course, author=request.user, title=title, body=body)
            messages.success(request, 'Thread created.')
            return redirect('forum:thread_list', course_id=course.id)

    return render(request, 'forum/thread_create.html', {'course': course})

@login_required
def thread_detail(request, thread_id):
    thread = (Thread.objects
              .select_related("course", "author")
              .prefetch_related("replies__author")
              .get(pk=thread_id))
    course = thread.course
    # Students: must be enrolled to view
    if not is_student(request.user) or not student_is_enrolled(request.user, course):
        messages.error(request, "You must be enrolled in this course to view its forum.")
        return redirect("courses:catalog")

    replies = thread.replies.all()
    return render(request, 'forum/thread_detail_student.html', {'thread': thread, 'replies': replies})

@login_required
def reply_create(request, thread_id):
    thread = get_object_or_404(Thread, pk=thread_id)
    course = thread.course
    if not is_student(request.user) or not student_is_enrolled(request.user, course):
        messages.error(request, "You must be enrolled to reply in this forum.")
        return redirect("forum:thread_detail", thread_id=thread.id)

    if request.method == 'POST':
        body = (request.POST.get('body') or '').strip()
        if not body:
            messages.error(request, 'Reply cannot be empty.')
        else:
            Reply.objects.create(thread=thread, author=request.user, body=body)
            messages.success(request, 'Reply posted.')
    return redirect('forum:thread_detail', thread_id=thread.id)

