import { Suspense, lazy, Component, type ReactNode, type ComponentType } from 'react'
import type { MicroFrontend } from '../microfrontends/types'
import { microFrontends } from '../microfrontends/registry'

const remoteMap = new Map<string, ComponentType<unknown>>()

for (const mf of microFrontends) {
  remoteMap.set(
    mf.name,
    lazy(() => import(/* @vite-ignore */ mf.moduleName)),
  )
}

function getComponent(mf: MicroFrontend): ComponentType<unknown> {
  return remoteMap.get(mf.name) ?? (() => null)
}

function RemoteFallback({ name }: { name: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-text-muted">
      <div className="mb-4 size-8 animate-spin rounded-full border-[3px] border-border border-t-primary" />
      <p className="text-sm">Загрузка {name}...</p>
    </div>
  )
}

function RemoteError({ name }: { name: string }) {
  return (
    <div className="mx-auto mt-20 max-w-md rounded-xl border border-border bg-surface p-10 text-center">
      <div className="mx-auto mb-4 flex size-12 items-center justify-center rounded-full bg-red-500/10">
        <svg className="size-6 text-red-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
      </div>
      <h2 className="text-lg font-semibold text-text">
        Ошибка загрузки {name}
      </h2>
      <p className="mt-2 text-sm text-text-muted">
        Микрофронтенд не запущен или недоступен.
      </p>
    </div>
  )
}

interface ErrorBoundaryProps {
  fallback: ReactNode
  children: ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true }
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback
    }
    return this.props.children
  }
}

/* eslint-disable react-hooks/static-components -- dynamic MF loading from registry */
export function RemoteApp({ mf }: { mf: MicroFrontend }) {
  const Component = getComponent(mf)

  return (
    <ErrorBoundary fallback={<RemoteError name={mf.displayName} />}>
      <Suspense fallback={<RemoteFallback name={mf.displayName} />}>
        <Component />
      </Suspense>
    </ErrorBoundary>
  )
}
/* eslint-enable react-hooks/static-components */
