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

  if (!entry.available || !entry.component) {
    return (
      <div className="flex flex-1 items-center justify-center p-8 text-ink/60">
        <p>Визуализация «{entry.title}» появится позже.</p>
      </div>
    )
  }

  const Scene = entry.component

  return (
    <VizPanel
      meta={entry.meta}
      scene={<Scene />}
      showSceneControls={entry.id === 'kernel'}
    />
  )
}
