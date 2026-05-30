import { NavLink } from 'react-router-dom'
import { getMFsForSidebar } from '../microfrontends/registry'

interface SidebarProps {
  open: boolean
  collapsed: boolean
  onClose: () => void
  onToggleCollapse: () => void
}

function HomeIcon() {
  return (
    <svg className="size-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
      <polyline points="9,22 9,12 15,12 15,22" />
    </svg>
  )
}

function ModuleIcon({ icon }: { icon: string }) {
  switch (icon) {
    case 'shield':
      return (
        <svg className="size-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
        </svg>
      )
    case 'layout':
      return (
        <svg className="size-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="3" width="7" height="7" />
          <rect x="14" y="3" width="7" height="7" />
          <rect x="3" y="14" width="7" height="7" />
          <rect x="14" y="14" width="7" height="7" />
        </svg>
      )
    default:
      return (
        <svg className="size-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
          <line x1="9" y1="3" x2="9" y2="21" />
        </svg>
      )
  }
}

export function Sidebar({ open, collapsed, onClose, onToggleCollapse }: SidebarProps) {
  const navItems = getMFsForSidebar()

  return (
    <>
      {open && (
        <div
          className="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-50 flex flex-col border-r border-border bg-sidebar-bg pt-14 transition-[width] duration-300 ease-out overflow-hidden w-64 ${collapsed ? 'lg:w-14' : 'lg:w-64'} ${open ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0`}
      >
        <div className="flex items-center justify-between border-b border-border px-4 py-3 lg:hidden">
          <span className="text-sm font-semibold text-text">Platform</span>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1.5 text-text-muted hover:bg-bg hover:text-text"
            aria-label="Закрыть меню"
          >
            <svg className="size-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        <div className={`hidden items-center border-b border-border px-3 py-2.5 lg:flex ${collapsed ? 'lg:justify-center lg:px-1' : ''}`}>
          {!collapsed && (
            <span className="mr-auto text-xs font-semibold tracking-tight text-text transition-opacity duration-150">
              Platform
            </span>
          )}
          <button
            type="button"
            onClick={onToggleCollapse}
            className={`rounded-lg p-1 text-text-muted transition-colors hover:bg-bg hover:text-text ${collapsed ? 'lg:p-0' : ''}`}
            aria-label={collapsed ? 'Развернуть меню' : 'Свернуть меню'}
          >
            <svg
              className={`size-4 transition-transform duration-300 ${collapsed ? 'rotate-180' : ''}`}
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M15 18l-6-6 6-6" />
            </svg>
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto p-3">
          <ul className="space-y-0.5">
            <li>
              <NavLink
                to="/"
                end
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center rounded-lg py-2 text-sm transition-colors duration-200 ${collapsed ? 'lg:justify-center lg:gap-0 lg:px-0' : 'gap-3 px-3'} ${
                    isActive
                      ? 'bg-primary/10 text-primary font-medium'
                      : 'text-text-muted hover:bg-primary/5 hover:text-text'
                  }`
                }
              >
                <HomeIcon />
                <span className={`transition-opacity duration-150 ${collapsed ? 'lg:opacity-0 lg:w-0 lg:overflow-hidden' : 'lg:opacity-100'}`}>
                  Главная
                </span>
              </NavLink>
            </li>

            <li className={`pt-4 pb-1 ${collapsed ? 'lg:hidden' : ''}`}>
              <span className="whitespace-nowrap px-3 text-xs font-semibold uppercase tracking-wider text-text-muted/60">
                Модули
              </span>
            </li>

            {navItems.map((item) => (
              <li key={item.path}>
                <NavLink
                  to={item.path}
                  onClick={onClose}
                  className={({ isActive }) =>
                    `flex items-center rounded-lg py-2 text-sm transition-colors duration-200 ${collapsed ? 'lg:justify-center lg:gap-0 lg:px-0' : 'gap-3 px-3'} ${
                      isActive
                        ? 'bg-primary/10 text-primary font-medium'
                        : 'text-text-muted hover:bg-primary/5 hover:text-text'
                    }`
                  }
                >
                  <ModuleIcon icon={item.icon} />
                  <span className={`transition-opacity duration-150 ${collapsed ? 'lg:opacity-0 lg:w-0 lg:overflow-hidden' : 'lg:opacity-100'}`}>
                    {item.label}
                  </span>
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        <div className="border-t border-border p-3">
          <div className={`flex items-center gap-3 rounded-lg px-3 py-2 text-xs text-text-muted ${collapsed ? 'lg:justify-center lg:px-0' : ''}`}>
            <div className="size-2 shrink-0 rounded-full bg-accent ring-1 ring-accent/30" />
          </div>
        </div>
      </aside>
    </>
  )
}
