import { useEffect, useMemo, useState } from 'react'
import { Dices, RotateCcw } from 'lucide-react'
import { MissionShell } from '../../game/components/MissionShell'
import { RepairMarker } from '../../game/components/RepairMarker'
import { ResultMoment } from '../../game/components/ResultMoment'
import { chooseMascotState, missionMessage } from '../../game/missionFeedback'
import { bayesForkMission } from '../../game/missions'
import type { MissionBadge, MissionLevel } from '../../game/missionTypes'
import { useMissionRuntime } from '../../game/useMissionRuntime'
import {
  bayesLevels,
  bayesLevelSuccess,
  diagnoseBayes,
  empiricalQuantity,
  formatProbability,
  runBayes,
  sampleSizeStops,
  type BayesLevelId,
} from './bayesForkModel'

const levelIdMap: Record<string, BayesLevelId> = {
  'conditional-frequency': 'conditional-frequency',
  'base-rate': 'base-rate',
  'two-tests': 'two-tests',
}

export function BayesForkMission() {
  const definition = bayesForkMission
  const runtime = useMissionRuntime(definition)
  const activeLevel = runtime.activeLevel
  return (
    <BayesForkLevel
      key={activeLevel.id}
      activeLevel={activeLevel}
      completeActiveLevel={runtime.completeActiveLevel}
      setActiveLevelId={runtime.setActiveLevelId}
    />
  )
}

function BayesForkLevel({
  activeLevel,
  completeActiveLevel,
  setActiveLevelId,
}: {
  activeLevel: MissionLevel
  completeActiveLevel: () => void
  setActiveLevelId: (levelId: string) => void
}) {
  const definition = bayesForkMission
  const levelId = levelIdMap[activeLevel.id]
  const config = bayesLevels[levelId]
  const [sampleSize, setSampleSize] = useState<number>(sampleSizeStops[0])
  const [estimate, setEstimate] = useState<number>(0.5)
  const [touched, setTouched] = useState(false)

  const run = useMemo(() => runBayes(levelId, sampleSize), [levelId, sampleSize])
  const empirical = empiricalQuantity(levelId, run)
  const diagnosis = diagnoseBayes({ levelId, sampleSize, estimate, touched })
  const levelSuccess = bayesLevelSuccess({ levelId, sampleSize, estimate })

  useEffect(() => {
    if (levelSuccess) completeActiveLevel()
  }, [completeActiveLevel, levelSuccess])

  const showRepairMarker =
    touched && !levelSuccess && diagnosis.kind !== 'idle' && diagnosis.kind !== 'success'
  const repairLabel =
    diagnosis.kind === 'too-few-samples'
      ? 'мало данных'
      : diagnosis.kind === 'base-rate-neglect'
        ? 'путаешь направление'
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
    thinking: 'Я считаю случаи по клеткам таблицы. Набери выборку и читай нужный срез.',
    idle: 'Условие сужает таблицу до строки или столбца. Сначала собери данные.',
  })

  const posLabel = config.doubleTest ? 'Два +' : 'Тест +'
  const negLabel = config.doubleTest ? 'Не оба +' : 'Тест −'
  const conditionRow = config.conditionOn === 'row'
  const readoutLabel = conditionRow ? `P(${posLabel.toLowerCase()} | болезнь)` : `P(болезнь | ${posLabel.toLowerCase()})`
  const numerator = run.a
  const denominator = conditionRow ? run.a + run.b : run.a + run.c

  const badges: MissionBadge[] = [
    {
      id: 'estimate',
      label: 'оценка',
      value: formatProbability(estimate),
      tone: levelSuccess ? 'success' : 'energy',
    },
    {
      id: 'read',
      label: conditionRow ? 'P(+|D)' : 'P(D|+)',
      value: formatProbability(empirical),
      tone: 'target',
    },
    {
      id: 'samples',
      label: 'n',
      value: sampleSize,
      tone: sampleSize >= config.minSamples ? 'success' : 'neutral',
    },
  ]

  // Highlight the slice the answer conditions on; the numerator cell glows most.
  const cellClass = (isNumerator: boolean, inSlice: boolean) =>
    isNumerator
      ? 'bg-orange/18 ring-1 ring-orange/45 text-ink'
      : inSlice
        ? 'bg-highlight text-ink'
        : 'bg-paper text-ink/55'

  const resetLevel = () => {
    setSampleSize(sampleSizeStops[0])
    setEstimate(0.5)
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
        <div className="relative flex h-full flex-col items-center justify-center gap-4 bg-[radial-gradient(circle_at_22%_16%,rgba(106,155,204,0.16),transparent_30%),linear-gradient(180deg,#fffdf7,#f5f3ec)] p-4">
          <ResultMoment show={levelSuccess} label="вероятность прочитана" />
          {showRepairMarker && (
            <RepairMarker tone="warning" label={repairLabel} xPercent={50} yPercent={4} />
          )}
          <div
            className="w-full max-w-[460px] rounded-md border border-ink/10 bg-paper/90 p-3 shadow-[0_18px_42px_rgba(20,20,19,0.12)]"
            data-testid="bayes-table"
          >
            <div className="grid grid-cols-[7rem_1fr_1fr] gap-1 text-center text-sm">
              <div className="px-2 py-1.5 text-[11px] font-semibold uppercase tracking-wide text-ink/40" />
              <div className={`rounded px-2 py-1.5 text-[11px] font-semibold uppercase tracking-wide ${!conditionRow ? 'text-orange' : 'text-ink/45'}`}>
                {posLabel}
              </div>
              <div className="px-2 py-1.5 text-[11px] font-semibold uppercase tracking-wide text-ink/45">
                {negLabel}
              </div>

              <div className={`rounded px-2 py-2 text-left text-xs font-semibold ${conditionRow ? 'text-orange' : 'text-ink/60'}`}>
                Болезнь есть
              </div>
              <div className={`rounded px-2 py-2 font-semibold tabular-nums ${cellClass(true, conditionRow)}`} data-testid="bayes-cell-a">
                {run.a}
              </div>
              <div className={`rounded px-2 py-2 font-semibold tabular-nums ${cellClass(false, conditionRow)}`}>
                {run.b}
              </div>

              <div className="rounded px-2 py-2 text-left text-xs font-semibold text-ink/60">
                Болезни нет
              </div>
              <div className={`rounded px-2 py-2 font-semibold tabular-nums ${cellClass(false, !conditionRow)}`} data-testid="bayes-cell-c">
                {run.c}
              </div>
              <div className="rounded bg-paper px-2 py-2 font-semibold tabular-nums text-ink/55">
                {run.d}
              </div>
            </div>
            <p className="mt-3 border-t border-ink/10 pt-2 text-center text-sm text-ink/75" data-testid="bayes-readout">
              {readoutLabel} ={' '}
              <span className="font-semibold tabular-nums text-ink">
                {numerator} / {denominator}
              </span>{' '}
              ={' '}
              <span className="font-semibold tabular-nums text-orange">{formatProbability(empirical)}</span>
            </p>
          </div>
          <p className="max-w-[460px] text-center text-xs leading-relaxed text-ink/55">
            {conditionRow
              ? 'Условие «болезнь есть» оставляет верхнюю строку: доля плюсов в ней — чувствительность.'
              : 'Условие «тест +» оставляет левый столбец: доля больных в нём — апостериор, и базовая частота тянет его вниз.'}
          </p>
        </div>
      }
      controls={
        <div className="space-y-3">
          <div>
            <p className="mb-1 text-[10px] font-black uppercase tracking-wide text-ink/45">наблюдений</p>
            <div className="flex flex-wrap gap-2" data-testid="bayes-sample-controls">
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
                  data-testid={`bayes-sample-${stop}`}
                >
                  <Dices size={13} /> {stop}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="mb-1 flex items-center justify-between text-[10px] font-black uppercase tracking-wide text-ink/45">
              <span>твоя оценка</span>
              <span className="tabular-nums text-ink/70">{formatProbability(estimate)}</span>
            </label>
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
              className="w-full accent-orange"
              data-testid="bayes-estimate"
              aria-label="Оценка условной вероятности"
            />
          </div>

          <div
            className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5 text-xs leading-relaxed text-ink/70"
            data-testid="bayes-diagnosis"
          >
            <p className="font-semibold text-ink">{diagnosis.message}</p>
            <p className="mt-1">{diagnosis.repairHint}</p>
            <p className="mt-1 text-ink/55">
              читаешь {numerator} из {denominator} (= {formatProbability(empirical)})
            </p>
          </div>

          <button
            type="button"
            onClick={resetLevel}
            className="inline-flex items-center gap-1 rounded border border-ink/10 bg-paper px-2 py-1 text-xs font-semibold text-ink/75 hover:border-orange/40 hover:text-ink"
            data-testid="bayes-reset"
          >
            <RotateCcw size={14} /> Сбросить уровень
          </button>
        </div>
      }
      feedback={
        <p>
          seed = <span className="font-semibold">{config.seed}</span>, читаешь ={' '}
          <span className="font-semibold">{formatProbability(empirical)}</span>. Диагноз:{' '}
          <span className="font-semibold">{diagnosis.kind}</span>.
        </p>
      }
    />
  )
}
