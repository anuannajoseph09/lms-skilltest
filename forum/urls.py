from django.urls import path
from . import views              # student/general
from . import instructor_views as iv  # instructor-only

app_name = 'forum'

urlpatterns = [
    # Student / General routes
    path('<int:course_id>/', views.thread_list, name='thread_list'),
    path('<int:course_id>/new/', views.thread_create, name='thread_create'),
    path('t/<int:thread_id>/', views.thread_detail, name='thread_detail'),
    path('t/<int:thread_id>/reply/', views.reply_create, name='reply_create'),

    # Instructor-only moderation/interaction
    path('instructor/<int:course_id>/', iv.thread_list, name='instructor_thread_list'),
    path('instructor/t/<int:thread_id>/', iv.thread_detail, name='instructor_thread_detail'),
    path('instructor/t/<int:thread_id>/reply/', iv.reply_to_thread, name='instructor_reply_to_thread'),
    path('instructor/t/<int:thread_id>/delete/', iv.delete_thread, name='delete_thread'),
    path('instructor/r/<int:reply_id>/delete/', iv.delete_reply, name='delete_reply'),
]

