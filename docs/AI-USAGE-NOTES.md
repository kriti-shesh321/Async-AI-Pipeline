## AI Usage Disclosure

AI tools were used as a development assistant for planning, explanation, debugging, and documentation support.

The project was implemented, tested, and corrected based on actual runtime behavior.

## Areas Where AI Was Used

### 1. Project Planning

AI was used to understand the assessment requirements and break the backend into manageable modules:

- authentication
- job APIs
- Celery processing
- Redis broker setup
- retry/error handling
- documentation

This helped convert the assignment brief into smaller implementation stages.

### 2. API and Module Design

AI was used to discuss how to structure the backend into focused Django apps and API layers.

This included planning:

- deciding on `accounts` and `jobs` apps
- user-scoped job access
- separate serializers for create/list/detail/status/result responses
- protected routes using JWT authentication
- status/result endpoint behavior

The final API structure was adjusted based on testing and the response shapes needed for better readability.

### 3. Authentication Module

AI was used to plan and guide implementation of:

- user registration
- password hashing
- SimpleJWT login/refresh routes
- protected current-user endpoint

The endpoints were manually tested using Postman including successful login, missing-token cases, and invalid credentials.

### 4. Job API Design

AI was used to discuss:

- the `Job` model
- job lifecycle statuses
- create/list/detail/status/result endpoints
- serializer separation by endpoint

### 5. Celery and Redis Integration

AI was used to understand and implement the asynchronous processing flow with Celery and Redis.

The main design decision made was to use Redis only as the Celery message broker, while keeping the database as the source of truth for job status and results.

This was validated by:

- submitting jobs through the API
- confirming Celery received tasks from Redis
- checking worker logs
- verifying database-backed status/result updates

### 6. Retry and Failure Handling

AI was used to design the retry flow around Celery's `self.retry()` behavior.

This included deciding how the job should move between:

- `in_progress`
- `retrying`
- `failed`

A development-only `force_fail` trigger was added to test failure behavior safely when `DEBUG=True`.

The retry flow was then manually verified using Postman and Celery logs.

### 7. Error History Design

AI was used to evaluate whether a single error field was enough for failed jobs.

I decided to add:

- `latest_error_message` for the latest user-facing error
- `error_history` for structured attempt-level failure details 

This design preserves retry-level debugging context without adding a separate log table, which keeps the implementation lightweight for the assessment scope.

### 8. Debugging Support and Design Review

AI was used to reason through issues found during testing, especially around asynchronous behavior.

Examples included:

- understanding how job status should move from `retrying` back to `in_progress` during retry attempts
- deciding what response examples should be kept in the Postman collection
- clarifying Redis's role as a broker rather than a result store
- improving how retry/failure states are documented for reviewers

Final fixes were made after checking actual API responses and Celery worker output.

### 9. Documentation

AI was used to polish and organize the content from my documentation drafts for:

- README file
- EXPLANATION architecture and considerations notes
- AI usage file
- limitations and future improvements

## How AI Output Was Validated

AI-assisted changes were validated against the running application output and logs.

Validation included:

- checking actual API response shapes in Postman
- testing authenticated and unauthenticated requests
- confirming Celery worker logs matched expected task flow
- testing successful, retrying, and failed job states
- verifying that `retry_count`, `latest_error_message`, and `error_history` updated correctly
- comparing documentation and Postman examples against the final implemented API

When runtime behavior differed from the expected design, the code and documentation were updated accordingly.

## What Was Modified/Added Manually

The following decisions and refinements were made manually during implementation:

- kept the project text-only to avoid file storage complexity within the deadline
- used mock AI-style processors so the project can run without paid third-party APIs
- used SQLite for simple local setup
- used Redis as a Celery broker, not as the source of truth
- stored final job state and results in the database
- added a development-only `force_fail` trigger for retry testing
- added structured `error_history` after testing retry behavior
- cleaned Postman examples to show only useful response states

## Summary

AI was used as a development assistant for planning, design discussion, debugging support, and documentation cleanup. The final implementation was manually tested and adjusted based on actual Django, Celery, Redis, and Postman behavior.