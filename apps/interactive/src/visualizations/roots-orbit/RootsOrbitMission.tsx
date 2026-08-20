import { useEffect, useMemo, useRef, useState, type PointerEvent } from 'react'
import { RotateCcw, Target } from 'lucide-react'
import { MissionShell } from '../../game/components/MissionShell'
import { RepairMarker } from '../../game/components/RepairMarker'
import { ResultMoment } from '../../game/components/ResultMoment'
import { chooseMascotState, missionMessage } from '../../game/missionFeedback'
import { rootsOrbitMission } from '../../game/missions'
import type { MissionBadge, MissionLevel } from '../../game/missionTypes'
import { useMissionRuntime } from '../../game/useMissionRuntime'
import {
  cabs,
  closureError,
  cpow,
  diagnoseRoots,
  formatComplex,
  orbit,
  rootsLevels,
  rootsLevelSuccess,
  type Complex,
  type RootsLevelId,
} from './rootsOrbitModel'

const levelIdMap: Record<string, RootsLevelId> = {
  triangle: 'triangle',
  square: 'square',
  pentagon: 'pentagon',
}

const VIEW = 1.6

function clampCoord(value: number): number {
  return Math.max(-VIEW, Math.min(VIEW, value))
}

export function RootsOrbitMission() {
  const definition = rootsOrbitMission
  const runtime = useMissionRuntime(definition)
  const activeLevel = runtime.activeLevel
  return (
    <RootsOrbitLevel
      key={activeLevel.id}
      activeLevel={activeLevel}
      completeActiveLevel={runtime.completeActiveLevel}
      setActiveLevelId={runtime.setActiveLevelId}
    />
  )
}

function RootsOrbitLevel({
  activeLevel,
  completeActiveLevel,
  setActiveLevelId,
}: {
  activeLevel: MissionLevel
  completeActiveLevel: () => void
  setActiveLevelId: (levelId: string) => void
}) {
  const definition = rootsOrbitMission
  const levelId = levelIdMap[activeLevel.id]
  const config = rootsLevels[levelId]
  const n = config.n
  const [z, setZ] = useState<Complex>(config.start)
  const [touched, setTouched] = useState(false)
  const svgRef = useRef<SVGSVGElement>(null)
  const dragging = useRef(false)

  const points = useMemo(() => orbit(z, n), [z, n])
  const zPowerN = cpow(z, n)
  const diagnosis = diagnoseRoots({ levelId, z, touched })
  const levelSuccess = rootsLevelSuccess({ levelId, z })

  useEffect(() => {
    if (levelSuccess) completeActiveLevel()
  }, [completeActiveLevel, levelSuccess])

  const showRepairMarker =
    touched && !levelSuccess && diagnosis.kind !== 'idle' && diagnosis.kind !== 'success'
  const repairLabel =
    diagnosis.kind === 'modulus-off'
      ? '|z| ≠ 1'
      : diagnosis.kind === 'angle-off'
        ? 'не замкнуто'
        : 'вырожден'
  const repairTone = diagnosis.kind === 'modulus-off' ? 'danger' : 'warning'

  const mascotState = chooseMascotState({
    success: levelSuccess,
    warning: showRepairMarker,
    hint: touched && Math.abs(cabs(z) - 1) < 0.06,
    thinking: !touched,
  })
  const mascotMessage = missionMessage(mascotState, {
    success: activeLevel.successText,
    warning: activeLevel.mistakeFeedback?.[0] ?? diagnosis.message,
    hint: activeLevel.hint,
    thinking: 'Я сижу на z. Поставь меня на окружность под нужным углом, и степени замкнут многоугольник.',
    idle: 'Двигай z. Степени z, z², ... обходят окружность.',
  })

  const badges: MissionBadge[] = [
    {
      id: 'modulus',
      label: '|z|',
      value: cabs(z).toFixed(2),
      tone: Math.abs(cabs(z) - 1) < 0.06 ? 'success' : 'danger',
    },
    {
      id: 'closure',
      label: `z^${n}-1`,
      value: closureError(z, n).toFixed(2),
      tone: closureError(z, n) < 0.08 ? 'success' : 'warning',
    },
    {
      id: 'vertices',
      label: 'n',
      value: n,
      tone: levelSuccess ? 'success' : 'target',
    },
  ]

  const eventToComplex = (event: PointerEvent<SVGSVGElement>): Complex => {
    const svg = svgRef.current
    if (!svg) return z
    const rect = svg.getBoundingClientRect()
    const x = ((event.clientX - rect.left) / rect.width) * (2 * VIEW) - VIEW
    const y = VIEW - ((event.clientY - rect.top) / rect.height) * (2 * VIEW)
    return [clampCoord(x), clampCoord(y)]
  }

  const handlePointerMove = (event: PointerEvent<SVGSVGElement>) => {
    if (!dragging.current) return
    setTouched(true)
    setZ(eventToComplex(event))
  }

  const setComponent = (axis: 0 | 1, value: number) => {
    const safe = Number.isFinite(value) ? clampCoord(value) : 0
    setTouched(true)
    setZ((current) => (axis === 0 ? [safe, current[1]] : [current[0], safe]))
  }

  const snapToRoot = () => {
    setTouched(true)
    setZ([Math.cos((2 * Math.PI) / n), Math.sin((2 * Math.PI) / n)])
  }

  const resetLevel = () => {
    setZ(config.start)
    setTouched(false)
  }

  const toScreen = ([re, im]: Complex): string => `${re},${im}`
  const polygonPoints = points.map(toScreen).join(' ')

  return (
    <MissionShell
      definition={definition}
      activeLevelId={activeLevel.id}
      onLevelSelect={setActiveLevelId}
      mascotState={mascotState}
      mascotMessage={mascotMessage}
      badges={badges}
      sceneViewportClassName="h-[480px] pt-[104px] sm:pt-[78px] lg:h-full"
      scene={
        <div className="relative flex h-full items-center justify-center bg-[radial-gradient(circle_at_24%_18%,rgba(124,108,207,0.14),transparent_30%),linear-gradient(180deg,#fffdf7,#f5f3ec)] p-4">
          <ResultMoment show={levelSuccess} label={`правильный ${n}-угольник`} />
          {showRepairMarker && (
            <RepairMarker tone={repairTone} label={repairLabel} xPercent={50} yPercent={3} />
          )}
          <svg
            ref={svgRef}
            viewBox={`${-VIEW} ${-VIEW} ${2 * VIEW} ${2 * VIEW}`}
            className="aspect-square max-h-full w-full max-w-[560px] touch-none rounded-md border border-ink/10 bg-paper shadow-[0_18px_42px_rgba(20,20,19,0.12)]"
            onPointerMove={handlePointerMove}
            onPointerUp={() => (dragging.current = false)}
            onPointerLeave={() => (dragging.current = false)}
            data-testid="roots-orbit-canvas"
            aria-label="Комплексная плоскость со степенями z"
          >
            <g transform="scale(1,-1)">
              <line x1={-VIEW} y1={0} x2={VIEW} y2={0} className="stroke-ink/30" strokeWidth="0.012" />
              <line x1={0} y1={-VIEW} x2={0} y2={VIEW} className="stroke-ink/30" strokeWidth="0.012" />
              <circle cx={0} cy={0} r={1} className="fill-none stroke-target/45" strokeWidth="0.012" strokeDasharray="0.05 0.04" />
              <circle cx={1} cy={0} r={0.04} className="fill-target" data-testid="roots-one-marker" />

              <polygon
                points={polygonPoints}
                className={levelSuccess ? 'fill-success/12 stroke-success' : 'fill-orange/8 stroke-orange/70'}
                strokeWidth="0.02"
                strokeLinejoin="round"
                data-testid="roots-polygon"
              />
              {points.map((point, index) => (
                <g key={index}>
                  <circle cx={point[0]} cy={point[1]} r={0.045} className="fill-orange/80 stroke-ink" strokeWidth="0.008" />
                </g>
              ))}

              <circle cx={zPowerN[0]} cy={zPowerN[1]} r={0.05} className="fill-none stroke-danger" strokeWidth="0.018" data-testid="roots-zpn" />

              <circle
                cx={z[0]}
                cy={z[1]}
                r={0.08}
                className="cursor-grab fill-orange stroke-ink"
                strokeWidth="0.014"
                data-testid="roots-handle"
                onPointerDown={(event) => {
                  dragging.current = true
                  event.currentTarget.setPointerCapture(event.pointerId)
                  setTouched(true)
                }}
              />
            </g>
          </svg>
        </div>
      }
      controls={
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-2">
            <label className="grid gap-1 text-xs text-ink/70">
              <span className="font-semibold text-ink">Re z</span>
              <input
                type="number"
                min={-VIEW}
                max={VIEW}
                step={0.01}
                value={z[0].toFixed(2)}
                onChange={(event) => setComponent(0, Number(event.target.value))}
                className="w-full rounded border border-ink/10 bg-paper px-2 py-1 text-right tabular-nums text-ink"
                data-testid="roots-re"
              />
            </label>
            <label className="grid gap-1 text-xs text-ink/70">
              <span className="font-semibold text-ink">Im z</span>
              <input
                type="number"
                min={-VIEW}
                max={VIEW}
                step={0.01}
                value={z[1].toFixed(2)}
                onChange={(event) => setComponent(1, Number(event.target.value))}
                className="w-full rounded border border-ink/10 bg-paper px-2 py-1 text-right tabular-nums text-ink"
                data-testid="roots-im"
              />
            </label>
          </div>

          <div
            className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5 text-xs leading-relaxed text-ink/70"
            data-testid="roots-diagnosis"
          >
            <p className="font-semibold text-ink">{diagnosis.message}</p>
            <p className="mt-1">{diagnosis.repairHint}</p>
          </div>

          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={resetLevel}
              className="inline-flex items-center gap-1 rounded border border-ink/10 bg-paper px-2 py-1 text-xs font-semibold text-ink/75 hover:border-orange/40 hover:text-ink"
              data-testid="roots-reset"
            >
              <RotateCcw size={14} /> reset
            </button>
            <button
              type="button"
              onClick={snapToRoot}
              className="inline-flex items-center gap-1 rounded border border-target/25 bg-target/10 px-2 py-1 text-xs font-semibold text-ink transition hover:border-target"
              data-testid="roots-snap"
            >
              <Target size={14} /> первообразный корень
            </button>
          </div>
        </div>
      }
      feedback={
        <p>
          z = <span className="font-semibold">{formatComplex(z)}</span>, |z| ={' '}
          <span className="font-semibold">{cabs(z).toFixed(2)}</span>. Диагноз:{' '}
          <span className="font-semibold">{diagnosis.kind}</span>.
        </p>
      }
    />
  )
}
