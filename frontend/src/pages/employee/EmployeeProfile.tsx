import { useEffect, useState } from 'react'
import { EmployeeLayout, PageHeader } from '../../components/layout/AppLayout'
import { Card, CardHeader } from '../../components/ui/Card'
import { Button } from '../../components/ui/Button'
import { Input, Textarea } from '../../components/ui/Input'
import { CardSkeleton } from '../../components/ui/Skeleton'
import { ErrorState } from '../../components/ui/EmptyState'
import { employeeService } from '../../services/employeeService'
import { useAuth } from '../../context/AuthContext'
import { useToast } from '../../context/ToastContext'
import { formatCurrency, formatDate, getInitials } from '../../utils/format'
import type { Employee } from '../../types/api'

export default function EmployeeProfile() {
  const { user } = useAuth()
  const { showToast } = useToast()
  const [employee, setEmployee] = useState<Employee | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [form, setForm] = useState({ phone: '', address: '' })

  useEffect(() => {
    employeeService.getById(user?.employee_id ?? 'EMP001')
      .then((emp) => { setEmployee(emp); setForm({ phone: emp.phone ?? '', address: emp.address ?? '' }) })
      .catch(() => showToast('Failed to load profile', 'error'))
      .finally(() => setLoading(false))
  }, [user, showToast])

  const handleSave = async () => {
    if (!employee) return
    setSaving(true)
    try {
      const updated = await employeeService.update(employee.id, form)
      setEmployee(updated)
      showToast('Profile updated', 'success')
    } catch {
      showToast('Update failed', 'error')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <EmployeeLayout><CardSkeleton /></EmployeeLayout>
  if (!employee) return <EmployeeLayout><ErrorState title="Profile not found" /></EmployeeLayout>

  return (
    <EmployeeLayout>
      <PageHeader title="My Profile" subtitle="View and update your personal information" />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card>
          <div className="flex flex-col items-center text-center">
            <div className="h-20 w-20 rounded-full bg-primary-100 flex items-center justify-center text-2xl font-bold text-primary-700 mb-4">
              {getInitials(employee.full_name)}
            </div>
            <h2 className="text-xl font-bold text-gray-900">{employee.full_name}</h2>
            <p className="text-gray-500">{employee.designation}</p>
            <p className="text-sm text-gray-400 mt-1">{employee.employee_id}</p>
          </div>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader title="Personal Information" />
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
            <div><p className="text-sm text-gray-500">Email</p><p className="font-medium">{employee.email}</p></div>
            <div><p className="text-sm text-gray-500">Department</p><p className="font-medium">{employee.department}</p></div>
            <div><p className="text-sm text-gray-500">Joining Date</p><p className="font-medium">{formatDate(employee.joining_date)}</p></div>
            <div><p className="text-sm text-gray-500">Employment Status</p><p className="font-medium">{employee.employment_status}</p></div>
            <div><p className="text-sm text-gray-500">Salary</p><p className="font-medium">{formatCurrency(employee.salary)}</p></div>
          </div>
          <div className="space-y-4 border-t pt-6">
            <Input label="Phone" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
            <Textarea label="Address" value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} />
            <Button onClick={handleSave} loading={saving}>Save Changes</Button>
          </div>
        </Card>
      </div>
    </EmployeeLayout>
  )
}
