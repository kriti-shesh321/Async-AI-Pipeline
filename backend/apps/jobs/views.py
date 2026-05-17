from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Job
from .serializers import (
    JobCreateSerializer,
    JobDetailSerializer,
    JobListSerializer,
    JobResultSerializer,
    JobStatusSerializer,
)


class JobListCreateView(generics.ListCreateAPIView):
    def get_queryset(self):
        return Job.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return JobCreateSerializer
        return JobListSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class JobDetailView(generics.RetrieveAPIView):
    serializer_class = JobDetailSerializer

    def get_queryset(self):
        return Job.objects.filter(user=self.request.user)


class JobStatusView(APIView):
    def get(self, request, pk):
        try:
            job = Job.objects.get(pk=pk, user=request.user)
        except Job.DoesNotExist:
            return Response(
                {"detail": "Job not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = JobStatusSerializer(job)
        return Response(serializer.data)


class JobResultView(APIView):
    def get(self, request, pk):
        try:
            job = Job.objects.get(pk=pk, user=request.user)
        except Job.DoesNotExist:
            return Response(
                {"detail": "Job not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if job.status == Job.Status.COMPLETED:
            message = "Result retrieved successfully."
        elif job.status == Job.Status.FAILED:
            message = "Job failed. See error_message for details."
        else:
            message = "Result is not available yet."

        serializer = JobResultSerializer(job)

        response_data = serializer.data
        response_data["message"] = message

        return Response(response_data, status=status.HTTP_200_OK)