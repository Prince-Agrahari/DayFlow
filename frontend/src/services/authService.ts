import api, { USE_MOCK } from './api'
import { MOCK_USERS } from '../mocks/data'
import { TOKEN_KEY, USER_KEY } from '../utils/constants'
import { delay } from '../utils/format'
import type { LoginResponse, SignupRequest, User } from '../types/api'

export const authService = {
  async login(email: string, password: string): Promise<LoginResponse> {
    if (USE_MOCK) {
      await delay(600)
      const user = Object.values(MOCK_USERS).find((u) => u.email === email && u.password === password)
      if (!user) throw new Error('Invalid email or password')
      const { password: _, ...safeUser } = user
      const response: LoginResponse = {
        access_token: `mock-jwt-${user.id}`, token_type: 'bearer', expires_in: 3600, user: safeUser,
      }
      localStorage.setItem(TOKEN_KEY, response.access_token)
      localStorage.setItem(USER_KEY, JSON.stringify(safeUser))
      return response
    }
    const { data } = await api.post<LoginResponse>('/auth/login', { email, password })
    localStorage.setItem(TOKEN_KEY, data.access_token)
    localStorage.setItem(USER_KEY, JSON.stringify(data.user))
    return data
  },

  async signup(payload: SignupRequest): Promise<User> {
    if (USE_MOCK) {
      await delay(600)
      const user: User = {
        id: `u-${Date.now()}`, email: payload.email, full_name: payload.full_name,
        role: payload.role ?? 'EMPLOYEE', employee_id: `EMP${String(Date.now()).slice(-3)}`,
      }
      return user
    }
    const { data } = await api.post<User>('/auth/signup', payload)
    return data
  },

  async me(): Promise<User> {
    const cached = localStorage.getItem(USER_KEY)
    if (USE_MOCK && cached) return JSON.parse(cached)
    const { data } = await api.get<User>('/auth/me')
    localStorage.setItem(USER_KEY, JSON.stringify(data))
    return data
  },

  logout(): void {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  },

  getStoredUser(): User | null {
    const raw = localStorage.getItem(USER_KEY)
    return raw ? JSON.parse(raw) : null
  },

  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY)
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem(TOKEN_KEY)
  },
}
