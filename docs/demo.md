# DayFlow Demo Guide

## Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin (HR) | `admin@dayflow.com` | `admin123` |
| Employee | `jane@dayflow.com` | `employee123` |
| Employee (anomaly demo) | `john@dayflow.com` | `employee123` |

## Seed Demo Data

```bash
cd backend
python scripts/seed.py
```

This creates 1 admin + 20 employees with:

- 60 days attendance history
- Payroll records
- Leave balances and requests
- Notifications

### Built-in Demo Patterns

| Pattern | Employee | What to Show |
|---------|----------|--------------|
| Attendance anomaly | John Smith (EMP003) | Late arrivals, short hours, recent absences |
| Workplace risk signal | John Smith | Elevated risk from attendance metrics |
| Leave conflict | Jane Doe (EMP001) | Pending leave with team overlap |
| Team availability | Engineering dept | Overlapping approved leave reduces capacity |
| Priority queue | Admin dashboard | Ranked HIGH/MEDIUM/LOW attention items |

## Admin Demo Flow

1. Login as `admin@dayflow.com`
2. **Dashboard** — KPIs, priority queue ("What needs your attention today")
3. **Analytics** — attendance trends, department absenteeism, team availability heatmap
4. **AI Copilot** — ask "Who needs attention today?" or "What should I prioritize?"
5. **Leave Management** — review pending requests with smart leave recommendations

## Employee Demo Flow

1. Login as `jane@dayflow.com`
2. **Dashboard** — personal attendance and leave balance
3. **AI Assistant** — ask "How many leaves do I have?" or "Show my attendance"
4. **Apply Leave** — submit request and preview AI recommendation

## Mock vs Live Mode

Frontend defaults to mock data (`VITE_USE_MOCK=true`). For full stack demo:

```env
VITE_USE_MOCK=false
VITE_API_BASE_URL=http://localhost:8000/api
```

## API Endpoints to Demo

| Feature | Endpoint |
|---------|----------|
| Dashboard KPIs | `GET /api/analytics/dashboard` |
| Priority queue | `GET /api/hr/priority-queue` |
| Team availability | `GET /api/analytics/team-availability?department=Engineering` |
| Attendance anomalies | `GET /api/ai/anomalies` |
| HR Copilot | `POST /api/ai/copilot` |
