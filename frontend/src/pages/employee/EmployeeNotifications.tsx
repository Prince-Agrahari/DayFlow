import { useEffect, useState } from 'react'
import { EmployeeLayout, PageHeader } from '../../components/layout/AppLayout'
import { Card } from '../../components/ui/Card'
import { Button } from '../../components/ui/Button'
import { TableSkeleton } from '../../components/ui/Skeleton'
import { EmptyState } from '../../components/ui/EmptyState'
import { notificationService } from '../../services/notificationService'
import { useToast } from '../../context/ToastContext'
import { formatDateTime } from '../../utils/format'
import type { Notification } from '../../types/api'

export default function EmployeeNotifications() {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [loading, setLoading] = useState(true)
  const { showToast } = useToast()

  const load = async () => {
    setLoading(true)
    try {
      const data = await notificationService.getAll()
      setNotifications(data.items)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const markRead = async (id: number) => {
    await notificationService.markRead(id)
    setNotifications((prev) => prev.map((n) => n.id === id ? { ...n, is_read: true } : n))
  }

  const markAllRead = async () => {
    await notificationService.markAllRead()
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })))
    showToast('All notifications marked as read', 'success')
  }

  return (
    <EmployeeLayout>
      <PageHeader title="Notifications" subtitle="Stay updated on leave, attendance, and HR alerts"
        action={<Button variant="secondary" size="sm" onClick={markAllRead}>Mark all read</Button>} />

      {loading ? <TableSkeleton rows={4} /> : notifications.length === 0 ? (
        <EmptyState title="No notifications" description="You're all caught up!" />
      ) : (
        <div className="space-y-3">
          {notifications.map((n) => (
            <Card key={n.id} className={n.is_read ? 'opacity-75' : ''}>
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-3">
                  {!n.is_read && <span className="h-2.5 w-2.5 rounded-full bg-primary-600 mt-2 shrink-0" />}
                  <div className={n.is_read ? 'ml-5' : ''}>
                    <p className="font-medium text-gray-900">{n.title}</p>
                    <p className="text-sm text-gray-600 mt-1">{n.message}</p>
                    <p className="text-xs text-gray-400 mt-2">{formatDateTime(n.created_at)}</p>
                  </div>
                </div>
                {!n.is_read && (
                  <Button variant="ghost" size="sm" onClick={() => markRead(n.id)}>Mark read</Button>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </EmployeeLayout>
  )
}
