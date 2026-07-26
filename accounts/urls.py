from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # HTML Views
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("change-password/", views.change_password_view, name="change_password"),
    path("verify-email/", views.verify_email_view, name="verify_email"),
    
    # REST API Endpoints
    path("api/register/", views.APIRegisterView.as_view(), name="api_register"),
    path("api/login/", views.APILoginView.as_view(), name="api_login"),
    path("api/profile/", views.APIProfileView.as_view(), name="api_profile"),
]
