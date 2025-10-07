# accounts/views.py
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse  # ✅ use named URLs

def ping(request):
    return HttpResponse("accounts ok")

@login_required
def redirect_after_login(request):
    """Redirect users to their respective dashboards based on role."""
    user = request.user
    if user.is_superuser or user.is_staff:
        return redirect(reverse("ap_dashboard"))
    elif user.role == "instructor":
        return redirect("courses:instructor-dashboard")  # keep if this URL exists
    elif user.role == "student":
        return redirect(reverse("accounts:student_dashboard"))  # ✅ name, not hardcoded
    else:
        return redirect("/")  # fallback
