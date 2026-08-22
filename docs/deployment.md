# DayFlow Deployment Guide

## Prerequisites

- Docker 24+ and Docker Compose v2
- Node.js 20+ (local frontend build)
- Python 3.11+ (local backend)
- PostgreSQL 15+ (or use Docker postgres service)

## Environment Setup

```bash
cp .env.example .env
```

Key variables:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | JWT secret (min 32 characters) |
| `DATABASE_URL` | PostgreSQL connection string |
| `GEMINI_API_KEY` | Google Gemini API key (server-side only) |
| `CORS_ORIGINS` | Allowed frontend origins |
| `VITE_API_BASE_URL` | Frontend API base URL |
| `VITE_USE_MOCK` | Set `false` for live backend |

## Docker Compose

### Development stack

```bash
docker compose --profile dev up -d
docker compose exec backend python scripts/seed.py
```

### Production stack

```bash
docker compose --profile prod up -d --build
docker compose exec backend python scripts/seed.py
```

## Health Checks

- **Backend:** `GET http://localhost:8000/api/health`
- **Database:** included in health response (`database: connected`)
- **Docker:** compose healthchecks on postgres and backend services

## Module PYTHONPATH

The backend Docker image sets:

```
PYTHONPATH=/app:/app/../ai-engine:/app/../analytics
```

This allows the backend to import `ai-engine` and `analytics` sibling packages without duplicating code.

## Production Checklist

- [ ] Set strong `SECRET_KEY`
- [ ] Configure PostgreSQL with persistent volume
- [ ] Set `DEBUG=false`
- [ ] Configure `CORS_ORIGINS` to production domain
- [ ] Set `GEMINI_API_KEY` for AI features
- [ ] Run seed script for demo/staging data
- [ ] Build frontend with `VITE_USE_MOCK=false`
- [ ] Enable HTTPS reverse proxy (nginx/Traefik)

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Backend can't connect to DB | Wait for postgres healthcheck; verify `DATABASE_URL` |
| Analytics empty | Run `python backend/scripts/seed.py` |
| AI fallback responses | Set `GEMINI_API_KEY` in `.env` |
| CORS errors | Add frontend URL to `CORS_ORIGINS` |
