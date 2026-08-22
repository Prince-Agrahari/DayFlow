import { useEffect, useState } from 'react'
import { LogIn, LogOut } from 'lucide-react'
import { EmployeeLayout, PageHeader } from '../../components/layout/AppLayout'
import { Card, CardHeader } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { TableSkeleton } from '../../components/ui/Skeleton'
import { ErrorState } from '../../components/ui/EmptyState'
import { SimpleBarChart } from '../../components/charts/Charts'
import { attendanceService } from '../../services/attendanceService'
import { useToast } from '../../context/ToastContext'
import { formatDateTime } from '../../utils/format'
import type { AttendancePeriodResponse } from '../../types/api'

type Period = 'daily' | 'weekly' | 'monthly'

export default function EmployeeAttendance() {
  const [period, setPeriod] = useState<Period>('weekly')
  const [data, setData] = useState<AttendancePeriodResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const { showToast } = useToast()

  const load = async () => {
    setLoading(true)
    try {
      setData(await attendanceService.getMyAttendance(period))
    } catch {
      showToast('Failed to load attendance', 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [period])

  const chartData = data?.records.slice(0, 7).reverse().map((r) => ({
    date: r.date.slice(5),
    hours: r.working_hours ?? 0,
  })) ?? []

  return (
    <EmployeeLayout>
      <PageHeader title="Attendance" subtitle="Track your check-ins, working hours, and attendance history" />

      <div className="flex flex-wrap gap-3 mb-6">
        <Button variant={period === 'daily' ? 'primary' : 'secondary'} size="sm" onClick={() => setPeriod('daily')}>Daily</Button>
        <Button variant={period === 'weekly' ? 'primary' : 'secondary'} size="sm" onClick={() => setPeriod('weekly')}>Weekly</Button>
        <Button variant={period === 'monthly' ? 'primary' : 'secondary'} size="sm" onClick={() => setPeriod('monthly')}>Monthly</Button>
        <div className="flex-1" />
        <Button size="sm" loading={actionLoading} onClick={async () => { setActionLoading(true); try { await attendanceService.checkIn(); showToast('Checked in', 'success'); load() } finally { setActionLoading(false) } }}>
          <LogIn className="h-4 w-4" /> Check In
        </Button>
        <Button size="sm" variant="secondary" loading={actionLoading} onClick={async () => { setActionLoading(true); try { await attendanceService.checkOut(); showToast('Checked out', 'success'); load() } finally { setActionLoading(false) } }}>
          <LogOut className="h-4 w-4" /> Check Out
        </Button>
      </div>

      {data && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {[
            { label: 'Present', value: data.summary.present },
            { label: 'Absent', value: data.summary.absent },
            { label: 'Late', value: data.summary.late_count },
            { label: 'Total Hours', value: data.summary.total_working_hours.toFixed(1) },
          ].map((s) => (
            <Card key={s.label} padding>
              <p className="text-sm text-gray-500">{s.label}</p>
              <p className="text-2xl font-bold text-gray-900">{s.value}</p>
            </Card>
          ))}
        </div>
      )}

      {loading ? <TableSkeleton /> : !data ? <ErrorState onRetry={load} /> : (
        <>
          <SimpleBarChart title="Working Hours" data={chartData} dataKey="hours" xKey="date" height={220} />
          <Card className="mt-6">
            <CardHeader title="Attendance Records" />
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200 text-left text-gray-500">
                    <th className="pb-3 font-medium">Date</th>
                    <th className="pb-3 font-medium">Check In</th>
                    <th className="pb-3 font-medium">Check Out</th>
                    <th className="pb-3 font-medium">Hours</th>
                    <th className="pb-3 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {data.records.map((r) => (
                    <tr key={r.id} className="border-b border-gray-100">
                      <td className="py-3">{r.date}</td>
                      <td className="py-3">{r.check_in_time ? formatDateTime(r.check_in_time) : '—'}</td>
                      <td className="py-3">{r.check_out_time ? formatDateTime(r.check_out_time) : '—'}</td>
                      <td className="py-3">{r.working_hours?.toFixed(1) ?? '—'}</td>
                      <td className="py-3"><Badge status={r.status} />{r.is_late && <span className="ml-2 text-xs text-amber-600">Late</span>}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </>
      )}
    </EmployeeLayout>
  )
}
