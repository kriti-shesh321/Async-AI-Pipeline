# AsyncAI Pipeline

A Django REST backend where authenticated users submit text-processing jobs and track them through an asynchronous processing pipeline. 

Jobs are processed asynchronously using Celery + Redis. The system supports task status tracking, result retrieval, retry handling, and mock AI workflows for summarization, sentiment analysis, and tag generation.

## Features

- User registration and JWT login
- Protected APIs using Bearer token authentication
- Submit text-processing jobs
- List authenticated user's jobs
- View job details
- Poll job status
- Retrieve job results
- Background processing with Celery
- Redis-backed task queue
- Retry handling for failed jobs
- Structured error history for debugging
- Mock AI processors with no paid third-party API dependency

## Tech Stack

- Python
- Django
- Django REST Framework
- SimpleJWT
- Celery
- Redis
- SQLite
- Postman for API testing

## Project Structure

```txt
async-ai-pipeline/
  backend/
    apps/
      accounts/        # Authentication-related serializers, views, and URLs
      jobs/            # Job model, APIs, Celery task, and processing services
    config/            # Django project settings, URLs, WSGI/ASGI, Celery config
    manage.py
    requirements.txt
    .env.example
  docs/                # Supporting documentation
    EXPLANATION.md
    AI-USAGE-NOTES.md
    postman-collection.json
  README.md
  .gitignore
```

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/kriti-shesh321/Async-AI-Pipeline
cd Async-AI-Pipeline
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Create environment file

Create a `.env` file inside the `backend/` directory.

```env
SECRET_KEY=replace-with-your-secret-key
DEBUG=True
REDIS_URL=redis://localhost:6379/0
```

Use `.env.example` as the safe template.

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Start Redis 

Local Redis setup for Ubuntu:

```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
redis-cli ping
```

Expected output:

```txt
PONG
```

Alternatively, a hosted Redis provider can be used by setting `REDIS_URL` in `.env`.

### 7. Start Django server

From the `backend/` directory:

```bash
python manage.py runserver
```

Server runs at:

```txt
http://127.0.0.1:8000/
```

### 8. Start Celery worker

Open a second terminal, activate the virtual environment, go to `backend/`, then run:

```bash
celery -A config worker --loglevel=info
```

Expected worker output should show the registered task:

```txt
apps.jobs.tasks.process_job
```

## API Overview

### Auth APIs

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register/` | Register a new user |
| POST | `/api/auth/login/` | Login and receive JWT access/refresh tokens |
| POST | `/api/auth/token/refresh/` | Generate a new access token |
| GET | `/api/auth/me/` | Get current authenticated user |

### Job APIs

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/jobs/` | Submit a new processing job |
| GET | `/api/jobs/` | List authenticated user's jobs |
| GET | `/api/jobs/<id>/` | Get full job details |
| GET | `/api/jobs/<id>/status/` | Get current job status |
| GET | `/api/jobs/<id>/result/` | Get result or failure details |

## Supported Task Types For Creating New Jobs

```txt
summarization
sentiment
tag_generation
```

## Example Job Request

```json
{
  "task_type": "summarization",
  "input_text": "For example, generative AI has seen a surge in development and investment, with applications that now outperform human experts in certain benchmarks and dramatically improve capabilities like programming and scientific research, within ethical reason."
}
```

## Job Lifecycle

```txt
pending
  ↓
in_progress
  ↓
completed
```

Failure/retry lifecycle:

```txt
in_progress
  ↓
retrying
  ↓
in_progress
  ↓
failed
```

## Notes on Redis and Celery

Redis is used as the Celery message broker. The application does not manually store job results in Redis. Instead:

- Django creates and stores the job in SQLite.
- Celery receives the job ID through Redis.
- The Celery worker processes the job.
- Final status, result, retry count, and error history are saved back to the database.

The database remains the source of truth for user-facing job state.

## Testing

The APIs were manually tested using Postman for:

- Registration
- Login
- Protected current-user route
- Job submission
- Job list/detail/status/result
- Successful completion flow
- Retry flow using controlled `force_fail` input
- Failed job flow after max retries are exhausted
- Unauthorized access
- Invalid request validation

`docs/postman-collection.json`: A Postman collection is included separately for easier testing.

---

### Testing 'retry' and 'failure handling'

Retry and failure handling can be tested manually using the included Postman collection.

To trigger a controlled processing failure:

1. Ensure `DEBUG=True` is set in the `.env` file.
2. Submit a new job using `POST /api/jobs/`.
3. Include the keyword `force_fail` anywhere inside the `input_text`.

Example request body:

```json
{
  "task_type": "tag_generation",
  "input_text": "This is a test input with force_fail to verify retry and failure handling."
}
```

Expected status progression:

```txt
pending → in_progress → retrying → in_progress → failed
```

4. The status can be checked using: `GET /api/jobs/{id}/status/`

5. The final failed result can be checked using: `GET /api/jobs/{id}/result/`

```txt
This controlled failure trigger is only enabled in debug mode so that normal production-like usage does not accidentally fail based on user input.
```

## Limitations

- Uses mock text processors instead of real AI APIs.
- Does not currently support file uploads, image processing, or video processing.
- Uses SQLite for local development.
- No frontend is included.
- No automated test suite is included yet.
- Celery uses one default queue.
- Deployment is not included yet.

## Future Improvements

- Add PostgreSQL for production deployment.
- Add file upload support with cloud object storage.
- Add real AI provider integrations.
- Add separate queues for text/image/video jobs.
- Add manual job cancellation.
- Add pagination and filtering.
- Add automated tests.
- Add frontend dashboard.