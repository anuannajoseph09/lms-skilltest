from django import forms
from .models import Course, Category

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title","description","category","thumbnail","enrollment_type"]

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]
