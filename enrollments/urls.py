# enrollments/urls.py
from django.urls import path
from . import instructor_views as iv

app_name = "enrollments"

urlpatterns = [
    path("courses/<int:course_id>/students/", iv.enrolled_students, name="enrolled_students"),
    path("enrollments/<int:pk>/approve/", iv.approve_enrollment, name="approve_enrollment"),
]
