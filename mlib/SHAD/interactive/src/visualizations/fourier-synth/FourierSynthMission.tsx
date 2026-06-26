import { useEffect, useMemo, useState } from 'react'
import { RotateCcw } from 'lucide-react'
import { MissionShell } from '../../game/components/MissionShell'
import { RepairMarker } from '../../game/components/RepairMarker'
import { ResultMoment } from '../../game/components/ResultMoment'
import { chooseMascotState, missionMessage } from '../../game/missionFeedback'
import { fourierSynthMission } from '../../game/missions'
import type { MissionBadge, MissionLevel } from '../../game/missionTypes'
import { useMissionRuntime } from '../../game/useMissionRuntime'
import {
  amplitudeStops,
  diagnoseFourier,
  formatAmplitude,
  fourierLevels,
  fourierLevelSuccess,
  HARMONICS,
  reconstruct,
  spectralError,
  type FourierLevelId,
} from './fourierSynthModel'

const levelIdMap: Record<string, FourierLevelId> = {
  'two-harmonics': 'two-harmonics',
  'square-wave': 'square-wave',
  sawtooth: 'sawtooth',
}

const PLOT_W = 100
const PLOT_H = 52
const PAD_X = 5
const Y_RANGE = 2.2
const SAMPLES = 200

function xToScreen(x: number): number {
  return PAD_X + (x / (2 * Math.PI)) * (PLOT_W - 2 * PAD_X)
}

function yToScreen(y: number): number {
  return PLOT_H / 2 - (y / Y_RANGE) * (PLOT_H / 2 - 3)
}

function curvePoints(amplitudes: number[]): string {
  const points: string[] = []
  for (let i = 0; i <= SAMPLES; i += 1) {
    const x = (i / SAMPLES) * 2 * Math.PI
    points.push(`${xToScreen(x).toFixed(2)},${yToScreen(reconstruct(amplitudes, x)).toFixed(2)}`)
  }
  return points.join(' ')
}

const zeroAmps = Array.from({ length: HARMONICS }, () => 0)

export function FourierSynthMission() {
  const definition = fourierSynthMission
  const runtime = useMissionRuntime(definition)
  const activeLevel = runtime.activeLevel
  return (
    <FourierSynthLevel
      key={activeLevel.id}
      activeLevel={activeLevel}
      completeActiveLevel={runtime.completeActiveLevel}
      setActiveLevelId={runtime.setActiveLevelId}
    />
  )
}

function FourierSynthLevel({
  activeLevel,
  completeActiveLevel,
  setActiveLevelId,
}: {
  activeLevel: MissionLevel
  completeActiveLevel: () => void
  setActiveLevelId: (levelId: string) => void
}) {
  const definition = fourierSynthMission
  const levelId = levelIdMap[activeLevel.id]
  const config = fourierLevels[levelId]
  const [amplitudes, setAmplitudes] = useState<number[]>(zeroAmps)
  const [touched, setTouched] = useState(false)

  const diagnosis = diagnoseFourier({ amplitudes, target: config.target, touched })
  const levelSuccess = fourierLevelSuccess(amplitudes, config.target)
  const error = spectralError(amplitudes, config.target)

  useEffect(() => {
    if (levelSuccess) completeActiveLevel()
  }, [completeActiveLevel, levelSuccess])

  const showRepairMarker = touched && !levelSuccess && diagnosis.kind === 'harmonic-off'

  const mascotState = chooseMascotState({
    success: levelSuccess,
    warning: showRepairMarker,
    hint: touched && error < 0.4,
    thinking: !touched,
  })
  const mascotMessage = missionMessage(mascotState, {
    success: activeLevel.successText,
    warning: activeLevel.mistakeFeedback?.[0] ?? diagnosis.message,
    hint: activeLevel.hint,
    thinking: 'Я слежу за энергией ошибки. Двигай гармоники, пока синяя кривая не ляжет на бледную.',
    idle: 'Каждая ручка — амплитуда гармоники sin(k·x). Собери из них целевой сигнал.',
  })

  const targetCurve = useMemo(() => curvePoints(config.target), [config.target])
  const reconCurve = curvePoints(amplitudes)

  const badges: MissionBadge[] = [
    {
      id: 'energy',
      label: 'energy',
      value: formatAmplitude(error),
      tone: levelSuccess ? 'success' : error < 0.4 ? 'warning' : 'danger',
    },
    {
      id: 'harmonics',
      label: 'k',
      value: HARMONICS,
      tone: 'neutral',
    },
  ]

  const setAmplitude = (index: number, value: number) => {
    setTouched(true)
    setAmplitudes((current) => {
      const next = current.slice()
      next[index] = value
      return next
    })
  }

  const resetLevel = () => {
    setAmplitudes(zeroAmps)
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
      sceneViewportClassName="h-[440px] pt-[104px] sm:pt-[78px] lg:h-full"
      scene={
        <div className="relative flex h-full items-center justify-center bg-[radial-gradient(circle_at_24%_18%,rgba(106,155,204,0.14),transparent_30%),linear-gradient(180deg,#fffdf7,#f5f3ec)] p-4">
          <ResultMoment show={levelSuccess} label="сигнал собран" />
          {showRepairMarker && diagnosis.worstHarmonic !== null && (
            <RepairMarker
              tone="warning"
              label={`гармоника ${diagnosis.worstHarmonic + 1}`}
              xPercent={50}
              yPercent={3}
            />
          )}
          <svg
            viewBox={`0 0 ${PLOT_W} ${PLOT_H}`}
            className="w-full max-w-[680px] rounded-md border border-ink/10 bg-paper shadow-[0_18px_42px_rgba(20,20,19,0.12)]"
            data-testid="fourier-synth-canvas"
            aria-label="Сумма гармоник против целевого сигнала"
          >
            <line x1={PAD_X} y1={PLOT_H / 2} x2={PLOT_W - PAD_X} y2={PLOT_H / 2} className="stroke-ink/25" strokeWidth="0.2" />
            <polyline
              points={targetCurve}
              className="fill-none stroke-target/55"
              strokeWidth="0.55"
              strokeDasharray="1.4 1"
              strokeLinejoin="round"
              data-testid="fourier-target-curve"
            />
            <polyline
              points={reconCurve}
              className={levelSuccess ? 'fill-none stroke-success' : 'fill-none stroke-orange'}
              strokeWidth="0.6"
              strokeLinejoin="round"
              strokeLinecap="round"
              data-testid="fourier-reconstruction-curve"
            />
          </svg>
        </div>
      }
      controls={
        <div className="space-y-3">
          <div className="grid gap-2">
            {amplitudes.map((amplitude, index) => {
              const isWorst = diagnosis.worstHarmonic === index && !levelSuccess
              return (
                <label key={index} className="grid gap-1 text-xs text-ink/70">
                  <span className="flex items-center justify-between gap-2">
                    <span className={`font-semibold ${isWorst ? 'text-orange' : 'text-ink'}`}>
                      sin({index + 1}·x)
                    </span>
                    <span className="tabular-nums">{formatAmplitude(amplitude)}</span>
                  </span>
                  <input
                    type="range"
                    min={amplitudeStops.min}
                    max={amplitudeStops.max}
                    step={amplitudeStops.step}
                    value={amplitude}
                    onChange={(event) => setAmplitude(index, Number(event.target.value))}
                    className="accent-orange"
                    data-testid={`fourier-harmonic-${index + 1}`}
                  />
                </label>
              )
            })}
          </div>

          <div
            className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5 text-xs leading-relaxed text-ink/70"
            data-testid="fourier-diagnosis"
          >
            <p className="font-semibold text-ink">{diagnosis.message}</p>
            <p className="mt-1">{diagnosis.repairHint}</p>
          </div>

          <button
            type="button"
            onClick={resetLevel}
            className="inline-flex items-center gap-1 rounded border border-ink/10 bg-paper px-2 py-1 text-xs font-semibold text-ink/75 hover:border-orange/40 hover:text-ink"
            data-testid="fourier-reset"
          >
            <RotateCcw size={14} /> Сбросить уровень
          </button>
        </div>
      }
      feedback={
        <p>
          Спектр: [{amplitudes.map((value) => formatAmplitude(value)).join(', ')}]. Энергия ошибки:{' '}
          <span className="font-semibold">{formatAmplitude(error)}</span>. Диагноз:{' '}
          <span className="font-semibold">{diagnosis.kind}</span>.
        </p>
      }
    />
  )
}
