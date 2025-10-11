from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Count
from .models import Thread, Reply
from .permissions import is_instructor
from courses.models import Course

@login_required
def thread_list(request, course_id):
    if not is_instructor(request.user):
        messages.error(request, "Not allowed.")
        return redirect("courses:instructor_dashboard")

    course = get_object_or_404(Course, pk=course_id, instructor=request.user)
    threads = (Thread.objects.filter(course=course)
               .select_related("author")
               .annotate(replies_count=Count("replies"))
               .order_by("-created_at"))
    return render(request, "forum/thread_list_instructor.html", {"course": course, "threads": threads})

@login_required
def thread_detail(request, thread_id):
    if not is_instructor(request.user):
        messages.error(request, "Not allowed.")
        return redirect("courses:instructor_dashboard")

    thread = get_object_or_404(Thread.objects.select_related("course", "author"), pk=thread_id)
    if thread.course.instructor_id != request.user.id:
        messages.error(request, "Not allowed.")
        return redirect("forum:instructor_thread_list", course_id=thread.course_id)

    replies = thread.replies.select_related("author").order_by("created_at")
    return render(request, "forum/thread_detail_instructor.html", {"thread": thread, "replies": replies})

@login_required
def reply_to_thread(request, thread_id):
    if not is_instructor(request.user):
        messages.error(request, "Not allowed.")
        return redirect("courses:instructor_dashboard")

    thread = get_object_or_404(Thread, pk=thread_id)
    if thread.course.instructor_id != request.user.id:
        messages.error(request, "Not allowed.")
        return redirect("forum:instructor_thread_detail", thread_id=thread.id)

    if request.method == "POST":
        body = (request.POST.get("body") or "").strip()
        if not body:
            messages.error(request, "Reply cannot be empty.")
        else:
            Reply.objects.create(thread=thread, author=request.user, body=body)
            messages.success(request, "Reply posted.")
        return redirect("forum:instructor_thread_detail", thread_id=thread.id)

    # Optional simple page for GET
    return render(request, "forum/reply_form.html", {"thread": thread})

@login_required
def delete_thread(request, thread_id):
    if not is_instructor(request.user):
        messages.error(request, "Not allowed.")
        return redirect("courses:instructor_dashboard")

    thread = get_object_or_404(Thread, pk=thread_id)
    if thread.course.instructor_id != request.user.id:
        messages.error(request, "Not allowed.")
        return redirect('forum:instructor_thread_detail', thread_id=thread.id)

    course_id = thread.course_id
    if request.method == "POST":
        thread.delete()
        messages.success(request, "Thread deleted.")
    return redirect('forum:instructor_thread_list', course_id=course_id)

@login_required
def delete_reply(request, reply_id):
    if not is_instructor(request.user):
        messages.error(request, "Not allowed.")
        return redirect("courses:instructor_dashboard")

    reply = get_object_or_404(Reply, pk=reply_id)
    if reply.thread.course.instructor_id != request.user.id:
        messages.error(request, "Not allowed.")
        return redirect('forum:instructor_thread_detail', thread_id=reply.thread_id)

    if request.method == "POST":
        reply.delete()
        messages.success(request, "Reply deleted.")
    return redirect('forum:instructor_thread_detail', thread_id=reply.thread_id)


