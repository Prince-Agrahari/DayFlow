-- DayFlow HRM Demo Seed Data
-- Primary seed: python backend/scripts/seed.py (recommended — includes demo patterns)
-- This SQL documents demo credentials and can supplement Docker init.

-- Demo credentials (created by seed.py):
--   admin@dayflow.com / admin123  (ADMIN)
--   jane@dayflow.com / employee123 (EMP001, Engineering)
--   john@dayflow.com / employee123 (EMP003, Engineering — anomalous attendance demo)

-- Demo patterns injected by seed.py:
--   • John Smith: late arrivals, short hours, recent absences (attendance anomaly + risk signal)
--   • Jane Doe: pending leave request (leave conflict demo)
--   • Engineering: overlapping approved leave (team availability conflict)
--   • 20 employees across 5 departments, 60 days attendance, payroll, notifications

-- To seed after schema init:
--   cd backend && python scripts/seed.py
