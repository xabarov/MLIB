import { useEffect, useMemo, useRef, useState, type PointerEvent } from 'react'
import { RotateCcw } from 'lucide-react'
import { MissionShell } from '../../game/components/MissionShell'
import { chooseMascotState, missionMessage } from '../../game/missionFeedback'
import { determinantForgeMission } from '../../game/missions'
import type { MissionBadge } from '../../game/missionTypes'
import { useMissionRuntime } from '../../game/useMissionRuntime'
import {
  diagnoseDeterminantState,
  determinant,
  determinantArea,
  determinantGridLimit,
  determinantLevelSuccess,
  formatDeterminantNumber,
  isDegenerate,
  svgPointToCoord,
  snapCoord,
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

function CoordInput({
  label,
  value,
  testId,
  onChange,
}: {
  label: string
  value: number
  testId: string
  onChange: (value: number) => void
}) {
  return (
    <label className="grid grid-cols-[44px_1fr] items-center gap-2 text-xs text-ink/70">
      <span className="font-semibold">{label}</span>
      <input
        type="number"
        min={-3}
        max={3}
        step={0.25}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
        className="w-full rounded border border-ink/10 bg-paper px-2 py-1 text-right tabular-nums text-ink"
        data-testid={testId}
      />
    </label>
  )
}

export function DeterminantForgeMission() {
  const definition = determinantForgeMission
  const [u, setU] = useState<Vec2>([1, 0])
  const [v, setV] = useState<Vec2>([0, 1])
  const [touched, setTouched] = useState(false)
  const svgRef = useRef<SVGSVGElement>(null)
  const dragTarget = useRef<DragTarget>(null)
  const runtime = useMissionRuntime(definition)
  const activeLevel = runtime.activeLevel
  const { completeActiveLevel, completedLevelIds, setActiveLevelId } = runtime
  const det = determinant(u, v)
  const area = determinantArea(u, v)
  const degenerate = isDegenerate(u, v)
  const diagnosis = diagnoseDeterminantState({
    levelId: activeLevel.id,
    u,
    v,
    completedLevelIds,
    touched,
  })

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
    warning:
      touched &&
      [
        'wrong-orientation',
        'unexpected-degenerate',
        'needs-degenerate',
        'needs-repair-after-degenerate',
      ].includes(diagnosis.kind),
    hint: Math.abs(area - 2) < 0.5 || Math.abs(det) < 0.35 || diagnosis.kind === 'area-too-small',
  })
  const mascotMessage = missionMessage(mascotState, {
    success: activeLevel.successText,
    warning: activeLevel.mistakeFeedback?.[0] ?? diagnosis.message,
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
    setTouched(true)
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
  const setVectorCoord = (target: 'u' | 'v', coord: 0 | 1, value: number) => {
    const safeValue = Number.isFinite(value) ? snapCoord(value) : 0
    setTouched(true)
    const setter = target === 'u' ? setU : setV
    setter((current) => {
      const next = [...current] as Vec2
      next[coord] = safeValue
      return next
    })
  }
  const resetLevel = () => {
    setU([1, 0])
    setV([0, 1])
    setTouched(false)
  }

  const gridLines = Array.from(
    { length: determinantGridLimit * 2 + 1 },
    (_, index) => index - determinantGridLimit,
  )
  const parallelogram = `0,0 ${u[0]},${-u[1]} ${u[0] + v[0]},${-(u[1] + v[1])} ${v[0]},${-v[1]}`
  const detClass =
    diagnosis.kind === 'success'
      ? 'fill-success/18 stroke-success'
      : diagnosis.kind === 'wrong-orientation'
        ? 'fill-target/18 stroke-target'
        : degenerate
          ? 'fill-danger/12 stroke-danger'
          : det > 0
            ? 'fill-energy/16 stroke-energy'
            : 'fill-target/16 stroke-target'
  const targetArea = activeLevel.id === 'area-two' ? 'Поймай |det A| = 2' : activeLevel.id === 'flip-orientation' ? 'Сделай det A < 0' : activeLevel.id === 'break-invertibility' ? 'Схлопни площадь в 0' : 'Верни det A ≠ 0'

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
                r={0.26}
                className="cursor-grab fill-orange/10 stroke-transparent"
                strokeWidth="0.02"
                onPointerDown={(event) => startDrag(event, 'u')}
              />
              <circle
                cx={u[0]}
                cy={u[1]}
                r={0.17}
                className="pointer-events-none fill-orange stroke-ink"
                strokeWidth="0.035"
                data-testid="determinant-handle-u"
              />
              <circle
                cx={v[0]}
                cy={v[1]}
                r={0.26}
                className="cursor-grab fill-target/10 stroke-transparent"
                strokeWidth="0.02"
                onPointerDown={(event) => startDrag(event, 'v')}
              />
              <circle
                cx={v[0]}
                cy={v[1]}
                r={0.17}
                className="pointer-events-none fill-target stroke-ink"
                strokeWidth="0.035"
                data-testid="determinant-handle-v"
              />
            </g>
          </svg>
        </div>
      }
      controls={
        <div className="space-y-2">
          <VectorReadout label="u" value={u} />
          <VectorReadout label="v" value={v} />
          <div
            className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5 text-xs leading-relaxed text-ink/70"
            data-testid="determinant-diagnosis"
          >
            <p className="font-semibold text-ink">{diagnosis.message}</p>
            <p className="mt-1">{diagnosis.repairHint}</p>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <CoordInput
              label="u.x"
              value={u[0]}
              testId="determinant-input-u-x"
              onChange={(value) => setVectorCoord('u', 0, value)}
            />
            <CoordInput
              label="u.y"
              value={u[1]}
              testId="determinant-input-u-y"
              onChange={(value) => setVectorCoord('u', 1, value)}
            />
            <CoordInput
              label="v.x"
              value={v[0]}
              testId="determinant-input-v-x"
              onChange={(value) => setVectorCoord('v', 0, value)}
            />
            <CoordInput
              label="v.y"
              value={v[1]}
              testId="determinant-input-v-y"
              onChange={(value) => setVectorCoord('v', 1, value)}
            />
          </div>
          <p className="text-xs leading-relaxed text-ink/60">
            Оранжевая ручка - первый столбец, синяя - второй. Координаты
            притягиваются к шагу 0.25. Поля ниже дают точный режим.
          </p>
          <p className="rounded border border-target/20 bg-target/10 px-2 py-1 text-xs font-medium text-target">
            Цель прибора: {targetArea}
          </p>
          <button
            type="button"
            onClick={resetLevel}
            className="inline-flex items-center gap-1 rounded border border-ink/10 bg-paper px-2 py-1 text-xs font-semibold text-ink/75 hover:border-orange/40 hover:text-ink"
            data-testid="determinant-reset"
          >
            <RotateCcw className="size-3.5" />
            Сбросить уровень
          </button>
        </div>
      }
      feedback={
        <p>
          Матрица собрана из столбцов: A = [[{formatDeterminantNumber(u[0])},{' '}
          {formatDeterminantNumber(v[0])}], [{formatDeterminantNumber(u[1])},{' '}
          {formatDeterminantNumber(v[1])}]]. Диагноз:{' '}
          <span className="font-semibold">{diagnosis.kind}</span>.
        </p>
      }
    />
  )
}
