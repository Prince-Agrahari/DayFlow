import api, { USE_MOCK } from './api'
import {
  MOCK_ANOMALIES, MOCK_DASHBOARD, MOCK_PRIORITY_QUEUE, MOCK_RISK_SIGNALS, MOCK_TEAM_AVAILABILITY,
} from '../mocks/data'
import { delay } from '../utils/format'
import type { AnomalyItem, DashboardAnalytics, PriorityQueueItem, RiskSignalItem, TeamAvailabilityDay } from '../types/api'

export const analyticsService = {
  async getDashboard(): Promise<DashboardAnalytics> {
    if (USE_MOCK) {
      await delay(500)
      return MOCK_DASHBOARD
    }
    const { data } = await api.get<DashboardAnalytics>('/analytics/dashboard')
    return data
  },

  async getTeamAvailability(department = 'Engineering'): Promise<TeamAvailabilityDay[]> {
    if (USE_MOCK) {
      await delay(400)
      return MOCK_TEAM_AVAILABILITY
    }
    const { data } = await api.get<{ daily_availability: TeamAvailabilityDay[] }>('/analytics/team-availability', { params: { department } })
    return data.daily_availability
  },

  async getAnomalies(): Promise<AnomalyItem[]> {
    if (USE_MOCK) {
      await delay(400)
      return MOCK_ANOMALIES
    }
    const { data } = await api.get<{ items: AnomalyItem[] }>('/ai/anomalies')
    return data.items
  },

  async getRiskSignals(): Promise<RiskSignalItem[]> {
    if (USE_MOCK) {
      await delay(400)
      return MOCK_RISK_SIGNALS
    }
    const { data } = await api.get<{ items: RiskSignalItem[] }>('/ai/risk-signals')
    return data.items
  },

  async getPriorityQueue(): Promise<PriorityQueueItem[]> {
    if (USE_MOCK) {
      await delay(400)
      return MOCK_PRIORITY_QUEUE
    }
    const { data } = await api.get<{ items: PriorityQueueItem[] }>('/hr/priority-queue')
    return data.items
  },
}
