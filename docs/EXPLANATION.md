## Tradeoffs & architectural decisisons

- Used Django + Django REST Framework because the assignment specifically required a Django-based REST backend.
- Used Celery + Redis for asynchronous processing, as required by the assignment.
- Used SQLite as the database because it is simple to set up, comes built-in with Django, and is enough for the assessment scope.
- Did not build a frontend because of the time limit and because this is mainly a backend-focused assignment.

The project is divided into two main modules:

### 1. Auth Module

For authentication, I used Django's built-in `User` model with SimpleJWT for token-based authentication.

Implemented endpoints:

- register
- login
- get current user
- refresh access token

### 2. Jobs Module

The `Job` model stores all job-related data in one table for the current assessment scope.

Main fields include:

- `user`
- `task_type`
- `input_text`
- `celery_task_id`
- `result`
- `retry_count`
- `latest_error_message`
- `error_history`

Supported task types:

- sentiment analysis
- tag generation
- summarization

In a larger production system, some of this data could be split into separate tables, such as: job results, job events/logs, retry/error history, etc

The processing is done using mock processor functions instead of real AI APIs. The asynchronous nature of the task is simulated using a short delay of around 10 seconds for each job.

#### Testing retry and error handling

For testing the retry and error handling flow, a `force_fail` keyword can be added inside the `input_text` while enabling DEBUG mode: `DEBUG=True`. This intentionally triggers a failure so the status endpoint can show the progression through retry/failure states.

Check the following fields to the test the flow:

- `status`
- `retry_count`
- `latest_error_message`
- `error_history`

---

- Main job flow:

```txt
Create a new job with a valid task_type
    |
    v
Django creates a Job record in the database
    |
    v
Django sends the job_id to Celery
    |
    v
Redis acts as the Celery message broker
    |
    v
Celery worker picks up the task
    |
    v
The task is processed using mock processor functions
    |
    v
If an error occurs, Celery retries the task
    |
    v
Final result or failure state is stored in the database
    |
    v
User can check status/result through API endpoints
```

---

## Problems faced during implementation

- Understanding how tasks move between Django, Redis, Celery, and the database.
- Understanding Celery concepts like `@shared_task`, `.delay()`, `bind=True`, `self.retry()`, and `self.request.retries`.
- Brushing up on Django and DRF since it had been a while since I last worked with them.
- Deciding how to design the Job model while keeping it complete but not overcomplicated.
- Deciding how to test retry and error handling without breaking normal processing
- Understanding why the job sometimes moved from retrying back to in_progress during retries.
- Keeping the API response objects clean and consistent across create, list, detail, status, and result endpoints.

---

## How issues were debugged and resolved

I discussed design and flow questions with ChatGPT, then implemented and validated manually.

- One issue was that the mock processing functions completed too quickly, making it hard to observe intermediate states like in_progress and retrying.

To solve this, I added a small artificial delay using time.sleep() so that the status endpoint could be tested properly through Postman.

- Another design question was whether a single error field was enough. Initially, one error message field seemed sufficient, but during retry testing it became clear that different retry attempts could fail for different reasons.

To handle this better, I added:

* `latest_error_message` for the most recent user-facing error
* `error_history` for structured retry-level error details

- I also tested the retry flow by using the force_fail keyword in the input text while DEBUG=True. This allowed me to intentionally trigger failures and verify that:

* the job moved to `retrying`
* retry count increased
* error history was updated
* the job eventually moved to `failed` after max retries

While testing, I noticed that the job could show in_progress during retry attempts. This was expected because:

* retrying means the next attempt has been scheduled
* in_progress means the worker is actively executing that attempt

The final API behavior was checked using Postman responses and Celery worker logs.

---

## Alternatives considered

### Database

Current choice: **SQLite**

Why: 
- good for local development
- simple setup
- enough for assessment scope.

Better production option: **PostgreSQL**

PostgreSQL would be better for production because it is more scalable and suitable for concurrent multi-user usage.

### Input Handling

Current choice is good for assignment scope:
- text input only
- input text is stored directly in the database

Production alternatives could be:
- allow file/media uploads
- store files in cloud storage
- store file metadata in the database
- define file expiry/retention rules

### Schema Design

Current choice: 
- store job status, result, retry count, latest error, and error history in the same `Job` model

Because of simpler implementation and ease of testing.

Production alternative:
- separate JobResult table
- separate JobEvent or JobAttemptLog table
- better querying/filtering of logs

I considered adding another table just for errors, but decided that the error_history JSON field was sufficient for the assessment scope.

### Job Ownership and API Behavior

Current choice: 
- each job belongs to a user
- users can only access their own jobs

Future improvements:
- rate limiting
- pagination for job listings
- soft deletion
- manual retry endpoint
- job cancellation

**Note: Why the Result Endpoint Returns 200 for Pending/In-Progress Jobs**

The result endpoint returns `200 OK` even when the result is not ready yet because the job exists and the request is valid. In this case, the response contains `result: null` and a message saying the result is not available yet.

A `404` is reserved for cases where the job does not exist or does not belong to the authenticated user.

### Celery Queue Design

Current choice:
- one default Celery queue

Because of simpler setup and it is enough for text-only mock jobs.

Production alternative:
- separate queues for text, image, video, or document processing (depending on input types supported)
- worker autoscaling
- priority queues
- dead-letter queues

---

## Limitations of the current implementation

- No real AI provider integrated yet.
- Jobs processed using only mock processor functions.
- No file or multi-media input support.
- No frontend.
- Pagination and filtering are not implemented for job listings.
- Rate limiting is not implemented.
- Manual job cancellation or retry endpoints are not implemented.
- The system is not deployed yet.
- SQLite is used, which is fine for local development but not ideal for production.
- Logging is currently mainly terminal/worker-log based and not stored in a separate persistent log table.

## Use of AI tools during development

- Used ChatGPT for design discussions, implementation guidance, debugging support, and documentation cleanup.
- Used Github Copilot for code completions and prompts.

please refer to `docs/AI-USAGE-NOTES.md` for detailed AI usage notes.