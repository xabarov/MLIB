import { useEffect, useMemo, useState } from 'react'
import { Dices, RotateCcw } from 'lucide-react'
import { MissionShell } from '../../game/components/MissionShell'
import { RepairMarker } from '../../game/components/RepairMarker'
import { ResultMoment } from '../../game/components/ResultMoment'
import { chooseMascotState, missionMessage } from '../../game/missionFeedback'
import { expectationLabMission } from '../../game/missions'
import type { MissionBadge, MissionLevel } from '../../game/missionTypes'
import { useMissionRuntime } from '../../game/useMissionRuntime'
import {
  DIE_FACES,
  diagnoseExpectation,
  empiricalMean,
  empiricalQuantity,
  empiricalVariance,
  expectationLevels,
  expectationLevelSuccess,
  formatExpectation,
  runExpectation,
  sampleSizeStops,
  type ExpectationLevelId,
} from './expectationLabModel'

const levelIdMap: Record<string, ExpectationLevelId> = {
  'sample-mean': 'sample-mean',
  'sample-variance': 'sample-variance',
  'estimate-mean': 'estimate-mean',
}

const PLOT_W = 120
const PLOT_H = 66

export function ExpectationLabMission() {
  const definition = expectationLabMission
  const runtime = useMissionRuntime(definition)
  const activeLevel = runtime.activeLevel
  return (
    <ExpectationLabLevel
      key={activeLevel.id}
      activeLevel={activeLevel}
      completeActiveLevel={runtime.completeActiveLevel}
      setActiveLevelId={runtime.setActiveLevelId}
    />
  )
}

function ExpectationLabLevel({
  activeLevel,
  completeActiveLevel,
  setActiveLevelId,
}: {
  activeLevel: MissionLevel
  completeActiveLevel: () => void
  setActiveLevelId: (levelId: string) => void
}) {
  const definition = expectationLabMission
  const levelId = levelIdMap[activeLevel.id]
  const config = expectationLevels[levelId]
  const [sampleSize, setSampleSize] = useState<number>(sampleSizeStops[0])
  const [estimate, setEstimate] = useState<number>(3)
  const [touched, setTouched] = useState(false)

  const run = useMemo(() => runExpectation(levelId, sampleSize), [levelId, sampleSize])
  const mean = empiricalMean(run)
  const variance = empiricalVariance(run)
  const reading = empiricalQuantity(levelId, run)
  const diagnosis = diagnoseExpectation({ levelId, sampleSize, estimate, touched })
  const levelSuccess = expectationLevelSuccess({ levelId, sampleSize, estimate })

  useEffect(() => {
    if (levelSuccess) completeActiveLevel()
  }, [completeActiveLevel, levelSuccess])

  const showRepairMarker =
    touched && !levelSuccess && diagnosis.kind !== 'idle' && diagnosis.kind !== 'success'
  const repairLabel =
    diagnosis.kind === 'too-few-samples'
      ? 'мало бросков'
      : diagnosis.kind === 'std-not-variance'
        ? 'это σ, не дисперсия'
        : 'оценка мимо'

  const mascotState = chooseMascotState({
    success: levelSuccess,
    warning: showRepairMarker,
    hint: touched && sampleSize >= config.minSamples,
    thinking: !touched,
  })
  const mascotMessage = missionMessage(mascotState, {
    success: activeLevel.successText,
    warning: diagnosis.message,
    hint: activeLevel.hint,
    thinking: 'Я считаю частоты граней. Брось больше — среднее и разброс устаканятся.',
    idle: 'Бросай кость и следи, к чему сходится среднее значение.',
  })

  const quantityLabel = config.quantity === 'mean' ? 'E[X]≈' : 'Var≈'
  const badges: MissionBadge[] = [
    {
      id: 'estimate',
      label: 'оценка',
      value: formatExpectation(estimate),
      tone: levelSuccess ? 'success' : 'energy',
    },
    {
      id: 'reading',
      label: quantityLabel,
      value: formatExpectation(reading),
      tone: 'target',
    },
    {
      id: 'samples',
      label: 'n',
      value: sampleSize,
      tone: sampleSize >= config.minSamples ? 'success' : 'neutral',
    },
  ]

  const maxCount = Math.max(1, ...run.counts)
  const barSlot = PLOT_W / DIE_FACES.length
  const meanX = ((mean - 0.5) / DIE_FACES.length) * PLOT_W

  const resetLevel = () => {
    setSampleSize(sampleSizeStops[0])
    setEstimate(3)
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
      sceneViewportClassName="h-[460px] pt-[104px] sm:pt-[78px] lg:h-full"
      scene={
        <div className="relative flex h-full flex-col items-center justify-center gap-4 bg-[radial-gradient(circle_at_22%_16%,rgba(95,141,101,0.16),transparent_30%),linear-gradient(180deg,#fffdf7,#f5f3ec)] p-4">
          <ResultMoment show={levelSuccess} label="оценка сошлась" />
          {showRepairMarker && (
            <RepairMarker tone="warning" label={repairLabel} xPercent={50} yPercent={4} />
          )}
          <svg
            viewBox={`-6 -8 ${PLOT_W + 12} ${PLOT_H + 24}`}
            className="w-full max-w-[520px] rounded-md border border-ink/10 bg-paper shadow-[0_18px_42px_rgba(20,20,19,0.12)]"
            data-testid="expectation-canvas"
            aria-label="Гистограмма граней кости"
          >
            <line x1={0} y1={PLOT_H} x2={PLOT_W} y2={PLOT_H} className="stroke-ink/30" strokeWidth="0.4" />
            {run.counts.map((count, index) => {
              const height = (count / maxCount) * (PLOT_H - 6)
              const x = index * barSlot + barSlot * 0.18
              const width = barSlot * 0.64
              return (
                <g key={index}>
                  <rect
                    x={x}
                    y={PLOT_H - height}
                    width={width}
                    height={height}
                    className="fill-success/55"
                  />
                  <text
                    x={x + width / 2}
                    y={PLOT_H + 6}
                    textAnchor="middle"
                    className="fill-ink/55"
                    style={{ fontSize: 4 }}
                  >
                    {DIE_FACES[index]}
                  </text>
                </g>
              )
            })}
            {/* Empirical mean marker. */}
            <line
              x1={meanX}
              y1={-4}
              x2={meanX}
              y2={PLOT_H}
              className="stroke-orange"
              strokeWidth="0.7"
              strokeDasharray="2 1.5"
              data-testid="expectation-mean-line"
            />
            <text x={meanX} y={-5} textAnchor="middle" className="fill-orange" style={{ fontSize: 4 }}>
              среднее {formatExpectation(mean)}
            </text>
          </svg>
          <p className="max-w-[460px] text-center text-sm text-ink/75" data-testid="expectation-readout">
            {config.quantity === 'mean' ? (
              <>
                среднее ={' '}
                <span className="font-semibold tabular-nums text-orange">{formatExpectation(mean)}</span>{' '}
                (цель E[X] = <span className="tabular-nums">{formatExpectation(config.target)}</span>
                {config.knownWeights ? '' : ', распределение скрыто'})
              </>
            ) : (
              <>
                дисперсия ={' '}
                <span className="font-semibold tabular-nums text-orange">{formatExpectation(variance)}</span>{' '}
                (σ = <span className="tabular-nums">{formatExpectation(Math.sqrt(Math.max(variance, 0)))}</span>,
                цель Var = <span className="tabular-nums">{formatExpectation(config.target)}</span>)
              </>
            )}
          </p>
        </div>
      }
      controls={
        <div className="space-y-3">
          <div>
            <p className="mb-1 text-[10px] font-black uppercase tracking-wide text-ink/45">бросков</p>
            <div className="flex flex-wrap gap-2" data-testid="expectation-sample-controls">
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
                  data-testid={`expectation-sample-${stop}`}
                >
                  <Dices size={13} /> {stop}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="mb-1 flex items-center justify-between text-[10px] font-black uppercase tracking-wide text-ink/45">
              <span>твоя оценка ({config.quantity === 'mean' ? 'E[X]' : 'Var'})</span>
              <span className="tabular-nums text-ink/70">{formatExpectation(estimate)}</span>
            </label>
            <input
              type="range"
              min={0}
              max={6}
              step={0.05}
              value={estimate}
              onChange={(event) => {
                setTouched(true)
                setEstimate(Number(event.target.value))
              }}
              className="w-full accent-orange"
              data-testid="expectation-estimate"
              aria-label="Оценка величины распределения"
            />
          </div>

          <div
            className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5 text-xs leading-relaxed text-ink/70"
            data-testid="expectation-diagnosis"
          >
            <p className="font-semibold text-ink">{diagnosis.message}</p>
            <p className="mt-1">{diagnosis.repairHint}</p>
            <p className="mt-1 text-ink/55">
              {config.quantity === 'mean' ? 'среднее' : 'дисперсия'} ={' '}
              {formatExpectation(reading)} на {sampleSize} бросках
            </p>
          </div>

          <button
            type="button"
            onClick={resetLevel}
            className="inline-flex items-center gap-1 rounded border border-ink/10 bg-paper px-2 py-1 text-xs font-semibold text-ink/75 hover:border-orange/40 hover:text-ink"
            data-testid="expectation-reset"
          >
            <RotateCcw size={14} /> Сбросить уровень
          </button>
        </div>
      }
      feedback={
        <p>
          seed = <span className="font-semibold">{config.seed}</span>, читаешь ={' '}
          <span className="font-semibold">{formatExpectation(reading)}</span>. Диагноз:{' '}
          <span className="font-semibold">{diagnosis.kind}</span>.
        </p>
      }
    />
  )
}
