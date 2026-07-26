from django.urls import path
from . import views

app_name = "jobs"

urlpatterns = [
    # HTML Views
    path("list/", views.list_jobs_view, name="list"),
    path("detail/<int:pk>/", views.detail_job_view, name="detail"),
    path("apply/<int:pk>/", views.apply_job_view, name="apply"),
    path("bookmark/<int:pk>/", views.bookmark_job_view, name="bookmark"),
    path("tracker/", views.tracker_view, name="tracker"),
    path("post/", views.post_job_view, name="post"),
    
    # REST API Endpoints
    path("api/", views.APIJobListCreateView.as_view(), name="api_list"),
    path("api/detail/<int:pk>/", views.APIJobDetailView.as_view(), name="api_detail"),
    path("api/apply/<int:pk>/", views.APIJobApplyView.as_view(), name="api_apply"),
    path("api/bookmark/<int:pk>/", views.APIJobBookmarkToggleView.as_view(), name="api_bookmark"),
    path("api/tracker/", views.APIApplicationTrackerListView.as_view(), name="api_tracker"),
]
