# enrollments/urls.py
from django.urls import path
from . import instructor_views as iv

app_name = "enrollments"

urlpatterns = [
    # ---------- Course-specific roster ----------
    path("courses/<int:course_id>/students/", iv.enrolled_students, name="enrolled_students"),
    path("courses/<int:pk>/approve/", iv.approve_enrollment, name="approve_enrollment"),

    # ---------- Pending queue for instructor ----------
    path("instructor/pending/", iv.pending_for_my_courses, name="pending"),
    path("instructor/approve/<int:enrollment_id>/", iv.approve, name="approve"),
    path("instructor/reject/<int:enrollment_id>/", iv.reject, name="reject"),
]