from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import InstructorSignUpForm
User = get_user_model()

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email", "qualifications", "profile_photo"]


def instructor_signup(request):
    if request.method == "POST":
        form = InstructorSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Thanks! Your instructor account request was submitted. "
                "An admin will review it. You can log in, but you’ll see a pending page until approved."
            )
            return redirect("accounts:login")
    else:
        form = InstructorSignUpForm()
    return render(request, "registration/instructor_signup.html", {"form": form})

@login_required
def instructor_pending(request):
    # If they got approved while browsing, bounce to instructor area
    if getattr(request.user, "is_instructor_approved", False):
        return redirect("courses:instructor_my_courses")
    return render(request, "registration/instructor_pending.html")


@login_required
def my_profile(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated.")
        return redirect("courses:instructor_dashboard")
    return render(request, "instructor/my_profile.html", {"form": form})