import { Route, Routes } from 'react-router-dom'
import { AppShell } from './components/layout/AppShell'
import { CourseMapPage } from './pages/CourseMapPage'
import { NotFound } from './pages/NotFound'
import { VizPage } from './pages/VizPage'

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<CourseMapPage />} />
        <Route path="map" element={<CourseMapPage />} />
        <Route path=":section/:topic/:vizId" element={<VizPage />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}
