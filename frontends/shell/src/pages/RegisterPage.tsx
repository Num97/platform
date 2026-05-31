import { useState, type FormEvent } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { useAuth } from '../context/useAuth'
import { AuthApiError } from '../api/auth'

export function RegisterPage() {
  const { register, isAuthenticated, isLoading } = useAuth()
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [passwordConfirm, setPasswordConfirm] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="size-8 animate-spin rounded-full border-[3px] border-border border-t-primary" />
      </div>
    )
  }

  if (isAuthenticated) {
    return <Navigate to="/" replace />
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setSubmitting(true)

    try {
      await register(email, username, password, passwordConfirm)
      setSuccess(true)
    } catch (err) {
      if (err instanceof AuthApiError) {
        setError(err.detail)
      } else {
        setError('Ошибка сети. Попробуйте позже.')
      }
    } finally {
      setSubmitting(false)
    }
  }

  if (success) {
    return (
      <div className="mx-auto mt-8 max-w-md">
        <div className="rounded-xl border border-border bg-surface p-8 text-center">
          <div className="mx-auto mb-4 flex size-12 items-center justify-center rounded-full bg-green-500/10">
            <svg className="size-6 text-green-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="20 6 9 17 4 12" />
            </svg>
          </div>
          <h1 className="text-xl font-semibold text-text">Регистрация успешна</h1>
          <p className="mt-2 text-sm text-text-muted">
            Аккаунт создан. Теперь вы можете войти.
          </p>
          <Link
            to="/login"
            className="mt-6 inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-2.5 text-sm font-medium text-white transition-colors hover:bg-primary-hover"
          >
            Перейти ко входу
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="mx-auto mt-8 max-w-md">
      <div className="rounded-xl border border-border bg-surface p-8">
        <div className="mb-8 text-center">
          <h1 className="text-2xl font-bold text-text">Регистрация</h1>
          <p className="mt-2 text-sm text-text-muted">
            Создайте аккаунт для доступа к платформе
          </p>
        </div>

        {error && (
          <div className="mb-6 rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-400">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label htmlFor="email" className="mb-1.5 block text-sm font-medium text-text">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoFocus
              className="w-full rounded-lg border border-border bg-bg px-4 py-2.5 text-sm text-text placeholder:text-text-muted/60 outline-none transition-colors focus:border-primary focus:ring-1 focus:ring-primary"
              placeholder="ivan@example.com"
            />
          </div>

          <div>
            <label htmlFor="reg-username" className="mb-1.5 block text-sm font-medium text-text">
              Имя пользователя
            </label>
            <input
              id="reg-username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              minLength={4}
              maxLength={100}
              pattern="^[a-zA-Z0-9_-]+$"
              className="w-full rounded-lg border border-border bg-bg px-4 py-2.5 text-sm text-text placeholder:text-text-muted/60 outline-none transition-colors focus:border-primary focus:ring-1 focus:ring-primary"
              placeholder="ivan_ivanov"
            />
          </div>

          <div>
            <label htmlFor="reg-password" className="mb-1.5 block text-sm font-medium text-text">
              Пароль
            </label>
            <input
              id="reg-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={4}
              className="w-full rounded-lg border border-border bg-bg px-4 py-2.5 text-sm text-text placeholder:text-text-muted/60 outline-none transition-colors focus:border-primary focus:ring-1 focus:ring-primary"
              placeholder="Минимум 4 символа"
            />
          </div>

          <div>
            <label htmlFor="reg-password-confirm" className="mb-1.5 block text-sm font-medium text-text">
              Подтверждение пароля
            </label>
            <input
              id="reg-password-confirm"
              type="password"
              value={passwordConfirm}
              onChange={(e) => setPasswordConfirm(e.target.value)}
              required
              minLength={4}
              className="w-full rounded-lg border border-border bg-bg px-4 py-2.5 text-sm text-text placeholder:text-text-muted/60 outline-none transition-colors focus:border-primary focus:ring-1 focus:ring-primary"
              placeholder="Повторите пароль"
            />
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-lg bg-primary py-2.5 text-sm font-medium text-white transition-colors hover:bg-primary-hover disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {submitting ? 'Регистрация...' : 'Зарегистрироваться'}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-text-muted">
          Уже есть аккаунт?{' '}
          <Link to="/login" className="font-medium text-primary hover:text-primary-hover">
            Войти
          </Link>
        </p>
      </div>
    </div>
  )
}
