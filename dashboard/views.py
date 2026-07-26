from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from accounts.models import Profile
from resume_analyzer.models import Resume, CoverLetter
from interview_ai.models import InterviewSession
from jobs.models import Job, Application, Bookmark

def landing_view(request):
    """
    Renders the public landing page.
    """
    if request.user.is_authenticated:
        return redirect("dashboard:home")
    return render(request, "dashboard/landing.html")

@login_required
def home_view(request):
    """
    Renders the authenticated professional dashboard.
    """
    user = request.user
    profile = user.profile
    
    # 1. Latest Resume Details
    latest_resume = Resume.objects.filter(user=user).first()
    ats_score = latest_resume.ats_score if latest_resume else 0
    ats_dashoffset = int(264 * (100 - ats_score) / 100)
    resume_analysis = latest_resume.analysis_json if latest_resume else {}
    
    # 2. Application Stats
    applications = Application.objects.filter(user=user)
    total_applications = applications.count()
    apps_reviewing = applications.filter(status="Reviewing").count()
    apps_interviews = applications.filter(status="Interview Scheduled").count()
    
    # 3. Interviews
    interviews = InterviewSession.objects.filter(user=user)
    total_interviews = interviews.count()
    upcoming_interviews = interviews.filter(is_completed=False).count()
    completed_interviews = interviews.filter(is_completed=True)
    
    # Average interview score
    completed_scores = [i.overall_score for i in completed_interviews if i.overall_score > 0]
    avg_interview_score = round(sum(completed_scores) / len(completed_scores), 1) if completed_scores else 0.0

    # 4. Profile Completion
    completion_meter = profile.profile_completion_score

    # 5. Skill & Learning Progress
    skills_list = profile.get_skills_list
    
    # 6. Recommended Jobs (Filter jobs that match user's profile skills)
    recommended_jobs = []
    all_jobs = Job.objects.all()[:10]
    for j in all_jobs:
        score = j.get_match_percentage(profile)
        if score >= 40 or not skills_list:  # Suggest if matching score is decent
            j.match_score = score
            recommended_jobs.append(j)
            
    # Sort recommended jobs by match score descending
    recommended_jobs = sorted(recommended_jobs, key=lambda x: getattr(x, "match_score", 0), reverse=True)[:4]

    # 7. AI Suggestions
    ai_suggestions = []
    if latest_resume and resume_analysis:
        ai_suggestions = resume_analysis.get("improvements", [])[:3]
    else:
        ai_suggestions = [
            "Upload your resume to receive professional ATS score analysis and missing skill check.",
            "Complete your profile profile picture, bio, and skills list to reach 100% profile score.",
            "Start a mock interview session for your target role to build tech skills confidence."
        ]

    # 8. Recent Activity Feed (Combine applications, resumes, interviews)
    activities = []
    for app in applications[:2]:
        activities.append({
            "icon": "briefcase",
            "color": "primary",
            "text": f"Applied for {app.job.title} at {app.job.company_name}",
            "time": app.applied_at
        })
    if latest_resume:
        activities.append({
            "icon": "file-earmark-text",
            "color": "success",
            "text": "Uploaded and analyzed a new resume",
            "time": latest_resume.created_at
        })
    for interview in interviews.filter(is_completed=True)[:2]:
        activities.append({
            "icon": "patch-check",
            "color": "info",
            "text": f"Completed {interview.role} Mock Interview (Score: {interview.overall_score}/10)",
            "time": interview.created_at
        })
    # Sort activities by time
    activities = sorted(activities, key=lambda x: x["time"], reverse=True)[:5]

    context = {
        "profile": profile,
        "ats_score": ats_score,
        "ats_dashoffset": ats_dashoffset,
        "latest_resume": latest_resume,
        "total_applications": total_applications,
        "apps_reviewing": apps_reviewing,
        "apps_interviews": apps_interviews,
        "total_interviews": total_interviews,
        "upcoming_interviews": upcoming_interviews,
        "avg_interview_score": avg_interview_score,
        "completion_meter": completion_meter,
        "skills_list": skills_list,
        "recommended_jobs": recommended_jobs,
        "ai_suggestions": ai_suggestions,
        "activities": activities,
    }
    return render(request, "dashboard/home.html", context)


# =====================================================================
# REST API VIEWS
# =====================================================================

class APIDashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        profile = user.profile
        
        latest_resume = Resume.objects.filter(user=user).first()
        applications = Application.objects.filter(user=user)
        interviews = InterviewSession.objects.filter(user=user)
        
        # Calculate stats
        ats_score = latest_resume.ats_score if latest_resume else 0
        total_apps = applications.count()
        total_interviews = interviews.count()
        upcoming_interviews = interviews.filter(is_completed=False).count()
        profile_completion = profile.profile_completion_score

        # Average interview score
        completed = interviews.filter(is_completed=True)
        scores = [i.overall_score for i in completed if i.overall_score > 0]
        avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0

        return Response({
            "ats_resume_score": ats_score,
            "total_applications": total_apps,
            "total_interviews": total_interviews,
            "upcoming_interviews": upcoming_interviews,
            "average_interview_score": avg_score,
            "profile_completion_score": profile_completion,
            "skills": profile.get_skills_list
        }, status=status.HTTP_200_OK)
