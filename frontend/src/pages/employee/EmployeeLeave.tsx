import { useEffect, useState } from 'react'
import { EmployeeLayout, PageHeader } from '../../components/layout/AppLayout'
import { Card, CardHeader, KPICard } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { Input, Select, Textarea } from '../../components/ui/Input'
import { TableSkeleton } from '../../components/ui/Skeleton'
import { leaveService } from '../../services/leaveService'
import { useToast } from '../../context/ToastContext'
import { formatDate } from '../../utils/format'
import type { LeaveBalance, LeaveRequest, LeaveType } from '../../types/api'

export default function EmployeeLeave() {
  const [leaves, setLeaves] = useState<LeaveRequest[]>([])
  const [balances, setBalances] = useState<LeaveBalance[]>([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [form, setForm] = useState({ leave_type: 'PAID' as LeaveType, start_date: '', end_date: '', reason: '' })
  const { showToast } = useToast()

  const load = async () => {
    setLoading(true)
    try {
      const [l, b] = await Promise.all([leaveService.getMyLeaves(), leaveService.getBalances()])
      setLeaves(l)
      setBalances(b)
    } catch {
      showToast('Failed to load leave data', 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      await leaveService.apply(form)
      showToast('Leave request submitted', 'success')
      setForm({ leave_type: 'PAID', start_date: '', end_date: '', reason: '' })
      load()
    } catch {
      showToast('Submission failed', 'error')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <EmployeeLayout>
      <PageHeader title="Leave Management" subtitle="Apply for leave and track your requests" />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        {balances.map((b) => (
          <KPICard key={b.leave_type} label={`${b.leave_type} Leave`} value={`${b.remaining_days} days`} sub={`${b.used_days} used of ${b.total_days}`} />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-1">
          <CardHeader title="Apply for Leave" />
          <form onSubmit={handleSubmit} className="space-y-4">
            <Select label="Leave Type" value={form.leave_type} onChange={(e) => setForm({ ...form, leave_type: e.target.value as LeaveType })}>
              <option value="PAID">Paid Leave</option>
              <option value="SICK">Sick Leave</option>
              <option value="UNPAID">Unpaid Leave</option>
            </Select>
            <Input label="Start Date" type="date" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} required />
            <Input label="End Date" type="date" value={form.end_date} onChange={(e) => setForm({ ...form, end_date: e.target.value })} required />
            <Textarea label="Reason" value={form.reason} onChange={(e) => setForm({ ...form, reason: e.target.value })} required />
            <Button type="submit" className="w-full" loading={submitting}>Submit Request</Button>
          </form>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader title="Leave History" />
          {loading ? <TableSkeleton rows={3} /> : leaves.length === 0 ? (
            <p className="text-sm text-gray-500">No leave requests yet.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200 text-left text-gray-500">
                    <th className="pb-3 font-medium">Type</th>
                    <th className="pb-3 font-medium">Dates</th>
                    <th className="pb-3 font-medium">Reason</th>
                    <th className="pb-3 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {leaves.map((l) => (
                    <tr key={l.id} className="border-b border-gray-100">
                      <td className="py-3">{l.leave_type}</td>
                      <td className="py-3">{formatDate(l.start_date)} – {formatDate(l.end_date)}</td>
                      <td className="py-3 max-w-xs truncate">{l.reason}</td>
                      <td className="py-3"><Badge status={l.status} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </div>
    </EmployeeLayout>
  )
}
