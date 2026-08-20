import { useEffect, useMemo, useState } from 'react'
import { DataTableMini } from '../../game/components/data/DataTableMini'
import { DecisionPlane } from '../../game/components/data/DecisionPlane'
import { MetricBoard } from '../../game/components/data/MetricBoard'
import { MissionShell } from '../../game/components/MissionShell'
import { RepairMarker } from '../../game/components/RepairMarker'
import { ResultMoment } from '../../game/components/ResultMoment'
import { chooseMascotState, missionMessage } from '../../game/missionFeedback'
import { mlPlaygroundMission } from '../../game/missions'
import type { MissionBadge, MissionLevel } from '../../game/missionTypes'
import { useMissionRuntime } from '../../game/useMissionRuntime'
import type { ThresholdModel } from '../../game/dataTypes'
import {
  applyModel,
  confusionCounts,
  diagnoseModel,
  formatPercent,
  mlColumns,
  mlFeatureLabels,
  mlLevelConfigs,
  rowsForLevel,
  splitRows,
  trainTestMetrics,
  type MlLevelId,
} from './mlPlaygroundModel'

const levelIdMap: Record<string, MlLevelId> = {
  'simple-threshold': 'simple-threshold',
  'test-control': 'test-control',
  'f1-threshold': 'f1-threshold',
  'leakage-trap': 'leakage-trap',
}

const primaryMetricByLevel: Record<MlLevelId, string> = {
  'simple-threshold': 'accuracy',
  'test-control': 'accuracy',
  'f1-threshold': 'f1',
  'leakage-trap': 'accuracy',
}

function metricValue(metrics: ReturnType<typeof trainTestMetrics>, metricId: string, split: 'train' | 'test') {
  return metrics.find((metric) => metric.id === metricId)?.[split] ?? 0
}

export function MlPlaygroundMission() {
  const definition = mlPlaygroundMission
  const runtime = useMissionRuntime(definition)
  const activeLevel = runtime.activeLevel
  return (
    <MlPlaygroundLevel
      key={activeLevel.id}
      activeLevel={activeLevel}
      completeActiveLevel={runtime.completeActiveLevel}
      setActiveLevelId={runtime.setActiveLevelId}
    />
  )
}

function MlPlaygroundLevel({
  activeLevel,
  completeActiveLevel,
  setActiveLevelId,
}: {
  activeLevel: MissionLevel
  completeActiveLevel: () => void
  setActiveLevelId: (levelId: string) => void
}) {
  const definition = mlPlaygroundMission
  const levelId = levelIdMap[activeLevel.id]
  const config = mlLevelConfigs[levelId]
  const [model, setModel] = useState<ThresholdModel>(config.model)
  const rawRows = rowsForLevel(levelId)
  const predictedRows = useMemo(() => applyModel(rawRows, model), [model, rawRows])
  const [selectedRowId, setSelectedRowId] = useState<string>(
    predictedRows.find((row) => row.flags?.includes('misclassified'))?.id ?? predictedRows[0]?.id ?? '',
  )
  const effectiveSelectedRowId = predictedRows.some((row) => row.id === selectedRowId)
    ? selectedRowId
    : predictedRows[0]?.id
  const diagnosis = diagnoseModel(levelId, rawRows, model)
  const levelSuccess = diagnosis.invariantOk
  const metrics = trainTestMetrics(predictedRows)
  const primaryMetricId = primaryMetricByLevel[levelId]
  const trainRows = splitRows(predictedRows, 'train')
  const testRows = splitRows(predictedRows, 'test')
  const visibleColumns =
    levelId === 'leakage-trap'
      ? mlColumns
      : mlColumns.filter((column) => column.id !== 'leakage_score')

  const repairLabelByKind: Record<string, string> = {
    'bad-threshold': 'порог не тот',
    'train-test-gap': 'train ≫ test',
    'accuracy-trap': 'accuracy обманула',
    'leakage-used': 'утечка в модели',
    underfit: 'недообучение',
    'wrong-feature': 'не тот признак',
  }
  const repairLabel = repairLabelByKind[diagnosis.kind] ?? 'почини модель'
  const repairTone = diagnosis.kind === 'leakage-used' ? 'danger' : 'warning'

  useEffect(() => {
    if (!levelSuccess) return
    completeActiveLevel()
  }, [completeActiveLevel, levelSuccess])

  const mascotState = chooseMascotState({
    success: levelSuccess,
    warning: !levelSuccess,
    hint: diagnosis.kind === 'train-test-gap' || diagnosis.kind === 'accuracy-trap',
  })
  const mascotMessage = missionMessage(mascotState, {
    success: activeLevel.successText,
    warning: activeLevel.mistakeFeedback?.[0] ?? diagnosis.message,
    hint: activeLevel.hint,
    thinking: 'Смотри на две колонки: train показывает подгонку, test проверяет обобщение.',
    idle: 'Двигай границу. Я подсвечу ошибки на train и test.',
  })

  const badges: MissionBadge[] = [
    {
      id: 'train',
      label: `train ${primaryMetricId}`,
      value: formatPercent(metricValue(metrics, primaryMetricId, 'train')),
      tone: levelSuccess ? 'success' : 'target',
    },
    {
      id: 'test',
      label: `test ${primaryMetricId}`,
      value: formatPercent(metricValue(metrics, primaryMetricId, 'test')),
      tone: levelSuccess ? 'success' : 'warning',
    },
    {
      id: 'feature',
      label: 'feature',
      value: mlFeatureLabels[model.featureId] ?? model.featureId,
      tone: model.featureId === 'leakage_score' ? 'danger' : 'neutral',
    },
  ]

  const setFeature = (featureId: string) => {
    const fallbackThreshold = featureId === 'leakage_score' ? 0.5 : 58
    setModel((current) => ({
      ...current,
      featureId,
      threshold: current.featureId === featureId ? current.threshold : fallbackThreshold,
    }))
  }

  return (
    <MissionShell
      definition={definition}
      activeLevelId={activeLevel.id}
      onLevelSelect={setActiveLevelId}
      mascotState={mascotState}
      mascotMessage={mascotMessage}
      badges={badges}
      sceneViewportClassName="min-h-[1120px] pt-[176px] sm:min-h-[1040px] sm:pt-[112px] lg:h-full lg:min-h-0 lg:pt-[74px]"
      scene={
        <div className="flex h-full items-start justify-center bg-[radial-gradient(circle_at_70%_14%,rgba(89,143,113,0.14),transparent_30%),linear-gradient(180deg,#fffdf7,#f7f4ed)] p-4 lg:items-center">
          <div className="relative grid w-full max-w-6xl gap-4 xl:grid-cols-[minmax(0,1.05fr)_minmax(0,0.95fr)]">
            <ResultMoment show={levelSuccess} label="модель обобщает" />
            {!levelSuccess && (
              <RepairMarker tone={repairTone} label={repairLabel} xPercent={50} yPercent={1} />
            )}
            <section className="min-w-0 space-y-4 rounded-md border border-ink/10 bg-paper/90 p-4 shadow-[0_18px_42px_rgba(20,20,19,0.08)]">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-wide text-orange">
                    model arena
                  </p>
                  <h2 className="mt-1 text-xl font-semibold text-ink">{config.title}</h2>
                  <p className="mt-1 max-w-xl text-sm leading-relaxed text-ink/62">
                    {config.goal}
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  {config.allowedFeatures.map((featureId) => (
                    <button
                      key={featureId}
                      type="button"
                      onClick={() => setFeature(featureId)}
                      className={`rounded-md border px-2.5 py-1.5 text-xs font-semibold transition ${
                        model.featureId === featureId
                          ? 'border-orange/45 bg-orange/12 text-ink'
                          : 'border-ink/10 bg-bg/80 text-ink/62 hover:border-orange/30'
                      }`}
                      data-testid={`ml-feature-${featureId}`}
                    >
                      {mlFeatureLabels[featureId] ?? featureId}
                    </button>
                  ))}
                </div>
              </div>

              <DecisionPlane
                rows={predictedRows}
                model={model}
                selectedRowId={effectiveSelectedRowId}
                onModelChange={setModel}
                onRowSelect={setSelectedRowId}
              />
            </section>

            <section className="min-w-0 space-y-4 rounded-md border border-ink/10 bg-panel/35 p-4 shadow-[0_18px_42px_rgba(20,20,19,0.06)]">
              <MetricBoard
                metrics={metrics}
                primaryMetricId={primaryMetricId}
                diagnosis={diagnosis.kind}
                confusionTrain={confusionCounts(trainRows)}
                confusionTest={confusionCounts(testRows)}
              />
              <DataTableMini
                rows={predictedRows}
                columns={visibleColumns}
                selectedRowId={effectiveSelectedRowId}
                onRowSelect={setSelectedRowId}
                highlightMode={levelId === 'leakage-trap' ? 'leakage' : 'errors'}
                maxRowsCollapsed={16}
              />
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
            Prediction rule: y=1, если {mlFeatureLabels[model.featureId] ?? model.featureId}{' '}
            {model.direction === 'gte' ? '>=' : '<'} {model.threshold}.
          </p>
        </div>
      }
      feedback={
        <p>
          Feature: <span className="font-semibold">{mlFeatureLabels[model.featureId] ?? model.featureId}</span>.
          Threshold: <span className="font-semibold">{model.threshold}</span>. Диагноз:{' '}
          <span className="font-semibold">{diagnosis.kind}</span>.
        </p>
      }
    />
  )
}
