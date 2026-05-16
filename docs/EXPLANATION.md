## Initial Project Decisions

- Chose Django and DRF because the assessment requires a Django-based REST backend.
- Used SQLite for local development because it is simple to set up and accepted by the assignment.
- Chose Redis as the Celery broker because it is simpler to configure locally than RabbitMQ.
- Created separate `accounts` and `jobs` apps to keep authentication and processing logic modular.
- Deferred frontend implementation because the assignment is backend-focused.