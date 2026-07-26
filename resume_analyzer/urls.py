from django.urls import path
from . import views

app_name = "resume_analyzer"

urlpatterns = [
    # HTML Views
    path("upload/", views.analyze_view, name="upload"),
    path("history/", views.history_view, name="history"),
    path("<int:pk>/", views.detail_view, name="detail"),
    
    # Cover Letter Views
    path("cover-letter/new/", views.generate_cover_letter_view, name="cover_letter_new"),
    path("cover-letter/<int:cl_id>/", views.cover_letter_detail_view, name="cover_letter_detail"),
    path("cover-letter/<int:cl_id>/docx/", views.download_docx_view, name="cover_letter_docx"),
    path("cover-letter/<int:cl_id>/txt/", views.download_txt_view, name="cover_letter_txt"),
    
    # REST API Endpoints
    path("api/analyze/", views.APIResumeAnalyzeView.as_view(), name="api_analyze"),
    path("api/history/", views.APIResumeHistoryView.as_view(), name="api_history"),
    path("api/cover-letter/", views.APICoverLetterGenerateView.as_view(), name="api_cover_letter"),
]

