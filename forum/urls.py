from django.urls import path
from . import instructor_views as v

urlpatterns = [
    path("forum/<int:course_id>/", v.thread_list, name="forum_threads"),
    path("forum/reply/<int:thread_id>/", v.reply_create, name="forum_reply"),
]
