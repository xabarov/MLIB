import { useEffect, useMemo, useState } from 'react'
import { RotateCcw } from 'lucide-react'
import { MissionShell } from '../../game/components/MissionShell'
import { RepairMarker } from '../../game/components/RepairMarker'
import { ResultMoment } from '../../game/components/ResultMoment'
import { chooseMascotState, missionMessage } from '../../game/missionFeedback'
import { taylorLabMission } from '../../game/missions'
import type { MissionBadge, MissionLevel } from '../../game/missionTypes'
import { useMissionRuntime } from '../../game/useMissionRuntime'
import {
  coeffStops,
  curveError,
  DEGREE,
  diagnoseTaylor,
  evaluatePolynomial,
  formatCoefficient,
  taylorLevels,
  taylorLevelSuccess,
  type TaylorLevelConfig,
  type TaylorLevelId,
} from './taylorLabModel'

const levelIdMap: Record<string, TaylorLevelId> = {
  tangent: 'tangent',
  curvature: 'curvature',
  sine: 'sine',
}

const COEFF_LABEL = ['c₀', 'c₁·x', 'c₂·x²', 'c₃·x³', 'c₄·x⁴']

const PLOT_W = 100
const PLOT_H = 58
const PAD = 4
const SAMPLES = 160

function xToScreen(x: number, config: TaylorLevelConfig): number {
  const { xMin, xMax } = config.view
  return PAD + ((x - xMin) / (xMax - xMin)) * (PLOT_W - 2 * PAD)
}

function yToScreen(y: number, config: TaylorLevelConfig): number {
  const { yMin, yMax } = config.view
  const clamped = Math.max(yMin, Math.min(yMax, y))
  return PLOT_H - PAD - ((clamped - yMin) / (yMax - yMin)) * (PLOT_H - 2 * PAD)
}

function samplePoints(fn: (x: number) => number, config: TaylorLevelConfig): string {
  const { xMin, xMax } = config.view
  const points: string[] = []
  for (let i = 0; i <= SAMPLES; i += 1) {
    const x = xMin + ((xMax - xMin) * i) / SAMPLES
    points.push(`${xToScreen(x, config).toFixed(2)},${yToScreen(fn(x), config).toFixed(2)}`)
  }
  return points.join(' ')
}

const zeroCoeffs = Array.from({ length: DEGREE }, () => 0)

export function TaylorLabMission() {
  const definition = taylorLabMission
  const runtime = useMissionRuntime(definition)
  const activeLevel = runtime.activeLevel
  return (
    <TaylorLabLevel
      key={activeLevel.id}
      activeLevel={activeLevel}
      completeActiveLevel={runtime.completeActiveLevel}
      setActiveLevelId={runtime.setActiveLevelId}
    />
  )
}

function TaylorLabLevel({
  activeLevel,
  completeActiveLevel,
  setActiveLevelId,
}: {
  activeLevel: MissionLevel
  completeActiveLevel: () => void
  setActiveLevelId: (levelId: string) => void
}) {
  const definition = taylorLabMission
  const levelId = levelIdMap[activeLevel.id]
  const config = taylorLevels[levelId]
  const [coeffs, setCoeffs] = useState<number[]>(zeroCoeffs)
  const [touched, setTouched] = useState(false)

  const diagnosis = diagnoseTaylor({ coeffs, target: config.target, touched })
  const levelSuccess = taylorLevelSuccess(coeffs, config.target)
  const error = curveError(coeffs, config)

  useEffect(() => {
    if (levelSuccess) completeActiveLevel()
  }, [completeActiveLevel, levelSuccess])

  const showRepairMarker = touched && !levelSuccess && diagnosis.kind === 'coefficient-off'

  const mascotState = chooseMascotState({
    success: levelSuccess,
    warning: showRepairMarker,
    hint: touched && error < 0.6,
    thinking: !touched,
  })
  const mascotMessage = missionMessage(mascotState, {
    success: activeLevel.successText,
    warning: activeLevel.mistakeFeedback?.[0] ?? diagnosis.message,
    hint: activeLevel.hint,
    thinking: 'Я слежу за невязкой у нуля. Двигай коэффициенты, пока кривые не совпадут.',
    idle: 'Каждая ручка — коэффициент при степени x. Подгони полином под функцию у нуля.',
  })

  const fnCurve = useMemo(() => samplePoints(config.fn, config), [config])
  const polyCurve = samplePoints((x) => evaluatePolynomial(coeffs, x), config)

  const badges: MissionBadge[] = [
    {
      id: 'error',
      label: 'невязка',
      value: formatCoefficient(error),
      tone: levelSuccess ? 'success' : error < 0.6 ? 'warning' : 'danger',
    },
    {
      id: 'fn',
      label: 'f(x)',
      value: config.label,
      tone: 'neutral',
    },
  ]

  const setCoeff = (index: number, value: number) => {
    setTouched(true)
    setCoeffs((current) => {
      const next = current.slice()
      next[index] = value
      return next
    })
  }

  const resetLevel = () => {
    setCoeffs(zeroCoeffs)
    setTouched(false)
  }

  const yZero = yToScreen(0, config)
  const xZero = xToScreen(0, config)

  return (
    <MissionShell
      definition={definition}
      activeLevelId={activeLevel.id}
      onLevelSelect={setActiveLevelId}
      mascotState={mascotState}
      mascotMessage={mascotMessage}
      badges={badges}
      sceneViewportClassName="h-[440px] pt-[104px] sm:pt-[78px] lg:h-full"
      scene={
        <div className="relative flex h-full items-center justify-center bg-[radial-gradient(circle_at_24%_18%,rgba(124,108,207,0.14),transparent_30%),linear-gradient(180deg,#fffdf7,#f5f3ec)] p-4">
          <ResultMoment show={levelSuccess} label="полином найден" />
          {showRepairMarker && diagnosis.worstCoeff !== null && (
            <RepairMarker
              tone="warning"
              label={`коэффициент x^${diagnosis.worstCoeff}`}
              xPercent={50}
              yPercent={3}
            />
          )}
          <svg
            viewBox={`0 0 ${PLOT_W} ${PLOT_H}`}
            className="w-full max-w-[680px] rounded-md border border-ink/10 bg-paper shadow-[0_18px_42px_rgba(20,20,19,0.12)]"
            data-testid="taylor-canvas"
            aria-label="Полином Тейлора против функции"
          >
            <line x1={PAD} y1={yZero} x2={PLOT_W - PAD} y2={yZero} className="stroke-ink/25" strokeWidth="0.2" />
            <line x1={xZero} y1={PAD} x2={xZero} y2={PLOT_H - PAD} className="stroke-ink/20" strokeWidth="0.2" />
            <polyline
              points={fnCurve}
              className="fill-none stroke-target/55"
              strokeWidth="0.55"
              strokeDasharray="1.4 1"
              strokeLinejoin="round"
              data-testid="taylor-function-curve"
            />
            <polyline
              points={polyCurve}
              className={levelSuccess ? 'fill-none stroke-success' : 'fill-none stroke-orange'}
              strokeWidth="0.6"
              strokeLinejoin="round"
              strokeLinecap="round"
              data-testid="taylor-polynomial-curve"
            />
            <circle cx={xZero} cy={yZero} r={0.8} className="fill-ink/40" />
          </svg>
        </div>
      }
      controls={
        <div className="space-y-3">
          <div className="grid gap-2">
            {coeffs.map((coeff, index) => {
              const isWorst = diagnosis.worstCoeff === index && !levelSuccess
              return (
                <label key={index} className="grid gap-1 text-xs text-ink/70">
                  <span className="flex items-center justify-between gap-2">
                    <span className={`font-semibold ${isWorst ? 'text-orange' : 'text-ink'}`}>
                      {COEFF_LABEL[index]}
                    </span>
                    <span className="tabular-nums">{formatCoefficient(coeff)}</span>
                  </span>
                  <input
                    type="range"
                    min={coeffStops.min}
                    max={coeffStops.max}
                    step={coeffStops.step}
                    value={coeff}
                    onChange={(event) => setCoeff(index, Number(event.target.value))}
                    className="accent-orange"
                    data-testid={`taylor-coeff-${index}`}
                  />
                </label>
              )
            })}
          </div>

          <div
            className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5 text-xs leading-relaxed text-ink/70"
            data-testid="taylor-diagnosis"
          >
            <p className="font-semibold text-ink">{diagnosis.message}</p>
            <p className="mt-1">{diagnosis.repairHint}</p>
          </div>

          <button
            type="button"
            onClick={resetLevel}
            className="inline-flex items-center gap-1 rounded border border-ink/10 bg-paper px-2 py-1 text-xs font-semibold text-ink/75 hover:border-orange/40 hover:text-ink"
            data-testid="taylor-reset"
          >
            <RotateCcw size={14} /> Сбросить уровень
          </button>
        </div>
      }
      feedback={
        <p>
          Коэффициенты: [{coeffs.map((value) => formatCoefficient(value)).join(', ')}]. Невязка:{' '}
          <span className="font-semibold">{formatCoefficient(error)}</span>. Диагноз:{' '}
          <span className="font-semibold">{diagnosis.kind}</span>.
        </p>
      }
    />
  )
}
