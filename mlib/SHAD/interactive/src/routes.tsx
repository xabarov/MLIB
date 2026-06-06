import { Route, Routes } from 'react-router-dom'
import { AppShell } from './components/layout/AppShell'
import { HomeRedirect } from './pages/HomeRedirect'
import { NotFound } from './pages/NotFound'
import { VizPage } from './pages/VizPage'

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<HomeRedirect />} />
        <Route path=":section/:topic/:vizId" element={<VizPage />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}
