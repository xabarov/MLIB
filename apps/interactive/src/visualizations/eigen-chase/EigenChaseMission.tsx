import { useEffect, useMemo, useRef, useState, type PointerEvent } from 'react'
import { RotateCcw } from 'lucide-react'
import { MissionShell } from '../../game/components/MissionShell'
import { RepairMarker } from '../../game/components/RepairMarker'
import { ResultMoment } from '../../game/components/ResultMoment'
import { chooseMascotState, missionMessage } from '../../game/missionFeedback'
import { eigenChaseMission } from '../../game/missions'
import type { MissionBadge, MissionLevel } from '../../game/missionTypes'
import { useMissionRuntime } from '../../game/useMissionRuntime'
import {
  diagnoseEigen,
  eigenLevels,
  eigenLevelSuccess,
  eigenState,
  formatEigenNumber,
  isAligned,
  type EigenLevelId,
} from './eigenChaseModel'

const levelIdMap: Record<string, EigenLevelId> = {
  'large-eigen': 'large-eigen',
  'small-eigen': 'small-eigen',
  'flip-eigen': 'flip-eigen',
}

const VIEW = 3.5

export function EigenChaseMission() {
  const definition = eigenChaseMission
  const runtime = useMissionRuntime(definition)
  const activeLevel = runtime.activeLevel
  return (
    <EigenChaseLevel
      key={activeLevel.id}
      activeLevel={activeLevel}
      completeActiveLevel={runtime.completeActiveLevel}
      setActiveLevelId={runtime.setActiveLevelId}
    />
  )
}

function EigenChaseLevel({
  activeLevel,
  completeActiveLevel,
  setActiveLevelId,
}: {
  activeLevel: MissionLevel
  completeActiveLevel: () => void
  setActiveLevelId: (levelId: string) => void
}) {
  const definition = eigenChaseMission
  const levelId = levelIdMap[activeLevel.id]
  const config = eigenLevels[levelId]
  const [angle, setAngle] = useState(0.4)
  const [touched, setTouched] = useState(false)
  const svgRef = useRef<SVGSVGElement>(null)
  const dragging = useRef(false)

  const direction = useMemo<[number, number]>(() => [Math.cos(angle), Math.sin(angle)], [angle])
  const state = eigenState(config.matrix, direction)
  const diagnosis = diagnoseEigen({ levelId, direction, touched })
  const levelSuccess = eigenLevelSuccess(levelId, direction)
  const aligned = isAligned(state)

  useEffect(() => {
    if (levelSuccess) completeActiveLevel()
  }, [completeActiveLevel, levelSuccess])

  const showRepairMarker =
    touched && !levelSuccess && (diagnosis.kind === 'not-aligned' || diagnosis.kind === 'wrong-eigenvalue')
  const repairLabel = diagnosis.kind === 'wrong-eigenvalue' ? 'не та λ' : 'A·v повёрнут'

  const mascotState = chooseMascotState({
    success: levelSuccess,
    warning: showRepairMarker,
    hint: aligned && !levelSuccess,
    thinking: !touched,
  })
  const mascotMessage = missionMessage(mascotState, {
    success: activeLevel.successText,
    warning: activeLevel.mistakeFeedback?.[0] ?? diagnosis.message,
    hint: activeLevel.hint,
    thinking: 'Я еду по концу A·v. Поверни v так, чтобы я лёг на ту же прямую.',
    idle: 'Вращай v по окружности и следи за A·v.',
  })

  const badges: MissionBadge[] = [
    {
      id: 'lambda',
      label: 'λ',
      value: formatEigenNumber(state.lambda),
      tone: levelSuccess ? 'success' : 'energy',
    },
    {
      id: 'align',
      label: 'skew',
      value: formatEigenNumber(state.alignment),
      tone: aligned ? 'success' : 'warning',
    },
    {
      id: 'target',
      label: 'target λ',
      value: formatEigenNumber(config.targetLambda),
      tone: 'target',
    },
  ]

  const eventToAngle = (event: PointerEvent<SVGSVGElement>) => {
    const svg = svgRef.current
    if (!svg) return
    const rect = svg.getBoundingClientRect()
    const x = ((event.clientX - rect.left) / rect.width) * (2 * VIEW) - VIEW
    const y = VIEW - ((event.clientY - rect.top) / rect.height) * (2 * VIEW)
    if (Math.hypot(x, y) < 0.05) return
    setTouched(true)
    setAngle(Math.atan2(y, x))
  }

  const resetLevel = () => {
    setAngle(0.4)
    setTouched(false)
  }

  const av = state.image
  const eigenLine: [number, number] = [direction[0] * VIEW, direction[1] * VIEW]

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
        <div className="relative flex h-full items-center justify-center bg-[radial-gradient(circle_at_24%_18%,rgba(106,155,204,0.14),transparent_30%),linear-gradient(180deg,#fffdf7,#f5f3ec)] p-4">
          <ResultMoment show={levelSuccess} label={`A·v = ${formatEigenNumber(state.lambda)}·v`} />
          {showRepairMarker && (
            <RepairMarker tone="warning" label={repairLabel} xPercent={50} yPercent={3} />
          )}
          <svg
            ref={svgRef}
            viewBox={`${-VIEW} ${-VIEW} ${2 * VIEW} ${2 * VIEW}`}
            className="aspect-square max-h-full w-full max-w-[560px] touch-none rounded-md border border-ink/10 bg-paper shadow-[0_18px_42px_rgba(20,20,19,0.12)]"
            onPointerMove={(event) => {
              if (dragging.current) eventToAngle(event)
            }}
            onPointerUp={() => (dragging.current = false)}
            onPointerLeave={() => (dragging.current = false)}
            data-testid="eigen-chase-canvas"
            aria-label="Поиск собственного вектора"
          >
            <g transform="scale(1,-1)">
              <line x1={-VIEW} y1={0} x2={VIEW} y2={0} className="stroke-ink/30" strokeWidth="0.02" />
              <line x1={0} y1={-VIEW} x2={0} y2={VIEW} className="stroke-ink/30" strokeWidth="0.02" />
              <circle cx={0} cy={0} r={1} className="fill-none stroke-target/40" strokeWidth="0.02" strokeDasharray="0.08 0.06" />

              {aligned && (
                <line
                  x1={-eigenLine[0]}
                  y1={-eigenLine[1]}
                  x2={eigenLine[0]}
                  y2={eigenLine[1]}
                  className="stroke-success/45"
                  strokeWidth="0.03"
                  strokeDasharray="0.12 0.1"
                  data-testid="eigen-line"
                />
              )}

              <line x1={0} y1={0} x2={av[0]} y2={av[1]} className={aligned ? 'stroke-success' : 'stroke-target'} strokeWidth="0.06" strokeLinecap="round" />
              <circle cx={av[0]} cy={av[1]} r={0.1} className={aligned ? 'fill-success' : 'fill-target'} data-testid="eigen-image" />

              <line x1={0} y1={0} x2={direction[0]} y2={direction[1]} className="stroke-orange" strokeWidth="0.05" strokeLinecap="round" />
              <circle
                cx={direction[0]}
                cy={direction[1]}
                r={0.13}
                className="cursor-grab fill-orange stroke-ink"
                strokeWidth="0.02"
                data-testid="eigen-handle"
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
          <label className="grid gap-1 text-xs text-ink/70">
            <span className="flex items-center justify-between gap-2">
              <span className="font-semibold text-ink">угол v, °</span>
              <span className="tabular-nums">{Math.round(((angle * 180) / Math.PI + 360) % 360)}</span>
            </span>
            <input
              type="range"
              min={0}
              max={359}
              step={1}
              value={Math.round(((angle * 180) / Math.PI + 360) % 360)}
              onChange={(event) => {
                setTouched(true)
                setAngle((Number(event.target.value) * Math.PI) / 180)
              }}
              className="accent-orange"
              data-testid="eigen-angle"
            />
          </label>

          <div className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5 text-xs text-ink" data-testid="eigen-readout">
            A·v = ({formatEigenNumber(av[0])}, {formatEigenNumber(av[1])}), λ = {formatEigenNumber(state.lambda)}
          </div>

          <div
            className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5 text-xs leading-relaxed text-ink/70"
            data-testid="eigen-diagnosis"
          >
            <p className="font-semibold text-ink">{diagnosis.message}</p>
            <p className="mt-1">{diagnosis.repairHint}</p>
          </div>

          <button
            type="button"
            onClick={resetLevel}
            className="inline-flex items-center gap-1 rounded border border-ink/10 bg-paper px-2 py-1 text-xs font-semibold text-ink/75 hover:border-orange/40 hover:text-ink"
            data-testid="eigen-reset"
          >
            <RotateCcw size={14} /> Сбросить уровень
          </button>
        </div>
      }
      feedback={
        <p>
          A·v = ({formatEigenNumber(av[0])}, {formatEigenNumber(av[1])}), перекос{' '}
          <span className="font-semibold">{formatEigenNumber(state.alignment)}</span>. Диагноз:{' '}
          <span className="font-semibold">{diagnosis.kind}</span>.
        </p>
      }
    />
  )
}
