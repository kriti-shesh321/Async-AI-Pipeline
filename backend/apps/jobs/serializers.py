from rest_framework import serializers

from .models import Job


class JobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ["id", "task_type", "input_text"]

    def validate_input_text(self, value):
        cleaned_value = value.strip()

        if not cleaned_value:
            raise serializers.ValidationError("Input text cannot be empty.")

        if len(cleaned_value) < 20:
            raise serializers.ValidationError(
                "Input text must be at least 20 characters long."
            )

        return cleaned_value


class JobListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            "id",
            "task_type",
            "status",
            "progress",
            "retry_count",
            "created_at",
            "updated_at",
        ]


class JobDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            "id",
            "task_type",
            "input_text",
            "status",
            "progress",
            "result",
            "error_message",
            "retry_count",
            "celery_task_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class JobStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            "id",
            "status",
            "progress",
            "retry_count",
            "error_message",
            "updated_at",
        ]


class JobResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            "id",
            "status",
            "result",
            "error_message",
        ]