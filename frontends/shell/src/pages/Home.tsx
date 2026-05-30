import { Link } from 'react-router-dom'
import { microFrontends } from '../microfrontends/registry'

export function Home() {
  return (
    <div className="mx-auto max-w-4xl">
      <div className="mb-12">
        <h1 className="text-3xl font-bold tracking-tight text-text lg:text-4xl">
          Добро пожаловать в Platform
        </h1>
        <p className="mt-3 text-base text-text-muted lg:text-lg">
          Платформа на микрофронтендах с Module Federation и React
        </p>
      </div>

      <section>
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-text">
            Доступные модули
          </h2>
          <span className="rounded-full border border-border px-3 py-0.5 text-xs text-text-muted">
            {microFrontends.length} активных
          </span>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          {microFrontends.map((mf) => (
            <Link
              key={mf.name}
              to={mf.routes[0]?.path ?? '/'}
              className="group rounded-xl border border-border bg-surface p-5 transition-all duration-200 hover:-translate-y-0.5 hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5"
            >
              <div className="flex items-start justify-between">
                <h3 className="font-semibold text-text">{mf.displayName}</h3>
                <svg
                  className="size-5 shrink-0 text-text-muted/40 transition-all duration-200 group-hover:translate-x-0.5 group-hover:text-primary"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M5 12h14" />
                  <path d="M12 5l7 7-7 7" />
                </svg>
              </div>
              <ul className="mt-3 space-y-1">
                {mf.routes.map((route) => (
                  <li key={route.path} className="text-sm text-text-muted">
                    <span className="mr-1 text-primary/60">/</span>
                    {route.label}
                  </li>
                ))}
              </ul>
            </Link>
          ))}
        </div>
      </section>
    </div>
  )
}
