import { useEffect, useState } from 'react'
import { EmployeeLayout, PageHeader } from '../../components/layout/AppLayout'
import { Card, CardHeader } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'
import { CardSkeleton } from '../../components/ui/Skeleton'
import { payrollService } from '../../services/payrollService'
import { formatCurrency } from '../../utils/format'
import type { PayrollHistoryItem, PayrollRecord } from '../../types/api'

export default function EmployeePayroll() {
  const [payroll, setPayroll] = useState<PayrollRecord | null>(null)
  const [history, setHistory] = useState<PayrollHistoryItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([payrollService.getMyPayroll(), payrollService.getMyHistory()])
      .then(([p, h]) => { setPayroll(p); setHistory(h) })
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <EmployeeLayout><CardSkeleton /></EmployeeLayout>

  return (
    <EmployeeLayout>
      <PageHeader title="Payroll" subtitle="View your salary structure and payment history" />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-1">
          <CardHeader title="Salary Overview" />
          {payroll && (
            <div className="text-center py-4">
              <p className="text-sm text-gray-500">Net Monthly Salary</p>
              <p className="text-4xl font-bold text-primary-600 mt-2">{formatCurrency(payroll.net_salary)}</p>
              <p className="text-sm text-gray-500 mt-2">Base: {formatCurrency(payroll.base_salary)}/year</p>
              <p className="text-xs text-gray-400 mt-1">{payroll.pay_frequency} · {payroll.currency}</p>
            </div>
          )}
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader title="Salary Structure" />
          {payroll && (
            <div className="space-y-3">
              {[
                { label: 'Basic', value: payroll.structure.basic },
                { label: 'HRA', value: payroll.structure.hra },
                { label: 'Allowances', value: payroll.structure.allowances },
                { label: 'Deductions', value: -payroll.structure.deductions },
              ].map((item) => (
                <div key={item.label} className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-600">{item.label}</span>
                  <span className={`font-medium ${item.value < 0 ? 'text-red-600' : ''}`}>{formatCurrency(Math.abs(item.value))}</span>
                </div>
              ))}
              <div className="flex justify-between pt-3 font-bold text-lg">
                <span>Net Salary</span>
                <span className="text-primary-600">{formatCurrency(payroll.net_salary)}</span>
              </div>
            </div>
          )}
        </Card>
      </div>

      <Card className="mt-6">
        <CardHeader title="Payment History" />
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 text-left text-gray-500">
                <th className="pb-3 font-medium">Month</th>
                <th className="pb-3 font-medium">Net Salary</th>
                <th className="pb-3 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {history.map((h) => (
                <tr key={h.id} className="border-b border-gray-100">
                  <td className="py-3">{h.month}</td>
                  <td className="py-3 font-medium">{formatCurrency(h.net_salary)}</td>
                  <td className="py-3"><Badge status={h.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </EmployeeLayout>
  )
}
