from django.db import models
from django.contrib.auth.models import User

class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="documents")
    file = models.FileField(upload_to="chat_docs/")
    title = models.CharField(max_length=255)
    extracted_text = models.TextField(blank=True, null=True)
    faiss_index_path = models.CharField(max_length=500, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    class Meta:
        ordering = ["-uploaded_at"]

class ChatMessage(models.Model):
    SENDER_CHOICES = [
        ("user", "User"),
        ("ai", "AI"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_messages")
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="messages", null=True, blank=True)
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message = models.TextField()
    source_info = models.JSONField(blank=True, null=True, help_text="List of source passages and page numbers")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.upper()} message in {self.document.title if self.document else 'General'} chat"

    class Meta:
        ordering = ["timestamp"]
