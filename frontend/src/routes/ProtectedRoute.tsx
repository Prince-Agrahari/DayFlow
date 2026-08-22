import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { DashboardSkeleton } from '../components/ui/Skeleton'
import type { UserRole } from '../types/api'

interface ProtectedRouteProps {
  children: React.ReactNode
  allowedRoles?: UserRole[]
}

export function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  const { isAuthenticated, loading, role } = useAuth()
  const location = useLocation()

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <DashboardSkeleton />
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (allowedRoles && role && !allowedRoles.includes(role)) {
    const redirect = role === 'ADMIN' ? '/admin/dashboard' : '/employee/dashboard'
    return <Navigate to={redirect} replace />
  }

  return <>{children}</>
}

export function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading, role } = useAuth()

  if (loading) return null
  if (isAuthenticated) {
    return <Navigate to={role === 'ADMIN' ? '/admin/dashboard' : '/employee/dashboard'} replace />
  }
  return <>{children}</>
}
