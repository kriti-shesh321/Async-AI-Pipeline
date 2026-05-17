from django.urls import path

from .views import (
    JobDetailView,
    JobListCreateView,
    JobResultView,
    JobStatusView,
)


urlpatterns = [
    path("", JobListCreateView.as_view(), name="job-list-create"),
    path("<int:pk>/", JobDetailView.as_view(), name="job-detail"),
    path("<int:pk>/status/", JobStatusView.as_view(), name="job-status"),
    path("<int:pk>/result/", JobResultView.as_view(), name="job-result"),
]