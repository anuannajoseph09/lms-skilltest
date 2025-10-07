from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class StudentSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    profile_photo = forms.ImageField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "email", "profile_photo", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "student"              # ✅ Assign the role
        user.email = self.cleaned_data.get("email")
        if commit:
            user.save()
        return user

