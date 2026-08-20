import { useEffect, useState } from 'react'
import { CodeTracePanel } from '../../game/components/programming/CodeTracePanel'
import { StrategyRace } from '../../game/components/programming/StrategyRace'
import { StrategyCompare } from '../../game/components/programming/StrategyCompare'
import { MissionShell } from '../../game/components/MissionShell'
import { RepairMarker } from '../../game/components/RepairMarker'
import { ResultMoment } from '../../game/components/ResultMoment'
import { chooseMascotState, missionMessage } from '../../game/missionFeedback'
import { asymptoticArenaMission } from '../../game/missions'
import type { MissionBadge, MissionLevel } from '../../game/missionTypes'
import { useMissionRuntime } from '../../game/useMissionRuntime'
import {
  asymptoticScenarios,
  asymptoticStrategies,
  bestStrategyForScenario,
  codeTraceForStrategy,
  diagnoseStrategyChoice,
  estimateCost,
  growthPoints,
  metricsForStrategy,
  strategyRaceEntries,
  type AlgorithmStrategyId,
  type InputScenarioId,
} from './asymptoticArenaModel'

const levelScenario: Record<string, InputScenarioId> = {
  'small-input': 'small-random',
  'large-input': 'large-random',
  'nearly-sorted': 'nearly-sorted',
  'many-lookups': 'many-lookups',
}

const initialStrategy: Record<InputScenarioId, AlgorithmStrategyId> = {
  'small-random': 'binary-search-after-sort',
  'large-random': 'insertion-sort',
  'nearly-sorted': 'merge-sort',
  'many-lookups': 'linear-scan',
}

function formatCost(value: number): string {
  if (value >= 1_000_000) return `${Math.round(value / 1_000_000)}M`
  if (value >= 1_000) return `${Math.round(value / 1_000)}k`
  return String(Math.round(value))
}

export function AsymptoticArenaMission() {
  const definition = asymptoticArenaMission
  const runtime = useMissionRuntime(definition)
  const activeLevel = runtime.activeLevel
  return (
    <AsymptoticArenaLevel
      key={activeLevel.id}
      activeLevel={activeLevel}
      completeActiveLevel={runtime.completeActiveLevel}
      setActiveLevelId={runtime.setActiveLevelId}
    />
  )
}

function AsymptoticArenaLevel({
  activeLevel,
  completeActiveLevel,
  setActiveLevelId,
}: {
  activeLevel: MissionLevel
  completeActiveLevel: () => void
  setActiveLevelId: (levelId: string) => void
}) {
  const definition = asymptoticArenaMission
  const scenario = asymptoticScenarios[levelScenario[activeLevel.id]]
  const [strategyId, setStrategyId] = useState<AlgorithmStrategyId>(initialStrategy[scenario.id])
  const bestStrategy = bestStrategyForScenario(scenario)
  const diagnosis = diagnoseStrategyChoice(strategyId, scenario)
  const levelSuccess = diagnosis.invariantOk
  const cost = estimateCost(strategyId, scenario)
  const metrics = metricsForStrategy(strategyId, scenario)
  const raceEntries = strategyRaceEntries(scenario)
  const growthByStrategy = Object.fromEntries(
    asymptoticStrategies.map((strategy) => [
      strategy.id,
      growthPoints(strategy.id as AlgorithmStrategyId, scenario),
    ]),
  )

  const repairLabelByKind: Record<string, string> = {
    'quadratic-explodes': 'O(n^2) взрыв',
    'setup-not-worth-it': 'setup зря',
    'preprocessing-pays-off': 'нужен препроцесс',
    'constant-wins-small-n': 'проще для малого n',
    'memory-tradeoff': 'память дорога',
    'wrong-cost-model': 'модель не та',
  }
  const repairLabel = repairLabelByKind[diagnosis.kind] ?? 'не оптимально'

  useEffect(() => {
    if (!levelSuccess) return
    completeActiveLevel()
  }, [completeActiveLevel, levelSuccess])

  const mascotState = chooseMascotState({
    success: levelSuccess,
    warning: !levelSuccess,
    hint: diagnosis.kind === 'setup-not-worth-it' || diagnosis.kind === 'preprocessing-pays-off',
  })
  const mascotMessage = missionMessage(mascotState, {
    success: activeLevel.successText,
    warning: activeLevel.mistakeFeedback?.[0] ?? diagnosis.message,
    hint: activeLevel.hint,
    thinking: 'Сравни setup, число запросов и рост на больших n.',
    idle: 'Выбери стратегию: я посчитаю стоимость по явной модели.',
  })

  const badges: MissionBadge[] = [
    {
      id: 'total',
      label: 'total',
      value: formatCost(cost.total),
      tone: levelSuccess ? 'success' : 'warning',
    },
    {
      id: 'complexity',
      label: 'best',
      value: asymptoticStrategies.find((strategy) => strategy.id === bestStrategy)?.complexity ?? '',
      tone: 'target',
    },
    {
      id: 'queries',
      label: 'q',
      value: scenario.queries,
      tone: scenario.queries > 1 ? 'energy' : 'neutral',
    },
  ]

  return (
    <MissionShell
      definition={definition}
      activeLevelId={activeLevel.id}
      onLevelSelect={setActiveLevelId}
      mascotState={mascotState}
      mascotMessage={mascotMessage}
      badges={badges}
      sceneViewportClassName="min-h-[1180px] pt-[176px] sm:min-h-[1040px] sm:pt-[112px] lg:h-full lg:min-h-0 lg:pt-[74px]"
      scene={
        <div className="flex h-full items-start justify-center bg-[radial-gradient(circle_at_68%_18%,rgba(77,134,168,0.14),transparent_28%),linear-gradient(180deg,#fffdf7,#faf9f5)] p-4 lg:items-center">
          <div className="relative grid w-full max-w-5xl gap-4 lg:grid-cols-[1.1fr_0.9fr]">
            <ResultMoment show={levelSuccess} label="стратегия-победитель" />
            {!levelSuccess && (
              <RepairMarker tone="warning" label={repairLabel} xPercent={50} yPercent={1} />
            )}
            <section className="rounded-md border border-ink/10 bg-paper/90 p-4 shadow-[0_18px_42px_rgba(20,20,19,0.08)]">
              <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-wide text-orange">
                    input scenario
                  </p>
                  <h2 className="mt-1 text-xl font-semibold text-ink">{scenario.title}</h2>
                  <p className="mt-1 text-sm leading-relaxed text-ink/62">{scenario.goal}</p>
                </div>
                <div className="grid grid-cols-3 gap-2 text-center text-xs">
                  <span className="rounded border border-ink/10 bg-bg px-2 py-1">
                    n <b>{scenario.n}</b>
                  </span>
                  <span className="rounded border border-ink/10 bg-bg px-2 py-1">
                    q <b>{scenario.queries}</b>
                  </span>
                  <span className="rounded border border-ink/10 bg-bg px-2 py-1">
                    disorder <b>{Math.round(scenario.disorder * 100)}%</b>
                  </span>
                </div>
              </div>
              <StrategyCompare
                strategies={asymptoticStrategies}
                selectedStrategyId={strategyId}
                onSelect={(next) => setStrategyId(next as AlgorithmStrategyId)}
                growthPointsByStrategy={growthByStrategy}
                recommendedStrategyId={bestStrategy}
                diagnosis={diagnosis.kind}
              />
            </section>

            <section className="rounded-md border border-ink/10 bg-panel/35 p-4 shadow-[0_18px_42px_rgba(20,20,19,0.06)]">
              <div className="space-y-4">
                <StrategyRace
                  entries={raceEntries}
                  selectedStrategyId={strategyId}
                  recommendedStrategyId={bestStrategy}
                />
                <CodeTracePanel
                  lines={codeTraceForStrategy(strategyId)}
                  variables={{
                    n: scenario.n,
                    q: scenario.queries,
                    strategy: strategyId,
                  }}
                  metrics={metrics}
                  invariantOk={diagnosis.invariantOk}
                  invariantLabel={diagnosis.invariantOk ? 'cost model matched' : 'cost model broken'}
                />
              </div>
            </section>
          </div>
        </div>
      }
      controls={
        <div className="space-y-2">
          <div className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5 text-xs leading-relaxed text-ink/70">
            <p className="font-semibold text-ink">{diagnosis.message}</p>
            <p className="mt-1">{diagnosis.repairHint}</p>
          </div>
          <p className="text-xs leading-relaxed text-ink/60">
            Cost model: total = setup + comparisons, memory считается отдельным
            ограничением.
          </p>
        </div>
      }
      feedback={
        <p>
          Выбрано: <span className="font-semibold">{strategyId}</span>. Total:{' '}
          <span className="font-semibold">{formatCost(cost.total)}</span>. Диагноз:{' '}
          <span className="font-semibold">{diagnosis.kind}</span>.
        </p>
      }
    />
  )
}
