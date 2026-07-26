from django.db import models
from django.contrib.auth.models import User

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="resumes")
    file = models.FileField(upload_to="resumes/")
    extracted_text = models.TextField(blank=True, null=True)
    ats_score = models.IntegerField(default=0)
    analysis_json = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Resume ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

    class Meta:
        ordering = ["-created_at"]

class CoverLetter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cover_letters")
    company_name = models.CharField(max_length=255)
    job_description = models.TextField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Cover Letter for {self.company_name} ({self.created_at.strftime('%Y-%m-%d')})"

    class Meta:
        ordering = ["-created_at"]

