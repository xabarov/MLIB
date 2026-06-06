import { useEffect, useMemo, useRef, useState, type PointerEvent } from 'react'
import { MissionShell } from '../../game/components/MissionShell'
import { chooseMascotState, missionMessage } from '../../game/missionFeedback'
import { determinantForgeMission } from '../../game/missions'
import type { MissionBadge } from '../../game/missionTypes'
import { useMissionRuntime } from '../../game/useMissionRuntime'
import {
  determinant,
  determinantArea,
  determinantGridLimit,
  determinantLevelSuccess,
  formatDeterminantNumber,
  isDegenerate,
  svgPointToCoord,
  type Vec2,
} from './determinantForgeModel'

type DragTarget = 'u' | 'v' | null

function VectorReadout({ label, value }: { label: string; value: Vec2 }) {
  return (
    <p className="text-xs text-ink/65">
      <span className="font-semibold text-ink">{label}</span> = ({formatDeterminantNumber(value[0])},{' '}
      {formatDeterminantNumber(value[1])})
    </p>
  )
}

export function DeterminantForgeMission() {
  const definition = determinantForgeMission
  const [u, setU] = useState<Vec2>([1, 0])
  const [v, setV] = useState<Vec2>([0, 1])
  const svgRef = useRef<SVGSVGElement>(null)
  const dragTarget = useRef<DragTarget>(null)
  const runtime = useMissionRuntime(definition)
  const activeLevel = runtime.activeLevel
  const { completeActiveLevel, completedLevelIds, setActiveLevelId } = runtime
  const det = determinant(u, v)
  const area = determinantArea(u, v)
  const degenerate = isDegenerate(u, v)

  const levelSuccess = useMemo(() => {
    return determinantLevelSuccess({
      levelId: activeLevel.id,
      u,
      v,
      completedLevelIds,
    })
  }, [activeLevel.id, completedLevelIds, u, v])

  useEffect(() => {
    if (!levelSuccess) return
    completeActiveLevel()
  }, [completeActiveLevel, levelSuccess])

  const mascotState = chooseMascotState({
    success: levelSuccess,
    warning: degenerate && activeLevel.id !== 'break-invertibility',
    hint: Math.abs(area - 2) < 0.5 || Math.abs(det) < 0.35,
  })
  const mascotMessage = missionMessage(mascotState, {
    success: activeLevel.successText,
    warning: 'Площадь исчезла. Это полезно только когда мы специально ломаем обратимость.',
    hint: activeLevel.hint,
    thinking: 'Смотри на форму: площадь - это модуль det A, а знак показывает ориентацию.',
    idle: 'Тяни концы векторов. Я буду считать площадь и ориентацию параллелограмма.',
  })

  const badges: MissionBadge[] = [
    {
      id: 'det',
      label: 'det A',
      value: formatDeterminantNumber(det),
      tone: levelSuccess ? 'success' : degenerate ? 'danger' : det < 0 ? 'target' : 'energy',
    },
    {
      id: 'area',
      label: 'area',
      value: formatDeterminantNumber(area),
      tone: Math.abs(area - 2) < 0.05 ? 'success' : 'neutral',
    },
    {
      id: 'orientation',
      label: 'orientation',
      value: degenerate ? 'flat' : det > 0 ? 'positive' : 'negative',
      tone: degenerate ? 'danger' : det > 0 ? 'energy' : 'target',
    },
  ]

  const setVector = (target: DragTarget, next: Vec2) => {
    if (target === 'u') setU(next)
    if (target === 'v') setV(next)
  }

  const eventToPoint = (event: PointerEvent<SVGSVGElement>): Vec2 => {
    const svg = svgRef.current
    if (!svg) return [0, 0]
    const rect = svg.getBoundingClientRect()
    return svgPointToCoord({ clientX: event.clientX, clientY: event.clientY, rect })
  }

  const handlePointerMove = (event: PointerEvent<SVGSVGElement>) => {
    if (!dragTarget.current) return
    setVector(dragTarget.current, eventToPoint(event))
  }

  const startDrag = (event: PointerEvent<SVGCircleElement>, target: DragTarget) => {
    dragTarget.current = target
    event.currentTarget.setPointerCapture(event.pointerId)
  }

  const stopDrag = () => {
    dragTarget.current = null
  }

  const gridLines = Array.from(
    { length: determinantGridLimit * 2 + 1 },
    (_, index) => index - determinantGridLimit,
  )
  const parallelogram = `0,0 ${u[0]},${-u[1]} ${u[0] + v[0]},${-(u[1] + v[1])} ${v[0]},${-v[1]}`
  const detClass = degenerate ? 'fill-danger/12 stroke-danger' : det > 0 ? 'fill-energy/16 stroke-energy' : 'fill-target/16 stroke-target'

  return (
    <MissionShell
      definition={definition}
      activeLevelId={activeLevel.id}
      onLevelSelect={setActiveLevelId}
      mascotState={mascotState}
      mascotMessage={mascotMessage}
      badges={badges}
      scene={
        <div className="flex h-full items-center justify-center bg-[radial-gradient(circle_at_20%_15%,rgba(217,119,87,0.13),transparent_32%),linear-gradient(180deg,#fffdf7,#faf9f5)] p-4">
          <svg
            ref={svgRef}
            viewBox="-4 -4 8 8"
            className="aspect-square max-h-full w-full max-w-[720px] touch-none rounded-md border border-ink/10 bg-paper shadow-[0_18px_42px_rgba(20,20,19,0.12)]"
            onPointerMove={handlePointerMove}
            onPointerUp={stopDrag}
            onPointerCancel={stopDrag}
            aria-label="Кузница определителя"
            data-testid="determinant-forge-plane"
          >
            <g transform="scale(1,-1)">
              {gridLines.map((line) => (
                <g key={line}>
                  <line x1={-4} y1={line} x2={4} y2={line} className="stroke-grid" strokeWidth="0.018" />
                  <line x1={line} y1={-4} x2={line} y2={4} className="stroke-grid" strokeWidth="0.018" />
                </g>
              ))}
              <line x1={-4} y1={0} x2={4} y2={0} className="stroke-ink/45" strokeWidth="0.035" />
              <line x1={0} y1={-4} x2={0} y2={4} className="stroke-ink/45" strokeWidth="0.035" />
              <polygon points={parallelogram} className={detClass} strokeWidth="0.055" />
              <line x1={0} y1={0} x2={u[0]} y2={u[1]} className="stroke-orange" strokeWidth="0.075" strokeLinecap="round" />
              <line x1={0} y1={0} x2={v[0]} y2={v[1]} className="stroke-target" strokeWidth="0.075" strokeLinecap="round" />
              <circle
                cx={u[0]}
                cy={u[1]}
                r={0.14}
                className="cursor-grab fill-orange stroke-ink"
                strokeWidth="0.035"
                data-testid="determinant-handle-u"
                onPointerDown={(event) => startDrag(event, 'u')}
              />
              <circle
                cx={v[0]}
                cy={v[1]}
                r={0.14}
                className="cursor-grab fill-target stroke-ink"
                strokeWidth="0.035"
                data-testid="determinant-handle-v"
                onPointerDown={(event) => startDrag(event, 'v')}
              />
            </g>
          </svg>
        </div>
      }
      controls={
        <div className="space-y-2">
          <VectorReadout label="u" value={u} />
          <VectorReadout label="v" value={v} />
          <p className="text-xs leading-relaxed text-ink/60">
            Оранжевая ручка - первый столбец, синяя - второй. Координаты
            притягиваются к шагу 0.25.
          </p>
        </div>
      }
      feedback={
        <p>
          Матрица собрана из столбцов: A = [[{formatDeterminantNumber(u[0])},{' '}
          {formatDeterminantNumber(v[0])}], [{formatDeterminantNumber(u[1])},{' '}
          {formatDeterminantNumber(v[1])}]].
        </p>
      }
    />
  )
}
