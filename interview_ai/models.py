from django.db import models
from django.contrib.auth.models import User

class InterviewSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="interviews")
    role = models.CharField(max_length=100)
    overall_score = models.FloatField(default=0.0)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.role} ({self.created_at.strftime('%Y-%m-%d')})"

    class Meta:
        ordering = ["-created_at"]

    def calculate_overall_score(self):
        """
        Computes the average score across answered questions.
        """
        answered = self.questions.exclude(user_answer__isnull=True).exclude(user_answer="")
        if not answered.exists():
            return 0.0
        total = sum(q.score for q in answered)
        self.overall_score = round(total / answered.count(), 1)
        self.save()
        return self.overall_score

class InterviewQuestionResponse(models.Model):
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    question_type = models.CharField(max_length=50)  # Technical, Coding, Behavioral
    user_answer = models.TextField(blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)
    suggested_answer = models.TextField(blank=True, null=True)
    score = models.IntegerField(default=0)  # 0 to 10 scale
    answered_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Q for {self.session.role}: {self.question_text[:50]}"

    class Meta:
        ordering = ["id"]
