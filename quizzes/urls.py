from django.urls import path
from . import instructor_views as v

urlpatterns = [
    path("manage/<int:course_id>/", v.quiz_manage, name="quiz_manage"),
    path("new/<int:course_id>/", v.quiz_create, name="quiz_create"),

      # edit/delete quiz
    path("<int:quiz_id>/edit/", v.quiz_edit, name="quiz_edit"),
    path("<int:quiz_id>/delete/", v.quiz_delete, name="quiz_delete"),

    path("<int:quiz_id>/question/new/", v.question_create, name="question_create"),
     path("question/<int:q_id>/edit/", v.question_edit, name="question_edit"),
    path("question/<int:q_id>/delete/", v.question_delete, name="question_delete"),

    path("question/<int:q_id>/option/new/", v.option_create, name="option_create"),
     path("option/<int:op_id>/edit/", v.option_edit, name="option_edit"),
    path("option/<int:op_id>/delete/", v.option_delete, name="option_delete"),

]
