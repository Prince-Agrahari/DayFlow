export type UserRole = 'EMPLOYEE' | 'ADMIN'
export type EmploymentStatus = 'ACTIVE' | 'INACTIVE' | 'ON_LEAVE' | 'TERMINATED'
export type AttendanceStatus = 'PRESENT' | 'ABSENT' | 'HALF_DAY' | 'LEAVE'
export type LeaveType = 'PAID' | 'SICK' | 'UNPAID'
export type LeaveStatus = 'PENDING' | 'APPROVED' | 'REJECTED'
export type PriorityLevel = 'HIGH' | 'MEDIUM' | 'LOW'
export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH'
export type ConflictLevel = 'LOW' | 'MEDIUM' | 'HIGH'
export type AnomalySeverity = 'LOW' | 'MEDIUM' | 'HIGH'
export type NotificationType =
  | 'LEAVE_SUBMITTED'
  | 'LEAVE_APPROVED'
  | 'LEAVE_REJECTED'
  | 'ATTENDANCE_REMINDER'
  | 'HR_ALERT'
  | 'AI_ALERT'

export interface User {
  id: string
  email: string
  full_name: string
  role: UserRole
  employee_id?: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface SignupRequest {
  email: string
  password: string
  full_name: string
  role?: UserRole
}

export interface Employee {
  id: string
  employee_id: string
  full_name: string
  email: string
  phone?: string
  address?: string
  department: string
  designation: string
  joining_date: string
  employment_status: EmploymentStatus
  salary: number
  profile_picture?: string
  role: UserRole
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export interface AttendanceRecord {
  id: number
  employee_id: string
  date: string
  check_in_time: string | null
  check_out_time: string | null
  working_hours: number | null
  status: AttendanceStatus
  is_late: boolean
  notes?: string
}

export interface AttendanceSummary {
  total_days: number
  present: number
  absent: number
  half_day: number
  leave: number
  total_working_hours: number
  late_count: number
}

export interface AttendancePeriodResponse {
  period: string
  start_date: string
  end_date: string
  records: AttendanceRecord[]
  summary: AttendanceSummary
}

export interface LeaveRequest {
  id: number
  employee_id: string
  employee_name?: string
  leave_type: LeaveType
  start_date: string
  end_date: string
  reason: string
  status: LeaveStatus
  admin_comment: string | null
  created_at: string
}

export interface LeaveBalance {
  leave_type: LeaveType
  total_days: number
  used_days: number
  remaining_days: number
}

export interface PayrollRecord {
  employee_id: string
  employee_name?: string
  base_salary: number
  currency: string
  pay_frequency: string
  structure: {
    basic: number
    hra: number
    allowances: number
    deductions: number
  }
  net_salary: number
}

export interface PayrollHistoryItem {
  id: number
  month: string
  net_salary: number
  status: 'PAID' | 'PENDING'
}

export interface Notification {
  id: number
  type: NotificationType
  title: string
  message: string
  is_read: boolean
  created_at: string
  metadata?: Record<string, unknown>
}

export interface AnomalyItem {
  employee_id: string
  employee_name: string
  anomaly: boolean
  score: number
  severity: AnomalySeverity
  reason: string
}

export interface RiskSignalItem {
  employee_id: string
  employee_name: string
  risk_score: number
  risk_level: RiskLevel
  reasons: string[]
  recommendations: string[]
}

export interface PriorityQueueItem {
  priority: PriorityLevel
  title: string
  description: string
  employee_id: string
  employee_name: string
  reason: string
  recommended_action: string
}

export interface DashboardAnalytics {
  total_employees: number
  attendance_rate: number
  present_today: number
  absent_today: number
  on_leave_today: number
  pending_leaves: number
  department_absenteeism: { department: string; rate: number }[]
  monthly_attendance_trend: { month: string; rate: number }[]
  leave_trend: { month: string; count: number }[]
  payroll_summary: { total_monthly: number; average_salary: number }
  risk_distribution: Record<RiskLevel, number>
  anomaly_distribution: Record<AnomalySeverity, number>
}

export interface TeamAvailabilityDay {
  date: string
  available: number
  on_leave: number
  absent: number
  availability_rate: number
}

export interface LeaveRecommendation {
  conflict_level: ConflictLevel
  recommendation: string
  reasons: string[]
}

export interface CopilotResponse {
  answer: string
  sources: { type: string; count: number }[]
}

export interface AssistantResponse {
  answer: string
  data_scope: string
}

export interface Employee360 {
  profile: Employee
  attendance_trend: { week: string; present_days: number; absent_days: number; avg_hours: number }[]
  leave_trend: { month: string; days_taken: number; type_breakdown: Record<string, number> }[]
  working_hours_summary: {
    avg_daily_hours: number
    total_overtime_hours: number
    late_arrival_rate: number
  }
  anomalies: AnomalyItem[]
  risk_signals: RiskSignalItem | null
  recommendations: string[]
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}
