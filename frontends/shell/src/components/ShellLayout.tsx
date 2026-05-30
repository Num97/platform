import { useState, useCallback, useEffect } from 'react'
import { Outlet } from 'react-router-dom'
import { Header } from './Header'
import { Sidebar } from './Sidebar'

function getCollapsed(): boolean {
  const stored = localStorage.getItem('shell-sidebar-collapsed')
  if (stored === null) return true
  return stored === '1'
}

export function ShellLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [collapsed, setCollapsed] = useState(getCollapsed)

  useEffect(() => {
    localStorage.setItem('shell-sidebar-collapsed', collapsed ? '1' : '0')
  }, [collapsed])

  const toggleCollapsed = useCallback(() => setCollapsed((v) => !v), [])

  return (
    <div className="flex min-h-screen flex-col bg-bg text-text">
      <Header onMenuToggle={() => setSidebarOpen((v) => !v)} />
      <div className="flex flex-1">
        <div
          aria-hidden
          className={`hidden shrink-0 transition-[width] duration-300 ease-out lg:block ${collapsed ? 'lg:w-14' : 'lg:w-64'}`}
        />
        <Sidebar
          open={sidebarOpen}
          collapsed={collapsed}
          onClose={() => setSidebarOpen(false)}
          onToggleCollapse={toggleCollapsed}
        />
        <main className="min-w-0 flex-1 overflow-y-auto px-4 pt-14 pb-6 lg:px-8 lg:pt-14 lg:pb-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
