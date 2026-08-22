import { useEffect, useState } from 'react'
import { AdminLayout, PageHeader } from '../../components/layout/AppLayout'
import { KPICard } from '../../components/ui/Card'
import { DashboardSkeleton } from '../../components/ui/Skeleton'
import {
  AttendanceTrendChart, LeaveTrendChart, DepartmentChart,
  DistributionChart, TeamAvailabilityChart,
} from '../../components/charts/Charts'
import { analyticsService } from '../../services/analyticsService'
import { formatCurrency, formatPercent } from '../../utils/format'
import type { DashboardAnalytics } from '../../types/api'

export default function AdminAnalytics() {
  const [dashboard, setDashboard] = useState<DashboardAnalytics | null>(null)
  const [teamAvail, setTeamAvail] = useState<{ date: string; availability_rate: number }[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([analyticsService.getDashboard(), analyticsService.getTeamAvailability()])
      .then(([d, t]) => { setDashboard(d); setTeamAvail(t) })
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <AdminLayout><DashboardSkeleton /></AdminLayout>
  if (!dashboard) return null

  const riskData = Object.entries(dashboard.risk_distribution).map(([name, value]) => ({ name, value }))
  const anomalyData = Object.entries(dashboard.anomaly_distribution).map(([name, value]) => ({ name, value }))

  return (
    <AdminLayout>
      <PageHeader title="Analytics Dashboard" subtitle="Workforce insights and trends" />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <KPICard label="Total Employees" value={dashboard.total_employees} />
        <KPICard label="Attendance Rate" value={formatPercent(dashboard.attendance_rate)} />
        <KPICard label="Avg Salary" value={formatCurrency(dashboard.payroll_summary.average_salary)} sub={`Total monthly: ${formatCurrency(dashboard.payroll_summary.total_monthly)}`} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <AttendanceTrendChart data={dashboard.monthly_attendance_trend} />
        <LeaveTrendChart data={dashboard.leave_trend} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <DepartmentChart data={dashboard.department_absenteeism} />
        <TeamAvailabilityChart data={teamAvail} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <DistributionChart title="Risk Distribution" data={riskData} />
        <DistributionChart title="Anomaly Distribution" data={anomalyData} />
      </div>
    </AdminLayout>
  )
}
