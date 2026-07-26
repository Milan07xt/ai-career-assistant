from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse
from django.http import HttpResponseRedirect

# REST Framework imports
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Profile
from .serializers import RegisterSerializer, UserSerializer, ProfileSerializer

# =====================================================================
# HTML TEMPLATE VIEWS
# =====================================================================

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")
        
    if request.method == "POST":
        u = request.POST.get("username")
        p = request.POST.get("password")
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("dashboard:home")
        else:
            messages.error(request, "Invalid username or password.")
            
    return render(request, "accounts/login.html")

def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")
        
    if request.method == "POST":
        u = request.POST.get("username")
        e = request.POST.get("email")
        p = request.POST.get("password")
        f_name = request.POST.get("first_name", "")
        l_name = request.POST.get("last_name", "")
        
        if User.objects.filter(username=u).exists():
            messages.error(request, "Username already exists.")
        elif User.objects.filter(email=e).exists():
            messages.error(request, "Email already registered.")
        else:
            user = User.objects.create_user(username=u, email=e, password=p, first_name=f_name, last_name=l_name)
            messages.success(request, "Account created! Please log in.")
            return redirect("accounts:login")
            
    return render(request, "accounts/register.html")

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("accounts:login")

@login_required
def profile_view(request):
    profile = request.user.profile
    if request.method == "POST":
        # Form handling user profile details
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        bio = request.POST.get("bio")
        skills = request.POST.get("skills")
        location = request.POST.get("location")
        preferred_role = request.POST.get("preferred_role")
        salary = request.POST.get("salary_expectation")
        
        # Files
        avatar = request.FILES.get("avatar")
        resume = request.FILES.get("resume_file")

        # Update User
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.save()

        # Update Profile
        profile.bio = bio
        profile.skills = skills
        profile.location = location
        profile.preferred_role = preferred_role
        if salary:
            try:
                profile.salary_expectation = float(salary)
            except ValueError:
                pass
        if avatar:
            profile.avatar = avatar
        if resume:
            profile.resume_file = resume
            
        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("accounts:profile")

    return render(request, "accounts/profile.html", {"profile": profile})

@login_required
def change_password_view(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, "Your password was successfully updated!")
            return redirect("accounts:profile")
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "accounts/change_password.html", {"form": form})

@login_required
def verify_email_view(request):
    profile = request.user.profile
    profile.is_email_verified = True
    profile.save()
    messages.success(request, "Your email has been successfully verified!")
    return redirect("accounts:profile")


# =====================================================================
# REST API VIEWS
# =====================================================================

class APIRegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

class APILoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            serializer = UserSerializer(user)
            return Response(
                {"message": "Login successful", "user": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_400_BAD_REQUEST
        )

class APIProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user
