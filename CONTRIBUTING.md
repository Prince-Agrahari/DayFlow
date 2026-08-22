# Contributing to DayFlow HRM

Thank you for contributing to DayFlow. This guide covers setup, conventions, and collaboration rules for our four-developer hackathon team.

## Team & Branch Ownership

| Developer | Branch | Scope |
|-----------|--------|-------|
| Dev 1 | `feature/frontend-ui` | `frontend/` — React UI, routing, components |
| Dev 2 | `feature/backend-hrms` | `backend/` — FastAPI, models, auth, CRUD |
| Dev 3 | `feature/ai-intelligence` | `ai-engine/` — ML, Gemini, AI endpoints |
| Dev 4 | `feature/analytics-devops` | `analytics/`, `database/`, `deployment/`, `tests/` |

**Shared files** (`docs/`, root config, `.env.example`) require team agreement before merging.

## Getting Started

1. Clone the repository
2. Copy `.env.example` to `.env` and configure
3. Read [docs/architecture.md](docs/architecture.md) and [docs/api-contract.md](docs/api-contract.md)
4. Create your feature branch from `main`
5. Work only within your module unless coordinating a cross-module change

```bash
git checkout main
git pull origin main
git checkout -b feature/your-module
```

## Development Setup

See [README.md](README.md) for full setup instructions.

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### AI Engine (standalone testing)

```bash
cd ai-engine
pip install -r requirements.txt
python -m pytest ../tests/ai-engine/ -v
```

## Code Standards

### Python (backend, ai-engine, analytics)

- Python 3.11+
- Type hints on public functions
- Pydantic models for request/response validation
- SQLAlchemy ORM for database access
- Format with `ruff format`, lint with `ruff check`

### TypeScript (frontend)

- Strict TypeScript mode
- Functional React components with hooks
- API types mirror `docs/api-contract.md`
- Tailwind CSS for styling — no inline styles unless dynamic

### Commits

Use conventional commit prefixes:

```
feat: add attendance check-in endpoint
fix: prevent duplicate check-in
docs: update API contract for leave module
refactor: extract auth dependency
test: add anomaly detection unit tests
```

### Pull Requests

1. Keep PRs focused on one module/feature
2. Update `docs/api-contract.md` if you change API shapes
3. Do not modify unrelated modules
4. Include a brief test plan in the PR description
5. Request review from at least one other developer

## Module Boundaries

```
frontend  ──HTTP──▶  backend  ──import──▶  ai-engine
                        │                      │
                        └────import────────────┤
                        │                      │
                        └────import──▶  analytics
```

- **Frontend** never calls Gemini or accesses the database directly
- **Backend** is the only HTTP entry point
- **AI Engine** receives structured data from backend — no direct DB credentials in ai-engine config for production
- **Analytics** provides query functions imported by backend routes

## Environment Variables

- Never commit `.env`
- Add new variables to `.env.example` with placeholder values
- Server secrets (`SECRET_KEY`, `GEMINI_API_KEY`, `DATABASE_URL`) stay backend-only
- Frontend only uses `VITE_*` prefixed variables

## AI Ethics Guidelines

When working on AI features:

- Use explainable terms: "Attendance Anomaly", "Workplace Risk Signal", "HR Recommendation"
- Never claim medical/psychological diagnosis or guaranteed resignation
- AI supports decisions — HR makes final calls
- Employee assistant only returns data for the authenticated user

## Questions?

Refer to [docs/git-workflow.md](docs/git-workflow.md) for merge and conflict resolution procedures.
