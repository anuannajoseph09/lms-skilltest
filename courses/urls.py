# courses/urls.py
from django.urls import path
from . import student_views as sv
from . import instructor_views as iv

app_name = "courses"

urlpatterns = [
    # ---------- Student routes ----------
    path("catalog/", sv.catalog, name="catalog"),
    path("enroll/<int:course_id>/", sv.enroll, name="enroll"),
    path("my/", sv.my_courses, name="my_courses"),
    path("<int:course_id>/learn/", sv.course_learn, name="learn"),

    # ---------- Instructor routes ----------
    path("dashboard/", iv.dashboard, name="instructor_dashboard"),
    path("instructor/my/", iv.my_courses, name="instructor_my_courses"),
    path("instructor/new/", iv.course_create, name="course_create"),
    path("instructor/<int:pk>/edit/", iv.course_edit, name="course_edit"),
    path("instructor/<int:pk>/delete/", iv.course_delete, name="course_delete"),
    path("instructor/categories/", iv.category_list, name="category_list"),
    path("instructor/categories/new/", iv.category_create, name="category_create"),

    # Progress pages
    path("instructor/<int:course_id>/students/", iv.course_students, name="course_students"),
    path("instructor/<int:course_id>/students/<int:user_id>/", iv.student_progress_detail, name="student_progress_detail"),
    path("lesson/<int:lesson_id>/done/", sv.mark_lesson_done, name="mark_lesson_done"),
]
