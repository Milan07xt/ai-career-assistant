from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    # HTML Views
    path("landing/", views.landing_view, name="landing"),
    path("home/", views.home_view, name="home"),
    
    # REST API Endpoints
    path("api/stats/", views.APIDashboardStatsView.as_view(), name="api_stats"),
]
