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


class InstructorSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    profile_photo = forms.ImageField(required=False)
    qualifications = forms.CharField(widget=forms.Textarea(attrs={"rows":3}), required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "email", "profile_photo", "qualifications", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "instructor"
        user.email = self.cleaned_data["email"]
        user.is_instructor_approved = False   # <-- approval required
        user.is_staff = False                 # <-- DO NOT make them staff
        user.is_superuser = False
        if commit:
            user.save()
        return user
    
    
class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "profile_photo", "qualifications"]
        widgets = {
            "username": forms.TextInput(attrs={
                "class": "mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            }),
            "email": forms.EmailInput(attrs={
                "class": "mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            }),
            "qualifications": forms.Textarea(attrs={
                "rows": 4,
                "class": "mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            }),
        }