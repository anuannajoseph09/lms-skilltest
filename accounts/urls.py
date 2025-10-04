from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("ping/", views.ping, name="accounts_ping"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="/accounts/login/"), name="logout"),
    path("redirect_after_login/", views.redirect_after_login, name="redirect_after_login"),
]
