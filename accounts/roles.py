from django.core.exceptions import PermissionDenied

def instructor_required(view_func):
    def _wrapped(request, *args, **kwargs):
        u = request.user
        if not u.is_authenticated or getattr(u, "role", "") != "instructor":
            raise PermissionDenied("Instructor only")
        return view_func(request, *args, **kwargs)
    return _wrapped
