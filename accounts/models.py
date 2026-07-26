from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True, help_text="Comma-separated skills (e.g. Python, Django, SQL)")
    location = models.CharField(max_length=100, blank=True, null=True)
    salary_expectation = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    preferred_role = models.CharField(max_length=100, blank=True, null=True)
    resume_file = models.FileField(upload_to="resumes/", null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def get_skills_list(self):
        if self.skills:
            return [s.strip() for s in self.skills.split(",") if s.strip()]
        return []

    @property
    def profile_completion_score(self):
        """
        Calculates profile completion percentage.
        """
        score = 0
        total_fields = 7
        if self.user.first_name and self.user.last_name:
            score += 1
        if self.avatar:
            score += 1
        if self.bio:
            score += 1
        if self.skills:
            score += 1
        if self.location:
            score += 1
        if self.preferred_role:
            score += 1
        if self.resume_file:
            score += 1
        
        return int((score / total_fields) * 100)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Ensure profile exists before saving
    if not hasattr(instance, 'profile'):
        Profile.objects.create(user=instance)
    instance.profile.save()
