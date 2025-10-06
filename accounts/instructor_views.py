from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model

User = get_user_model()

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email", "qualifications", "profile_photo"]

@login_required
def my_profile(request):
    u = request.user
    form = ProfileForm(request.POST or None, request.FILES or None, instance=u)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated.")
        return redirect("instructor_profile")
    return render(request, "instructor/my_profile.html", {"form": form})
