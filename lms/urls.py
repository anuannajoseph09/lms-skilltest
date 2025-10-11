from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # namespaced includes (critical)
    path(
        "adminpanel/",
        include(("accounts.adminpanel_urls", "adminpanel"), namespace="adminpanel"),
    ),
    path(
        "accounts/",
        include(("accounts.urls", "accounts"), namespace="accounts"),
    ),
    path(
        "courses/",
        include(("courses.urls", "courses"), namespace="courses"),
    ),
    path(
        "enrollments/",
        include(("enrollments.urls", "enrollments"), namespace="enrollments"),
    ),
    path(
        "quizzes/",  # <-- use plural consistently
        include(("quizzes.urls", "quizzes"), namespace="quizzes"),
    ),
    path(
        "forum/",
        include(("forum.urls", "forum"), namespace="forum"),
    ),
    path(
        "analytics/",
        include(("analytics.urls", "analytics"), namespace="analytics"),
    ),
    path(
        "learning/",
        include(("learning.urls", "learning"), namespace="learning"),
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
