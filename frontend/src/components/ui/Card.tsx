import { cn } from '../../utils/cn'

interface CardProps {
  children: React.ReactNode
  className?: string
  padding?: boolean
}

export function Card({ children, className, padding = true }: CardProps) {
  return (
    <div className={cn('bg-white rounded-xl border border-gray-200 shadow-sm', padding && 'p-6', className)}>
      {children}
    </div>
  )
}

export function CardHeader({ title, subtitle, action }: { title: string; subtitle?: string; action?: React.ReactNode }) {
  return (
    <div className="flex items-start justify-between mb-4">
      <div>
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        {subtitle && <p className="text-sm text-gray-500 mt-0.5">{subtitle}</p>}
      </div>
      {action}
    </div>
  )
}

export function KPICard({ label, value, sub, icon: Icon, trend }: {
  label: string; value: string | number; sub?: string
  icon?: React.ComponentType<{ className?: string }>; trend?: 'up' | 'down' | 'neutral'
}) {
  return (
    <Card>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500">{label}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
          {sub && <p className={cn('text-xs mt-1', trend === 'up' ? 'text-emerald-600' : trend === 'down' ? 'text-red-600' : 'text-gray-500')}>{sub}</p>}
        </div>
        {Icon && (
          <div className="p-2.5 bg-primary-50 rounded-lg">
            <Icon className="h-5 w-5 text-primary-600" />
          </div>
        )}
      </div>
    </Card>
  )
}
