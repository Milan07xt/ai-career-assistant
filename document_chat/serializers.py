from rest_framework import serializers
from .models import Document, ChatMessage

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "file", "title", "uploaded_at"]
        read_only_fields = ["title", "uploaded_at"]

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["id", "document", "sender", "message", "source_info", "timestamp"]
        read_only_fields = ["sender", "source_info", "timestamp"]
