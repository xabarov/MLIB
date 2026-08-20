import { Suspense } from 'react'
import { useParams, Navigate } from 'react-router-dom'
import { VizPanel } from '../components/layout/VizPanel'
import { findVizByPath } from '../visualizations/registry'

export function VizPage() {
  const { section, topic, vizId } = useParams<{
    section: string
    topic: string
    vizId: string
  }>()

  const path = `/${section}/${topic}/${vizId}`
  const entry = findVizByPath(path)

  if (!entry) {
    return <Navigate to="/algebra/linear-maps/kernel" replace />
  }

  if (entry.status === 'planned') {
    return (
      <div className="flex flex-1 items-center justify-center p-8 text-ink/60">
        <p>Визуализация «{entry.title}» появится позже.</p>
      </div>
    )
  }

  const Scene = entry.component

  if (entry.kind === 'mission') {
    return (
      <Suspense
        fallback={
          <div className="flex flex-1 items-center justify-center p-8 text-sm font-medium text-ink/60">
            Загружаем миссию...
          </div>
        }
      >
        <Scene />
      </Suspense>
    )
  }

  return (
    <Suspense
      fallback={
        <div className="flex flex-1 items-center justify-center p-8 text-sm font-medium text-ink/60">
          Загружаем визуализацию...
        </div>
      }
    >
      <VizPanel
        meta={entry.meta}
        scene={<Scene />}
        showSceneControls={entry.id === 'kernel'}
      />
    </Suspense>
  )
}
