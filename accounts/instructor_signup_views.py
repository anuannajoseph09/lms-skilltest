from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .forms import InstructorSignUpForm


def instructor_signup(request):
    """Public signup page for instructors. Approval required by admin."""
    if request.user.is_authenticated:
        # already logged in -> send them where they belong
        return redirect(reverse("accounts:redirect_after_login"))  # ✅ namespace fixed

    if request.method == "POST":
        form = InstructorSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            instructor = form.save(commit=False)
            instructor.role = "instructor"
            instructor.is_instructor_approved = False  # 🚦 Require admin approval
            instructor.save()

            messages.success(
                request,
                "✅ Your instructor account has been created successfully! "
                "An admin must approve it before you can access your dashboard."
            )
            return redirect(reverse("accounts:login"))  # ✅ explicit redirect to login page
    else:
        form = InstructorSignUpForm()

    return render(request, "registration/instructor_signup.html", {"form": form})


@login_required
def instructor_pending(request):
    """Shown to instructors who are not yet approved."""
    # If instructor is already approved → redirect to dashboard
    if getattr(request.user, "role", "") == "instructor" and getattr(request.user, "is_instructor_approved", False):
        return redirect(reverse("courses:instructor-dashboard"))  # ✅ use reverse here too

    return render(request, "registration/instructor_pending.html")

