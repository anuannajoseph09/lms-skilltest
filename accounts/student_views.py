from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .forms import StudentSignUpForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib.auth import update_session_auth_hash



def student_signup(request):
    if request.user.is_authenticated:
        return redirect("redirect_after_login")

    form = StudentSignUpForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Welcome! Your student account has been created successfully.")
        return redirect("redirect_after_login")
    return render(request, "registration/signup.html", {"form": form})


@login_required
def student_dashboard(request):
    return render(request, "student/dashboard/index.html")


@login_required
def student_profile_edit(request):
    """Edit student's own profile (inline handling, no ModelForm)."""
    user = request.user

    if request.method == "POST":
        # basic fields
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name  = request.POST.get("last_name", user.last_name)
        user.email      = request.POST.get("email", user.email)

        # handle photo remove
        if request.POST.get("remove_photo") == "on" and user.profile_photo:
            user.profile_photo.delete(save=False)
            user.profile_photo = None

        # handle new photo upload
        if "profile_photo" in request.FILES:
            user.profile_photo = request.FILES["profile_photo"]

        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("student_profile_edit")

    return render(request, "student/dashboard/profile_edit.html", {"user_obj": user})


# ---------- OPTIONAL: Change password (no custom form) ----------
class _StudentPasswordChangeView(PasswordChangeView):
    template_name = "student/dashboard/change_password.html"
    success_url = reverse_lazy("student_profile_edit")

    def form_valid(self, form):
        response = super().form_valid(form)
        # keep the session authenticated after password change
        update_session_auth_hash(self.request, form.user)
        messages.success(self.request, "Password changed successfully.")
        return response

@login_required
def student_change_password(request):
    """Thin wrapper to call Django's PasswordChangeView."""
    view = _StudentPasswordChangeView.as_view()
    return view(request)



