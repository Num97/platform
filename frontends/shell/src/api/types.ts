export interface User {
  id: number
  email: string
  username: string
  full_name: string | null
  role: string
  status: string
  is_active: boolean | null
  created_at: string
  last_login: string | null
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface LoginRequest {
  username: string
  password: string
  remember_me: boolean
}

export interface RegisterRequest {
  email: string
  username: string
  password: string
  password_confirm: string
  full_name?: string
  role?: string
}

export interface ApiError {
  detail: string
  status: number
}
