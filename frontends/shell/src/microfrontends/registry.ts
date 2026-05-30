import type { MicroFrontend } from './types'

export const microFrontends: MicroFrontend[] = [
  {
    name: 'auth',
    displayName: 'Auth',
    remoteEntry: 'http://localhost:3001/assets/remoteEntry.js',
    moduleName: 'auth/App',
    icon: 'shield',
    routes: [
      { path: '/login', label: 'Login' },
      { path: '/register', label: 'Register' },
    ],
  },
  {
    name: 'dashboard',
    displayName: 'Dashboard',
    remoteEntry: 'http://localhost:3002/assets/remoteEntry.js',
    moduleName: 'dashboard/App',
    icon: 'layout',
    routes: [
      { path: '/dashboard', label: 'Dashboard', icon: 'home' },
    ],
  },
]

export function getMFByName(name: string): MicroFrontend | undefined {
  return microFrontends.find((mf) => mf.name === name)
}

export function getMFsForSidebar(): { path: string; label: string; icon: string }[] {
  const items: { path: string; label: string; icon: string }[] = []
  for (const mf of microFrontends) {
    for (const route of mf.routes) {
      items.push({ path: route.path, label: `${mf.displayName}/${route.label}`, icon: mf.icon })
    }
  }
  return items
}
