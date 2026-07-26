from django.urls import path
from . import views

app_name = "document_chat"

urlpatterns = [
    # HTML Views
    path("", views.chat_session_view, name="session"),
    path("<int:doc_id>/", views.chat_session_view, name="session_detail"),
    path("upload/", views.upload_document_view, name="upload"),
    
    # REST API Endpoints
    path("api/upload/", views.APIDocumentUploadView.as_view(), name="api_upload"),
    path("api/messages/<int:doc_id>/", views.APIChatMessageListView.as_view(), name="api_messages"),
    path("api/ask/<int:doc_id>/", views.APIChatAskView.as_view(), name="api_ask"),
]
