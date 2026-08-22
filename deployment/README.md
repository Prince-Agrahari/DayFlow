# DayFlow Deployment

## Quick Start (Development)

```bash
cp .env.example .env
docker compose --profile dev up -d
```

Services:
- PostgreSQL: `localhost:5432`
- Backend API: `http://localhost:8000` (health: `/api/health`)
- Frontend dev: `http://localhost:5173`

Seed demo data:

```bash
docker compose exec backend python scripts/seed.py
```

## Production Profile

```bash
docker compose --profile prod up -d --build
```

- Backend: FastAPI on port 8000
- Frontend: nginx serving static build on port 8080

## Health Checks

| Service | Endpoint |
|---------|----------|
| Backend | `GET /api/health` → `{ status, version, database }` |
| Postgres | `pg_isready` via Docker healthcheck |

## Environment Variables

See root `.env.example`. Required for production:

- `SECRET_KEY` — JWT signing (min 32 chars)
- `DATABASE_URL` — PostgreSQL connection string
- `GEMINI_API_KEY` — server-side AI only (optional for fallback mode)
- `CORS_ORIGINS` — frontend origin whitelist

## Dockerfiles

| File | Purpose |
|------|---------|
| `backend/Dockerfile` | Python 3.11, includes ai-engine + analytics via PYTHONPATH |
| `frontend/Dockerfile` | Multi-stage Node build → nginx production serve |

## Manual Deployment

1. Apply `database/schema.sql`
2. Run `python backend/scripts/seed.py`
3. Start backend: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
4. Build frontend: `npm run build` → serve `dist/` via nginx or static host

See [docs/deployment.md](../docs/deployment.md) for full instructions.
