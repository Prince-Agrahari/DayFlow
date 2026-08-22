# DayFlow HRM — Deployment Guide

## Local Development (Docker Compose)

From project root:

```bash
cp .env.example .env
docker compose up --build
```

Services:
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **PostgreSQL:** localhost:5432

## Manual Development

See root [README.md](../README.md) for step-by-step setup without Docker.

## Production Considerations

- Set strong `SECRET_KEY` (32+ random characters)
- Use managed PostgreSQL
- Configure CORS for production domain
- Store `GEMINI_API_KEY` in secrets manager
- Enable HTTPS via reverse proxy (Nginx/Traefik)
- Set `DEBUG=false` and `APP_ENV=production`

## Environment Variables

All configuration via environment variables. See `.env.example` at project root.

Never commit `.env` files to version control.
