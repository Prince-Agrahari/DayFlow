-- DayFlow HRM — PostgreSQL Schema
-- Version: 0.1.0
-- Apply: psql -U dayflow -d dayflow_hrm -f database/schema.sql

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- ENUMS
-- =============================================================================

CREATE TYPE user_role AS ENUM ('EMPLOYEE', 'ADMIN');
CREATE TYPE employment_status AS ENUM ('ACTIVE', 'INACTIVE', 'ON_LEAVE', 'TERMINATED');
CREATE TYPE attendance_status AS ENUM ('PRESENT', 'ABSENT', 'HALF_DAY', 'LEAVE');
CREATE TYPE leave_type AS ENUM ('PAID', 'SICK', 'UNPAID');
CREATE TYPE leave_status AS ENUM ('PENDING', 'APPROVED', 'REJECTED');
CREATE TYPE notification_type AS ENUM (
    'LEAVE_SUBMITTED', 'LEAVE_APPROVED', 'LEAVE_REJECTED',
    'ATTENDANCE_REMINDER', 'HR_ALERT', 'AI_ALERT'
);

-- =============================================================================
-- USERS (Authentication)
-- =============================================================================

CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    full_name       VARCHAR(255) NOT NULL,
    role            user_role NOT NULL DEFAULT 'EMPLOYEE',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- =============================================================================
-- EMPLOYEES (Profile)
-- =============================================================================

CREATE TABLE employees (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    employee_id         VARCHAR(20) NOT NULL UNIQUE,
    phone               VARCHAR(20),
    address             TEXT,
    department          VARCHAR(100) NOT NULL,
    designation         VARCHAR(100) NOT NULL,
    joining_date        DATE NOT NULL,
    employment_status   employment_status NOT NULL DEFAULT 'ACTIVE',
    salary              DECIMAL(12, 2) NOT NULL DEFAULT 0,
    profile_picture     VARCHAR(500),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_employees_department ON employees(department);
CREATE INDEX idx_employees_status ON employees(employment_status);
CREATE INDEX idx_employees_employee_id ON employees(employee_id);

-- =============================================================================
-- ATTENDANCE
-- =============================================================================

CREATE TABLE attendance (
    id              SERIAL PRIMARY KEY,
    employee_id     UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    date            DATE NOT NULL,
    check_in_time   TIMESTAMPTZ,
    check_out_time  TIMESTAMPTZ,
    working_hours   DECIMAL(5, 2),
    status          attendance_status NOT NULL DEFAULT 'ABSENT',
    is_late         BOOLEAN NOT NULL DEFAULT FALSE,
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (employee_id, date)
);

CREATE INDEX idx_attendance_employee_date ON attendance(employee_id, date);
CREATE INDEX idx_attendance_date ON attendance(date);
CREATE INDEX idx_attendance_status ON attendance(status);

-- =============================================================================
-- LEAVE REQUESTS
-- =============================================================================

CREATE TABLE leave_requests (
    id              SERIAL PRIMARY KEY,
    employee_id     UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    leave_type      leave_type NOT NULL,
    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,
    reason          TEXT NOT NULL,
    status          leave_status NOT NULL DEFAULT 'PENDING',
    admin_comment   TEXT,
    reviewed_by     UUID REFERENCES users(id),
    reviewed_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_leave_employee ON leave_requests(employee_id);
CREATE INDEX idx_leave_status ON leave_requests(status);
CREATE INDEX idx_leave_dates ON leave_requests(start_date, end_date);

-- =============================================================================
-- LEAVE BALANCE
-- =============================================================================

CREATE TABLE leave_balances (
    id              SERIAL PRIMARY KEY,
    employee_id     UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    leave_type      leave_type NOT NULL,
    total_days      DECIMAL(5, 1) NOT NULL DEFAULT 0,
    used_days       DECIMAL(5, 1) NOT NULL DEFAULT 0,
    year            INTEGER NOT NULL DEFAULT EXTRACT(YEAR FROM NOW()),
    UNIQUE (employee_id, leave_type, year)
);

-- =============================================================================
-- PAYROLL
-- =============================================================================

CREATE TABLE payroll (
    id              SERIAL PRIMARY KEY,
    employee_id     UUID NOT NULL UNIQUE REFERENCES employees(id) ON DELETE CASCADE,
    base_salary     DECIMAL(12, 2) NOT NULL,
    currency        VARCHAR(3) NOT NULL DEFAULT 'USD',
    pay_frequency   VARCHAR(20) NOT NULL DEFAULT 'MONTHLY',
    basic           DECIMAL(12, 2) NOT NULL DEFAULT 0,
    hra             DECIMAL(12, 2) NOT NULL DEFAULT 0,
    allowances      DECIMAL(12, 2) NOT NULL DEFAULT 0,
    deductions      DECIMAL(12, 2) NOT NULL DEFAULT 0,
    net_salary      DECIMAL(12, 2) NOT NULL DEFAULT 0,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- NOTIFICATIONS
-- =============================================================================

CREATE TABLE notifications (
    id              SERIAL PRIMARY KEY,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type            notification_type NOT NULL,
    title           VARCHAR(255) NOT NULL,
    message         TEXT NOT NULL,
    is_read         BOOLEAN NOT NULL DEFAULT FALSE,
    metadata        JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_unread ON notifications(user_id, is_read) WHERE is_read = FALSE;

-- =============================================================================
-- DEPARTMENTS
-- =============================================================================

CREATE TABLE departments (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(100) NOT NULL UNIQUE,
    description     VARCHAR(500),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE employees ADD COLUMN IF NOT EXISTS department_id UUID REFERENCES departments(id);

-- =============================================================================
-- ACTIVITY LOGS
-- =============================================================================

CREATE TYPE activity_action AS ENUM (
    'LOGIN', 'CHECK_IN', 'CHECK_OUT', 'LEAVE_APPLIED', 'LEAVE_APPROVED',
    'LEAVE_REJECTED', 'PAYROLL_UPDATED', 'PROFILE_UPDATED', 'EMPLOYEE_CREATED', 'EMPLOYEE_DELETED'
);

CREATE TABLE activity_logs (
    id              SERIAL PRIMARY KEY,
    user_id         UUID REFERENCES users(id) ON DELETE SET NULL,
    action          activity_action NOT NULL,
    entity_type     VARCHAR(50),
    entity_id       VARCHAR(50),
    description     TEXT NOT NULL,
    metadata        JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_activity_logs_user ON activity_logs(user_id);

-- =============================================================================
-- UPDATED_AT TRIGGER
-- =============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_employees_updated_at
    BEFORE UPDATE ON employees FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_attendance_updated_at
    BEFORE UPDATE ON attendance FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_leave_requests_updated_at
    BEFORE UPDATE ON leave_requests FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
