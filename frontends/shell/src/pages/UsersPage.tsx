import { useState, useEffect, type FormEvent } from 'react'
import { useAuth } from '../context/useAuth'
import * as usersApi from '../api/users'
import { AuthApiError } from '../api/auth'
import type { User } from '../api/types'

const ROLES = [
  { value: 'user', label: 'Пользователь' },
  { value: 'manager', label: 'Менеджер' },
  { value: 'admin', label: 'Админ' },
]

export function UsersPage() {
  const { user: currentUser, register } = useAuth()
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [editingId, setEditingId] = useState<number | null>(null)
  const [saveError, setSaveError] = useState('')

  const [showCreate, setShowCreate] = useState(false)
  const [createError, setCreateError] = useState('')
  const [createSubmitting, setCreateSubmitting] = useState(false)
  const [createEmail, setCreateEmail] = useState('')
  const [createUsername, setCreateUsername] = useState('')
  const [createPassword, setCreatePassword] = useState('')
  const [createPasswordConfirm, setCreatePasswordConfirm] = useState('')
  const [createRole, setCreateRole] = useState('user')

  const [editForm, setEditForm] = useState<{ email: string; full_name: string; role: string; is_active: boolean }>({
    email: '',
    full_name: '',
    role: 'user',
    is_active: true,
  })

  const loadUsers = async () => {
    try {
      const data = await usersApi.getUsers()
      setUsers(data)
    } catch {
      setError('Не удалось загрузить пользователей')
    }
  }

  useEffect(() => {
    let cancelled = false
    const fetch = async () => {
      try {
        const data = await usersApi.getUsers()
        if (!cancelled) {
          setUsers(data)
          setLoading(false)
        }
      } catch {
        if (!cancelled) {
          setError('Не удалось загрузить пользователей')
          setLoading(false)
        }
      }
    }
    fetch()
    return () => { cancelled = true }
  }, [])

  const startEdit = (u: User) => {
    setEditingId(u.id)
    setSaveError('')
    setEditForm({
      email: u.email,
      full_name: u.full_name ?? '',
      role: u.role,
      is_active: u.is_active ?? true,
    })
  }

  const cancelEdit = () => {
    setEditingId(null)
    setSaveError('')
  }

  const handleSave = async (userId: number) => {
    setSaveError('')
    try {
      const updated = await usersApi.updateUser(userId, {
        email: editForm.email,
        full_name: editForm.full_name || undefined,
        role: editForm.role,
        is_active: editForm.is_active,
      })
      setUsers((prev) => prev.map((u) => (u.id === userId ? updated : u)))
      setEditingId(null)
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : 'Ошибка сохранения')
    }
  }

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault()
    setCreateError('')
    setCreateSubmitting(true)
    try {
      await register(createEmail, createUsername, createPassword, createPasswordConfirm, createRole)
      setShowCreate(false)
      setCreateEmail('')
      setCreateUsername('')
      setCreatePassword('')
      setCreatePasswordConfirm('')
      setCreateRole('user')
      await loadUsers()
    } catch (err) {
      if (err instanceof AuthApiError) {
        setCreateError(err.detail)
      } else {
        setCreateError(err instanceof Error ? err.message : 'Ошибка создания')
      }
    } finally {
      setCreateSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="size-8 animate-spin rounded-full border-[3px] border-border border-t-primary" />
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-4xl">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text">Пользователи</h1>
          <p className="mt-1 text-sm text-text-muted">
            Управление пользователями платформы
          </p>
        </div>
        <button
          type="button"
          onClick={() => setShowCreate(true)}
          className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-primary-hover"
        >
          Создать пользователя
        </button>
      </div>

      {error && (
        <div className="mb-6 rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {showCreate && (
        <div className="mb-6 rounded-xl border border-border bg-surface p-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-semibold text-text">Создание пользователя</h2>
            <button
              type="button"
              onClick={() => setShowCreate(false)}
              className="rounded-lg p-1.5 text-text-muted hover:bg-bg hover:text-text"
            >
              <svg className="size-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>

          {createError && (
            <div className="mb-4 rounded-lg border border-red-500/20 bg-red-500/10 px-3 py-2 text-sm text-red-400">
              {createError}
            </div>
          )}

          <form onSubmit={handleCreate} className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-1 block text-sm font-medium text-text">Email</label>
                <input
                  type="email"
                  value={createEmail}
                  onChange={(e) => setCreateEmail(e.target.value)}
                  required
                  className="w-full rounded-lg border border-border bg-bg px-3 py-2 text-sm text-text outline-none focus:border-primary"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-text">Имя пользователя</label>
                <input
                  type="text"
                  value={createUsername}
                  onChange={(e) => setCreateUsername(e.target.value)}
                  required
                  minLength={4}
                  pattern="^[a-zA-Z0-9_-]+$"
                  className="w-full rounded-lg border border-border bg-bg px-3 py-2 text-sm text-text outline-none focus:border-primary"
                />
              </div>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-1 block text-sm font-medium text-text">Пароль</label>
                <input
                  type="password"
                  value={createPassword}
                  onChange={(e) => setCreatePassword(e.target.value)}
                  required
                  minLength={4}
                  className="w-full rounded-lg border border-border bg-bg px-3 py-2 text-sm text-text outline-none focus:border-primary"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-text">Подтверждение пароля</label>
                <input
                  type="password"
                  value={createPasswordConfirm}
                  onChange={(e) => setCreatePasswordConfirm(e.target.value)}
                  required
                  minLength={4}
                  className="w-full rounded-lg border border-border bg-bg px-3 py-2 text-sm text-text outline-none focus:border-primary"
                />
              </div>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-text">Роль</label>
              <select
                value={createRole}
                onChange={(e) => setCreateRole(e.target.value)}
                className="w-full rounded-lg border border-border bg-bg px-3 py-2 text-sm text-text outline-none focus:border-primary"
              >
                {ROLES.map((r) => (
                  <option key={r.value} value={r.value}>{r.label}</option>
                ))}
              </select>
            </div>
            <button
              type="submit"
              disabled={createSubmitting}
              className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-primary-hover disabled:opacity-60"
            >
              {createSubmitting ? 'Создание...' : 'Создать'}
            </button>
          </form>
        </div>
      )}

      <div className="rounded-xl border border-border bg-surface overflow-hidden">
        {saveError && (
          <div className="border-b border-red-500/20 bg-red-500/10 px-4 py-2 text-sm text-red-400">
            {saveError}
          </div>
        )}
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left text-text-muted">
              <th className="px-4 py-3 font-medium">ID</th>
              <th className="px-4 py-3 font-medium">Имя</th>
              <th className="px-4 py-3 font-medium">Email</th>
              <th className="px-4 py-3 font-medium">Роль</th>
              <th className="px-4 py-3 font-medium">Статус</th>
              <th className="px-4 py-3 font-medium w-20" />
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className="border-b border-border last:border-b-0 hover:bg-bg/50">
                <td className="px-4 py-3 text-text-muted">{u.id}</td>
                <td className="px-4 py-3 text-text font-medium">{u.username}</td>
                <td className="px-4 py-3 text-text-muted">{u.email}</td>
                {editingId === u.id ? (
                  <>
                    <td className="px-4 py-3">
                      <select
                        value={editForm.role}
                        onChange={(e) => setEditForm((f) => ({ ...f, role: e.target.value }))}
                        className="w-full rounded border border-border bg-bg px-2 py-1 text-xs text-text outline-none focus:border-primary"
                      >
                        {ROLES.map((r) => (
                          <option key={r.value} value={r.value}>{r.label}</option>
                        ))}
                      </select>
                    </td>
                    <td className="px-4 py-3">
                      <select
                        value={editForm.is_active ? 'active' : 'inactive'}
                        onChange={(e) => setEditForm((f) => ({ ...f, is_active: e.target.value === 'active' }))}
                        className="w-full rounded border border-border bg-bg px-2 py-1 text-xs text-text outline-none focus:border-primary"
                      >
                        <option value="active">Активен</option>
                        <option value="inactive">Неактивен</option>
                      </select>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-1">
                        <button
                          type="button"
                          onClick={() => handleSave(u.id)}
                          className="rounded px-2 py-1 text-xs font-medium text-primary hover:bg-primary/10"
                        >
                          Сохранить
                        </button>
                        <button
                          type="button"
                          onClick={cancelEdit}
                          className="rounded px-2 py-1 text-xs text-text-muted hover:bg-bg"
                        >
                          Отмена
                        </button>
                      </div>
                    </td>
                  </>
                ) : (
                  <>
                    <td className="px-4 py-3">
                      <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                        u.role === 'admin'
                          ? 'bg-red-500/10 text-red-400'
                          : u.role === 'manager'
                            ? 'bg-yellow-500/10 text-yellow-500'
                            : 'bg-primary/10 text-primary'
                      }`}>
                        {ROLES.find((r) => r.value === u.role)?.label ?? u.role}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                        u.is_active
                          ? 'bg-green-500/10 text-green-400'
                          : 'bg-red-500/10 text-red-400'
                      }`}>
                        {u.is_active ? 'Активен' : 'Неактивен'}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {u.id !== currentUser?.id && (
                        <button
                          type="button"
                          onClick={() => startEdit(u)}
                          className="rounded px-2 py-1 text-xs text-text-muted hover:bg-bg hover:text-text"
                        >
                          Изменить
                        </button>
                      )}
                    </td>
                  </>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
