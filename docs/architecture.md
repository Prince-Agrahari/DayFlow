# DayFlow HRM — System Architecture

## Overview

DayFlow is a monorepo Human Resource Management System with an AI intelligence layer. The architecture follows a **layered, module-boundary** design optimized for parallel development by four developers.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLIENT (Browser)                              │
│                     React SPA — frontend/                               │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │ HTTPS / REST (JWT)
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY LAYER                               │
│                    FastAPI — backend/app/                               │
│   Auth │ RBAC │ Validation │ Business Logic │ Route Handlers            │
└──────┬──────────────────────────┬──────────────────────────┬────────────┘
       │                          │                          │
       ▼                          ▼                          ▼
┌──────────────┐         ┌─────────────────┐        ┌──────────────────┐
│  PostgreSQL  │         │   ai-engine/    │        │   analytics/     │
│  database/   │         │  ML + Gemini    │        │  KPIs, Reports   │
└──────────────┘         └─────────────────┘        └──────────────────┘
```

## Core Principle

```
DATA → INTELLIGENCE → PRIORITY → RECOMMENDATION → HUMAN DECISION
```

AI outputs are **signals and recommendations**, not autonomous employment actions.

---

## Module Boundaries

### `frontend/` — Presentation Layer

**Owner:** `feature/frontend-ui`

| Responsibility | Details |
|----------------|---------|
| UI rendering | Employee & HR dashboards, forms, charts |
| Client routing | React Router with role-based route guards |
| API consumption | Axios client → backend REST only |
| State | Local component state + React Context for auth |

**Must NOT:**
- Store or use Gemini API keys
- Connect to PostgreSQL directly
- Implement business logic that belongs in backend

**Key directories:**
```
frontend/src/
├── api/           # Axios client, typed API calls
├── components/    # Reusable UI (sidebar, cards, tables, modals)
├── pages/         # Route-level pages (employee/, hr/)
├── hooks/         # useAuth, useNotifications, etc.
├── types/         # TypeScript interfaces mirroring API contract
├── layouts/       # EmployeeLayout, HRLayout
└── utils/         # Formatters, constants
```

---

### `backend/` — Application Layer

**Owner:** `feature/backend-hrms`

| Responsibility | Details |
|----------------|---------|
| Authentication | JWT issue/validate, password hashing |
| Authorization | Role-based access (EMPLOYEE, ADMIN) |
| Business logic | Attendance, leave, payroll, notifications |
| Data access | SQLAlchemy ORM → PostgreSQL |
| AI orchestration | Calls ai-engine & analytics modules |

**Must NOT:**
- Expose raw SQL to LLM
- Return another employee's data to non-admin users
- Leak secrets in API responses

**Key directories:**
```
backend/app/
├── main.py        # FastAPI app factory, CORS, middleware
├── config.py      # Settings from environment
├── api/
│   ├── deps.py    # get_db, get_current_user, require_role
│   └── routes/    # auth, employees, attendance, leave, payroll,
│                  # notifications, analytics, ai
├── core/
│   └── security.py # JWT, password hashing
├── models/        # SQLAlchemy ORM models
├── schemas/       # Pydantic request/response schemas
└── services/      # Business logic services
```

---

### `ai-engine/` — Intelligence Layer

**Owner:** `feature/ai-intelligence`

| Responsibility | Details |
|----------------|---------|
| Attendance anomaly detection | Isolation Forest on attendance features |
| Workplace risk signals | Explainable composite scoring |
| Smart leave recommendation | Team availability conflict analysis |
| HR AI Copilot | Gemini with structured context injection |
| Employee AI Assistant | Gemini with user-scoped data only |

**Must NOT:**
- Expose database credentials to frontend
- Generate unrestricted SQL from LLM prompts
- Make medical/psychological claims in outputs

**Key files:**
```
ai-engine/
├── anomaly_detection.py      # Isolation Forest pipeline
├── risk_signals.py           # Workplace risk scoring
├── leave_recommendation.py   # Leave conflict analysis
├── copilot.py                # HR copilot (structured data → Gemini)
├── employee_assistant.py     # Employee-scoped assistant
├── prompts/                  # Controlled prompt templates
└── schemas.py                # Shared AI response types
```

**Integration pattern:**
```python
# backend calls ai-engine with pre-fetched structured data
from ai_engine.anomaly_detection import detect_anomalies

result = detect_anomalies(attendance_records=records)  # list[dict], not raw SQL
```

---

### `analytics/` — Analytics Layer

**Owner:** `feature/analytics-devops`

| Responsibility | Details |
|----------------|---------|
| KPI calculations | Headcount, attendance rate, trends |
| Aggregations | Department absenteeism, risk distribution |
| HR Priority Queue | Ranked attention items from signals |
| Team availability | Department staffing calculations |

**Key files:**
```
analytics/
├── metrics.py           # Core KPI functions
├── trends.py            # Time-series aggregations
├── priority_queue.py    # HR attention ranking
├── team_availability.py # Staffing analysis
├── reports.py           # Report-ready export data
└── __init__.py          # Public API
```

---

### `database/` — Data Layer

**Owner:** `feature/analytics-devops`

| Responsibility | Details |
|----------------|---------|
| Schema definition | `schema.sql` — canonical DDL |
| Seed data | Demo data for hackathon demo |
| Migrations | Alembic (managed from backend/) |

---

## Authentication Flow

```
1. POST /api/auth/login  →  validate credentials  →  issue JWT
2. Client stores token in memory/localStorage
3. Subsequent requests: Authorization: Bearer <token>
4. backend/api/deps.py validates JWT, loads user + role
5. Route handlers enforce role + employee data isolation
```

### Role Matrix

| Resource | EMPLOYEE | ADMIN |
|----------|----------|-------|
| Own profile | Read/Update (limited) | Full CRUD |
| Other profiles | Denied | Full CRUD |
| Own attendance | Read/Check-in/out | Read all |
| Leave requests | Create/Read own | Read/Approve/Reject all |
| Payroll | Read own | Read/Update all |
| Analytics | Denied | Full |
| AI Copilot | Denied | Full |
| AI Assistant | Own data only | N/A |
| Priority Queue | Denied | Full |

---

## AI Feature Architecture

### Feature 1: Attendance Anomaly Detection

```
Historical attendance (backend fetches)
    → ai-engine/anomaly_detection.py
    → Isolation Forest on features:
        check_in_hour, check_out_hour, working_hours,
        late_flag, absence_flag, day_of_week
    → Output: { employee_id, anomaly, score, severity, reason }
```

### Feature 2: Workplace Risk Signal

```
Composite signals (attendance trend, late rate, absence trend,
                   leave pattern, overtime, workload indicators)
    → ai-engine/risk_signals.py
    → Weighted explainable scoring
    → Output: { risk_score, risk_level, reasons[], recommendations[] }
    → Levels: LOW | MEDIUM | HIGH
```

### Feature 3: Smart Leave Recommendation

```
Team availability + department staffing + existing leave +
employee balance + requested dates
    → ai-engine/leave_recommendation.py
    → Output: { conflict_level, recommendation, reasons[] }
    → Levels: LOW | MEDIUM | HIGH
```

### Feature 4: HR AI Copilot

```
HR question + pre-aggregated structured context (backend builds)
    → ai-engine/copilot.py
    → Gemini with system prompt enforcing:
        - No SQL generation
        - Cite only provided data
        - Use HR-safe terminology
    → Output: natural language answer + structured citations
```

### Feature 5: Employee AI Assistant

```
Employee question + user-scoped data snapshot (backend builds)
    → ai-engine/employee_assistant.py
    → Gemini with strict data boundary prompt
    → Output: answer from authorized data only
```

---

## HR Priority Queue

Generated by `analytics/priority_queue.py` combining:

| Priority | Source |
|----------|--------|
| HIGH | Attendance anomaly (severity ≥ threshold) |
| HIGH | Workplace risk signal (HIGH level) |
| MEDIUM | Leave conflict (MEDIUM/HIGH) |
| MEDIUM | Low team availability |
| LOW | Pending administrative actions |

Each item: `{ priority, title, description, employee, reason, recommended_action }`

---

## Data Flow: Employee 360 View

```
GET /api/hr/employees/{id}/360

Backend orchestrates:
  1. Employee profile (models)
  2. Attendance trend (analytics/trends.py)
  3. Leave trend (analytics/trends.py)
  4. Anomalies (ai-engine/anomaly_detection.py)
  5. Risk signals (ai-engine/risk_signals.py)
  6. Recommendations (aggregated)

Returns unified Employee360Response
```

---

## Security Architecture

| Control | Implementation |
|---------|----------------|
| Authentication | JWT (HS256), bcrypt passwords |
| Authorization | FastAPI dependencies + role decorators |
| CORS | Whitelist frontend origin via env |
| Input validation | Pydantic schemas on all endpoints |
| Data isolation | employee_id filter on employee routes |
| Secrets | Environment variables, never in code |
| AI safety | Controlled prompts, no SQL generation |

---

## Deployment Architecture

```
                    ┌─────────────┐
                    │   Nginx     │  (optional reverse proxy)
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
       ┌─────────────┐           ┌─────────────┐
       │  Frontend   │           │   Backend   │
       │  (static)   │           │  (FastAPI)  │
       └─────────────┘           └──────┬──────┘
                                        │
                                 ┌──────┴──────┐
                                 ▼             ▼
                          ┌──────────┐  ┌──────────┐
                          │ Postgres │  │  Gemini  │
                          └──────────┘  └──────────┘
```

See `deployment/` and root `docker-compose.yml` for local orchestration.

---

## Technology Decisions

| Decision | Rationale |
|----------|-----------|
| Monorepo | Single clone, shared API contract, hackathon speed |
| FastAPI | Async, auto OpenAPI docs, Pydantic integration |
| PostgreSQL | Relational HR data, ACID, JSON support |
| Isolation Forest | Unsupervised anomaly detection, explainable features |
| Gemini | Hackathon-friendly LLM with structured output support |
| JWT | Stateless auth, frontend-friendly |
| Vite | Fast dev server, modern React tooling |

---

## Future Considerations (Post-Hackathon)

- Alembic migrations for schema versioning
- Redis for session/cache
- WebSocket for real-time notifications
- CI/CD pipeline (GitHub Actions)
- Rate limiting on AI endpoints
