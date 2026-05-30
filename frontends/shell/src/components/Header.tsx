import { Link } from 'react-router-dom'
import { useTheme } from '../context/useTheme'

interface HeaderProps {
  onMenuToggle: () => void
}

export function Header({ onMenuToggle }: HeaderProps) {
  const { theme, toggleTheme } = useTheme()

  return (
    <header className="fixed inset-x-0 top-0 z-50 flex h-14 items-center justify-between border-b border-border bg-surface/80 px-4 backdrop-blur-md lg:px-6">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onMenuToggle}
          className="inline-flex items-center justify-center rounded-lg p-2 text-text-muted transition-all duration-200 hover:scale-110 hover:bg-primary/10 hover:text-primary lg:hidden"
          aria-label="Меню"
        >
          <svg className="size-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="3" y1="12" x2="21" y2="12" />
            <line x1="3" y1="18" x2="21" y2="18" />
          </svg>
        </button>

        <Link
          to="/"
          className="flex items-center gap-2.5 rounded-lg px-2 py-1 text-text transition-all duration-200 hover:text-primary hover:scale-[1.02]"
        >
          <svg className="size-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2L2 7l10 5 10-5-10-5z" />
            <path d="M2 17l10 5 10-5" />
            <path d="M2 12l10 5 10-5" />
          </svg>
          <span className="text-sm font-semibold tracking-tight">Platform</span>
        </Link>
      </div>

      <div className="flex items-center gap-0.5">
        <div className="hidden items-center gap-0.5 lg:flex">
          <Link
            to="/dashboard"
            className="rounded-lg px-3 py-1.5 text-sm text-text-muted transition-all duration-200 hover:bg-primary/8 hover:text-primary hover:scale-[1.03]"
          >
            Панель
          </Link>
          <Link
            to="/login"
            className="rounded-lg px-3 py-1.5 text-sm text-text-muted transition-all duration-200 hover:bg-primary/8 hover:text-primary hover:scale-[1.03]"
          >
            Вход
          </Link>
        </div>

        <button
          type="button"
          className="inline-flex items-center justify-center rounded-lg p-2 text-text-muted transition-all duration-200 hover:scale-110 hover:bg-primary/10 hover:text-primary"
          aria-label="Профиль"
        >
          <svg className="size-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="8" r="4" />
            <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" />
          </svg>
        </button>

        <button
          type="button"
          onClick={toggleTheme}
          className="inline-flex items-center justify-center rounded-lg p-2 text-text-muted transition-all duration-200 hover:scale-110 hover:bg-primary/10 hover:text-primary"
          aria-label={theme === 'dark' ? 'Светлая тема' : 'Тёмная тема'}
        >
          {theme === 'dark' ? (
            <svg className="size-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="5" />
              <line x1="12" y1="1" x2="12" y2="3" />
              <line x1="12" y1="21" x2="12" y2="23" />
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
              <line x1="1" y1="12" x2="3" y2="12" />
              <line x1="21" y1="12" x2="23" y2="12" />
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
            </svg>
          ) : (
            <svg className="size-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" />
            </svg>
          )}
        </button>
      </div>
    </header>
  )
}
