import api, { USE_MOCK } from './api'
import { MOCK_NOTIFICATIONS } from '../mocks/data'
import { delay } from '../utils/format'
import type { Notification } from '../types/api'

export const notificationService = {
  async getAll(unreadOnly = false): Promise<{ items: Notification[]; unread_count: number }> {
    if (USE_MOCK) {
      await delay(300)
      const items = unreadOnly ? MOCK_NOTIFICATIONS.filter((n) => !n.is_read) : MOCK_NOTIFICATIONS
      return { items, unread_count: MOCK_NOTIFICATIONS.filter((n) => !n.is_read).length }
    }
    const { data } = await api.get<{ items: Notification[]; unread_count: number }>('/notifications', { params: { unread_only: unreadOnly } })
    return data
  },

  async markRead(id: number): Promise<void> {
    if (USE_MOCK) {
      await delay(200)
      const n = MOCK_NOTIFICATIONS.find((x) => x.id === id)
      if (n) n.is_read = true
      return
    }
    await api.put(`/notifications/${id}/read`)
  },

  async markAllRead(): Promise<void> {
    if (USE_MOCK) {
      await delay(200)
      MOCK_NOTIFICATIONS.forEach((n) => { n.is_read = true })
      return
    }
    await api.put('/notifications/read-all')
  },
}
