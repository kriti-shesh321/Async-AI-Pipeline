from django.contrib import admin

from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "task_type",
        "status",
        "progress",
        "retry_count",
        "created_at",
    ]
    list_filter = ["task_type", "status", "created_at"]
    search_fields = ["user__username", "input_text"]
    readonly_fields = ["created_at", "updated_at"]