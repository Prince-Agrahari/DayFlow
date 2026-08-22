import { useEffect, useState } from 'react'
import { AdminLayout, PageHeader } from '../../components/layout/AppLayout'
import { Card, CardHeader } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'
import { SearchInput } from '../../components/ui/SearchInput'
import { TableSkeleton } from '../../components/ui/Skeleton'
import { attendanceService } from '../../services/attendanceService'
import { formatDateTime } from '../../utils/format'
import type { AttendanceRecord } from '../../types/api'

export default function AdminAttendance() {
  const [records, setRecords] = useState<AttendanceRecord[]>([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    attendanceService.getAll().then((res) => setRecords(res.items)).finally(() => setLoading(false))
  }, [])

  const filtered = records.filter((r) => !search || r.employee_id.toLowerCase().includes(search.toLowerCase()))

  return (
    <AdminLayout>
      <PageHeader title="Attendance Management" subtitle="Monitor attendance across all employees" />
      <SearchInput value={search} onChange={setSearch} placeholder="Filter by employee ID..." className="mb-6 max-w-xs" />

      {loading ? <TableSkeleton /> : (
        <Card>
          <CardHeader title="Attendance Records" subtitle={`${filtered.length} records`} />
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 text-left text-gray-500">
                  <th className="pb-3 font-medium">Employee</th>
                  <th className="pb-3 font-medium">Date</th>
                  <th className="pb-3 font-medium">Check In</th>
                  <th className="pb-3 font-medium">Check Out</th>
                  <th className="pb-3 font-medium">Hours</th>
                  <th className="pb-3 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((r) => (
                  <tr key={`${r.employee_id}-${r.date}`} className="border-b border-gray-100">
                    <td className="py-3 font-medium">{r.employee_id}</td>
                    <td className="py-3">{r.date}</td>
                    <td className="py-3">{r.check_in_time ? formatDateTime(r.check_in_time) : '—'}</td>
                    <td className="py-3">{r.check_out_time ? formatDateTime(r.check_out_time) : '—'}</td>
                    <td className="py-3">{r.working_hours?.toFixed(1) ?? '—'}</td>
                    <td className="py-3"><Badge status={r.status} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </AdminLayout>
  )
}
