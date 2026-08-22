import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Users, UserCheck, CalendarDays, AlertTriangle, Shield, TrendingUp } from 'lucide-react'
import { AdminLayout, PageHeader } from '../../components/layout/AppLayout'
import { KPICard, Card, CardHeader } from '../../components/ui/Card'
import { PriorityBadge } from '../../components/ui/Badge'
import { DashboardSkeleton } from '../../components/ui/Skeleton'
import { ErrorState } from '../../components/ui/EmptyState'
import { TeamAvailabilityChart } from '../../components/charts/Charts'
import { analyticsService } from '../../services/analyticsService'
import { formatPercent } from '../../utils/format'
import type { DashboardAnalytics, PriorityQueueItem } from '../../types/api'

export default function AdminDashboard() {
  const [dashboard, setDashboard] = useState<DashboardAnalytics | null>(null)
  const [priority, setPriority] = useState<PriorityQueueItem[]>([])
  const [teamAvail, setTeamAvail] = useState<{ date: string; availability_rate: number }[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      analyticsService.getDashboard(),
      analyticsService.getPriorityQueue(),
      analyticsService.getTeamAvailability(),
    ]).then(([d, p, t]) => {
      setDashboard(d)
      setPriority(p)
      setTeamAvail(t)
    }).finally(() => setLoading(false))
  }, [])

  if (loading) return <AdminLayout><DashboardSkeleton /></AdminLayout>
  if (!dashboard) return <AdminLayout><ErrorState /></AdminLayout>

  return (
    <AdminLayout>
      <PageHeader title="HR Command Center" subtitle="Real-time overview of your workforce intelligence" />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <KPICard label="Total Employees" value={dashboard.total_employees} icon={Users} />
        <KPICard label="Present Today" value={dashboard.present_today} sub={`${dashboard.absent_today} absent`} icon={UserCheck} trend="up" />
        <KPICard label="On Leave" value={dashboard.on_leave_today} icon={CalendarDays} />
        <KPICard label="Attendance Rate" value={formatPercent(dashboard.attendance_rate)} icon={TrendingUp} trend="up" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <KPICard label="Pending Leaves" value={dashboard.pending_leaves} icon={CalendarDays} />
        <KPICard label="Attendance Anomalies" value={dashboard.anomaly_distribution.HIGH + dashboard.anomaly_distribution.MEDIUM} icon={AlertTriangle} />
        <KPICard label="Risk Signals (High)" value={dashboard.risk_distribution.HIGH} icon={Shield} />
      </div>

      <Card className="mb-8">
        <CardHeader title="What Needs Your Attention Today" subtitle="Prioritized HR action items based on AI intelligence" />
        <div className="space-y-3">
          {priority.map((item, i) => (
            <div key={i} className="flex items-start gap-4 p-4 rounded-lg border border-gray-200 hover:border-primary-200 transition-colors">
              <PriorityBadge priority={item.priority} />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <h4 className="font-semibold text-gray-900">{item.title}</h4>
                  <Link to={`/admin/employees/${item.employee_id}`} className="text-sm text-primary-600 hover:underline">{item.employee_name}</Link>
                </div>
                <p className="text-sm text-gray-600 mt-1">{item.description}</p>
                <p className="text-xs text-gray-500 mt-2"><span className="font-medium">Reason:</span> {item.reason}</p>
                <p className="text-xs text-primary-700 mt-1"><span className="font-medium">Action:</span> {item.recommended_action}</p>
              </div>
            </div>
          ))}
        </div>
      </Card>

      <TeamAvailabilityChart data={teamAvail} />
    </AdminLayout>
  )
}
