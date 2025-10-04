from django.urls import path
from . import instructor_views as v

urlpatterns = [
    path("my/", v.my_courses, name="my_courses"),
    path("new/", v.course_create, name="course_create"),
    path("<int:pk>/edit/", v.course_edit, name="course_edit"),
    path("<int:pk>/delete/", v.course_delete, name="course_delete"),

    path("categories/", v.category_list, name="category_list"),
    path("categories/new/", v.category_create, name="category_create"),
]
