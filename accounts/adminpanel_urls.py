from django.urls import path
from . import adminpanel_views as ap

urlpatterns = [
    path("ping/", ap.ping, name="ap_ping"),  # quick health check
    # we'll add more routes here in the next steps
]
