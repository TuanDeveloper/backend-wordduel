# WordDuel backend setup

Configure `DATABASE_URL`, `SECRET_KEY` (at least 32 characters), `REDIS_URL`, and comma-separated `CORS_ORIGINS` in the environment. Use generated secrets in deployment; do not reuse the example values below.

For the local Compose services, set `POSTGRES_PASSWORD` and `REDIS_PASSWORD` before starting Compose. PostgreSQL and Redis bind only to loopback on the host. Point the backend at those services with `DATABASE_URL` and `REDIS_URL`.

Apply migrations before starting the API:

```powershell
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API startup and `/health/ready` check require the database to be at the current Alembic revision. `/health/live` reports process liveness only.

## Phase 6–9 features

Run `alembic upgrade head` after pulling these changes. The migration adds solo sessions, saved words, context sentences, adjustable room rounds, account roles, and word-set moderation. Excel imports accept `.xlsx` and `.csv` files up to 5 MB and 500 non-empty rows; `/api/v1/word-sets/import/template` downloads the spreadsheet template.

New accounts are regular users. To grant administrator access locally, register the account, then run:

```powershell
docker compose exec postgres psql -U wordduel -d wordduel_db -c "UPDATE users SET role = 'admin' WHERE username = 'your_username';"
```

Sign out and sign back in after changing a role so the new JWT contains the updated role.
