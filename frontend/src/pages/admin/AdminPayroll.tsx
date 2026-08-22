import { useEffect, useState } from 'react'
import { AdminLayout, PageHeader } from '../../components/layout/AppLayout'
import { Card, CardHeader } from '../../components/ui/Card'
import { Button } from '../../components/ui/Button'
import { Modal } from '../../components/ui/Modal'
import { Input } from '../../components/ui/Input'
import { TableSkeleton } from '../../components/ui/Skeleton'
import { payrollService } from '../../services/payrollService'
import { useToast } from '../../context/ToastContext'
import { formatCurrency } from '../../utils/format'
import type { PayrollRecord } from '../../types/api'

export default function AdminPayroll() {
  const [records, setRecords] = useState<PayrollRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [editRecord, setEditRecord] = useState<PayrollRecord | null>(null)
  const [form, setForm] = useState({ base_salary: 0, basic: 0, hra: 0, allowances: 0, deductions: 0 })
  const [saving, setSaving] = useState(false)
  const { showToast } = useToast()

  useEffect(() => {
    payrollService.getAll().then(setRecords).finally(() => setLoading(false))
  }, [])

  const openEdit = (record: PayrollRecord) => {
    setEditRecord(record)
    setForm({
      base_salary: record.base_salary,
      basic: record.structure.basic,
      hra: record.structure.hra,
      allowances: record.structure.allowances,
      deductions: record.structure.deductions,
    })
  }

  const handleSave = async () => {
    if (!editRecord) return
    setSaving(true)
    try {
      await payrollService.update(editRecord.employee_id, {
        base_salary: form.base_salary,
        structure: { basic: form.basic, hra: form.hra, allowances: form.allowances, deductions: form.deductions },
        net_salary: form.basic + form.hra + form.allowances - form.deductions,
      })
      showToast('Payroll updated', 'success')
      setEditRecord(null)
      payrollService.getAll().then(setRecords)
    } catch {
      showToast('Update failed', 'error')
    } finally {
      setSaving(false)
    }
  }

  return (
    <AdminLayout>
      <PageHeader title="Payroll Management" subtitle="View and manage employee compensation" />

      {loading ? <TableSkeleton /> : (
        <Card>
          <CardHeader title="Employee Payroll" subtitle={`${records.length} employees`} />
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 text-left text-gray-500">
                  <th className="pb-3 font-medium">Employee</th>
                  <th className="pb-3 font-medium">Base Salary</th>
                  <th className="pb-3 font-medium">Basic</th>
                  <th className="pb-3 font-medium">HRA</th>
                  <th className="pb-3 font-medium">Net Salary</th>
                  <th className="pb-3 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {records.map((r) => (
                  <tr key={r.employee_id} className="border-b border-gray-100">
                    <td className="py-3"><p className="font-medium">{r.employee_name}</p><p className="text-xs text-gray-400">{r.employee_id}</p></td>
                    <td className="py-3">{formatCurrency(r.base_salary)}</td>
                    <td className="py-3">{formatCurrency(r.structure.basic)}</td>
                    <td className="py-3">{formatCurrency(r.structure.hra)}</td>
                    <td className="py-3 font-medium">{formatCurrency(r.net_salary)}</td>
                    <td className="py-3"><Button size="sm" variant="secondary" onClick={() => openEdit(r)}>Edit</Button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      <Modal open={!!editRecord} onClose={() => setEditRecord(null)} title={`Edit Payroll — ${editRecord?.employee_name}`}
        footer={<>
          <Button variant="secondary" onClick={() => setEditRecord(null)}>Cancel</Button>
          <Button onClick={handleSave} loading={saving}>Save Changes</Button>
        </>}
      >
        <div className="grid grid-cols-2 gap-4">
          <Input label="Base Salary" type="number" value={form.base_salary} onChange={(e) => setForm({ ...form, base_salary: +e.target.value })} />
          <Input label="Basic" type="number" value={form.basic} onChange={(e) => setForm({ ...form, basic: +e.target.value })} />
          <Input label="HRA" type="number" value={form.hra} onChange={(e) => setForm({ ...form, hra: +e.target.value })} />
          <Input label="Allowances" type="number" value={form.allowances} onChange={(e) => setForm({ ...form, allowances: +e.target.value })} />
          <Input label="Deductions" type="number" value={form.deductions} onChange={(e) => setForm({ ...form, deductions: +e.target.value })} />
          <div className="col-span-2 pt-2 border-t">
            <p className="text-sm text-gray-500">Net Salary</p>
            <p className="text-lg font-bold text-primary-600">{formatCurrency(form.basic + form.hra + form.allowances - form.deductions)}</p>
          </div>
        </div>
      </Modal>
    </AdminLayout>
  )
}
