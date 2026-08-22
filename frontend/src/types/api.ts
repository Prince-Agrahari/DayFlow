/**
 * TypeScript types mirroring docs/api-contract.md
 * Implementation on feature/frontend-ui branch.
 */

export type UserRole = 'EMPLOYEE' | 'ADMIN'

export type EmploymentStatus = 'ACTIVE' | 'INACTIVE' | 'ON_LEAVE' | 'TERMINATED'

export type AttendanceStatus = 'PRESENT' | 'ABSENT' | 'HALF_DAY' | 'LEAVE'

export type LeaveType = 'PAID' | 'SICK' | 'UNPAID'

export type LeaveStatus = 'PENDING' | 'APPROVED' | 'REJECTED'

export type PriorityLevel = 'HIGH' | 'MEDIUM' | 'LOW'

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH'

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
