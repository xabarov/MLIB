import { useEffect, useMemo, useState } from 'react'
import { Dices, RotateCcw } from 'lucide-react'
import { MissionShell } from '../../game/components/MissionShell'
import { RepairMarker } from '../../game/components/RepairMarker'
import { ResultMoment } from '../../game/components/ResultMoment'
import { chooseMascotState, missionMessage } from '../../game/missionFeedback'
import { bernoulliLabMission } from '../../game/missions'
import type { MissionBadge, MissionLevel } from '../../game/missionTypes'
import { useMissionRuntime } from '../../game/useMissionRuntime'
import {
  bernoulliLevelSuccess,
  bernoulliLevels,
  diagnoseBernoulli,
  formatProbability,
  runBernoulli,
  runningFrequency,
  sampleSizeStops,
  type BernoulliLevelId,
} from './bernoulliLabModel'

const levelIdMap: Record<string, BernoulliLevelId> = {
  'fair-coin': 'fair-coin',
  'estimate-bias': 'estimate-bias',
  'law-of-large-numbers': 'law-of-large-numbers',
}

const CHART_W = 100
const CHART_H = 60
const PAD = 6

function freqToY(freq: number): number {
  return CHART_H - PAD - freq * (CHART_H - 2 * PAD)
}

function indexToX(index: number, total: number): number {
  if (total <= 1) return PAD
  return PAD + (index / (total - 1)) * (CHART_W - 2 * PAD)
}

/** Downsample a long frequency series so the polyline stays light. */
function sampleSeries(freqs: number[], maxPoints = 160): { i: number; freq: number }[] {
  if (freqs.length <= maxPoints) {
    return freqs.map((freq, i) => ({ i, freq }))
  }
  const step = freqs.length / maxPoints
  const points: { i: number; freq: number }[] = []
  for (let k = 0; k < maxPoints; k += 1) {
    const i = Math.min(freqs.length - 1, Math.floor(k * step))
    points.push({ i, freq: freqs[i] })
  }
  points.push({ i: freqs.length - 1, freq: freqs[freqs.length - 1] })
  return points
}

export function BernoulliLabMission() {
  const definition = bernoulliLabMission
  const runtime = useMissionRuntime(definition)
  const activeLevel = runtime.activeLevel
  return (
    <BernoulliLabLevel
      key={activeLevel.id}
      activeLevel={activeLevel}
      completeActiveLevel={runtime.completeActiveLevel}
      setActiveLevelId={runtime.setActiveLevelId}
    />
  )
}

function BernoulliLabLevel({
  activeLevel,
  completeActiveLevel,
  setActiveLevelId,
}: {
  activeLevel: MissionLevel
  completeActiveLevel: () => void
  setActiveLevelId: (levelId: string) => void
}) {
  const definition = bernoulliLabMission
  const levelId = levelIdMap[activeLevel.id]
  const config = bernoulliLevels[levelId]
  const [sampleSize, setSampleSize] = useState<number>(sampleSizeStops[0])
  const [estimate, setEstimate] = useState<number>(0.5)
  const [touched, setTouched] = useState(false)

  const run = useMemo(() => runBernoulli(config.seed, config.trueP, sampleSize), [config, sampleSize])
  const freqs = useMemo(() => runningFrequency(run.sequence), [run])
  const series = useMemo(() => sampleSeries(freqs), [freqs])
  const diagnosis = diagnoseBernoulli({ levelId, sampleSize, estimate, touched })
  const levelSuccess = bernoulliLevelSuccess({ levelId, sampleSize, estimate })

  useEffect(() => {
    if (levelSuccess) completeActiveLevel()
  }, [completeActiveLevel, levelSuccess])

  const showRepairMarker =
    touched && !levelSuccess && diagnosis.kind !== 'idle' && diagnosis.kind !== 'success'
  const repairLabel =
    diagnosis.kind === 'too-few-samples'
      ? 'мало бросков'
      : diagnosis.kind === 'estimate-off'
        ? 'оценка мимо'
        : 'коридор шире'

  const mascotState = chooseMascotState({
    success: levelSuccess,
    warning: showRepairMarker,
    hint: touched && sampleSize >= config.minSamples,
    thinking: !touched,
  })
  const mascotMessage = missionMessage(mascotState, {
    success: activeLevel.successText,
    warning: activeLevel.mistakeFeedback?.[0] ?? diagnosis.message,
    hint: activeLevel.hint,
    thinking: 'Я сижу на линии частоты. Брось больше монет и смотри, куда она садится.',
    idle: 'Выбери число бросков. Частота — это доля решек в выборке.',
  })

  const badges: MissionBadge[] = [
    {
      id: 'samples',
      label: 'n',
      value: sampleSize,
      tone: sampleSize >= config.minSamples ? 'success' : 'neutral',
    },
    {
      id: 'frequency',
      label: 'freq',
      value: formatProbability(run.frequency),
      tone: levelSuccess ? 'success' : 'energy',
    },
    {
      id: 'heads',
      label: 'heads',
      value: `${run.heads}/${sampleSize}`,
      tone: 'target',
    },
  ]

  const resetLevel = () => {
    setSampleSize(sampleSizeStops[0])
    setEstimate(0.5)
    setTouched(false)
  }

  const targetY = freqToY(config.targetFreq)
  const bandTop = freqToY(config.targetFreq + config.tolerance)
  const bandBottom = freqToY(config.targetFreq - config.tolerance)
  const estimateY = freqToY(estimate)
  const polyline = series.map((point) => `${indexToX(point.i, sampleSize)},${freqToY(point.freq)}`).join(' ')
  const headsWidth = sampleSize > 0 ? (run.heads / sampleSize) * 100 : 0

  return (
    <MissionShell
      definition={definition}
      activeLevelId={activeLevel.id}
      onLevelSelect={setActiveLevelId}
      mascotState={mascotState}
      mascotMessage={mascotMessage}
      badges={badges}
      sceneViewportClassName="min-h-[440px] pt-[112px] sm:pt-[82px] lg:h-full"
      scene={
        <div className="relative flex h-full flex-col gap-3 bg-[radial-gradient(circle_at_24%_18%,rgba(124,108,207,0.14),transparent_30%),linear-gradient(180deg,#fffdf7,#f6f3ee)] p-4">
          <ResultMoment show={levelSuccess} label="частота поймала вероятность" />
          {showRepairMarker && (
            <RepairMarker tone="warning" label={repairLabel} xPercent={50} yPercent={2} />
          )}
          <svg
            viewBox={`0 0 ${CHART_W} ${CHART_H}`}
            className="w-full flex-1 rounded-md border border-ink/10 bg-paper shadow-[0_16px_36px_rgba(20,20,19,0.10)]"
            data-testid="bernoulli-lab-canvas"
            aria-label="Сходимость частоты бросков к вероятности"
          >
            {[0, 0.25, 0.5, 0.75, 1].map((tick) => (
              <g key={tick}>
                <line
                  x1={PAD}
                  y1={freqToY(tick)}
                  x2={CHART_W - PAD}
                  y2={freqToY(tick)}
                  className="stroke-grid"
                  strokeWidth="0.2"
                />
                <text x={1.5} y={freqToY(tick) + 1} className="fill-ink/40" fontSize="2.6">
                  {tick.toFixed(2)}
                </text>
              </g>
            ))}

            {config.knownP && (
              <>
                <rect
                  x={PAD}
                  y={bandTop}
                  width={CHART_W - 2 * PAD}
                  height={Math.max(0, bandBottom - bandTop)}
                  className="fill-success/12"
                />
                <line
                  x1={PAD}
                  y1={targetY}
                  x2={CHART_W - PAD}
                  y2={targetY}
                  className="stroke-success"
                  strokeWidth="0.35"
                  strokeDasharray="1.4 1"
                  data-testid="bernoulli-target-line"
                />
              </>
            )}

            {levelId === 'estimate-bias' && (
              <line
                x1={PAD}
                y1={estimateY}
                x2={CHART_W - PAD}
                y2={estimateY}
                className="stroke-orange"
                strokeWidth="0.35"
                strokeDasharray="1.2 0.8"
                data-testid="bernoulli-estimate-line"
              />
            )}

            <polyline
              points={polyline}
              className="fill-none stroke-target"
              strokeWidth="0.5"
              strokeLinejoin="round"
              strokeLinecap="round"
              data-testid="bernoulli-frequency-line"
            />
            <circle
              cx={indexToX(sampleSize - 1, sampleSize)}
              cy={freqToY(run.frequency)}
              r={1.1}
              className="fill-orange stroke-ink"
              strokeWidth="0.2"
            />
          </svg>

          <div className="grid grid-cols-[auto_1fr] items-center gap-3 rounded-md border border-ink/10 bg-bg/80 px-3 py-2 text-xs">
            <span className="font-semibold text-ink">heads vs tails</span>
            <div className="h-4 w-full overflow-hidden rounded-full border border-ink/10 bg-target/15">
              <div
                className="h-full rounded-l-full bg-orange/70"
                style={{ width: `${headsWidth}%` }}
                data-testid="bernoulli-heads-bar"
              />
            </div>
          </div>
        </div>
      }
      controls={
        <div className="space-y-3">
          <div>
            <p className="mb-1 text-[10px] font-black uppercase tracking-wide text-ink/45">бросков</p>
            <div className="flex flex-wrap gap-2" data-testid="bernoulli-sample-controls">
              {sampleSizeStops.map((stop) => (
                <button
                  key={stop}
                  type="button"
                  onClick={() => {
                    setTouched(true)
                    setSampleSize(stop)
                  }}
                  className={`inline-flex items-center gap-1 rounded border px-2.5 py-1.5 text-xs font-semibold transition ${
                    sampleSize === stop
                      ? 'border-target bg-target text-bg'
                      : 'border-ink/10 bg-paper text-ink hover:border-target/50'
                  }`}
                  data-testid={`bernoulli-sample-${stop}`}
                >
                  <Dices size={13} /> {stop}
                </button>
              ))}
            </div>
          </div>

          {levelId === 'estimate-bias' && (
            <label className="grid gap-1 text-xs text-ink/70">
              <span className="flex items-center justify-between gap-2">
                <span className="font-semibold text-ink">оценка p</span>
                <span className="tabular-nums">{formatProbability(estimate)}</span>
              </span>
              <input
                type="range"
                min={0}
                max={1}
                step={0.01}
                value={estimate}
                onChange={(event) => {
                  setTouched(true)
                  setEstimate(Number(event.target.value))
                }}
                className="accent-orange"
                data-testid="bernoulli-estimate"
              />
            </label>
          )}

          <div
            className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5 text-xs leading-relaxed text-ink/70"
            data-testid="bernoulli-diagnosis"
          >
            <p className="font-semibold text-ink">{diagnosis.message}</p>
            <p className="mt-1">{diagnosis.repairHint}</p>
          </div>

          <button
            type="button"
            onClick={resetLevel}
            className="inline-flex items-center gap-1 rounded border border-ink/10 bg-paper px-2 py-1 text-xs font-semibold text-ink/75 hover:border-orange/40 hover:text-ink"
            data-testid="bernoulli-reset"
          >
            <RotateCcw size={14} /> Сбросить уровень
          </button>
        </div>
      }
      feedback={
        <p>
          seed = <span className="font-semibold">{config.seed}</span>, freq ={' '}
          <span className="font-semibold">{formatProbability(run.frequency)}</span>. Диагноз:{' '}
          <span className="font-semibold">{diagnosis.kind}</span>.
        </p>
      }
    />
  )
}
