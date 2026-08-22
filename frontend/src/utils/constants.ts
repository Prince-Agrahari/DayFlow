export const TOKEN_KEY = 'dayflow_access_token'
export const USER_KEY = 'dayflow_user'

export const DEPARTMENTS = ['Engineering', 'HR', 'Finance', 'Marketing', 'Design'] as const

export const LEAVE_TYPES = ['PAID', 'SICK', 'UNPAID'] as const

export const STATUS_COLORS: Record<string, string> = {
  PRESENT: 'bg-emerald-50 text-emerald-700 ring-emerald-600/20',
  ABSENT: 'bg-red-50 text-red-700 ring-red-600/20',
  HALF_DAY: 'bg-amber-50 text-amber-700 ring-amber-600/20',
  LEAVE: 'bg-blue-50 text-blue-700 ring-blue-600/20',
  PENDING: 'bg-amber-50 text-amber-700 ring-amber-600/20',
  APPROVED: 'bg-emerald-50 text-emerald-700 ring-emerald-600/20',
  REJECTED: 'bg-red-50 text-red-700 ring-red-600/20',
  HIGH: 'bg-red-50 text-red-700 ring-red-600/20',
  MEDIUM: 'bg-amber-50 text-amber-700 ring-amber-600/20',
  LOW: 'bg-emerald-50 text-emerald-700 ring-emerald-600/20',
  ACTIVE: 'bg-emerald-50 text-emerald-700 ring-emerald-600/20',
}
