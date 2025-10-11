from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse_lazy

def _redir():
    # send the user back through the post-login router
    return reverse_lazy("accounts:redirect_after_login")

def student_required(view):
    return user_passes_test(
        lambda u: u.is_authenticated and getattr(u, "role", None) == "student",
        login_url=_redir()
    )(view)

def instructor_required(view):
    return user_passes_test(
        lambda u: u.is_authenticated and getattr(u, "role", None) == "instructor" and getattr(u, "is_instructor_approved", False),
        login_url=_redir()
    )(view)

def admin_required(view):
    return user_passes_test(
        lambda u: u.is_authenticated and (u.is_staff or u.is_superuser),
        login_url=_redir()
    )(view)
