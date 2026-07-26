from rest_framework import serializers
from .models import InterviewSession, InterviewQuestionResponse

class InterviewQuestionResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewQuestionResponse
        fields = [
            "id",
            "question_text",
            "question_type",
            "user_answer",
            "feedback",
            "suggested_answer",
            "score",
        ]
        read_only_fields = ["question_text", "question_type", "feedback", "suggested_answer", "score"]

class InterviewSessionSerializer(serializers.ModelSerializer):
    questions = InterviewQuestionResponseSerializer(many=True, read_only=True)

    class Meta:
        model = InterviewSession
        fields = ["id", "role", "overall_score", "is_completed", "created_at", "questions"]
        read_only_fields = ["overall_score", "is_completed", "created_at"]
