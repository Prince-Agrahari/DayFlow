import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Clock, CalendarDays, DollarSign, Bell, LogIn, LogOut, TrendingUp } from 'lucide-react'
import { EmployeeLayout, PageHeader } from '../../components/layout/AppLayout'
import { KPICard, Card, CardHeader } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { DashboardSkeleton } from '../../components/ui/Skeleton'
import { ErrorState } from '../../components/ui/EmptyState'
import { attendanceService } from '../../services/attendanceService'
import { leaveService } from '../../services/leaveService'
import { payrollService } from '../../services/payrollService'
import { notificationService } from '../../services/notificationService'
import { useToast } from '../../context/ToastContext'
import { formatCurrency, formatDateTime, formatPercent } from '../../utils/format'
import type { AttendanceRecord, LeaveBalance, Notification, PayrollRecord } from '../../types/api'

export default function EmployeeDashboard() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [today, setToday] = useState<AttendanceRecord | null>(null)
  const [summary, setSummary] = useState<{ rate: number; present: number; total: number } | null>(null)
  const [balances, setBalances] = useState<LeaveBalance[]>([])
  const [payroll, setPayroll] = useState<PayrollRecord | null>(null)
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [checkedIn, setCheckedIn] = useState(false)
  const [actionLoading, setActionLoading] = useState(false)
  const { showToast } = useToast()

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const [attendance, leaves, pay, notifs] = await Promise.all([
        attendanceService.getMyAttendance('monthly'),
        leaveService.getBalances(),
        payrollService.getMyPayroll(),
        notificationService.getAll(),
      ])
      const todayRecord = attendance.records[0] ?? null
      setToday(todayRecord)
      setCheckedIn(!!todayRecord?.check_in_time && !todayRecord?.check_out_time)
      setSummary({
        rate: attendance.summary.total_days ? attendance.summary.present / attendance.summary.total_days : 0,
        present: attendance.summary.present,
        total: attendance.summary.total_days,
      })
      setBalances(leaves)
      setPayroll(pay)
      setNotifications(notifs.items.slice(0, 4))
    } catch {
      setError('Failed to load dashboard')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleCheckIn = async () => {
    setActionLoading(true)
    try {
      const record = await attendanceService.checkIn()
      setToday(record)
      setCheckedIn(true)
      showToast('Checked in successfully', 'success')
    } catch {
      showToast('Check-in failed', 'error')
    } finally {
      setActionLoading(false)
    }
  }

  const handleCheckOut = async () => {
    setActionLoading(true)
    try {
      const record = await attendanceService.checkOut()
      setToday(record)
      setCheckedIn(false)
      showToast('Checked out successfully', 'success')
    } catch {
      showToast('Check-out failed', 'error')
    } finally {
      setActionLoading(false)
    }
  }

  if (loading) return <EmployeeLayout><DashboardSkeleton /></EmployeeLayout>
  if (error) return <EmployeeLayout><ErrorState onRetry={load} /></EmployeeLayout>

  const paidBalance = balances.find((b) => b.leave_type === 'PAID')

  return (
    <EmployeeLayout>
      <PageHeader title="Dashboard" subtitle={`Welcome back! Here's your overview for today.`} />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <KPICard label="Attendance Rate" value={formatPercent(summary?.rate ?? 0)} sub={`${summary?.present}/${summary?.total} days present`} icon={TrendingUp} trend="up" />
        <KPICard label="Paid Leave Balance" value={`${paidBalance?.remaining_days ?? 0} days`} sub={`${paidBalance?.used_days ?? 0} used of ${paidBalance?.total_days ?? 0}`} icon={CalendarDays} />
        <KPICard label="Net Salary" value={formatCurrency(payroll?.net_salary ?? 0)} sub="Monthly" icon={DollarSign} />
        <KPICard label="Notifications" value={notifications.filter((n) => !n.is_read).length} sub="Unread" icon={Bell} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <Card className="lg:col-span-1">
          <CardHeader title="Today's Attendance" />
          <div className="space-y-4">
            {today ? (
              <>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Status</span>
                  <Badge status={today.status} />
                </div>
                {today.check_in_time && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">Check-in</span>
                    <span className="text-sm font-medium">{formatDateTime(today.check_in_time)}</span>
                  </div>
                )}
                {today.check_out_time && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">Check-out</span>
                    <span className="text-sm font-medium">{formatDateTime(today.check_out_time)}</span>
                  </div>
                )}
                {today.working_hours && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">Hours</span>
                    <span className="text-sm font-medium">{today.working_hours.toFixed(1)} hrs</span>
                  </div>
                )}
              </>
            ) : (
              <p className="text-sm text-gray-500">No attendance record for today.</p>
            )}
            <div className="flex gap-3 pt-2">
              {!checkedIn ? (
                <Button onClick={handleCheckIn} loading={actionLoading} className="flex-1"><LogIn className="h-4 w-4" /> Check In</Button>
              ) : (
                <Button onClick={handleCheckOut} loading={actionLoading} variant="secondary" className="flex-1"><LogOut className="h-4 w-4" /> Check Out</Button>
              )}
            </div>
          </div>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader title="Quick Actions" />
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[
              { to: '/employee/attendance', label: 'Attendance', icon: Clock },
              { to: '/employee/leave', label: 'Apply Leave', icon: CalendarDays },
              { to: '/employee/payroll', label: 'Payroll', icon: DollarSign },
              { to: '/employee/assistant', label: 'AI Assistant', icon: Bell },
            ].map(({ to, label, icon: Icon }) => (
              <Link key={to} to={to} className="flex flex-col items-center gap-2 p-4 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors">
                <Icon className="h-6 w-6 text-primary-600" />
                <span className="text-sm font-medium text-gray-700">{label}</span>
              </Link>
            ))}
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader title="Recent Notifications" action={<Link to="/employee/notifications" className="text-sm text-primary-600 hover:underline">View all</Link>} />
          {notifications.length === 0 ? (
            <p className="text-sm text-gray-500">No notifications</p>
          ) : (
            <div className="space-y-3">
              {notifications.map((n) => (
                <div key={n.id} className="flex items-start gap-3 p-3 rounded-lg bg-gray-50">
                  {!n.is_read && <span className="h-2 w-2 rounded-full bg-primary-600 mt-2 shrink-0" />}
                  <div className={n.is_read ? 'ml-5' : ''}>
                    <p className="text-sm font-medium text-gray-900">{n.title}</p>
                    <p className="text-xs text-gray-500 mt-0.5">{n.message}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        <Card>
          <CardHeader title="Payroll Summary" />
          {payroll && (
            <div className="space-y-3">
              <div className="flex justify-between"><span className="text-sm text-gray-500">Base Salary</span><span className="font-medium">{formatCurrency(payroll.base_salary)}</span></div>
              <div className="flex justify-between"><span className="text-sm text-gray-500">Basic</span><span>{formatCurrency(payroll.structure.basic)}</span></div>
              <div className="flex justify-between"><span className="text-sm text-gray-500">HRA</span><span>{formatCurrency(payroll.structure.hra)}</span></div>
              <div className="flex justify-between"><span className="text-sm text-gray-500">Allowances</span><span>{formatCurrency(payroll.structure.allowances)}</span></div>
              <div className="flex justify-between border-t pt-3"><span className="font-medium">Net Salary</span><span className="font-bold text-primary-600">{formatCurrency(payroll.net_salary)}</span></div>
            </div>
          )}
        </Card>
      </div>
    </EmployeeLayout>
  )
}
