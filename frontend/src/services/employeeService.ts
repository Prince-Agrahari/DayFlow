import api, { USE_MOCK } from './api'
import { getMockEmployee360, MOCK_EMPLOYEES } from '../mocks/data'
import { delay } from '../utils/format'
import type { Employee, Employee360, PaginatedResponse } from '../types/api'

export const employeeService = {
  async getAll(params?: { search?: string; department?: string; page?: number; page_size?: number }): Promise<PaginatedResponse<Employee>> {
    if (USE_MOCK) {
      await delay(400)
      let items = [...MOCK_EMPLOYEES]
      if (params?.search) {
        const q = params.search.toLowerCase()
        items = items.filter((e) => e.full_name.toLowerCase().includes(q) || e.employee_id.toLowerCase().includes(q))
      }
      if (params?.department) items = items.filter((e) => e.department === params.department)
      const page = params?.page ?? 1
      const pageSize = params?.page_size ?? 10
      const start = (page - 1) * pageSize
      return { items: items.slice(start, start + pageSize), total: items.length, page, page_size: pageSize }
    }
    const { data } = await api.get<PaginatedResponse<Employee>>('/employees', { params })
    return data
  },

  async getById(id: string): Promise<Employee> {
    if (USE_MOCK) {
      await delay(300)
      const emp = MOCK_EMPLOYEES.find((e) => e.id === id || e.employee_id === id)
      if (!emp) throw new Error('Employee not found')
      return emp
    }
    const { data } = await api.get<Employee>(`/employees/${id}`)
    return data
  },

  async update(id: string, payload: Partial<Employee>): Promise<Employee> {
    if (USE_MOCK) {
      await delay(400)
      const emp = MOCK_EMPLOYEES.find((e) => e.id === id || e.employee_id === id)
      if (!emp) throw new Error('Employee not found')
      return { ...emp, ...payload }
    }
    const { data } = await api.put<Employee>(`/employees/${id}`, payload)
    return data
  },

  async get360(id: string): Promise<Employee360> {
    if (USE_MOCK) {
      await delay(500)
      const data = getMockEmployee360(id)
      if (!data) throw new Error('Employee not found')
      return data
    }
    const { data } = await api.get<Employee360>(`/hr/employees/${id}/360`)
    return data
  },
}
