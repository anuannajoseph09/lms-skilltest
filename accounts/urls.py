# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import instructor_views as ac
from . import student_views as sv

urlpatterns = [
    path("ping/", views.ping, name="accounts_ping"),

    # Auth
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="/accounts/login/"),
        name="logout",
    ),
    path("redirect_after_login/", views.redirect_after_login, name="redirect_after_login"),

    # Student
    path("signup/student/", sv.student_signup, name="student_signup"),
    path("student/dashboard/", sv.student_dashboard, name="student_dashboard"),
    path("student/profile/", sv.student_profile_edit, name="student_profile_edit"),
    path("student/change-password/", sv.student_change_password, name="student_change_password"),  # optional


    # Instructor
    path("me/", ac.my_profile, name="instructor_profile"),
    
]
