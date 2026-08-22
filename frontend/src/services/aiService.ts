import api, { USE_MOCK } from './api'
import { MOCK_ASSISTANT_RESPONSES, MOCK_COPILOT_RESPONSES } from '../mocks/data'
import { delay } from '../utils/format'
import type { AssistantResponse, CopilotResponse } from '../types/api'

function matchCopilotResponse(question: string): CopilotResponse {
  const q = question.toLowerCase()
  if (q.includes('attention') || q.includes('needs')) return MOCK_COPILOT_RESPONSES['who needs attention']
  if (q.includes('unusual') || q.includes('anomaly') || q.includes('anomalies')) return MOCK_COPILOT_RESPONSES['unusual attendance']
  if (q.includes('absenteeism') || q.includes('department')) return MOCK_COPILOT_RESPONSES['absenteeism']
  if (q.includes('priorit')) return MOCK_COPILOT_RESPONSES['prioritize']
  return {
    answer: 'I can help you with HR insights. Try asking about employees needing attention, attendance anomalies, department absenteeism, or daily priorities.',
    sources: [{ type: 'general', count: 0 }],
  }
}

function matchAssistantResponse(question: string): AssistantResponse {
  const q = question.toLowerCase()
  if (q.includes('leave') && (q.includes('how many') || q.includes('balance'))) return MOCK_ASSISTANT_RESPONSES['leaves']
  if (q.includes('attendance')) return MOCK_ASSISTANT_RESPONSES['attendance']
  if (q.includes('status')) return MOCK_ASSISTANT_RESPONSES['leave status']
  if (q.includes('salary') || q.includes('pay')) return MOCK_ASSISTANT_RESPONSES['salary']
  return {
    answer: 'I can help with your leaves, attendance, leave status, and salary. What would you like to know?',
    data_scope: 'employee_self',
  }
}

export const aiService = {
  async askCopilot(question: string): Promise<CopilotResponse> {
    if (USE_MOCK) {
      await delay(800)
      return matchCopilotResponse(question)
    }
    const { data } = await api.post<CopilotResponse>('/ai/copilot', { question })
    return data
  },

  async askAssistant(question: string): Promise<AssistantResponse> {
    if (USE_MOCK) {
      await delay(800)
      return matchAssistantResponse(question)
    }
    const { data } = await api.post<AssistantResponse>('/ai/assistant', { question })
    return data
  },
}
