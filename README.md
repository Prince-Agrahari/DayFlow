# DayFlow — Intelligent HR Command Center

> **DATA → INTELLIGENCE → PRIORITY → RECOMMENDATION → HUMAN DECISION**

DayFlow is a production-quality Human Resource Management System that transforms traditional HR data into actionable HR intelligence. AI supports HR decisions—it never makes irreversible employment decisions.

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React, TypeScript, Vite, Tailwind CSS, React Router, Axios, Recharts, Lucide React |
| **Backend** | Python, FastAPI, SQLAlchemy, PostgreSQL, Pydantic, JWT |
| **AI** | Google Gemini API |
| **ML** | Pandas, NumPy, Scikit-learn, Isolation Forest |
| **DevOps** | Git, GitHub, Docker |

## Project Structure

```
DayFlow HRM/
├── frontend/          # React SPA — UI for Employee & HR dashboards
├── backend/           # FastAPI REST API — auth, business logic, data
├── ai-engine/         # ML models & Gemini integrations (server-side only)
├── analytics/         # Aggregations, KPIs, reporting queries
├── database/          # Schema, migrations, seed data
├── docs/              # Architecture, API contracts, git workflow
├── tests/             # Cross-module integration & unit tests
├── deployment/        # Docker, compose, deployment configs
├── docker-compose.yml # Local development orchestration
└── .env.example       # Environment template (copy to .env)
```

## Quick Start

### Prerequisites

- Node.js 20+
- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose (optional)

### 1. Clone & Configure

```bash
cp .env.example .env
# Edit .env with your values (especially SECRET_KEY and GEMINI_API_KEY)
```

### 2. Database

```bash
# Using Docker
docker compose up -d postgres

# Or apply schema manually
psql -U dayflow -d dayflow_hrm -f database/schema.sql
```

### 3. Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

### 5. Full Stack (Docker)

```bash
docker compose up --build
```

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## User Roles

| Role | Access |
|------|--------|
| **Employee** | Dashboard, profile, attendance, leave, payroll, notifications, AI assistant |
| **Admin/HR** | HR command center, employee 360, analytics, AI copilot, priority queue |

## Feature Modules & Ownership

| Branch | Owner Scope |
|--------|-------------|
| `feature/frontend-ui` | React components, pages, routing, styling |
| `feature/backend-hrms` | FastAPI routes, models, auth, CRUD |
| `feature/ai-intelligence` | ai-engine/, Gemini, ML models |
| `feature/analytics-devops` | analytics/, deployment/, database seeds |

See [docs/git-workflow.md](docs/git-workflow.md) for branch conventions.

## Documentation

- [Architecture](docs/architecture.md) — system design & module boundaries
- [API Contract](docs/api-contract.md) — REST endpoints & schemas
- [Git Workflow](docs/git-workflow.md) — branching & collaboration
- [Contributing](CONTRIBUTING.md) — setup & code standards

## Security

- JWT authentication with role-based authorization
- Passwords hashed with bcrypt
- Gemini API keys server-side only
- Employee data isolation enforced at API layer
- Never commit `.env` files

## License

Hackathon project — internal use.
