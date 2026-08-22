import api, { USE_MOCK } from './api'
import { MOCK_ALL_PAYROLL, MOCK_PAYROLL, MOCK_PAYROLL_HISTORY } from '../mocks/data'
import { delay } from '../utils/format'
import type { PayrollHistoryItem, PayrollRecord } from '../types/api'

export const payrollService = {
  async getMyPayroll(): Promise<PayrollRecord> {
    if (USE_MOCK) {
      await delay(300)
      return MOCK_PAYROLL
    }
    const { data } = await api.get<PayrollRecord>('/payroll/me')
    return data
  },

  async getMyHistory(): Promise<PayrollHistoryItem[]> {
    if (USE_MOCK) {
      await delay(300)
      return MOCK_PAYROLL_HISTORY
    }
    const { data } = await api.get<PayrollHistoryItem[]>('/payroll/me/history')
    return data
  },

  async getAll(): Promise<PayrollRecord[]> {
    if (USE_MOCK) {
      await delay(400)
      return MOCK_ALL_PAYROLL
    }
    const { data } = await api.get<{ items: PayrollRecord[] }>('/payroll')
    return data.items
  },

  async update(employeeId: string, payload: Partial<PayrollRecord>): Promise<PayrollRecord> {
    if (USE_MOCK) {
      await delay(400)
      const record = MOCK_ALL_PAYROLL.find((p) => p.employee_id === employeeId)
      if (!record) throw new Error('Payroll not found')
      return { ...record, ...payload }
    }
    const { data } = await api.put<PayrollRecord>(`/payroll/${employeeId}`, payload)
    return data
  },
}
