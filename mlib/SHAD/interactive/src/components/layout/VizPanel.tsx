import { RotateCcw, Layers } from 'lucide-react'
import type { ReactNode } from 'react'
import { MathBlock } from '../math/MathBlock'
import type { VizMeta } from '../../visualizations/registry'
import { useSceneStore } from '../../store/sceneStore'

type VizPanelProps = {
  meta: VizMeta
  scene: ReactNode
  controls?: ReactNode
  showSceneControls?: boolean
}

export function VizPanel({
  meta,
  scene,
  controls,
  showSceneControls = false,
}: VizPanelProps) {
  const showPlane = useSceneStore((s) => s.showAuxiliaryPlane)
  const togglePlane = useSceneStore((s) => s.togglePlane)
  const resetCamera = useSceneStore((s) => s.resetCamera)

  return (
    <div className="flex h-full min-h-0 flex-1 flex-col lg:flex-row">
      <div className="relative h-[520px] min-h-[420px] shrink-0 border-b border-panel lg:h-auto lg:min-h-0 lg:flex-1 lg:shrink lg:border-b-0 lg:border-r">
        {meta.sceneTitle && (
          <h2 className="absolute top-3 left-4 z-10 text-sm font-semibold text-ink/90">
            {meta.sceneTitle}
          </h2>
        )}
        {(showSceneControls || controls) && (
          <div className="absolute top-10 left-3 right-3 z-10 flex flex-wrap gap-2 md:top-3 md:left-auto md:right-3">
            {showSceneControls && (
              <>
                <button
                  type="button"
                  onClick={resetCamera}
                  className="flex items-center gap-1.5 rounded-lg border border-panel bg-bg/90 px-2.5 py-1.5 text-xs text-ink shadow-sm hover:bg-panel/60"
                  title="Сбросить вид"
                >
                  <RotateCcw className="size-3.5" />
                  Сбросить вид
                </button>
                <button
                  type="button"
                  onClick={togglePlane}
                  className="flex items-center gap-1.5 rounded-lg border border-panel bg-bg/90 px-2.5 py-1.5 text-xs text-ink shadow-sm hover:bg-panel/60"
                  title="Показать / скрыть плоскость"
                >
                  <Layers className="size-3.5" />
                  {showPlane ? 'Скрыть плоскость' : 'Показать плоскость'}
                </button>
              </>
            )}
            {controls}
          </div>
        )}
        {scene}
      </div>

      <aside className="w-full shrink-0 overflow-y-auto p-5 lg:w-[340px] xl:w-[380px]">
        <h1 className="mb-4 text-lg font-semibold text-ink">{meta.title}</h1>
        {meta.formula && (
          <div className="mb-4 rounded-lg border border-orange/40 bg-highlight px-3 py-2">
            <MathBlock math={meta.formula} />
          </div>
        )}
        {meta.description && (
          <p className="mb-3 text-sm leading-relaxed text-ink/90">{meta.description}</p>
        )}
        {meta.note && (
          <p className="text-xs leading-relaxed text-ink/70 border-l-2 border-gray pl-3">
            {meta.note}
          </p>
        )}
      </aside>
    </div>
  )
}
