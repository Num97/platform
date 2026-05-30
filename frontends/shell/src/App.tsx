import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ThemeProvider } from './context/ThemeProvider'
import { ShellLayout } from './components/ShellLayout'
import { Home } from './pages/Home'
import { NotFound } from './pages/NotFound'
import { microFrontends } from './microfrontends/registry'
import { RemoteApp } from './components/RemoteApp'

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<ShellLayout />}>
            <Route index element={<Home />} />
            {microFrontends.map((mf) =>
              mf.routes.map((route) => (
                <Route
                  key={route.path}
                  path={route.path}
                  element={<RemoteApp mf={mf} />}
                />
              )),
            )}
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  )
}

export default App
