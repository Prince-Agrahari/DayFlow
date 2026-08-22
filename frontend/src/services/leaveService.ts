import api, { USE_MOCK } from './api'
import { MOCK_LEAVE_BALANCES, MOCK_LEAVE_RECOMMENDATION, MOCK_LEAVE_REQUESTS } from '../mocks/data'
import { delay } from '../utils/format'
import type { LeaveBalance, LeaveRecommendation, LeaveRequest, LeaveType } from '../types/api'

export const leaveService = {
  async apply(payload: { leave_type: LeaveType; start_date: string; end_date: string; reason: string }): Promise<LeaveRequest> {
    if (USE_MOCK) {
      await delay(500)
      return {
        id: Date.now(), employee_id: 'EMP001', leave_type: payload.leave_type,
        start_date: payload.start_date, end_date: payload.end_date, reason: payload.reason,
        status: 'PENDING', admin_comment: null, created_at: new Date().toISOString(),
      }
    }
    const { data } = await api.post<LeaveRequest>('/leave', payload)
    return data
  },

  async getMyLeaves(): Promise<LeaveRequest[]> {
    if (USE_MOCK) {
      await delay(300)
      return MOCK_LEAVE_REQUESTS.filter((l) => l.employee_id === 'EMP001')
    }
    const { data } = await api.get<LeaveRequest[]>('/leave/me')
    return data
  },

  async getAll(params?: { status?: string; department?: string }): Promise<LeaveRequest[]> {
    if (USE_MOCK) {
      await delay(400)
      let items = [...MOCK_LEAVE_REQUESTS]
      if (params?.status) items = items.filter((l) => l.status === params.status)
      return items
    }
    const { data } = await api.get<{ items: LeaveRequest[] }>('/leave', { params })
    return data.items
  },

  async approve(id: number, comment: string): Promise<LeaveRequest> {
    if (USE_MOCK) {
      await delay(400)
      const req = MOCK_LEAVE_REQUESTS.find((l) => l.id === id)
      if (!req) throw new Error('Leave not found')
      return { ...req, status: 'APPROVED', admin_comment: comment }
    }
    const { data } = await api.put<LeaveRequest>(`/leave/${id}/approve`, { comment })
    return data
  },

  async reject(id: number, comment: string): Promise<LeaveRequest> {
    if (USE_MOCK) {
      await delay(400)
      const req = MOCK_LEAVE_REQUESTS.find((l) => l.id === id)
      if (!req) throw new Error('Leave not found')
      return { ...req, status: 'REJECTED', admin_comment: comment }
    }
    const { data } = await api.put<LeaveRequest>(`/leave/${id}/reject`, { comment })
    return data
  },

  async getBalances(): Promise<LeaveBalance[]> {
    if (USE_MOCK) {
      await delay(200)
      return MOCK_LEAVE_BALANCES
    }
    const { data } = await api.get<LeaveBalance[]>('/leave/balances')
    return data
  },

  async getRecommendation(payload: { employee_id: string; start_date: string; end_date: string; leave_type: LeaveType }): Promise<LeaveRecommendation> {
    if (USE_MOCK) {
      await delay(600)
      return MOCK_LEAVE_RECOMMENDATION
    }
    const { data } = await api.post<LeaveRecommendation>('/ai/leave-recommendation', payload)
    return data
  },
}
