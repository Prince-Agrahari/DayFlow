# DayFlow Tests

Cross-module and unit tests for DayFlow HRM.

## Structure

```
tests/
├── backend/       # FastAPI route & service tests
├── frontend/      # React component tests (Vitest)
├── ai-engine/     # ML model & Gemini integration tests
├── analytics/     # KPI & priority queue tests
└── integration/   # End-to-end API tests
```

## Running Tests

### Backend

```bash
cd backend
pip install pytest pytest-asyncio httpx
pytest ../tests/backend/ -v
```

### AI Engine

```bash
pip install -r ai-engine/requirements.txt pytest
pytest tests/ai-engine/ -v
```

### Analytics

```bash
pip install -r analytics/requirements.txt pytest
pytest tests/analytics/ -v
```

### Frontend

```bash
cd frontend
npm install -D vitest @testing-library/react
npm test
```

## Test Plan (To Implement)

| Module | Key Tests |
|--------|-----------|
| Auth | Login, signup, JWT validation, role enforcement |
| Attendance | Check-in/out, duplicate prevention, hours calc |
| Leave | Apply, approve, reject, balance deduction |
| AI | Anomaly detection accuracy, risk scoring bounds |
| Analytics | KPI calculations, priority queue ranking |
| Security | Employee data isolation, no cross-user access |
