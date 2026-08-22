import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { AdminLayout, PageHeader } from '../../components/layout/AppLayout'
import { Card } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'
import { SearchInput } from '../../components/ui/SearchInput'
import { Select } from '../../components/ui/Input'
import { Pagination } from '../../components/ui/Pagination'
import { TableSkeleton } from '../../components/ui/Skeleton'
import { employeeService } from '../../services/employeeService'
import { DEPARTMENTS } from '../../utils/constants'
import { formatCurrency, getInitials } from '../../utils/format'
import type { Employee } from '../../types/api'

export default function AdminEmployees() {
  const [employees, setEmployees] = useState<Employee[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [department, setDepartment] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    employeeService.getAll({ search, department: department || undefined, page, page_size: 8 })
      .then((res) => { setEmployees(res.items); setTotal(res.total) })
      .finally(() => setLoading(false))
  }, [search, department, page])

  return (
    <AdminLayout>
      <PageHeader title="Employee Management" subtitle="View and manage all employees" />

      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <SearchInput value={search} onChange={setSearch} placeholder="Search by name or ID..." className="sm:w-72" />
        <Select value={department} onChange={(e) => { setDepartment(e.target.value); setPage(1) }} className="sm:w-48">
          <option value="">All Departments</option>
          {DEPARTMENTS.map((d) => <option key={d} value={d}>{d}</option>)}
        </Select>
      </div>

      {loading ? <TableSkeleton /> : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {employees.map((emp) => (
              <Link key={emp.id} to={`/admin/employees/${emp.employee_id}`}>
                <Card className="hover:border-primary-300 transition-colors cursor-pointer">
                  <div className="flex items-center gap-4">
                    <div className="h-12 w-12 rounded-full bg-primary-100 flex items-center justify-center font-semibold text-primary-700">
                      {getInitials(emp.full_name)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-gray-900 truncate">{emp.full_name}</h3>
                        <Badge status={emp.employment_status} />
                      </div>
                      <p className="text-sm text-gray-500">{emp.designation} · {emp.department}</p>
                      <p className="text-xs text-gray-400 mt-1">{emp.employee_id} · {formatCurrency(emp.salary)}</p>
                    </div>
                  </div>
                </Card>
              </Link>
            ))}
          </div>
          <Pagination page={page} total={total} pageSize={8} onPageChange={setPage} />
        </>
      )}
    </AdminLayout>
  )
}
