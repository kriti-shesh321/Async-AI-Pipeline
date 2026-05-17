import logging
import time

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from .models import Job
from .services.processors import process_text

logger = logging.getLogger(__name__)


def append_error_history(job, attempt, stage, message):
    history = job.error_history or []

    history.append(
        {
            "attempt": attempt,
            "stage": stage,
            "message": message,
            "timestamp": timezone.now().isoformat(),
        }
    )

    job.error_history = history


@shared_task(bind=True, max_retries=3)
def process_job(self, job_id):
    start_time = time.monotonic()

    try:
        job = Job.objects.get(id=job_id)

        logger.info(
            "Starting processing for job_id=%s task_type=%s", job.id, job.task_type
        )

        job.status = Job.Status.IN_PROGRESS
        job.progress = 25

        if self.request.retries == 0:
            job.latest_error_message = None
            job.error_history = []

        job.save(
            update_fields=[
                "status",
                "progress",
                "latest_error_message",
                "error_history",
                "updated_at",
            ]
        )

        result = process_text(job.task_type, job.input_text)

        processing_time_ms = int((time.monotonic() - start_time) * 1000)

        result["metadata"] = {
            **result.get("metadata", {}),
            "processing_time_ms": processing_time_ms,
            "retries_used": self.request.retries,
        }

        with transaction.atomic():
            job.result = result
            job.status = Job.Status.COMPLETED
            job.progress = 100
            job.latest_error_message = None
            job.retry_count = self.request.retries
            job.save(
                update_fields=[
                    "result",
                    "status",
                    "progress",
                    "latest_error_message",
                    "retry_count",
                    "updated_at",
                ]
            )

        logger.info("Completed processing for job_id=%s", job.id)

        return {
            "job_id": job.id,
            "status": job.status,
        }

    except Job.DoesNotExist:
        logger.error("Job not found for job_id=%s", job_id)
        return {
            "job_id": job_id,
            "status": "not_found",
        }

    except Exception as exc:
        retry_count = self.request.retries

        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            logger.error("Job disappeared during failure handling job_id=%s", job_id)
            return {
                "job_id": job_id,
                "status": "not_found",
            }

        if retry_count < self.max_retries:
            job.status = Job.Status.RETRYING
            job.progress = 50
            job.latest_error_message = "Temporary processing error. Retrying..."
            job.retry_count = retry_count + 1

            append_error_history(
                job=job,
                attempt=retry_count + 1,
                stage="retry_scheduled",
                message=str(exc),
            )

            job.save(
                update_fields=[
                    "status",
                    "progress",
                    "latest_error_message",
                    "error_history",
                    "retry_count",
                    "updated_at",
                ]
            )

            logger.warning(
                "Retrying job_id=%s retry=%s/%s error=%s",
                job_id,
                retry_count + 1,
                self.max_retries,
                str(exc),
            )

            raise self.retry(exc=exc, countdown=5)

        job.status = Job.Status.FAILED
        job.progress = 100
        job.latest_error_message = str(exc)
        job.retry_count = retry_count

        append_error_history(
            job=job,
            attempt=retry_count,
            stage="failed",
            message=str(exc),
        )

        job.save(
            update_fields=[
                "status",
                "progress",
                "latest_error_message",
                "error_history",
                "retry_count",
                "updated_at",
            ]
        )

        logger.error(
            "Failed processing job_id=%s error=%s", job_id, str(exc), exc_info=True
        )

        return {
            "job_id": job_id,
            "status": "failed",
            "error": str(exc),
        }