from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def ping(request):
    return HttpResponse("accounts ok")

@login_required
def redirect_after_login(request):
    """Redirect users to their respective dashboards based on role."""
    user = request.user
    if user.is_superuser or user.is_staff:
        return redirect("/adminpanel/users/")
    elif user.role == "instructor":
        return redirect("/courses/my/")
    elif user.role == "student":
        return redirect("/student/dashboard/")
    else:
        return redirect("/")  # fallback

