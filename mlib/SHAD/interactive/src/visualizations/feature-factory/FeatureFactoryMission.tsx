import { useEffect, useMemo, useState } from 'react'
import { DataTableMini } from '../../game/components/data/DataTableMini'
import { FeatureTogglePanel } from '../../game/components/data/FeatureTogglePanel'
import { MetricBoard } from '../../game/components/data/MetricBoard'
import { PipelineDiff } from '../../game/components/data/PipelineDiff'
import { PipelineStrip } from '../../game/components/data/PipelineStrip'
import { SplitInspector } from '../../game/components/data/SplitInspector'
import { MissionShell } from '../../game/components/MissionShell'
import { RepairMarker } from '../../game/components/RepairMarker'
import { ResultMoment } from '../../game/components/ResultMoment'
import { chooseMascotState, missionMessage } from '../../game/missionFeedback'
import { featureFactoryMission } from '../../game/missions'
import type { MissionBadge, MissionLevel } from '../../game/missionTypes'
import { useMissionRuntime } from '../../game/useMissionRuntime'
import {
  diagnoseFactory,
  chooseSplitSeed,
  dropRow,
  dropMissingRows,
  encodeCategory,
  factoryColumns,
  factoryFeatureLabels,
  factoryMetrics,
  fillZero,
  formatPercent,
  imputeMedian,
  initialFactoryState,
  keepRawCategory,
  pipelineDiff,
  splitQuality,
  splitSeedOptions,
  toggleFeature,
  type FeatureFactoryLevelId,
  type FeatureFactoryState,
} from './featureFactoryModel'

const levelIdMap: Record<string, FeatureFactoryLevelId> = {
  'missing-values': 'missing-values',
  'outlier-repair': 'outlier-repair',
  'leakage-off': 'leakage-off',
  'encode-category': 'encode-category',
  'split-check': 'split-check',
}

const levelGoal: Record<FeatureFactoryLevelId, string> = {
  'missing-values': 'Заполни пропуски в temperature так, чтобы не выкинуть test-наблюдения.',
  'outlier-repair': 'Убери только явный выброс ff-07 и сохрани полезные строки.',
  'leakage-off': 'Отключи leakage code: он знает ответ и портит честную проверку.',
  'encode-category': 'Закодируй segment, чтобы категориальный сигнал стал модельным признаком.',
  'split-check': 'Выбери seed, где train/test похожи по label ratio и диапазону signal.',
}

function visibleColumns(state: FeatureFactoryState) {
  const enabled = new Set(state.features.filter((feature) => feature.enabled).map((feature) => feature.id))
  return factoryColumns.filter((column) => enabled.has(column.id))
}

function repairMarkerLabel(kind: string): string | undefined {
  if (kind === 'missing-left' || kind === 'zero-filled' || kind === 'coverage-lost') return 'dirty temp'
  if (kind === 'outlier-left' || kind === 'over-cleaned') return 'outlier'
  if (kind === 'leakage-enabled') return 'leakage'
  if (kind === 'category-raw') return 'raw category'
  if (kind === 'split-skewed') return 'split skew'
  if (kind === 'useful-feature-disabled') return 'feature off'
  return undefined
}

export function FeatureFactoryMission() {
  const definition = featureFactoryMission
  const runtime = useMissionRuntime(definition)
  const activeLevel = runtime.activeLevel
  return (
    <FeatureFactoryLevel
      key={activeLevel.id}
      activeLevel={activeLevel}
      completeActiveLevel={runtime.completeActiveLevel}
      setActiveLevelId={runtime.setActiveLevelId}
    />
  )
}

function FeatureFactoryLevel({
  activeLevel,
  completeActiveLevel,
  setActiveLevelId,
}: {
  activeLevel: MissionLevel
  completeActiveLevel: () => void
  setActiveLevelId: (levelId: string) => void
}) {
  const definition = featureFactoryMission
  const levelId = levelIdMap[activeLevel.id]
  const [state, setState] = useState<FeatureFactoryState>(() => initialFactoryState(levelId))
  const [selectedRowId, setSelectedRowId] = useState(state.rows[0]?.id ?? '')
  const diagnosis = diagnoseFactory(levelId, state)
  const levelSuccess = diagnosis.invariantOk
  const metrics = useMemo(() => factoryMetrics(state), [state])
  const quality = useMemo(() => splitQuality(state.rows), [state.rows])
  const diff = useMemo(() => pipelineDiff(state), [state])
  const columns = visibleColumns(state)
  const markerLabel = repairMarkerLabel(diagnosis.kind)
  const effectiveSelectedRowId = state.rows.some((row) => row.id === selectedRowId)
    ? selectedRowId
    : state.rows[0]?.id

  useEffect(() => {
    if (!levelSuccess) return
    completeActiveLevel()
  }, [completeActiveLevel, levelSuccess])

  const handleColumnAction = (actionId: string, columnId: string) => {
    if (actionId === 'impute-median') {
      setState((current) => imputeMedian(current, columnId))
    }
    if (actionId === 'fill-zero') {
      setState((current) => fillZero(current, columnId))
    }
    if (actionId === 'drop-missing') {
      setState((current) => dropMissingRows(current, columnId))
    }
  }

  const handleRowAction = (actionId: string, rowId: string) => {
    if (actionId === 'drop-row') {
      setState((current) => dropRow(current, rowId))
    }
  }

  const mascotState = chooseMascotState({
    success: levelSuccess,
    warning: !levelSuccess,
    hint: diagnosis.kind === 'leakage-enabled' || diagnosis.kind === 'category-raw',
  })
  const mascotMessage = missionMessage(mascotState, {
    success: activeLevel.successText,
    warning: activeLevel.mistakeFeedback?.[0] ?? diagnosis.message,
    hint: activeLevel.hint,
    thinking: 'Я смотрю на pipeline: один неверный шаг может сделать метрику красивой, но нечестной.',
    idle: 'Потрогай данные. Я подсвечу, какой шаг реально чинит набор.',
  })

  const badges: MissionBadge[] = [
    {
      id: 'stability',
      label: 'test stability',
      value: formatPercent(metrics.find((metric) => metric.id === 'stability')?.test ?? 0),
      tone: levelSuccess ? 'success' : 'warning',
    },
    {
      id: 'rows',
      label: 'rows',
      value: String(state.rows.length),
      tone: diagnosis.kind === 'over-cleaned' ? 'danger' : 'neutral',
    },
    {
      id: 'pipeline',
      label: 'steps',
      value: String(state.steps.length),
      tone: levelSuccess ? 'success' : 'target',
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
      sceneViewportClassName="min-h-[1180px] pt-[176px] sm:min-h-[1080px] sm:pt-[112px] lg:h-full lg:min-h-0 lg:pt-[74px]"
      scene={
        <div className="flex h-full items-start justify-center bg-[radial-gradient(circle_at_20%_18%,rgba(214,101,69,0.12),transparent_30%),linear-gradient(180deg,#fffdf7,#f3f0e9)] p-4 lg:items-center">
          <div
            className="grid w-full max-w-6xl gap-4 xl:grid-cols-[minmax(0,1.08fr)_minmax(0,0.92fr)]"
            data-testid="mission-feature-factory"
          >
            <section className="min-w-0 space-y-4 rounded-md border border-ink/10 bg-paper/92 p-4 shadow-[0_18px_42px_rgba(20,20,19,0.08)]">
              <div className="relative min-h-7">
                <ResultMoment show={levelSuccess} label="pipeline clean" />
                {!levelSuccess && markerLabel && (
                  <RepairMarker tone="warning" label={markerLabel} />
                )}
              </div>
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-wide text-orange">
                    feature factory
                  </p>
                  <h2 className="mt-1 text-xl font-semibold text-ink">{activeLevel.title}</h2>
                  <p className="mt-1 max-w-xl text-sm leading-relaxed text-ink/62">
                    {levelGoal[levelId]}
                  </p>
                </div>
                <div className="rounded-md border border-ink/10 bg-bg/75 px-3 py-2 text-xs text-ink/62">
                  <span className="font-semibold text-ink">goal:</span> {activeLevel.successConditionLabel}
                </div>
              </div>

              <DataTableMini
                rows={state.rows}
                columns={columns}
                selectedRowId={effectiveSelectedRowId}
                onRowSelect={setSelectedRowId}
                rowActions={levelId === 'outlier-repair' ? [{ id: 'drop-row', label: 'drop' }] : []}
                columnActions={
                  levelId === 'missing-values'
                    ? [
                        { id: 'impute-median', label: 'median', targetIds: ['temperature'] },
                        { id: 'fill-zero', label: 'zero', targetIds: ['temperature'] },
                        { id: 'drop-missing', label: 'drop NA', targetIds: ['temperature'] },
                      ]
                    : []
                }
                onRowAction={handleRowAction}
                onColumnAction={handleColumnAction}
                highlightMode={levelId === 'leakage-off' ? 'leakage' : 'errors'}
                maxRowsCollapsed={12}
              />

              {levelId === 'encode-category' && (
                <div className="grid gap-2 sm:grid-cols-2">
                  <button
                    type="button"
                    onClick={() => setState((current) => keepRawCategory(current, 'segment'))}
                    className="rounded-md border border-danger/25 bg-danger/10 px-3 py-2 text-left text-xs font-semibold text-danger transition hover:border-danger/45"
                    data-testid="feature-keep-raw-segment"
                  >
                    keep raw segment
                    <span className="mt-1 block font-normal text-ink/58">
                      Оставляет буквы как есть: pipeline выглядит быстрым, но не model-ready.
                    </span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setState((current) => encodeCategory(current, 'segment'))}
                    className="rounded-md border border-target/25 bg-target/10 px-3 py-2 text-left text-xs font-semibold text-target transition hover:border-target/45"
                    data-testid="feature-encode-main-segment"
                  >
                    encode segment
                    <span className="mt-1 block font-normal text-ink/58">
                      Превращает категорию в признак, который можно использовать.
                    </span>
                  </button>
                </div>
              )}

              {levelId === 'split-check' && (
                <div className="space-y-2" data-testid="split-seed-picker">
                  <p className="text-[10px] font-semibold uppercase tracking-wide text-ink/45">
                    split seeds
                  </p>
                  <div className="grid gap-2 sm:grid-cols-3">
                    {splitSeedOptions.map((option) => {
                      const selected = state.splitSeedId === option.id
                      return (
                        <button
                          key={option.id}
                          type="button"
                          onClick={() => setState((current) => chooseSplitSeed(current, option.id))}
                          className={`rounded-md border p-2 text-left text-xs transition ${
                            selected
                              ? 'border-orange/45 bg-orange/12 text-ink'
                              : 'border-ink/10 bg-bg/78 text-ink/62 hover:border-orange/30'
                          }`}
                          data-testid={`split-seed-${option.id}`}
                        >
                          <span className="block font-semibold">{option.label}</span>
                          <span className="mt-1 block leading-snug">{option.description}</span>
                        </button>
                      )
                    })}
                  </div>
                </div>
              )}

              <PipelineStrip steps={state.steps} />
              <PipelineDiff {...diff} />
            </section>

            <section className="min-w-0 space-y-4 rounded-md border border-ink/10 bg-panel/35 p-4 shadow-[0_18px_42px_rgba(20,20,19,0.06)]">
              <FeatureTogglePanel
                features={state.features}
                onToggle={(featureId) => setState((current) => toggleFeature(current, featureId))}
                onEncode={(featureId) => setState((current) => encodeCategory(current, featureId))}
              />
              <MetricBoard metrics={metrics} primaryMetricId="stability" diagnosis={diagnosis.kind} />
              <SplitInspector quality={quality} />
            </section>
          </div>
        </div>
      }
      controls={
        <div className="space-y-2">
          <div
            className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5 text-xs leading-relaxed text-ink/70"
            data-testid="feature-factory-diagnosis"
          >
            <p className="font-semibold text-ink">{diagnosis.message}</p>
            <p className="mt-1">{diagnosis.repairHint}</p>
          </div>
          <p className="text-xs leading-relaxed text-ink/60">
            Active features:{' '}
            <span className="font-semibold">
              {state.features
                .filter((feature) => feature.enabled)
                .map((feature) => factoryFeatureLabels[feature.id] ?? feature.id)
                .join(', ')}
            </span>
            .
          </p>
        </div>
      }
      feedback={
        <p>
          Pipeline: <span className="font-semibold">{state.steps.length}</span> steps.
          Диагноз: <span className="font-semibold">{diagnosis.kind}</span>.
        </p>
      }
    />
  )
}
