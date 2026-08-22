# DayFlow Database

Canonical PostgreSQL schema and seed data for the DayFlow HRM hackathon project.

## Files

| File | Purpose |
|------|---------|
| `schema.sql` | DDL — tables, indexes, triggers, enums |
| `seed/` | Demo data scripts (1 admin, 20 employees) |

## Apply Schema

```bash
# Create database
createdb -U postgres dayflow_hrm

# Create user
psql -U postgres -c "CREATE USER dayflow WITH PASSWORD 'dayflow_secret';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE dayflow_hrm TO dayflow;"

# Apply schema
psql -U dayflow -d dayflow_hrm -f database/schema.sql
```

## Demo Data (Pending)

Seed script will create:

- **1 Admin** — admin@dayflow.com
- **20 Employees** across departments:
  - Engineering (6)
  - HR (2)
  - Finance (4)
  - Marketing (4)
  - Design (4)
- **90 days** of attendance history with realistic variation
- Leave records (pending, approved, rejected)
- Payroll structures
- Notifications

Implementation: `feature/analytics-devops` branch → `database/seed/demo_data.sql`

## Entity Relationship

```
users (1) ──── (1) employees
                    │
        ┌───────────┼───────────┬──────────────┐
        ▼           ▼           ▼              ▼
   attendance  leave_requests  payroll   leave_balances

users (1) ──── (*) notifications
```

## Departments

- Engineering
- HR
- Finance
- Marketing
- Design
