import type { ComponentType } from 'react'

export interface MicroFrontendRoute {
  path: string
  label: string
  icon?: string
}

export interface MicroFrontend {
  name: string
  displayName: string
  remoteEntry: string
  moduleName: string
  icon: string
  routes: MicroFrontendRoute[]
}

export interface RemoteComponent {
  url: string
  scope: string
  module: string
}

export interface RegisteredMF extends MicroFrontend {
  Component: ComponentType<unknown>
}
