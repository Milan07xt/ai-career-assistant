from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Job, Application, Bookmark
from .serializers import JobSerializer, ApplicationSerializer, BookmarkSerializer

# =====================================================================
# HTML TEMPLATE VIEWS
# =====================================================================

@login_required
def list_jobs_view(request):
    query = request.GET.get("q", "").strip()
    location = request.GET.get("location", "").strip()
    
    jobs = Job.objects.all()
    if query:
        jobs = jobs.filter(Q(title__icontains=query) | Q(company_name__icontains=query) | Q(description__icontains=query))
    if location:
        jobs = jobs.filter(location__icontains=location)
        
    # Calculate match percentage for each job
    profile = request.user.profile
    for j in jobs:
        j.match_score = j.get_match_percentage(profile)
        j.is_bookmarked = Bookmark.objects.filter(job=j, user=request.user).exists()
        
    return render(request, "jobs/list.html", {"jobs": jobs, "query": query, "location": location})

@login_required
def detail_job_view(request, pk):
    job = get_object_or_404(Job, pk=pk)
    profile = request.user.profile
    match_score = job.get_match_percentage(profile)
    is_bookmarked = Bookmark.objects.filter(job=job, user=request.user).exists()
    has_applied = Application.objects.filter(job=job, user=request.user).exists()
    
    return render(request, "jobs/detail.html", {
        "job": job,
        "match_score": match_score,
        "is_bookmarked": is_bookmarked,
        "has_applied": has_applied
    })

@login_required
def apply_job_view(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if Application.objects.filter(job=job, user=request.user).exists():
        messages.warning(request, "You have already applied to this job.")
        return redirect("jobs:detail", pk=pk)
        
    if request.method == "POST":
        cover_letter = request.POST.get("cover_letter", "")
        # Use existing resume from profile
        profile = request.user.profile
        if not profile.resume_file:
            messages.error(request, "Please upload a resume in your profile before applying.")
            return redirect("accounts:profile")
            
        Application.objects.create(
            job=job,
            user=request.user,
            resume_file=profile.resume_file,
            cover_letter=cover_letter
        )
        messages.success(request, f"Successfully applied for {job.title} at {job.company_name}!")
        return redirect("jobs:tracker")
        
    return render(request, "jobs/apply.html", {"job": job})

@login_required
def bookmark_job_view(request, pk):
    job = get_object_or_404(Job, pk=pk)
    bookmark_qs = Bookmark.objects.filter(job=job, user=request.user)
    
    if bookmark_qs.exists():
        bookmark_qs.delete()
        messages.info(request, "Job removed from bookmarks.")
    else:
        Bookmark.objects.create(job=job, user=request.user)
        messages.success(request, "Job bookmarked!")
        
    # Redirect back to where they came from
    next_url = request.GET.get("next") or request.META.get("HTTP_REFERER")
    if next_url:
        return redirect(next_url)
    return redirect("jobs:list")

@login_required
def tracker_view(request):
    applications = Application.objects.filter(user=request.user)
    bookmarks = Bookmark.objects.filter(user=request.user)
    return render(request, "jobs/tracker.html", {"applications": applications, "bookmarks": bookmarks})

@login_required
def post_job_view(request):
    if request.method == "POST":
        title = request.POST.get("title")
        company = request.POST.get("company_name")
        desc = request.POST.get("description")
        reqs = request.POST.get("requirements")
        loc = request.POST.get("location")
        sal = request.POST.get("salary")
        
        Job.objects.create(
            title=title,
            company_name=company,
            description=desc,
            requirements=reqs,
            location=loc,
            salary=sal,
            posted_by=request.user
        )
        messages.success(request, "Job posted successfully!")
        return redirect("jobs:list")
        
    return render(request, "jobs/post.html")


# =====================================================================
# REST API VIEWS
# =====================================================================

class APIJobListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = JobSerializer

    def get_queryset(self):
        queryset = Job.objects.all()
        q = self.request.query_params.get("q")
        loc = self.request.query_params.get("location")
        if q:
            queryset = queryset.filter(Q(title__icontains=q) | Q(company_name__icontains=q) | Q(description__icontains=q))
        if loc:
            queryset = queryset.filter(location__icontains=loc)
        return queryset

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)

class APIJobDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = JobSerializer
    queryset = Job.objects.all()

class APIJobApplyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        job = get_object_or_404(Job, pk=pk)
        if Application.objects.filter(job=job, user=request.user).exists():
            return Response({"error": "Already applied"}, status=status.HTTP_400_BAD_REQUEST)
            
        cover_letter = request.data.get("cover_letter", "")
        profile = request.user.profile
        
        if not profile.resume_file:
            return Response({"error": "Upload a resume on your profile first"}, status=status.HTTP_400_BAD_REQUEST)
            
        app = Application.objects.create(
            job=job,
            user=request.user,
            resume_file=profile.resume_file,
            cover_letter=cover_letter
        )
        serializer = ApplicationSerializer(app)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class APIJobBookmarkToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        job = get_object_or_404(Job, pk=pk)
        bookmark_qs = Bookmark.objects.filter(job=job, user=request.user)
        
        if bookmark_qs.exists():
            bookmark_qs.delete()
            return Response({"message": "Job removed from bookmarks"}, status=status.HTTP_200_OK)
        else:
            Bookmark.objects.create(job=job, user=request.user)
            return Response({"message": "Job bookmarked"}, status=status.HTTP_201_CREATED)

class APIApplicationTrackerListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ApplicationSerializer

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)
