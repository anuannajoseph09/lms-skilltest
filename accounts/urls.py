# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import student_views as sv
from . import instructor_views as iv

app_name = "accounts"

urlpatterns = [
    # auth
    path("login/",  auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="/accounts/login/"), name="logout"),

    # role choice + post-login router
    path("signup/", views.signup_choice, name="signup_choice"),
    path("redirect_after_login/", views.redirect_after_login, name="redirect_after_login"),

    # registrations
    path("signup/student/", sv.student_signup, name="student_signup"),
    path("signup/instructor/", iv.instructor_signup, name="instructor_signup"),
    path("instructor/pending/", iv.instructor_pending, name="instructor_pending"),
    path("pending/", views.instructor_pending, name="pending"),

    # dashboards
    path("student/dashboard/", sv.student_dashboard, name="student_dashboard"),
    path("student/profile/", sv.student_profile_edit, name="student_profile_edit"),
    path("student/change-password/", sv.student_change_password, name="student_change_password"),

    # instructor profile (when approved)
    path("me/", iv.my_profile, name="instructor_profile"),
]

