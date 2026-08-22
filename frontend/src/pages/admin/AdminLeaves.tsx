import { useEffect, useState } from 'react'
import { AdminLayout, PageHeader } from '../../components/layout/AppLayout'
import { Card, CardHeader } from '../../components/ui/Card'
import { Badge, PriorityBadge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { Modal } from '../../components/ui/Modal'
import { Textarea, Select } from '../../components/ui/Input'
import { TableSkeleton } from '../../components/ui/Skeleton'
import { leaveService } from '../../services/leaveService'
import { useToast } from '../../context/ToastContext'
import { formatDate } from '../../utils/format'
import type { LeaveRecommendation, LeaveRequest } from '../../types/api'

export default function AdminLeaves() {
  const [leaves, setLeaves] = useState<LeaveRequest[]>([])
  const [statusFilter, setStatusFilter] = useState('')
  const [loading, setLoading] = useState(true)
  const [modal, setModal] = useState<{ type: 'approve' | 'reject'; leave: LeaveRequest } | null>(null)
  const [comment, setComment] = useState('')
  const [actionLoading, setActionLoading] = useState(false)
  const [recommendation, setRecommendation] = useState<LeaveRecommendation | null>(null)
  const { showToast } = useToast()

  const load = async () => {
    setLoading(true)
    try {
      setLeaves(await leaveService.getAll({ status: statusFilter || undefined }))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [statusFilter])

  const openModal = async (type: 'approve' | 'reject', leave: LeaveRequest) => {
    setModal({ type, leave })
    setComment('')
    try {
      const rec = await leaveService.getRecommendation({
        employee_id: leave.employee_id, start_date: leave.start_date,
        end_date: leave.end_date, leave_type: leave.leave_type,
      })
      setRecommendation(rec)
    } catch {
      setRecommendation(null)
    }
  }

  const handleAction = async () => {
    if (!modal) return
    setActionLoading(true)
    try {
      if (modal.type === 'approve') {
        await leaveService.approve(modal.leave.id, comment)
        showToast('Leave approved', 'success')
      } else {
        await leaveService.reject(modal.leave.id, comment)
        showToast('Leave rejected', 'success')
      }
      setModal(null)
      load()
    } catch {
      showToast('Action failed', 'error')
    } finally {
      setActionLoading(false)
    }
  }

  return (
    <AdminLayout>
      <PageHeader title="Leave Management" subtitle="Review, approve, and manage leave requests" />

      <Select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="mb-6 max-w-xs">
        <option value="">All Statuses</option>
        <option value="PENDING">Pending</option>
        <option value="APPROVED">Approved</option>
        <option value="REJECTED">Rejected</option>
      </Select>

      {loading ? <TableSkeleton /> : (
        <Card>
          <CardHeader title="Leave Requests" />
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 text-left text-gray-500">
                  <th className="pb-3 font-medium">Employee</th>
                  <th className="pb-3 font-medium">Type</th>
                  <th className="pb-3 font-medium">Dates</th>
                  <th className="pb-3 font-medium">Reason</th>
                  <th className="pb-3 font-medium">Status</th>
                  <th className="pb-3 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {leaves.map((l) => (
                  <tr key={l.id} className="border-b border-gray-100">
                    <td className="py-3"><p className="font-medium">{l.employee_name}</p><p className="text-xs text-gray-400">{l.employee_id}</p></td>
                    <td className="py-3">{l.leave_type}</td>
                    <td className="py-3">{formatDate(l.start_date)} – {formatDate(l.end_date)}</td>
                    <td className="py-3 max-w-xs truncate">{l.reason}</td>
                    <td className="py-3"><Badge status={l.status} /></td>
                    <td className="py-3">
                      {l.status === 'PENDING' && (
                        <div className="flex gap-2">
                          <Button size="sm" onClick={() => openModal('approve', l)}>Approve</Button>
                          <Button size="sm" variant="danger" onClick={() => openModal('reject', l)}>Reject</Button>
                        </div>
                      )}
                      {l.admin_comment && <p className="text-xs text-gray-500 mt-1">{l.admin_comment}</p>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      <Modal
        open={!!modal}
        onClose={() => setModal(null)}
        title={modal?.type === 'approve' ? 'Approve Leave' : 'Reject Leave'}
        footer={<>
          <Button variant="secondary" onClick={() => setModal(null)}>Cancel</Button>
          <Button variant={modal?.type === 'reject' ? 'danger' : 'primary'} onClick={handleAction} loading={actionLoading}>
            {modal?.type === 'approve' ? 'Approve' : 'Reject'}
          </Button>
        </>}
      >
        {modal && (
          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              {modal.leave.employee_name} · {modal.leave.leave_type} · {formatDate(modal.leave.start_date)} – {formatDate(modal.leave.end_date)}
            </p>
            {recommendation && (
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-sm font-medium text-blue-900">Smart Leave Recommendation</span>
                  <PriorityBadge priority={recommendation.conflict_level} />
                </div>
                <p className="text-sm text-blue-800">{recommendation.recommendation}</p>
                <ul className="mt-2 space-y-1">{recommendation.reasons.map((r, i) => <li key={i} className="text-xs text-blue-700">• {r}</li>)}</ul>
              </div>
            )}
            <Textarea label="Comment" value={comment} onChange={(e) => setComment(e.target.value)} placeholder="Add a comment for the employee..." />
          </div>
        )}
      </Modal>
    </AdminLayout>
  )
}
