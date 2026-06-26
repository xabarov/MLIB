import { Suspense, lazy } from 'react'
import { Route, Routes } from 'react-router-dom'
import { AppShell } from './components/layout/AppShell'
import { CourseMapPage } from './pages/CourseMapPage'
import { NotFound } from './pages/NotFound'

// VizPage pulls in the mission infrastructure (VizPanel, MathBlock, KaTeX) and
// every lazy scene. Keeping it lazy means the initial map route does not ship
// KaTeX in the entry chunk.
const VizPage = lazy(() => import('./pages/VizPage').then((module) => ({ default: module.VizPage })))

function VizFallback() {
  return (
    <div className="flex flex-1 items-center justify-center p-8 text-sm font-medium text-ink/60">
      Загружаем миссию...
    </div>
  )
}

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<CourseMapPage />} />
        <Route path="map" element={<CourseMapPage />} />
        <Route
          path=":section/:topic/:vizId"
          element={
            <Suspense fallback={<VizFallback />}>
              <VizPage />
            </Suspense>
          }
        />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}
