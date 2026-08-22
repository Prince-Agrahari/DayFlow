import type {
  AnomalyItem, AssistantResponse, AttendanceRecord, AttendancePeriodResponse,
  CopilotResponse, DashboardAnalytics, Employee, Employee360, LeaveBalance,
  LeaveRecommendation, LeaveRequest, Notification, PayrollHistoryItem,
  PayrollRecord, PriorityQueueItem, RiskSignalItem, TeamAvailabilityDay, User,
} from '../types/api'

export const MOCK_USERS: Record<string, User & { password: string }> = {
  admin: {
    id: 'u-admin', email: 'admin@dayflow.com', password: 'admin123',
    full_name: 'Sarah Mitchell', role: 'ADMIN', employee_id: 'EMP000',
  },
  employee: {
    id: 'u-001', email: 'jane@dayflow.com', password: 'employee123',
    full_name: 'Jane Doe', role: 'EMPLOYEE', employee_id: 'EMP001',
  },
}

export const MOCK_EMPLOYEES: Employee[] = [
  { id: 'e-001', employee_id: 'EMP001', full_name: 'Jane Doe', email: 'jane@dayflow.com', phone: '+1-555-0101', address: '123 Main St, Austin, TX', department: 'Engineering', designation: 'Senior Software Engineer', joining_date: '2022-03-15', employment_status: 'ACTIVE', salary: 95000, role: 'EMPLOYEE' },
  { id: 'e-002', employee_id: 'EMP002', full_name: 'Michael Chen', email: 'michael@dayflow.com', phone: '+1-555-0102', department: 'Engineering', designation: 'Tech Lead', joining_date: '2021-06-01', employment_status: 'ACTIVE', salary: 115000, role: 'EMPLOYEE' },
  { id: 'e-003', employee_id: 'EMP003', full_name: 'Alice Johnson', email: 'alice@dayflow.com', department: 'HR', designation: 'HR Specialist', joining_date: '2023-01-10', employment_status: 'ACTIVE', salary: 72000, role: 'EMPLOYEE' },
  { id: 'e-004', employee_id: 'EMP004', full_name: 'Robert Williams', email: 'robert@dayflow.com', department: 'Finance', designation: 'Financial Analyst', joining_date: '2020-09-20', employment_status: 'ACTIVE', salary: 88000, role: 'EMPLOYEE' },
  { id: 'e-005', employee_id: 'EMP005', full_name: 'Emily Davis', email: 'emily@dayflow.com', department: 'Marketing', designation: 'Marketing Manager', joining_date: '2022-11-05', employment_status: 'ACTIVE', salary: 92000, role: 'EMPLOYEE' },
  { id: 'e-006', employee_id: 'EMP006', full_name: 'James Wilson', email: 'james@dayflow.com', department: 'Design', designation: 'UX Designer', joining_date: '2023-04-18', employment_status: 'ACTIVE', salary: 85000, role: 'EMPLOYEE' },
  { id: 'e-007', employee_id: 'EMP007', full_name: 'John Smith', email: 'john@dayflow.com', department: 'Engineering', designation: 'Backend Developer', joining_date: '2022-08-22', employment_status: 'ACTIVE', salary: 90000, role: 'EMPLOYEE' },
  { id: 'e-008', employee_id: 'EMP008', full_name: 'Lisa Brown', email: 'lisa@dayflow.com', department: 'Finance', designation: 'Accountant', joining_date: '2021-02-14', employment_status: 'ON_LEAVE', salary: 78000, role: 'EMPLOYEE' },
]

const today = new Date()
const fmt = (d: Date) => d.toISOString().split('T')[0]

function genAttendance(employeeId: string, days: number): AttendanceRecord[] {
  const records: AttendanceRecord[] = []
  for (let i = 0; i < days; i++) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    const isWeekend = d.getDay() === 0 || d.getDay() === 6
    if (isWeekend) continue
    const absent = Math.random() < 0.08
    const late = !absent && Math.random() < 0.15
    const checkIn = new Date(d)
    checkIn.setHours(late ? 9 + Math.floor(Math.random() * 2) : 8 + Math.floor(Math.random() * 30) / 60, late ? 15 + Math.floor(Math.random() * 30) : Math.floor(Math.random() * 30))
    const checkOut = new Date(checkIn)
    checkOut.setHours(checkIn.getHours() + 8 + Math.floor(Math.random() * 2))
    records.push({
      id: i + 1, employee_id: employeeId, date: fmt(d),
      check_in_time: absent ? null : checkIn.toISOString(),
      check_out_time: absent ? null : checkOut.toISOString(),
      working_hours: absent ? null : 7.5 + Math.random() * 1.5,
      status: absent ? 'ABSENT' : 'PRESENT', is_late: late,
    })
  }
  return records
}

export const MOCK_ATTENDANCE: Record<string, AttendanceRecord[]> = {
  EMP001: genAttendance('EMP001', 30),
}

export function getMockAttendancePeriod(employeeId: string, period: string): AttendancePeriodResponse {
  const all = MOCK_ATTENDANCE[employeeId] ?? genAttendance(employeeId, 30)
  const days = period === 'daily' ? 1 : period === 'weekly' ? 7 : 30
  const records = all.slice(0, days)
  const present = records.filter((r) => r.status === 'PRESENT').length
  return {
    period, start_date: records[records.length - 1]?.date ?? fmt(today),
    end_date: records[0]?.date ?? fmt(today), records,
    summary: {
      total_days: records.length, present, absent: records.filter((r) => r.status === 'ABSENT').length,
      half_day: 0, leave: records.filter((r) => r.status === 'LEAVE').length,
      total_working_hours: records.reduce((s, r) => s + (r.working_hours ?? 0), 0),
      late_count: records.filter((r) => r.is_late).length,
    },
  }
}

export const MOCK_LEAVE_REQUESTS: LeaveRequest[] = [
  { id: 1, employee_id: 'EMP001', employee_name: 'Jane Doe', leave_type: 'PAID', start_date: '2026-09-01', end_date: '2026-09-03', reason: 'Family vacation', status: 'PENDING', admin_comment: null, created_at: '2026-08-20T10:00:00Z' },
  { id: 2, employee_id: 'EMP007', employee_name: 'John Smith', leave_type: 'SICK', start_date: '2026-08-25', end_date: '2026-08-26', reason: 'Medical appointment', status: 'PENDING', admin_comment: null, created_at: '2026-08-21T09:00:00Z' },
  { id: 3, employee_id: 'EMP005', employee_name: 'Emily Davis', leave_type: 'PAID', start_date: '2026-08-10', end_date: '2026-08-12', reason: 'Personal travel', status: 'APPROVED', admin_comment: 'Approved. Enjoy!', created_at: '2026-08-01T14:00:00Z' },
  { id: 4, employee_id: 'EMP003', employee_name: 'Alice Johnson', leave_type: 'UNPAID', start_date: '2026-07-15', end_date: '2026-07-16', reason: 'Personal matter', status: 'REJECTED', admin_comment: 'Critical HR audit period.', created_at: '2026-07-10T11:00:00Z' },
]

export const MOCK_LEAVE_BALANCES: LeaveBalance[] = [
  { leave_type: 'PAID', total_days: 20, used_days: 8, remaining_days: 12 },
  { leave_type: 'SICK', total_days: 10, used_days: 3, remaining_days: 7 },
  { leave_type: 'UNPAID', total_days: 5, used_days: 0, remaining_days: 5 },
]

export const MOCK_PAYROLL: PayrollRecord = {
  employee_id: 'EMP001', base_salary: 95000, currency: 'USD', pay_frequency: 'MONTHLY',
  structure: { basic: 65000, hra: 18000, allowances: 12000, deductions: 5500 },
  net_salary: 89500,
}

export const MOCK_PAYROLL_HISTORY: PayrollHistoryItem[] = [
  { id: 1, month: '2026-07', net_salary: 89500, status: 'PAID' },
  { id: 2, month: '2026-06', net_salary: 89500, status: 'PAID' },
  { id: 3, month: '2026-05', net_salary: 89000, status: 'PAID' },
]

export const MOCK_ALL_PAYROLL: PayrollRecord[] = MOCK_EMPLOYEES.map((e) => ({
  employee_id: e.employee_id, employee_name: e.full_name, base_salary: e.salary, currency: 'USD',
  pay_frequency: 'MONTHLY',
  structure: { basic: e.salary * 0.65, hra: e.salary * 0.18, allowances: e.salary * 0.12, deductions: e.salary * 0.05 },
  net_salary: e.salary * 0.94,
}))

export const MOCK_NOTIFICATIONS: Notification[] = [
  { id: 1, type: 'LEAVE_SUBMITTED', title: 'Leave Request Submitted', message: 'Your leave request for Sep 1-3 is pending approval.', is_read: false, created_at: '2026-08-20T10:05:00Z', metadata: { leave_id: 1 } },
  { id: 2, type: 'ATTENDANCE_REMINDER', title: 'Check-in Reminder', message: 'You haven\'t checked in yet today.', is_read: false, created_at: '2026-08-22T09:30:00Z' },
  { id: 3, type: 'LEAVE_APPROVED', title: 'Leave Approved', message: 'Your leave for Aug 10-12 was approved.', is_read: true, created_at: '2026-08-02T09:00:00Z' },
  { id: 4, type: 'AI_ALERT', title: 'Attendance Pattern Notice', message: 'Your attendance rate this month is 94%. Keep it up!', is_read: true, created_at: '2026-08-15T08:00:00Z' },
]

export const MOCK_DASHBOARD: DashboardAnalytics = {
  total_employees: 20, attendance_rate: 0.92, present_today: 17, absent_today: 1,
  on_leave_today: 2, pending_leaves: 5,
  department_absenteeism: [
    { department: 'Engineering', rate: 0.05 }, { department: 'Marketing', rate: 0.12 },
    { department: 'Finance', rate: 0.08 }, { department: 'HR', rate: 0.03 },
    { department: 'Design', rate: 0.07 },
  ],
  monthly_attendance_trend: [
    { month: '2026-03', rate: 0.89 }, { month: '2026-04', rate: 0.91 },
    { month: '2026-05', rate: 0.90 }, { month: '2026-06', rate: 0.93 },
    { month: '2026-07', rate: 0.91 }, { month: '2026-08', rate: 0.92 },
  ],
  leave_trend: [
    { month: '2026-03', count: 6 }, { month: '2026-04', count: 9 },
    { month: '2026-05', count: 7 }, { month: '2026-06', count: 11 },
    { month: '2026-07', count: 8 }, { month: '2026-08', count: 12 },
  ],
  payroll_summary: { total_monthly: 1700000, average_salary: 85000 },
  risk_distribution: { LOW: 14, MEDIUM: 4, HIGH: 2 },
  anomaly_distribution: { LOW: 16, MEDIUM: 3, HIGH: 1 },
}

export const MOCK_ANOMALIES: AnomalyItem[] = [
  { employee_id: 'EMP007', employee_name: 'John Smith', anomaly: true, score: -0.42, severity: 'HIGH', reason: 'Check-in time shifted 2+ hours earlier than baseline; 3 unplanned absences in 14 days' },
  { employee_id: 'EMP004', employee_name: 'Robert Williams', anomaly: true, score: -0.28, severity: 'MEDIUM', reason: 'Working hours dropped 30% below 30-day average' },
  { employee_id: 'EMP006', employee_name: 'James Wilson', anomaly: true, score: -0.15, severity: 'LOW', reason: 'Late arrival frequency increased to 40%' },
]

export const MOCK_RISK_SIGNALS: RiskSignalItem[] = [
  { employee_id: 'EMP007', employee_name: 'John Smith', risk_score: 0.78, risk_level: 'HIGH', reasons: ['Absence frequency up 40% in 30 days', 'Late arrival rate: 60%', 'Overtime decreased 50%'], recommendations: ['Schedule HR check-in', 'Review workload allocation', 'Monitor over next 2 weeks'] },
  { employee_id: 'EMP004', employee_name: 'Robert Williams', risk_score: 0.55, risk_level: 'MEDIUM', reasons: ['Declining attendance trend', 'Increased half-day requests'], recommendations: ['Review team dynamics', 'Check project assignments'] },
]

export const MOCK_PRIORITY_QUEUE: PriorityQueueItem[] = [
  { priority: 'HIGH', title: 'Attendance Anomaly Detected', description: 'Unusual check-in pattern for John Smith', employee_id: 'EMP007', employee_name: 'John Smith', reason: 'Check-in anomaly with increased absence frequency', recommended_action: 'Review attendance and schedule HR check-in' },
  { priority: 'HIGH', title: 'Workplace Risk Signal', description: 'Elevated risk indicators for John Smith', employee_id: 'EMP007', employee_name: 'John Smith', reason: 'Multiple risk factors above threshold', recommended_action: 'Schedule supportive conversation' },
  { priority: 'MEDIUM', title: 'Leave Conflict', description: 'Overlapping leave in Engineering', employee_id: 'EMP001', employee_name: 'Jane Doe', reason: 'Team availability drops to 62%', recommended_action: 'Review team calendar before approving' },
  { priority: 'MEDIUM', title: 'Low Team Availability', description: 'Marketing team at 55% capacity next week', employee_id: 'EMP005', employee_name: 'Emily Davis', reason: '3 members on leave simultaneously', recommended_action: 'Coordinate coverage plan' },
  { priority: 'LOW', title: 'Pending Administrative Action', description: '2 leave requests awaiting review', employee_id: 'EMP003', employee_name: 'Alice Johnson', reason: 'Requests pending > 3 days', recommended_action: 'Review and respond to pending requests' },
]

export const MOCK_TEAM_AVAILABILITY: TeamAvailabilityDay[] = Array.from({ length: 7 }, (_, i) => {
  const d = new Date(today)
  d.setDate(d.getDate() + i)
  const avail = 6 + Math.floor(Math.random() * 2)
  return { date: fmt(d), available: avail, on_leave: 8 - avail - 1, absent: 1, availability_rate: avail / 8 }
})

export const MOCK_LEAVE_RECOMMENDATION: LeaveRecommendation = {
  conflict_level: 'MEDIUM',
  recommendation: 'Consider approving with team coverage plan',
  reasons: ['2 of 8 Engineering members on leave during this period', 'Team availability drops to 62% on Sep 2', 'Employee has 12 paid leave days remaining'],
}

export const MOCK_COPILOT_RESPONSES: Record<string, CopilotResponse> = {
  'who needs attention': { answer: 'Based on current HR data, 3 employees require attention today:\n\n1. **John Smith (EMP007)** — HIGH priority attendance anomaly and workplace risk signal. Recommend scheduling an HR check-in.\n\n2. **Jane Doe (EMP001)** — MEDIUM priority leave conflict. Engineering team availability drops to 62% during requested dates.\n\n3. **Marketing Team** — MEDIUM priority low availability next week with 3 members on leave.', sources: [{ type: 'priority_queue', count: 3 }, { type: 'anomalies', count: 2 }] },
  'unusual attendance': { answer: 'Employees with attendance anomalies detected:\n\n• **John Smith** — HIGH severity: shifted check-in times, 3 unplanned absences\n• **Robert Williams** — MEDIUM: working hours 30% below average\n• **James Wilson** — LOW: increased late arrivals (40%)', sources: [{ type: 'anomalies', count: 3 }] },
  'absenteeism': { answer: 'Department absenteeism ranking:\n\n1. **Marketing** — 12% (highest)\n2. **Finance** — 8%\n3. **Design** — 7%\n4. **Engineering** — 5%\n5. **HR** — 3% (lowest)', sources: [{ type: 'analytics', count: 5 }] },
  'prioritize': { answer: 'Recommended priorities for today:\n\n1. Review John Smith\'s attendance anomaly (HIGH)\n2. Address workplace risk signal for EMP007 (HIGH)\n3. Process 5 pending leave requests (MEDIUM)\n4. Plan Marketing team coverage for next week (MEDIUM)\n5. Follow up on administrative backlog (LOW)', sources: [{ type: 'priority_queue', count: 5 }] },
}

export const MOCK_ASSISTANT_RESPONSES: Record<string, AssistantResponse> = {
  'leaves': { answer: 'You have **12 paid leave days** remaining, **7 sick leave days**, and **5 unpaid leave days**. You have 1 pending request (Sep 1-3, Family vacation).', data_scope: 'employee_self' },
  'attendance': { answer: 'Your attendance this month:\n• Present: 18 days\n• Absent: 1 day\n• Late arrivals: 2\n• Average working hours: 8.2 hrs/day\n• Attendance rate: 94%', data_scope: 'employee_self' },
  'leave status': { answer: 'Your leave requests:\n• **Sep 1-3** (PAID) — PENDING\n• **Aug 10-12** (PAID) — APPROVED\n• **Jul 15-16** (UNPAID) — REJECTED', data_scope: 'employee_self' },
  'salary': { answer: 'Your current compensation:\n• Base salary: $95,000/year\n• Net monthly: $89,500\n• Structure: Basic $65,000 | HRA $18,000 | Allowances $12,000 | Deductions $5,500', data_scope: 'employee_self' },
}

export function getMockEmployee360(employeeId: string): Employee360 | null {
  const profile = MOCK_EMPLOYEES.find((e) => e.employee_id === employeeId || e.id === employeeId)
  if (!profile) return null
  return {
    profile,
    attendance_trend: [
      { week: '2026-W30', present_days: 4, absent_days: 1, avg_hours: 8.1 },
      { week: '2026-W31', present_days: 5, absent_days: 0, avg_hours: 8.4 },
      { week: '2026-W32', present_days: 3, absent_days: 2, avg_hours: 7.6 },
      { week: '2026-W33', present_days: 4, absent_days: 0, avg_hours: 8.2 },
    ],
    leave_trend: [
      { month: '2026-06', days_taken: 2, type_breakdown: { PAID: 2 } },
      { month: '2026-07', days_taken: 3, type_breakdown: { PAID: 2, SICK: 1 } },
      { month: '2026-08', days_taken: 1, type_breakdown: { PAID: 1 } },
    ],
    working_hours_summary: { avg_daily_hours: 8.1, total_overtime_hours: 12.5, late_arrival_rate: 0.15 },
    anomalies: MOCK_ANOMALIES.filter((a) => a.employee_id === profile.employee_id),
    risk_signals: MOCK_RISK_SIGNALS.find((r) => r.employee_id === profile.employee_id) ?? null,
    recommendations: profile.employee_id === 'EMP007'
      ? ['Monitor attendance pattern — late arrivals increasing', 'Consider workload review — overtime decreased 50%']
      : ['Maintain current performance trajectory', 'Consider leadership development opportunities'],
  }
}
