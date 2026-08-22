# DayFlow HRM — API Contract

> **Version:** 0.1.0 (Architecture Phase)  
> **Base URL:** `http://localhost:8000/api`  
> **Auth:** Bearer JWT in `Authorization` header

This document is the **single source of truth** for REST API shapes. All modules must conform to these contracts. Update this file when endpoints change.

---

## Conventions

- All timestamps: ISO 8601 UTC (`2026-08-22T09:30:00Z`)
- All dates: ISO 8601 date (`2026-08-22`)
- Pagination: `?page=1&page_size=20` → `{ items, total, page, page_size }`
- Errors: `{ "detail": "message" }` or `{ "detail": [{ "loc", "msg", "type" }] }`
- IDs: UUID strings for users/employees; integer IDs for attendance/leave records

---

## Enums

```typescript
enum UserRole {
  EMPLOYEE = "EMPLOYEE",
  ADMIN = "ADMIN"
}

enum EmploymentStatus {
  ACTIVE = "ACTIVE",
  INACTIVE = "INACTIVE",
  ON_LEAVE = "ON_LEAVE",
  TERMINATED = "TERMINATED"
}

enum AttendanceStatus {
  PRESENT = "PRESENT",
  ABSENT = "ABSENT",
  HALF_DAY = "HALF_DAY",
  LEAVE = "LEAVE"
}

enum LeaveType {
  PAID = "PAID",
  SICK = "SICK",
  UNPAID = "UNPAID"
}

enum LeaveStatus {
  PENDING = "PENDING",
  APPROVED = "APPROVED",
  REJECTED = "REJECTED"
}

enum NotificationType {
  LEAVE_SUBMITTED = "LEAVE_SUBMITTED",
  LEAVE_APPROVED = "LEAVE_APPROVED",
  LEAVE_REJECTED = "LEAVE_REJECTED",
  ATTENDANCE_REMINDER = "ATTENDANCE_REMINDER",
  HR_ALERT = "HR_ALERT",
  AI_ALERT = "AI_ALERT"
}

enum PriorityLevel {
  HIGH = "HIGH",
  MEDIUM = "MEDIUM",
  LOW = "LOW"
}

enum RiskLevel {
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH"
}

enum ConflictLevel {
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH"
}

enum AnomalySeverity {
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH"
}
```

---

## Authentication

### POST `/auth/signup`

Register a new user (admin-only in production; open for demo seed).

**Request:**
```json
{
  "email": "user@company.com",
  "password": "securePassword123",
  "full_name": "Jane Doe",
  "role": "EMPLOYEE"
}
```

**Response `201`:**
```json
{
  "id": "uuid",
  "email": "user@company.com",
  "full_name": "Jane Doe",
  "role": "EMPLOYEE",
  "created_at": "2026-08-22T09:00:00Z"
}
```

---

### POST `/auth/login`

**Request:**
```json
{
  "email": "admin@dayflow.com",
  "password": "admin123"
}
```

**Response `200`:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "admin@dayflow.com",
    "full_name": "Admin User",
    "role": "ADMIN",
    "employee_id": "EMP001"
  }
}
```

---

### GET `/auth/me`

**Auth:** Required  
**Response `200`:** Same user object as login response.

---

## Employees

### GET `/employees`

**Auth:** ADMIN  
**Query:** `?department=Engineering&status=ACTIVE&search=jane&page=1&page_size=20`

**Response `200`:**
```json
{
  "items": [
    {
      "id": "uuid",
      "employee_id": "EMP001",
      "full_name": "Jane Doe",
      "email": "jane@company.com",
      "phone": "+1-555-0100",
      "address": "123 Main St",
      "department": "Engineering",
      "designation": "Software Engineer",
      "joining_date": "2024-01-15",
      "employment_status": "ACTIVE",
      "salary": 85000.00,
      "profile_picture": "/uploads/emp001.jpg",
      "role": "EMPLOYEE"
    }
  ],
  "total": 20,
  "page": 1,
  "page_size": 20
}
```

---

### GET `/employees/{id}`

**Auth:** ADMIN or own employee record  
**Response `200`:** Single employee object.

---

### PUT `/employees/{id}`

**Auth:** ADMIN (full update) or EMPLOYEE (limited fields: phone, address, profile_picture)

**Request (employee self-update):**
```json
{
  "phone": "+1-555-0199",
  "address": "456 Oak Ave",
  "profile_picture": "/uploads/new.jpg"
}
```

---

### POST `/employees`

**Auth:** ADMIN  
**Request:** Full employee object (creates user account + employee profile).

---

## Attendance

### POST `/attendance/check-in`

**Auth:** EMPLOYEE  
**Request:**
```json
{
  "notes": "Working from office"
}
```

**Response `201`:**
```json
{
  "id": 1,
  "employee_id": "EMP001",
  "date": "2026-08-22",
  "check_in_time": "2026-08-22T09:05:00Z",
  "check_out_time": null,
  "working_hours": null,
  "status": "PRESENT",
  "is_late": true
}
```

**Errors:**
- `409` — Already checked in today

---

### POST `/attendance/check-out`

**Auth:** EMPLOYEE  
**Response `200`:** Updated attendance record with `check_out_time` and `working_hours`.

**Errors:**
- `400` — No check-in found for today

---

### GET `/attendance/me`

**Auth:** EMPLOYEE  
**Query:** `?period=daily|weekly|monthly&date=2026-08-22`

**Response `200`:**
```json
{
  "period": "weekly",
  "start_date": "2026-08-18",
  "end_date": "2026-08-22",
  "records": [ /* attendance objects */ ],
  "summary": {
    "total_days": 5,
    "present": 4,
    "absent": 0,
    "half_day": 0,
    "leave": 1,
    "total_working_hours": 36.5,
    "late_count": 1
  }
}
```

---

### GET `/attendance`

**Auth:** ADMIN  
**Query:** `?employee_id=EMP001&date=2026-08-22&department=Engineering&page=1`

**Response `200`:** Paginated attendance records.

---

## Leave

### POST `/leave`

**Auth:** EMPLOYEE  
**Request:**
```json
{
  "leave_type": "PAID",
  "start_date": "2026-09-01",
  "end_date": "2026-09-03",
  "reason": "Family vacation"
}
```

**Response `201`:**
```json
{
  "id": 1,
  "employee_id": "EMP001",
  "leave_type": "PAID",
  "start_date": "2026-09-01",
  "end_date": "2026-09-03",
  "reason": "Family vacation",
  "status": "PENDING",
  "admin_comment": null,
  "created_at": "2026-08-22T10:00:00Z"
}
```

---

### GET `/leave/me`

**Auth:** EMPLOYEE  
**Response `200`:** List of own leave requests.

---

### GET `/leave`

**Auth:** ADMIN  
**Query:** `?status=PENDING&department=Engineering`

**Response `200`:** Paginated leave requests.

---

### PUT `/leave/{id}/approve`

**Auth:** ADMIN  
**Request:**
```json
{
  "comment": "Approved. Enjoy your vacation."
}
```

---

### PUT `/leave/{id}/reject`

**Auth:** ADMIN  
**Request:**
```json
{
  "comment": "Critical project deadline during requested dates."
}
```

---

## Payroll

### GET `/payroll/me`

**Auth:** EMPLOYEE  
**Response `200`:**
```json
{
  "employee_id": "EMP001",
  "base_salary": 85000.00,
  "currency": "USD",
  "pay_frequency": "MONTHLY",
  "structure": {
    "basic": 60000.00,
    "hra": 15000.00,
    "allowances": 10000.00,
    "deductions": 5000.00
  },
  "net_salary": 80000.00
}
```

---

### GET `/payroll`

**Auth:** ADMIN  
**Response `200`:** Paginated payroll records for all employees.

---

### PUT `/payroll/{employee_id}`

**Auth:** ADMIN  
**Request:** Updated salary structure fields.

---

## Notifications

### GET `/notifications`

**Auth:** Required (own notifications)  
**Query:** `?unread_only=true&page=1`

**Response `200`:**
```json
{
  "items": [
    {
      "id": 1,
      "type": "LEAVE_APPROVED",
      "title": "Leave Approved",
      "message": "Your leave request for Sep 1-3 has been approved.",
      "is_read": false,
      "created_at": "2026-08-22T11:00:00Z",
      "metadata": { "leave_id": 1 }
    }
  ],
  "total": 5,
  "unread_count": 2
}
```

---

### PUT `/notifications/{id}/read`

**Auth:** Required  
**Response `200`:** `{ "is_read": true }`

---

### PUT `/notifications/read-all`

**Auth:** Required  
**Response `200`:** `{ "updated_count": 5 }`

---

## Analytics (Admin)

### GET `/analytics/dashboard`

**Auth:** ADMIN  
**Response `200`:**
```json
{
  "total_employees": 20,
  "attendance_rate": 0.92,
  "present_today": 17,
  "absent_today": 1,
  "on_leave_today": 2,
  "department_absenteeism": [
    { "department": "Engineering", "rate": 0.05 },
    { "department": "Marketing", "rate": 0.12 }
  ],
  "monthly_attendance_trend": [
    { "month": "2026-06", "rate": 0.90 },
    { "month": "2026-07", "rate": 0.93 }
  ],
  "leave_trend": [
    { "month": "2026-06", "count": 8 },
    { "month": "2026-07", "count": 12 }
  ],
  "payroll_summary": {
    "total_monthly": 1700000.00,
    "average_salary": 85000.00
  },
  "risk_distribution": { "LOW": 14, "MEDIUM": 4, "HIGH": 2 },
  "anomaly_distribution": { "LOW": 16, "MEDIUM": 3, "HIGH": 1 }
}
```

---

### GET `/analytics/team-availability`

**Auth:** ADMIN  
**Query:** `?department=Engineering&start_date=2026-09-01&end_date=2026-09-07`

**Response `200`:**
```json
{
  "department": "Engineering",
  "start_date": "2026-09-01",
  "end_date": "2026-09-07",
  "total_employees": 8,
  "daily_availability": [
    {
      "date": "2026-09-01",
      "available": 6,
      "on_leave": 1,
      "absent": 1,
      "availability_rate": 0.75
    }
  ]
}
```

---

## AI Endpoints

### GET `/ai/anomalies`

**Auth:** ADMIN  
**Query:** `?department=Engineering&severity=HIGH`

**Response `200`:**
```json
{
  "items": [
    {
      "employee_id": "EMP007",
      "employee_name": "John Smith",
      "anomaly": true,
      "score": -0.42,
      "severity": "HIGH",
      "reason": "Check-in time shifted 2+ hours earlier than 30-day baseline; 3 unplanned absences in last 14 days"
    }
  ]
}
```

---

### GET `/ai/risk-signals`

**Auth:** ADMIN  
**Query:** `?employee_id=EMP007&risk_level=HIGH`

**Response `200`:**
```json
{
  "items": [
    {
      "employee_id": "EMP007",
      "employee_name": "John Smith",
      "risk_score": 0.78,
      "risk_level": "HIGH",
      "reasons": [
        "Absence frequency increased 40% over last 30 days",
        "Late arrival rate: 60% (baseline: 15%)",
        "Overtime hours decreased 50%"
      ],
      "recommendations": [
        "Schedule a check-in conversation with HR",
        "Review current workload allocation",
        "Monitor attendance pattern over next 2 weeks"
      ]
    }
  ]
}
```

---

### POST `/ai/leave-recommendation`

**Auth:** ADMIN or EMPLOYEE (own request preview)  
**Request:**
```json
{
  "employee_id": "EMP001",
  "start_date": "2026-09-01",
  "end_date": "2026-09-03",
  "leave_type": "PAID"
}
```

**Response `200`:**
```json
{
  "conflict_level": "MEDIUM",
  "recommendation": "Consider approving with team coverage plan",
  "reasons": [
    "2 of 8 Engineering team members already on leave during this period",
    "Team availability drops to 62% on Sep 2",
    "Employee has sufficient paid leave balance (12 days remaining)"
  ]
}
```

---

### POST `/ai/copilot`

**Auth:** ADMIN  
**Request:**
```json
{
  "question": "Who needs attention today?"
}
```

**Response `200`:**
```json
{
  "answer": "Based on current HR data, 3 employees require attention today...",
  "sources": [
    { "type": "priority_queue", "count": 3 },
    { "type": "pending_leaves", "count": 5 },
    { "type": "anomalies", "count": 2 }
  ],
  "structured_data": {
    "priority_items": [ /* subset of priority queue */ ],
    "pending_leaves": [ /* pending leave summaries */ ]
  }
}
```

---

### POST `/ai/assistant`

**Auth:** EMPLOYEE  
**Request:**
```json
{
  "question": "How many leaves do I have?"
}
```

**Response `200`:**
```json
{
  "answer": "You have 12 paid leave days remaining, 5 sick leave days, and 2 pending requests.",
  "data_scope": "employee_self"
}
```

---

## HR Priority Queue

### GET `/hr/priority-queue`

**Auth:** ADMIN  
**Response `200`:**
```json
{
  "generated_at": "2026-08-22T08:00:00Z",
  "items": [
    {
      "priority": "HIGH",
      "title": "Attendance Anomaly Detected",
      "description": "Unusual check-in pattern detected for John Smith",
      "employee_id": "EMP007",
      "employee_name": "John Smith",
      "reason": "Check-in time anomaly with increased absence frequency",
      "recommended_action": "Review attendance record and schedule HR check-in"
    },
    {
      "priority": "MEDIUM",
      "title": "Leave Conflict",
      "description": "Multiple leave requests overlap in Engineering",
      "employee_id": "EMP003",
      "employee_name": "Alice Chen",
      "reason": "Team availability drops below 60% during requested dates",
      "recommended_action": "Review team calendar before approving"
    }
  ]
}
```

---

## Employee 360

### GET `/hr/employees/{id}/360`

**Auth:** ADMIN  
**Response `200`:**
```json
{
  "profile": { /* full employee object */ },
  "attendance_trend": [
    { "week": "2026-W33", "present_days": 4, "absent_days": 1, "avg_hours": 8.2 }
  ],
  "leave_trend": [
    { "month": "2026-07", "days_taken": 3, "type_breakdown": { "PAID": 2, "SICK": 1 } }
  ],
  "working_hours_summary": {
    "avg_daily_hours": 8.1,
    "total_overtime_hours": 12.5,
    "late_arrival_rate": 0.15
  },
  "anomalies": [ /* anomaly objects for this employee */ ],
  "risk_signals": { /* risk signal object for this employee */ },
  "recommendations": [
    "Monitor attendance pattern — late arrivals increasing",
    "Consider workload review — overtime decreased 50%"
  ]
}
```

---

## Health Check

### GET `/health`

**Auth:** None  
**Response `200`:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "database": "connected"
}
```

---

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Validation error / bad request |
| 401 | Missing or invalid JWT |
| 403 | Insufficient role permissions |
| 404 | Resource not found |
| 409 | Conflict (duplicate check-in, etc.) |
| 422 | Pydantic validation failure |
| 500 | Internal server error |

---

## Module Ownership Reference

| Endpoint Group | Primary Owner |
|----------------|---------------|
| `/auth/*` | backend-hrms |
| `/employees/*` | backend-hrms |
| `/attendance/*` | backend-hrms |
| `/leave/*` | backend-hrms |
| `/payroll/*` | backend-hrms |
| `/notifications/*` | backend-hrms |
| `/analytics/*` | analytics-devops |
| `/ai/*` | ai-intelligence |
| `/hr/*` | backend-hrms + analytics-devops |

Cross-module endpoints require coordination via PR review.
