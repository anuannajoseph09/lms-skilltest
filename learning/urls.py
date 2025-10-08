from django.urls import path
from . import instructor_views as v
from . import live_views as lv

app_name = "learning"

urlpatterns = [
    path("manage/<int:course_id>/", v.manage_lessons, name="manage_lessons"),
    path("lesson/new/<int:course_id>/", v.lesson_create, name="lesson_create"),
    path("lesson/<int:pk>/edit/", v.lesson_edit, name="lesson_edit"),
    path("lesson/<int:pk>/delete/", v.lesson_delete, name="lesson_delete"),

    path("material/new/<int:lesson_id>/", v.material_create, name="material_create"),
    path("material/<int:pk>/delete/", v.material_delete, name="material_delete"),

    path("live/<int:course_id>/", lv.live_list, name="live_list"),
    path("live/new/<int:course_id>/", lv.live_create, name="live_create"),
    path("live/<int:pk>/edit/", lv.live_edit, name="live_edit"),
]
