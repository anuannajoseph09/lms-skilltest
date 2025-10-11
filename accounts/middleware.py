from django.shortcuts import redirect
from django.urls import reverse

class InstructorApprovalGate:
    """
    If a logged-in user is role='instructor' and not approved,
    force them onto the 'pending' page, except for safe/allowed paths.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)

        if user and user.is_authenticated:
            role = getattr(user, "role", "")
            approved = getattr(user, "is_instructor_approved", False)

            if role == "instructor" and not approved:
                # Allowed paths while unapproved:
                allowed = {
                    reverse("accounts:pending"),
                    reverse("accounts:logout"),
                }
                # Also allow admin login/logout & static & Django admin
                path = request.path
                if (
                    path not in allowed
                    and not path.startswith("/admin/")        # Django admin
                    and not path.startswith("/static/")       # static files
                    and not path.startswith("/media/")        # media if needed
                ):
                    return redirect("accounts:pending")

        return self.get_response(request)
