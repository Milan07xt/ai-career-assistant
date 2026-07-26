from django.db import models
from django.contrib.auth.models import User

class Job(models.Model):
    title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField(help_text="Comma-separated skills (e.g. Python, Django, SQL)")
    location = models.CharField(max_length=255)
    salary = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. $80,000 - $100,000")
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posted_jobs")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} at {self.company_name}"

    class Meta:
        ordering = ["-created_at"]

    def get_requirements_list(self):
        if self.requirements:
            return [r.strip() for r in self.requirements.split(",") if r.strip()]
        return []

    def get_match_percentage(self, profile):
        """
        Calculate match percentage based on user's profile skills vs job requirements.
        """
        if not profile:
            return 0
        user_skills = set(s.lower() for s in profile.get_skills_list)
        if not user_skills:
            return 10  # Baseline default
        
        job_reqs = set(r.lower() for r in self.get_requirements_list())
        if not job_reqs:
            return 50  # Neutral default
            
        matching_skills = user_skills.intersection(job_reqs)
        
        # Jaccard index style matching score
        score = int((len(matching_skills) / len(job_reqs)) * 100)
        
        # Boost if preferred role matches the job title
        if profile.preferred_role and profile.preferred_role.lower() in self.title.lower():
            score += 15
            
        return min(max(score, 15), 98)  # Clamp between 15% and 98%

class Application(models.Model):
    STATUS_CHOICES = [
        ("Applied", "Applied"),
        ("Reviewing", "Reviewing"),
        ("Interview Scheduled", "Interview Scheduled"),
        ("Accepted", "Accepted"),
        ("Rejected", "Rejected"),
    ]
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applications")
    resume_file = models.FileField(upload_to="application_resumes/", null=True, blank=True)
    cover_letter = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, default="Applied", choices=STATUS_CHOICES)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} application for {self.job.title}"

    class Meta:
        ordering = ["-applied_at"]
        unique_together = ["job", "user"]

class Bookmark(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="bookmarks")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookmarks")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} bookmarked {self.job.title}"

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["job", "user"]
