# WordDuel backend setup

Configure `DATABASE_URL`, `SECRET_KEY` (at least 32 characters), `REDIS_PASSWORD`, and comma-separated `CORS_ORIGINS` in the environment. `REDIS_URL` is optional and defaults to local Redis. Use generated secrets in deployment; do not reuse the example values below.

For the local Compose services, set `POSTGRES_PASSWORD` and `REDIS_PASSWORD` before starting Compose. PostgreSQL and Redis bind only to loopback on the host. The backend automatically uses `REDIS_PASSWORD` when connecting to local Redis; set `REDIS_URL` only to override the default host/database or configure managed Redis.

Apply migrations before starting the API:

```powershell
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API startup and `/health/ready` check require the database to be at the current Alembic revision. `/health/live` reports process liveness only.

## Phase 6–14 features

Run `alembic upgrade head` after pulling these changes and before starting the API. The latest migration adds selectable question modes, persistent board-game state, profile preferences and avatars, friend requests, and notifications. Existing Phase 6–9 additions include solo sessions, saved words, context sentences, adjustable room rounds, account roles, word-set moderation, and spreadsheet import. Excel imports accept `.xlsx` and `.csv` files up to 5 MB and 500 non-empty rows; `/api/v1/word-sets/import/template` downloads the spreadsheet template.

Rooms support classic, reverse, multiple-choice, listen-and-choose, listen-and-spell, fill-in-the-blank, and speak-and-pronounce question modes. Multiplayer rooms can additionally choose Vocabulary Monopoly, Boss Battle, Vocabulary Race, or Vocabulary Territory. Solo sessions can disable the timer. Profile preferences store theme, accent, locale, audio toggles, and speech voice/rate. Browser speech recognition sends a transcript for grading; audio is not uploaded to the API.

Friend, room-invitation, and profile endpoints are under `/api/v1/social` and `/api/v1/profile`. Notifications use `/api/v1/social/ws/notifications`; room play remains on the room WebSocket. Group/Classroom and the optional bonus roulette are not part of this release.

New accounts are regular users. To grant administrator access locally, register the account, then run:

```powershell
docker compose exec postgres psql -U wordduel -d wordduel_db -c "UPDATE users SET role = 'admin' WHERE username = 'your_username';"
```

Sign out and sign back in after changing a role so the new JWT contains the updated role.
