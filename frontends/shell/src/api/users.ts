import { API_BASE_URL } from './config'
import type { User } from './types'

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
    throw new Error(detail)
  }

  return response.json() as Promise<T>
}

export async function getUsers(): Promise<User[]> {
  return request<User[]>('/api/v1/auth/users/')
}

export async function getUser(userId: number): Promise<User> {
  return request<User>(`/api/v1/auth/users/${userId}`)
}

export async function updateUser(userId: number, data: {
  email?: string
  full_name?: string
  role?: string
  is_active?: boolean
}): Promise<User> {
  return request<User>(`/api/v1/auth/users/${userId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}
