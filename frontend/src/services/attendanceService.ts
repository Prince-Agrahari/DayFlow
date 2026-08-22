import api, { USE_MOCK } from './api'
import { getMockAttendancePeriod, MOCK_ATTENDANCE } from '../mocks/data'
import { delay } from '../utils/format'
import type { AttendancePeriodResponse, AttendanceRecord, PaginatedResponse } from '../types/api'

export const attendanceService = {
  async checkIn(notes?: string): Promise<AttendanceRecord> {
    if (USE_MOCK) {
      await delay(500)
      const now = new Date()
      return {
        id: Date.now(), employee_id: 'EMP001', date: now.toISOString().split('T')[0],
        check_in_time: now.toISOString(), check_out_time: null, working_hours: null,
        status: 'PRESENT', is_late: now.getHours() >= 9, notes,
      }
    }
    const { data } = await api.post<AttendanceRecord>('/attendance/check-in', { notes })
    return data
  },

  async checkOut(): Promise<AttendanceRecord> {
    if (USE_MOCK) {
      await delay(500)
      const now = new Date()
      const checkIn = new Date(now)
      checkIn.setHours(9, 0, 0)
      return {
        id: Date.now(), employee_id: 'EMP001', date: now.toISOString().split('T')[0],
        check_in_time: checkIn.toISOString(), check_out_time: now.toISOString(),
        working_hours: 8.2, status: 'PRESENT', is_late: false,
      }
    }
    const { data } = await api.post<AttendanceRecord>('/attendance/check-out')
    return data
  },

  async getMyAttendance(period: 'daily' | 'weekly' | 'monthly' = 'weekly'): Promise<AttendancePeriodResponse> {
    if (USE_MOCK) {
      await delay(400)
      return getMockAttendancePeriod('EMP001', period)
    }
    const { data } = await api.get<AttendancePeriodResponse>('/attendance/me', { params: { period } })
    return data
  },

  async getAll(params?: { employee_id?: string; department?: string; page?: number }): Promise<PaginatedResponse<AttendanceRecord>> {
    if (USE_MOCK) {
      await delay(400)
      const records = Object.values(MOCK_ATTENDANCE).flat()
      return { items: records, total: records.length, page: 1, page_size: 20 }
    }
    const { data } = await api.get<PaginatedResponse<AttendanceRecord>>('/attendance', { params })
    return data
  },

  async getTodayStatus(): Promise<AttendanceRecord | null> {
    if (USE_MOCK) {
      await delay(200)
      const records = MOCK_ATTENDANCE['EMP001'] ?? []
      const today = new Date().toISOString().split('T')[0]
      return records.find((r) => r.date === today) ?? null
    }
    const { data } = await api.get<AttendancePeriodResponse>('/attendance/me', { params: { period: 'daily' } })
    return data.records[0] ?? null
  },
}
