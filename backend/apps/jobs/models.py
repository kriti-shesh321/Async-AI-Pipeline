from django.conf import settings
from django.db import models


class Job(models.Model):
    class TaskType(models.TextChoices):
        SUMMARIZATION = "summarization", "Summarization"
        SENTIMENT = "sentiment", "Sentiment Analysis"
        TAG_GENERATION = "tag_generation", "Tag Generation"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        RETRYING = "retrying", "Retrying"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="jobs"
    )

    task_type = models.CharField(max_length=50, choices=TaskType.choices)

    input_text = models.TextField()

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )

    progress = models.PositiveSmallIntegerField(default=0)

    result = models.JSONField(null=True, blank=True)

    error_message = models.TextField(null=True, blank=True)

    retry_count = models.PositiveSmallIntegerField(default=0)

    celery_task_id = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Job {self.id} - {self.task_type} - {self.status}"