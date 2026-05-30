declare module 'auth/App' {
  const App: React.ComponentType
  export default App
}

declare module 'auth/*' {
  const mod: unknown
  export default mod
}

declare module 'dashboard/App' {
  const App: React.ComponentType
  export default App
}

declare module 'dashboard/*' {
  const mod: unknown
  export default mod
}
