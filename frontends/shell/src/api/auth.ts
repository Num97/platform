import { API_BASE_URL } from './config'
import type { AuthTokens, LoginRequest, RegisterRequest, User } from './types'

class AuthApiError extends Error {
  status: number
  detail: string

  constructor(status: number, detail: string) {
    super(detail)
    this.name = 'AuthApiError'
    this.status = status
    this.detail = detail
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('access_token')
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> | undefined),
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  })

  if (!response.ok) {
    let detail = `HTTP ${response.status}`
    try {
      const body = await response.json()
      const d = body.detail
      if (Array.isArray(d)) {
        detail = d.map((e: { loc: string[]; msg: string }) => e.msg).join('; ')
      } else if (typeof d === 'string') {
        detail = d
      }
    } catch {
      // non-JSON response
    }
    throw new AuthApiError(response.status, detail)
  }

  return response.json() as Promise<T>
}

export async function login(data: LoginRequest): Promise<AuthTokens> {
  const tokens = await request<AuthTokens>('/api/v1/auth/login', {
    method: 'POST',
    body: JSON.stringify(data),
  })
  return tokens
}

export async function register(data: RegisterRequest): Promise<{ message: string; user_id: number; email: string; username: string }> {
  return request('/api/v1/auth/register', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function refreshToken(refresh_token: string): Promise<AuthTokens> {
  return request<AuthTokens>('/api/v1/auth/refresh', {
    method: 'POST',
    body: JSON.stringify({ refresh_token }),
  })
}

export async function logout(refresh_token: string): Promise<void> {
  await request('/api/v1/auth/logout', {
    method: 'POST',
    body: JSON.stringify({ refresh_token }),
  })
}

export async function getMe(): Promise<User> {
  return request<User>('/api/v1/auth/me')
}

export { AuthApiError }
