import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, AlertTriangle, Shield } from 'lucide-react'
import { AdminLayout } from '../../components/layout/AppLayout'
import { Card, CardHeader, KPICard } from '../../components/ui/Card'
import { Badge, PriorityBadge } from '../../components/ui/Badge'
import { CardSkeleton } from '../../components/ui/Skeleton'
import { ErrorState } from '../../components/ui/EmptyState'
import { WorkingHoursChart, SimpleBarChart } from '../../components/charts/Charts'
import { employeeService } from '../../services/employeeService'
import { formatCurrency, formatDate, formatPercent, getInitials } from '../../utils/format'
import type { Employee360 } from '../../types/api'

export default function Employee360Page() {
  const { id } = useParams<{ id: string }>()
  const [data, setData] = useState<Employee360 | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    employeeService.get360(id)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <AdminLayout><CardSkeleton /></AdminLayout>
  if (!data) return <AdminLayout><ErrorState title="Employee not found" /></AdminLayout>

  const { profile } = data
  const leaveChartData = data.leave_trend.map((l) => ({ month: l.month.slice(5), days: l.days_taken }))

  return (
    <AdminLayout>
      <Link to="/admin/employees" className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700 mb-4">
        <ArrowLeft className="h-4 w-4" /> Back to employees
      </Link>

      <div className="flex items-start gap-6 mb-8">
        <div className="h-20 w-20 rounded-full bg-primary-100 flex items-center justify-center text-2xl font-bold text-primary-700">
          {getInitials(profile.full_name)}
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{profile.full_name}</h1>
          <p className="text-gray-500">{profile.designation} · {profile.department}</p>
          <div className="flex gap-2 mt-2">
            <Badge status={profile.employment_status} />
            <span className="text-sm text-gray-400">{profile.employee_id}</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <KPICard label="Avg Daily Hours" value={`${data.working_hours_summary.avg_daily_hours}h`} />
        <KPICard label="Overtime (30d)" value={`${data.working_hours_summary.total_overtime_hours}h`} />
        <KPICard label="Late Arrival Rate" value={formatPercent(data.working_hours_summary.late_arrival_rate)} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <Card>
          <CardHeader title="Profile & Job Information" />
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div><p className="text-gray-500">Email</p><p className="font-medium">{profile.email}</p></div>
            <div><p className="text-gray-500">Phone</p><p className="font-medium">{profile.phone ?? '—'}</p></div>
            <div><p className="text-gray-500">Department</p><p className="font-medium">{profile.department}</p></div>
            <div><p className="text-gray-500">Joining Date</p><p className="font-medium">{formatDate(profile.joining_date)}</p></div>
            <div><p className="text-gray-500">Salary</p><p className="font-medium">{formatCurrency(profile.salary)}</p></div>
            <div><p className="text-gray-500">Address</p><p className="font-medium">{profile.address ?? '—'}</p></div>
          </div>
        </Card>

        <WorkingHoursChart title="Attendance Trend (Weekly)" data={data.attendance_trend.map((t) => ({ week: t.week.slice(5), avg_hours: t.avg_hours }))} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <SimpleBarChart title="Leave Trend" data={leaveChartData} dataKey="days" xKey="month" color="#059669" />

        <Card>
          <CardHeader title="HR Recommendations" />
          <ul className="space-y-3">
            {data.recommendations.map((r, i) => (
              <li key={i} className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg text-sm text-blue-900">
                <Shield className="h-4 w-4 mt-0.5 shrink-0" />
                {r}
              </li>
            ))}
          </ul>
        </Card>
      </div>

      {data.anomalies.length > 0 && (
        <Card className="mb-6">
          <CardHeader title="Attendance Anomalies" />
          <div className="space-y-3">
            {data.anomalies.map((a, i) => (
              <div key={i} className="flex items-start gap-3 p-3 border border-amber-200 bg-amber-50 rounded-lg">
                <AlertTriangle className="h-5 w-5 text-amber-600 shrink-0" />
                <div>
                  <div className="flex items-center gap-2"><PriorityBadge priority={a.severity} /><span className="text-sm font-medium">Score: {a.score.toFixed(2)}</span></div>
                  <p className="text-sm text-gray-700 mt-1">{a.reason}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {data.risk_signals && (
        <Card>
          <CardHeader title="Workplace Risk Signal" />
          <div className="flex items-center gap-3 mb-4">
            <PriorityBadge priority={data.risk_signals.risk_level} />
            <span className="text-sm font-medium">Risk Score: {(data.risk_signals.risk_score * 100).toFixed(0)}%</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <p className="text-sm font-medium text-gray-700 mb-2">Reasons</p>
              <ul className="space-y-1">{data.risk_signals.reasons.map((r, i) => <li key={i} className="text-sm text-gray-600">• {r}</li>)}</ul>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700 mb-2">Recommendations</p>
              <ul className="space-y-1">{data.risk_signals.recommendations.map((r, i) => <li key={i} className="text-sm text-primary-700">• {r}</li>)}</ul>
            </div>
          </div>
        </Card>
      )}
    </AdminLayout>
  )
}
