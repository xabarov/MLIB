import { useEffect, useMemo, useState } from 'react'
import { RotateCcw } from 'lucide-react'
import { MissionShell } from '../../game/components/MissionShell'
import { RepairMarker } from '../../game/components/RepairMarker'
import { ResultMoment } from '../../game/components/ResultMoment'
import { chooseMascotState, missionMessage } from '../../game/missionFeedback'
import { gradientSlopeMission } from '../../game/missions'
import type { MissionBadge, MissionLevel } from '../../game/missionTypes'
import { useMissionRuntime } from '../../game/useMissionRuntime'
import {
  diagnoseGradient,
  distanceToMin,
  formatGradientNumber,
  gradientLevels,
  gradientLevelSuccess,
  hasDiverged,
  learningRateStops,
  runDescent,
  surfaceValue,
  type GradientLevelId,
} from './gradientSlopeModel'

const levelIdMap: Record<string, GradientLevelId> = {
  'roll-to-min': 'roll-to-min',
  'tame-the-step': 'tame-the-step',
  'narrow-valley': 'narrow-valley',
}

const VIEW = 3.2
const CONTOUR_FRACTIONS = [1, 0.62, 0.36, 0.18, 0.07]

function clampForSvg(value: number): number {
  return Math.max(-VIEW * 1.6, Math.min(VIEW * 1.6, value))
}

export function GradientSlopeMission() {
  const definition = gradientSlopeMission
  const runtime = useMissionRuntime(definition)
  const activeLevel = runtime.activeLevel
  return (
    <GradientSlopeLevel
      key={activeLevel.id}
      activeLevel={activeLevel}
      completeActiveLevel={runtime.completeActiveLevel}
      setActiveLevelId={runtime.setActiveLevelId}
    />
  )
}

function GradientSlopeLevel({
  activeLevel,
  completeActiveLevel,
  setActiveLevelId,
}: {
  activeLevel: MissionLevel
  completeActiveLevel: () => void
  setActiveLevelId: (levelId: string) => void
}) {
  const definition = gradientSlopeMission
  const levelId = levelIdMap[activeLevel.id]
  const config = gradientLevels[levelId]
  const [lr, setLr] = useState<number>(learningRateStops.min)
  const [touched, setTouched] = useState(false)

  const path = useMemo(
    () => runDescent(config.surface, config.start, lr, config.steps),
    [config, lr],
  )
  const diagnosis = diagnoseGradient({ levelId, lr, touched })
  const levelSuccess = gradientLevelSuccess({ levelId, lr })
  const diverged = hasDiverged(path)
  const finalPoint = path[path.length - 1]
  const finalDistance = distanceToMin(finalPoint)

  useEffect(() => {
    if (levelSuccess) completeActiveLevel()
  }, [completeActiveLevel, levelSuccess])

  const showRepairMarker =
    touched && !levelSuccess && diagnosis.kind !== 'idle' && diagnosis.kind !== 'success'
  const repairLabel =
    diagnosis.kind === 'exploded'
      ? 'шаг взорвался'
      : diagnosis.kind === 'oscillating'
        ? 'перелёт'
        : 'слишком медленно'
  const repairTone = diagnosis.kind === 'exploded' ? 'danger' : 'warning'

  const mascotState = chooseMascotState({
    success: levelSuccess,
    warning: showRepairMarker,
    hint: touched && diagnosis.kind === 'too-slow',
    thinking: !touched,
  })
  const mascotMessage = missionMessage(mascotState, {
    success: activeLevel.successText,
    warning: activeLevel.mistakeFeedback?.[0] ?? diagnosis.message,
    hint: activeLevel.hint,
    thinking: 'Я еду по поверхности. Подбери шаг, чтобы скатиться в минимум без перелёта.',
    idle: 'Двигай learning rate. Шаг идёт против градиента.',
  })

  const badges: MissionBadge[] = [
    {
      id: 'lr',
      label: 'lr',
      value: formatGradientNumber(lr),
      tone: levelSuccess ? 'success' : 'energy',
    },
    {
      id: 'dist',
      label: 'dist',
      value: diverged ? 'inf' : formatGradientNumber(finalDistance),
      tone: levelSuccess ? 'success' : diverged ? 'danger' : 'warning',
    },
    {
      id: 'f',
      label: 'f',
      value: diverged ? 'inf' : formatGradientNumber(surfaceValue(config.surface, finalPoint)),
      tone: 'target',
    },
  ]

  const startValue = surfaceValue(config.surface, config.start)
  const contours = CONTOUR_FRACTIONS.map((fraction) => {
    const c = startValue * fraction
    return {
      rx: Math.sqrt(c / config.surface.a),
      ry: Math.sqrt(c / config.surface.b),
      key: fraction,
    }
  })
  const polyline = path
    .map(([x, y]) => `${clampForSvg(x)},${clampForSvg(y)}`)
    .join(' ')

  const resetLevel = () => {
    setLr(learningRateStops.min)
    setTouched(false)
  }

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
        <div className="relative flex h-full items-center justify-center bg-[radial-gradient(circle_at_24%_18%,rgba(95,141,99,0.16),transparent_30%),linear-gradient(180deg,#fffdf7,#f5f3ec)] p-4">
          <ResultMoment show={levelSuccess} label="скатился в минимум" />
          {showRepairMarker && (
            <RepairMarker tone={repairTone} label={repairLabel} xPercent={50} yPercent={3} />
          )}
          <svg
            viewBox={`${-VIEW} ${-VIEW} ${2 * VIEW} ${2 * VIEW}`}
            className="aspect-square max-h-full w-full max-w-[640px] rounded-md border border-ink/10 bg-paper shadow-[0_18px_42px_rgba(20,20,19,0.12)]"
            data-testid="gradient-slope-canvas"
            aria-label="Градиентный спуск по поверхности"
          >
            <g transform="scale(1,-1)">
              <line x1={-VIEW} y1={0} x2={VIEW} y2={0} className="stroke-ink/30" strokeWidth="0.02" />
              <line x1={0} y1={-VIEW} x2={0} y2={VIEW} className="stroke-ink/30" strokeWidth="0.02" />

              {contours.map((contour) => (
                <ellipse
                  key={contour.key}
                  cx={0}
                  cy={0}
                  rx={contour.rx}
                  ry={contour.ry}
                  className="fill-none stroke-target/35"
                  strokeWidth="0.022"
                />
              ))}

              <polyline
                points={polyline}
                className="fill-none stroke-orange"
                strokeWidth="0.05"
                strokeLinejoin="round"
                strokeLinecap="round"
                data-testid="gradient-trajectory"
              />
              {path.map(([x, y], index) => (
                <circle
                  key={index}
                  cx={clampForSvg(x)}
                  cy={clampForSvg(y)}
                  r={index === 0 ? 0.09 : 0.05}
                  className={index === 0 ? 'fill-ink' : 'fill-orange/80'}
                />
              ))}
              <circle cx={0} cy={0} r={0.1} className="fill-success stroke-ink" strokeWidth="0.02" />
            </g>
          </svg>
        </div>
      }
      controls={
        <div className="space-y-3">
          <label className="grid gap-1 text-xs text-ink/70">
            <span className="flex items-center justify-between gap-2">
              <span className="font-semibold text-ink">learning rate</span>
              <span className="tabular-nums">{formatGradientNumber(lr)}</span>
            </span>
            <input
              type="range"
              min={learningRateStops.min}
              max={learningRateStops.max}
              step={learningRateStops.step}
              value={lr}
              onChange={(event) => {
                setTouched(true)
                setLr(Number(event.target.value))
              }}
              className="accent-orange"
              data-testid="gradient-lr"
            />
          </label>

          <div
            className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5 text-xs leading-relaxed text-ink/70"
            data-testid="gradient-diagnosis"
          >
            <p className="font-semibold text-ink">{diagnosis.message}</p>
            <p className="mt-1">{diagnosis.repairHint}</p>
          </div>

          <button
            type="button"
            onClick={resetLevel}
            className="inline-flex items-center gap-1 rounded border border-ink/10 bg-paper px-2 py-1 text-xs font-semibold text-ink/75 hover:border-orange/40 hover:text-ink"
            data-testid="gradient-reset"
          >
            <RotateCcw size={14} /> Сбросить уровень
          </button>
        </div>
      }
      feedback={
        <p>
          f = {formatGradientNumber(config.surface.a)}x² + {formatGradientNumber(config.surface.b)}y².
          lr = <span className="font-semibold">{formatGradientNumber(lr)}</span>. Диагноз:{' '}
          <span className="font-semibold">{diagnosis.kind}</span>.
        </p>
      }
    />
  )
}
