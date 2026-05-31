import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ThemeProvider } from './context/ThemeProvider'
import { AuthProvider } from './context/AuthProvider'
import { ShellLayout } from './components/ShellLayout'
import { AuthGuard } from './components/guards/AuthGuard'
import { AdminGuard } from './components/guards/AdminGuard'
import { GuestGuard } from './components/guards/GuestGuard'
import { Home } from './pages/Home'
import { LoginPage } from './pages/LoginPage'
import { UsersPage } from './pages/UsersPage'
import { NotFound } from './pages/NotFound'
import { microFrontends } from './microfrontends/registry'
import { RemoteApp } from './components/RemoteApp'

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route element={<ShellLayout />}>
              <Route
                index
                element={
                  <AuthGuard>
                    <Home />
                  </AuthGuard>
                }
              />
              <Route
                path="/login"
                element={
                  <GuestGuard>
                    <LoginPage />
                  </GuestGuard>
                }
              />
              <Route
                path="/users"
                element={
                  <AdminGuard>
                    <UsersPage />
                  </AdminGuard>
                }
              />
              {microFrontends.map((mf) =>
                mf.routes.map((route) => (
                  <Route
                    key={route.path}
                    path={route.path}
                    element={
                      <AuthGuard>
                        <RemoteApp mf={mf} />
                      </AuthGuard>
                    }
                  />
                )),
              )}
              <Route path="*" element={<NotFound />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App
