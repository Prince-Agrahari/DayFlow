import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, User, Clock, CalendarDays, DollarSign, Bell, Bot,
  Users, BarChart3, LogOut, Menu, X, Sparkles,
} from 'lucide-react'
import { useState } from 'react'
import { useAuth } from '../../context/AuthContext'
import { cn } from '../../utils/cn'
import { getInitials } from '../../utils/format'

interface NavItem { to: string; label: string; icon: React.ComponentType<{ className?: string }> }

const employeeNav: NavItem[] = [
  { to: '/employee/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/employee/profile', label: 'Profile', icon: User },
  { to: '/employee/attendance', label: 'Attendance', icon: Clock },
  { to: '/employee/leave', label: 'Leave', icon: CalendarDays },
  { to: '/employee/payroll', label: 'Payroll', icon: DollarSign },
  { to: '/employee/notifications', label: 'Notifications', icon: Bell },
  { to: '/employee/assistant', label: 'AI Assistant', icon: Bot },
]

const adminNav: NavItem[] = [
  { to: '/admin/dashboard', label: 'Command Center', icon: LayoutDashboard },
  { to: '/admin/employees', label: 'Employees', icon: Users },
  { to: '/admin/attendance', label: 'Attendance', icon: Clock },
  { to: '/admin/leaves', label: 'Leave Management', icon: CalendarDays },
  { to: '/admin/payroll', label: 'Payroll', icon: DollarSign },
  { to: '/admin/analytics', label: 'Analytics', icon: BarChart3 },
  { to: '/admin/copilot', label: 'AI Copilot', icon: Sparkles },
]

function Sidebar({ nav, title }: { nav: NavItem[]; title: string }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [mobileOpen, setMobileOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const sidebar = (
    <div className="flex flex-col h-full">
      <div className="px-6 py-5 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 bg-primary-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">DF</span>
          </div>
          <div>
            <h1 className="font-bold text-gray-900">DayFlow</h1>
            <p className="text-xs text-gray-500">{title}</p>
          </div>
        </div>
      </div>
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {nav.map(({ to, label, icon: Icon }) => (
          <NavLink key={to} to={to} onClick={() => setMobileOpen(false)}
            className={({ isActive }) => cn(
              'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
              isActive ? 'bg-primary-50 text-primary-700' : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900',
            )}
          >
            <Icon className="h-5 w-5 shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="px-4 py-4 border-t border-gray-200">
        <div className="flex items-center gap-3 mb-3">
          <div className="h-9 w-9 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 text-sm font-semibold">
            {getInitials(user?.full_name ?? 'U')}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">{user?.full_name}</p>
            <p className="text-xs text-gray-500 truncate">{user?.role}</p>
          </div>
        </div>
        <button onClick={handleLogout} className="flex items-center gap-2 w-full px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg">
          <LogOut className="h-4 w-4" /> Sign out
        </button>
      </div>
    </div>
  )

  return (
    <>
      <button className="lg:hidden fixed top-4 left-4 z-40 p-2 bg-white rounded-lg border border-gray-200 shadow-sm" onClick={() => setMobileOpen(!mobileOpen)}>
        {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </button>
      {mobileOpen && <div className="lg:hidden fixed inset-0 bg-gray-900/50 z-30" onClick={() => setMobileOpen(false)} />}
      <aside className={cn(
        'fixed lg:static inset-y-0 left-0 z-40 w-64 bg-white border-r border-gray-200 transform transition-transform lg:transform-none',
        mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
      )}>
        {sidebar}
      </aside>
    </>
  )
}

export function EmployeeLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar nav={employeeNav} title="Employee Portal" />
      <main className="flex-1 lg:ml-0 min-w-0">
        <div className="p-4 lg:p-8 pt-16 lg:pt-8 max-w-7xl mx-auto">{children}</div>
      </main>
    </div>
  )
}

export function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar nav={adminNav} title="HR Command Center" />
      <main className="flex-1 lg:ml-0 min-w-0">
        <div className="p-4 lg:p-8 pt-16 lg:pt-8 max-w-7xl mx-auto">{children}</div>
      </main>
    </div>
  )
}

export function PageHeader({ title, subtitle, action }: { title: string; subtitle?: string; action?: React.ReactNode }) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
        {subtitle && <p className="text-gray-500 mt-1">{subtitle}</p>}
      </div>
      {action}
    </div>
  )
}
