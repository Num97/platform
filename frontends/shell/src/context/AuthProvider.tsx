import { useCallback, useEffect, useRef, useState, type ReactNode } from 'react'
import { AuthContext } from './AuthContext'
import * as authApi from '../api/auth'
import type { User } from '../api/types'

const ACCESS_TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'
const EXPIRES_AT_KEY = 'token_expires_at'

function getStoredTokens(): { accessToken: string; refreshToken: string; expiresAt: number } | null {
  const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY)
  const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
  const expiresAtStr = localStorage.getItem(EXPIRES_AT_KEY)
  if (!accessToken || !refreshToken || !expiresAtStr) return null
  return { accessToken, refreshToken, expiresAt: Number(expiresAtStr) }
}

function setStoredTokens(accessToken: string, refreshToken: string, expiresIn: number) {
  const expiresAt = Date.now() + expiresIn * 1000
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken)
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
  localStorage.setItem(EXPIRES_AT_KEY, String(expiresAt))
}

function clearStoredTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  localStorage.removeItem(EXPIRES_AT_KEY)
}

function getExpiresAt(): number {
  const val = localStorage.getItem(EXPIRES_AT_KEY)
  return val ? Number(val) : 0
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const refreshTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const attemptRefreshRef = useRef<() => Promise<void>>(async () => {})

  const clearRefreshTimer = useCallback(() => {
    if (refreshTimerRef.current) {
      clearTimeout(refreshTimerRef.current)
      refreshTimerRef.current = null
    }
  }, [])

  const scheduleRefresh = useCallback((expiresAt: number) => {
    clearRefreshTimer()
    const delay = expiresAt - Date.now() - 60_000
    if (delay <= 0) return
    refreshTimerRef.current = setTimeout(() => {
      attemptRefreshRef.current()
    }, delay)
  }, [clearRefreshTimer])

  const attemptRefresh = useCallback(async () => {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
    if (!refreshToken) {
      setUser(null)
      return
    }
    try {
      const tokens = await authApi.refreshToken(refreshToken)
      setStoredTokens(tokens.access_token, tokens.refresh_token, tokens.expires_in)
      scheduleRefresh(getExpiresAt())
      const me = await authApi.getMe()
      setUser(me)
    } catch {
      clearStoredTokens()
      clearRefreshTimer()
      setUser(null)
    }
  }, [scheduleRefresh, clearRefreshTimer])

  useEffect(() => {
    attemptRefreshRef.current = attemptRefresh
  }, [attemptRefresh])

  useEffect(() => {
    const init = async () => {
      const stored = getStoredTokens()
      if (!stored) {
        setIsLoading(false)
        return
      }

      if (Date.now() >= stored.expiresAt) {
        await attemptRefreshRef.current()
        setIsLoading(false)
        return
      }

      try {
        const me = await authApi.getMe()
        setUser(me)
        scheduleRefresh(stored.expiresAt)
      } catch {
        await attemptRefreshRef.current()
      } finally {
        setIsLoading(false)
      }
    }

    init()

    return () => {
      clearRefreshTimer()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const login = useCallback(async (username: string, password: string, rememberMe = false) => {
    const tokens = await authApi.login({ username, password, remember_me: rememberMe })
    setStoredTokens(tokens.access_token, tokens.refresh_token, tokens.expires_in)
    scheduleRefresh(getExpiresAt())
    const me = await authApi.getMe()
    setUser(me)
  }, [scheduleRefresh])

  const register = useCallback(async (
    email: string,
    username: string,
    password: string,
    passwordConfirm: string,
    role?: string,
  ) => {
    await authApi.register({
      email,
      username,
      password,
      password_confirm: passwordConfirm,
      role,
    })
  }, [])

  const logout = useCallback(async () => {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
    clearStoredTokens()
    clearRefreshTimer()
    setUser(null)
    if (refreshToken) {
      try {
        await authApi.logout(refreshToken)
      } catch {
        // ignore — token may already be invalid
      }
    }
  }, [clearRefreshTimer])

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: user !== null,
        isLoading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}
