import { useEffect, useMemo, useRef, useState, type PointerEvent } from 'react'
import { RotateCcw } from 'lucide-react'
import { MissionShell } from '../../game/components/MissionShell'
import { chooseMascotState, missionMessage } from '../../game/missionFeedback'
import { matrixMachineMission } from '../../game/missions'
import type { MissionBadge } from '../../game/missionTypes'
import { useMissionRuntime } from '../../game/useMissionRuntime'
import {
  diagnoseMatrixMachineState,
  formatMatrixNumber,
  matrixFromColumns,
  matrixMachineLevelSuccess,
  matrixMachineTargets,
  svgPointToMatrixCoord,
  targetError,
  type Vec2,
} from './matrixMachineModel'

type DragTarget = 'u' | 'v' | null

function VectorReadout({ label, value, target }: { label: string; value: Vec2; target: Vec2 }) {
  return (
    <p className="text-xs text-ink/65">
      <span className="font-semibold text-ink">{label}</span> = (
      {formatMatrixNumber(value[0])}, {formatMatrixNumber(value[1])}){' '}
      <span className="text-ink/45">
        цель ({formatMatrixNumber(target[0])}, {formatMatrixNumber(target[1])})
      </span>
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

export function MatrixMachineMission() {
  const definition = matrixMachineMission
  const runtime = useMissionRuntime(definition)
  const activeLevel = runtime.activeLevel
  const { completeActiveLevel, setActiveLevelId } = runtime
  const target = matrixMachineTargets[activeLevel.id]
  const [u, setU] = useState<Vec2>([1, 0])
  const [v, setV] = useState<Vec2>([0, 1])
  const [touched, setTouched] = useState(false)
  const svgRef = useRef<SVGSVGElement>(null)
  const dragTarget = useRef<DragTarget>(null)

  const error = targetError(activeLevel.id, u, v)
  const levelSuccess = useMemo(
    () => matrixMachineLevelSuccess(activeLevel.id, u, v),
    [activeLevel.id, u, v],
  )
  const diagnosis = diagnoseMatrixMachineState({
    levelId: activeLevel.id,
    u,
    v,
    touched,
  })

  useEffect(() => {
    if (!levelSuccess) return
    completeActiveLevel()
  }, [completeActiveLevel, levelSuccess])

  const mascotState = chooseMascotState({
    success: levelSuccess,
    warning:
      touched &&
      ['swapped-columns', 'wrong-direction', 'wrong-first-column', 'wrong-second-column'].includes(
        diagnosis.kind,
      ),
    hint: error < 0.6,
    thinking: error < 1.3,
  })
  const mascotMessage = missionMessage(mascotState, {
    success: activeLevel.successText,
    warning: activeLevel.mistakeFeedback?.[0] ?? diagnosis.message,
    hint: activeLevel.hint,
    thinking: 'Матрица уже похожа на цель. Дотяни один из столбцов.',
    idle: 'Тяни оранжевую и синюю ручки. Это образы e1 и e2, то есть столбцы матрицы.',
  })

  const matrix = matrixFromColumns(u, v)
  const badges: MissionBadge[] = [
    {
      id: 'target-error',
      label: 'distance',
      value: formatMatrixNumber(error),
      tone: levelSuccess ? 'success' : error < 0.6 ? 'warning' : 'target',
    },
    {
      id: 'u',
      label: 'A e1',
      value: `(${formatMatrixNumber(u[0])}, ${formatMatrixNumber(u[1])})`,
      tone: 'energy',
    },
    {
      id: 'v',
      label: 'A e2',
      value: `(${formatMatrixNumber(v[0])}, ${formatMatrixNumber(v[1])})`,
      tone: 'target',
    },
  ]

  const setVector = (targetName: DragTarget, next: Vec2) => {
    setTouched(true)
    if (targetName === 'u') setU(next)
    if (targetName === 'v') setV(next)
  }

  const eventToPoint = (event: PointerEvent<SVGSVGElement>): Vec2 => {
    const svg = svgRef.current
    if (!svg) return [0, 0]
    return svgPointToMatrixCoord({
      clientX: event.clientX,
      clientY: event.clientY,
      rect: svg.getBoundingClientRect(),
    })
  }

  const handlePointerMove = (event: PointerEvent<SVGSVGElement>) => {
    if (!dragTarget.current) return
    setVector(dragTarget.current, eventToPoint(event))
  }

  const startDrag = (event: PointerEvent<SVGCircleElement>, targetName: DragTarget) => {
    dragTarget.current = targetName
    event.currentTarget.setPointerCapture(event.pointerId)
  }

  const stopDrag = () => {
    dragTarget.current = null
  }

  const gridLines = Array.from({ length: 7 }, (_, index) => index - 3)
  const resetLevel = () => {
    setU([1, 0])
    setV([0, 1])
    setTouched(false)
  }
  const setVectorCoord = (targetName: 'u' | 'v', coord: 0 | 1, value: number) => {
    const safeValue = Number.isFinite(value) ? Math.max(-3, Math.min(3, value)) : 0
    setTouched(true)
    const setter = targetName === 'u' ? setU : setV
    setter((current) => {
      const next = [...current] as Vec2
      next[coord] = safeValue
      return next
    })
  }

  return (
    <MissionShell
      definition={definition}
      activeLevelId={activeLevel.id}
      onLevelSelect={setActiveLevelId}
      mascotState={mascotState}
      mascotMessage={mascotMessage}
      badges={badges}
      scene={
        <div className="flex h-full items-center justify-center bg-[radial-gradient(circle_at_72%_18%,rgba(106,155,204,0.18),transparent_30%),linear-gradient(180deg,#fffdf7,#faf9f5)] p-4">
          <svg
            ref={svgRef}
            viewBox="-4 -4 8 8"
            className="aspect-square max-h-full w-full max-w-[720px] touch-none rounded-md border border-ink/10 bg-paper shadow-[0_18px_42px_rgba(20,20,19,0.12)]"
            onPointerMove={handlePointerMove}
            onPointerUp={stopDrag}
            onPointerCancel={stopDrag}
            aria-label="Матрица как машина"
            data-testid="matrix-machine-plane"
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

              <line x1={0} y1={0} x2={target.u[0]} y2={target.u[1]} className="stroke-orange/30" strokeWidth="0.13" strokeLinecap="round" />
              <line x1={0} y1={0} x2={target.v[0]} y2={target.v[1]} className="stroke-target/30" strokeWidth="0.13" strokeLinecap="round" />
              <circle cx={target.u[0]} cy={target.u[1]} r={0.12} className="fill-orange/30" />
              <circle cx={target.v[0]} cy={target.v[1]} r={0.12} className="fill-target/30" />

              <line x1={0} y1={0} x2={u[0]} y2={u[1]} className="stroke-orange" strokeWidth="0.075" strokeLinecap="round" />
              <line x1={0} y1={0} x2={v[0]} y2={v[1]} className="stroke-target" strokeWidth="0.075" strokeLinecap="round" />
              <circle
                cx={u[0]}
                cy={u[1]}
                r={0.17}
                className="cursor-grab fill-orange stroke-ink"
                strokeWidth="0.035"
                data-testid="matrix-handle-u"
                onPointerDown={(event) => startDrag(event, 'u')}
              />
              <circle
                cx={v[0]}
                cy={v[1]}
                r={0.17}
                className="cursor-grab fill-target stroke-ink"
                strokeWidth="0.035"
                data-testid="matrix-handle-v"
                onPointerDown={(event) => startDrag(event, 'v')}
              />
            </g>
          </svg>
        </div>
      }
      controls={
        <div className="space-y-2">
          <div className="rounded border border-target/20 bg-target/10 px-2 py-1 text-xs text-ink">
            Целевая матрица: [[{formatMatrixNumber(target.u[0])},{' '}
            {formatMatrixNumber(target.v[0])}], [{formatMatrixNumber(target.u[1])},{' '}
            {formatMatrixNumber(target.v[1])}]]
          </div>
          <VectorReadout label="A e1" value={u} target={target.u} />
          <VectorReadout label="A e2" value={v} target={target.v} />
          <div
            className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5 text-xs leading-relaxed text-ink/70"
            data-testid="matrix-diagnosis"
          >
            <p className="font-semibold text-ink">{diagnosis.message}</p>
            <p className="mt-1">{diagnosis.repairHint}</p>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <CoordInput
              label="u.x"
              value={u[0]}
              testId="matrix-input-u-x"
              onChange={(value) => setVectorCoord('u', 0, value)}
            />
            <CoordInput
              label="u.y"
              value={u[1]}
              testId="matrix-input-u-y"
              onChange={(value) => setVectorCoord('u', 1, value)}
            />
            <CoordInput
              label="v.x"
              value={v[0]}
              testId="matrix-input-v-x"
              onChange={(value) => setVectorCoord('v', 0, value)}
            />
            <CoordInput
              label="v.y"
              value={v[1]}
              testId="matrix-input-v-y"
              onChange={(value) => setVectorCoord('v', 1, value)}
            />
          </div>
          <p className="text-xs leading-relaxed text-ink/60">
            Оранжевая ручка задает первый столбец, синяя - второй. Бледные
            направляющие показывают цель уровня. Поля ниже дают точный режим.
          </p>
          <button
            type="button"
            onClick={resetLevel}
            className="inline-flex items-center gap-1 rounded border border-ink/10 bg-paper px-2 py-1 text-xs font-semibold text-ink/75 hover:border-orange/40 hover:text-ink"
            data-testid="matrix-reset"
          >
            <RotateCcw className="size-3.5" />
            Сбросить уровень
          </button>
        </div>
      }
      feedback={
        <p>
          A = [[{formatMatrixNumber(matrix[0][0])}, {formatMatrixNumber(matrix[0][1])}], [
          {formatMatrixNumber(matrix[1][0])}, {formatMatrixNumber(matrix[1][1])}]]. Диагноз:{' '}
          <span className="font-semibold">{diagnosis.kind}</span>.
        </p>
      }
    />
  )
}
