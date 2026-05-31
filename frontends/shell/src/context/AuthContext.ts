import { createContext } from 'react'
import type { User } from '../api/types'

export interface AuthContextValue {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (username: string, password: string, rememberMe?: boolean) => Promise<void>
  register: (email: string, username: string, password: string, passwordConfirm: string, role?: string) => Promise<void>
  logout: () => Promise<void>
}

export const AuthContext = createContext<AuthContextValue>({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  login: async () => {},
  register: async () => {},
  logout: async () => {},
})
