# WordDuel backend setup

Configure `DATABASE_URL`, `SECRET_KEY` (at least 32 characters), `REDIS_URL`, and comma-separated `CORS_ORIGINS` in the environment. Use generated secrets in deployment; do not reuse the example values below.

For the local Compose services, set `POSTGRES_PASSWORD` and `REDIS_PASSWORD` before starting Compose. PostgreSQL and Redis bind only to loopback on the host. Point the backend at those services with `DATABASE_URL` and `REDIS_URL`.

Apply migrations before starting the API:

```powershell
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API startup and `/health/ready` check require the database to be at the current Alembic revision. `/health/live` reports process liveness only.
