from django.urls import path
from . import adminpanel_views as ap


urlpatterns = [
    path("ping/", ap.ping, name="ap_ping"),

    # user management
    path("users/", ap.user_list, name="ap_user_list"),
    path("users/new/student/", ap.create_student, name="ap_create_student"),
    path("users/new/instructor/", ap.create_instructor, name="ap_create_instructor"),
    path("users/<int:pk>/edit/", ap.user_edit, name="ap_user_edit"),
    path("users/<int:pk>/delete/", ap.user_delete, name="ap_user_delete"),
    path("users/<int:pk>/reset-password/", ap.reset_password, name="ap_reset_password"),
    path("users/<int:pk>/approve-instructor/", ap.approve_instructor, name="ap_approve_instructor"),
    path("courses/", ap.course_list, name="ap_course_list"),
    path("courses/<int:pk>/toggle/", ap.course_toggle_active, name="ap_course_toggle"),
    path("users/<int:pk>/approve-instructor/", ap.approve_instructor, name="ap_approve_instructor"),
    path("users/<int:pk>/reject-instructor/", ap.reject_instructor,  name="ap_reject_instructor"),
    path("categories/", ap.category_list,   name="ap_category_list"),
    path("categories/new/", ap.category_create, name="ap_category_create"),
    path("categories/<int:pk>/delete/", ap.category_delete, name="ap_category_delete"),
    path("dashboard/", ap.dashboard, name="ap_dashboard"),

]
