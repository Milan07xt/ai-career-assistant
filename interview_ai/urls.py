from django.urls import path
from . import views

app_name = "interview_ai"

urlpatterns = [
    # HTML Views
    path("start/", views.start_session_view, name="start"),
    path("session/<int:session_id>/q/<int:question_idx>/", views.question_view, name="question"),
    path("session/<int:session_id>/summary/", views.summary_view, name="summary"),
    
    # REST API Endpoints
    path("api/start/", views.APIStartSessionView.as_view(), name="api_start"),
    path("api/submit/<int:question_id>/", views.APISubmitAnswerView.as_view(), name="api_submit"),
    path("api/session/<int:pk>/", views.APISessionDetailView.as_view(), name="api_session"),
]
