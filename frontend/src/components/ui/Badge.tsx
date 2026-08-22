import { cn } from '../../utils/cn'
import { STATUS_COLORS } from '../../utils/constants'

export function Badge({ status, children }: { status: string; children?: React.ReactNode }) {
  return (
    <span className={cn('inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset', STATUS_COLORS[status] ?? 'bg-gray-50 text-gray-700 ring-gray-600/20')}>
      {children ?? status.replace('_', ' ')}
    </span>
  )
}

export function PriorityBadge({ priority }: { priority: string }) {
  return <Badge status={priority}>{priority}</Badge>
}
