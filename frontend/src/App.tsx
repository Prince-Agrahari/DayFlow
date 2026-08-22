import { Routes, Route, Navigate } from 'react-router-dom'
import { ProtectedRoute, PublicRoute } from './routes/ProtectedRoute'
import LoginPage from './pages/auth/LoginPage'
import SignupPage from './pages/auth/SignupPage'
import EmployeeDashboard from './pages/employee/EmployeeDashboard'
import EmployeeProfile from './pages/employee/EmployeeProfile'
import EmployeeAttendance from './pages/employee/EmployeeAttendance'
import EmployeeLeave from './pages/employee/EmployeeLeave'
import EmployeePayroll from './pages/employee/EmployeePayroll'
import EmployeeNotifications from './pages/employee/EmployeeNotifications'
import EmployeeAssistant from './pages/employee/EmployeeAssistant'
import AdminDashboard from './pages/admin/AdminDashboard'
import AdminEmployees from './pages/admin/AdminEmployees'
import Employee360Page from './pages/admin/Employee360Page'
import AdminAttendance from './pages/admin/AdminAttendance'
import AdminLeaves from './pages/admin/AdminLeaves'
import AdminPayroll from './pages/admin/AdminPayroll'
import AdminAnalytics from './pages/admin/AdminAnalytics'
import AdminCopilot from './pages/admin/AdminCopilot'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />

      <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
      <Route path="/signup" element={<PublicRoute><SignupPage /></PublicRoute>} />

      <Route path="/employee/dashboard" element={<ProtectedRoute allowedRoles={['EMPLOYEE']}><EmployeeDashboard /></ProtectedRoute>} />
      <Route path="/employee/profile" element={<ProtectedRoute allowedRoles={['EMPLOYEE']}><EmployeeProfile /></ProtectedRoute>} />
      <Route path="/employee/attendance" element={<ProtectedRoute allowedRoles={['EMPLOYEE']}><EmployeeAttendance /></ProtectedRoute>} />
      <Route path="/employee/leave" element={<ProtectedRoute allowedRoles={['EMPLOYEE']}><EmployeeLeave /></ProtectedRoute>} />
      <Route path="/employee/payroll" element={<ProtectedRoute allowedRoles={['EMPLOYEE']}><EmployeePayroll /></ProtectedRoute>} />
      <Route path="/employee/notifications" element={<ProtectedRoute allowedRoles={['EMPLOYEE']}><EmployeeNotifications /></ProtectedRoute>} />
      <Route path="/employee/assistant" element={<ProtectedRoute allowedRoles={['EMPLOYEE']}><EmployeeAssistant /></ProtectedRoute>} />

      <Route path="/admin/dashboard" element={<ProtectedRoute allowedRoles={['ADMIN']}><AdminDashboard /></ProtectedRoute>} />
      <Route path="/admin/employees" element={<ProtectedRoute allowedRoles={['ADMIN']}><AdminEmployees /></ProtectedRoute>} />
      <Route path="/admin/employees/:id" element={<ProtectedRoute allowedRoles={['ADMIN']}><Employee360Page /></ProtectedRoute>} />
      <Route path="/admin/attendance" element={<ProtectedRoute allowedRoles={['ADMIN']}><AdminAttendance /></ProtectedRoute>} />
      <Route path="/admin/leaves" element={<ProtectedRoute allowedRoles={['ADMIN']}><AdminLeaves /></ProtectedRoute>} />
      <Route path="/admin/payroll" element={<ProtectedRoute allowedRoles={['ADMIN']}><AdminPayroll /></ProtectedRoute>} />
      <Route path="/admin/analytics" element={<ProtectedRoute allowedRoles={['ADMIN']}><AdminAnalytics /></ProtectedRoute>} />
      <Route path="/admin/copilot" element={<ProtectedRoute allowedRoles={['ADMIN']}><AdminCopilot /></ProtectedRoute>} />

      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}
