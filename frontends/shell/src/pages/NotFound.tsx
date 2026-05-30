import { Link } from 'react-router-dom'

export function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <span className="text-8xl font-extrabold tracking-tight text-primary/20">
        404
      </span>
      <h1 className="-mt-6 text-2xl font-semibold text-text">
        Страница не найдена
      </h1>
      <p className="mt-2 text-sm text-text-muted">
        Запрашиваемая страница не существует или была перемещена.
      </p>
      <Link
        to="/"
        className="mt-8 inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-primary-hover"
      >
        <svg className="size-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M19 12H5" />
          <path d="M12 19l-7-7 7-7" />
        </svg>
        На главную
      </Link>
    </div>
  )
}
