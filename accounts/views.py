from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

def ping(request):
    return HttpResponse("accounts ok")

def signup_choice(request):
    return render(request, "registration/signup_choice.html")

@login_required
def redirect_after_login(request):
    u = request.user

    # Admin / Superuser
    if u.is_superuser or u.is_staff:
        return redirect("adminpanel:ap_dashboard")   # namespaced admin URL

    # Instructor
    if u.role == "instructor":
        if not getattr(u, "is_instructor_approved", False):
            return redirect("accounts:instructor_pending")
        return redirect("courses:instructor_dashboard")  # ✅ underscore

    # Student
    if u.role == "student":
        return redirect("accounts:student_dashboard")

    # Fallback
    return redirect("/")


@login_required
def instructor_pending(request):
    u = request.user
    # If this user is not an unapproved instructor, don't show this page.
    if not (getattr(u, "role", "") == "instructor" and not getattr(u, "is_instructor_approved", False)):
        return redirect("/")  # or wherever you prefer
    return render(request, "accounts/instructor_pending.html")
