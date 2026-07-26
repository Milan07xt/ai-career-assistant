from rest_framework import serializers
from .models import Job, Application, Bookmark

class JobSerializer(serializers.ModelSerializer):
    match_percentage = serializers.SerializerMethodField()
    requirements_list = serializers.ReadOnlyField(source="get_requirements_list")

    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "company_name",
            "description",
            "requirements",
            "requirements_list",
            "location",
            "salary",
            "posted_by",
            "created_at",
            "match_percentage",
        ]
        read_only_fields = ["posted_by", "created_at"]

    def get_match_percentage(self, obj):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            return obj.get_match_percentage(request.user.profile)
        return 0

class ApplicationSerializer(serializers.ModelSerializer):
    job_details = JobSerializer(source="job", read_only=True)

    class Meta:
        model = Application
        fields = ["id", "job", "job_details", "user", "resume_file", "cover_letter", "status", "applied_at"]
        read_only_fields = ["user", "applied_at"]

class BookmarkSerializer(serializers.ModelSerializer):
    job_details = JobSerializer(source="job", read_only=True)

    class Meta:
        model = Bookmark
        fields = ["id", "job", "job_details", "user", "created_at"]
        read_only_fields = ["user", "created_at"]
