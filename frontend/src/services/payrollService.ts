import api, { USE_MOCK } from './api'
import { MOCK_ALL_PAYROLL, MOCK_PAYROLL, MOCK_PAYROLL_HISTORY } from '../mocks/data'
import { delay } from '../utils/format'
import type { PayrollHistoryItem, PayrollRecord } from '../types/api'

function normalizePayroll(record: PayrollRecord): PayrollRecord {
  return {
    ...record,
    base_salary: Number(record.base_salary),
    net_salary: Number(record.net_salary),
    structure: {
      basic: Number(record.structure.basic),
      hra: Number(record.structure.hra),
      allowances: Number(record.structure.allowances),
      deductions: Number(record.structure.deductions),
    },
  }
}

export const payrollService = {
  async getMyPayroll(): Promise<PayrollRecord> {
    if (USE_MOCK) {
      await delay(300)
      return MOCK_PAYROLL
    }
    const { data } = await api.get<PayrollRecord>('/payroll/me')
    return normalizePayroll(data)
  },

  async getMyHistory(): Promise<PayrollHistoryItem[]> {
    if (USE_MOCK) {
      await delay(300)
      return MOCK_PAYROLL_HISTORY
    }
    const { data } = await api.get<PayrollHistoryItem[]>('/payroll/me/history')
    return data.map((item) => ({ ...item, net_salary: Number(item.net_salary) }))
  },

  async getAll(): Promise<PayrollRecord[]> {
    if (USE_MOCK) {
      await delay(400)
      return MOCK_ALL_PAYROLL
    }
    const { data } = await api.get<{ items: PayrollRecord[] }>('/payroll')
    return data.items.map(normalizePayroll)
  },

  async update(employeeId: string, payload: Partial<PayrollRecord>): Promise<PayrollRecord> {
    if (USE_MOCK) {
      await delay(400)
      const record = MOCK_ALL_PAYROLL.find((p) => p.employee_id === employeeId)
      if (!record) throw new Error('Payroll not found')
      return { ...record, ...payload }
    }
    const body: Record<string, number> = {}
    if (payload.base_salary != null) body.base_salary = payload.base_salary
    if (payload.net_salary != null) body.net_salary = payload.net_salary
    if (payload.structure) {
      body.basic = payload.structure.basic
      body.hra = payload.structure.hra
      body.allowances = payload.structure.allowances
      body.deductions = payload.structure.deductions
    }
    const { data } = await api.put<PayrollRecord>(`/payroll/${employeeId}`, body)
    return normalizePayroll(data)
  },
}
