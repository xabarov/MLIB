import { useEffect, useMemo, useState } from 'react'
import { Check, Crosshair, RotateCcw, ScanSearch } from 'lucide-react'
import { MissionShell } from '../../game/components/MissionShell'
import { RepairMarker } from '../../game/components/RepairMarker'
import { ResultMoment } from '../../game/components/ResultMoment'
import { chooseMascotState, missionMessage } from '../../game/missionFeedback'
import { pcaCompressionMission } from '../../game/missions'
import type { MissionBadge } from '../../game/missionTypes'
import { useMissionRuntime } from '../../game/useMissionRuntime'
import {
  centerColumns,
  compressionResult,
  detailMatrix,
  diagnoseCentering,
  diagnoseCompressionBudget,
  formatCompressionNumber,
  glyphMatrix,
  maxAbsCell,
  normalizeMatrixForHeatmap,
  reconstructionErrorForCenteredRank,
  shiftedCloudMatrix,
  shape,
  svdSmallMatrix,
  worstResidualCell,
  type CompressionDiagnosis,
  type MatrixData,
  type ResidualHotspot,
} from './pcaCompressionModel'

type LevelPreset = {
  dataset: MatrixData
  selectedIndexes: number[]
  centered: boolean
  featureDimensions: 1 | 2
  budget: number
}

const presets: Record<string, LevelPreset> = {
  'rank-budget': {
    dataset: glyphMatrix,
    selectedIndexes: [0, 1],
    centered: false,
    featureDimensions: 2,
    budget: 26,
  },
  'component-detective': {
    dataset: detailMatrix,
    selectedIndexes: [0],
    centered: false,
    featureDimensions: 2,
    budget: 26,
  },
  'center-before-pca': {
    dataset: shiftedCloudMatrix,
    selectedIndexes: [0],
    centered: false,
    featureDimensions: 2,
    budget: 22,
  },
  'quality-gate': {
    dataset: detailMatrix,
    selectedIndexes: [0],
    centered: false,
    featureDimensions: 2,
    budget: 39,
  },
  'transfer-to-features': {
    dataset: shiftedCloudMatrix,
    selectedIndexes: [0, 1],
    centered: true,
    featureDimensions: 1,
    budget: 22,
  },
}

const qualityByLevel = {
  'rank-budget': { maxStorage: 26, minRetainedEnergy: 0.87, maxCellError: 0.55 },
  'component-detective': { maxStorage: 26, minRetainedEnergy: 0.8, maxCellError: 0.6 },
  'quality-gate': { maxStorage: 39, minRetainedEnergy: 0.85, maxCellError: 0.3 },
}

function cellTone(value: number, max: number, residual = false): string {
  const magnitude = max > 0 ? Math.min(1, Math.abs(value) / max) : 0
  if (residual) {
    if (value > 0.02) return `rgba(199, 88, 63, ${0.18 + magnitude * 0.72})`
    if (value < -0.02) return `rgba(67, 119, 168, ${0.18 + magnitude * 0.72})`
    return 'rgba(245, 242, 232, 0.85)'
  }
  return `rgba(48, 90, 96, ${0.12 + magnitude * 0.74})`
}

function Heatmap({
  title,
  matrix,
  testId,
  residual = false,
  hotspot = null,
}: {
  title: string
  matrix: MatrixData
  testId: string
  residual?: boolean
  hotspot?: ResidualHotspot | null
}) {
  const [rows, cols] = shape(matrix)
  const max = maxAbsCell(matrix)
  return (
    <div className="min-w-0">
      <div className="mb-1 flex items-center justify-between gap-2">
        <p className="text-[10px] font-black uppercase tracking-wide text-ink/55">{title}</p>
        <p className="text-[10px] tabular-nums text-ink/45">
          {rows}x{cols}
        </p>
      </div>
      <div className="relative">
        <div
          className="grid aspect-square w-full overflow-hidden rounded-md border border-ink/15 bg-paper shadow-[inset_0_0_0_1px_rgba(255,255,255,0.45)]"
          style={{ gridTemplateColumns: `repeat(${Math.max(cols, 1)}, minmax(0, 1fr))` }}
          data-testid={testId}
        >
          {matrix.flatMap((row, rowIndex) =>
            row.map((value, colIndex) => {
              const isHotspot =
                hotspot != null && hotspot.row === rowIndex && hotspot.col === colIndex
              return (
                <div
                  key={`${rowIndex}-${colIndex}`}
                  className={`border-r border-b border-bg/70 ${
                    isHotspot ? 'outline outline-2 -outline-offset-2 outline-danger' : ''
                  }`}
                  style={{ backgroundColor: cellTone(value, max, residual) }}
                  title={`${formatCompressionNumber(value)}`}
                />
              )
            }),
          )}
        </div>
        {hotspot != null && (
          <span
            className="pointer-events-none absolute z-20 -translate-x-1/2 -translate-y-1/2 rounded-full border border-danger/55 bg-danger/15 px-1.5 py-0.5 text-[9px] font-black uppercase tracking-wide text-danger shadow-sm"
            style={{
              left: `${((hotspot.col + 0.5) / Math.max(cols, 1)) * 100}%`,
              top: `${((hotspot.row + 0.5) / Math.max(rows, 1)) * 100}%`,
            }}
            data-testid="pca-residual-hotspot"
          >
            {formatCompressionNumber(hotspot.value)}
          </span>
        )}
      </div>
    </div>
  )
}

function ComponentToggle({
  active,
  index,
  sigma,
  preview,
  onToggle,
  recommended = false,
}: {
  active: boolean
  index: number
  sigma: number
  preview: MatrixData
  onToggle: () => void
  recommended?: boolean
}) {
  const normalized = normalizeMatrixForHeatmap(preview)
  return (
    <button
      type="button"
      className={`relative min-w-[118px] rounded-md border p-2 text-left transition ${
        active
          ? 'border-target bg-target/12 shadow-[0_8px_22px_rgba(48,90,96,0.14)]'
          : recommended
            ? 'border-orange/50 bg-orange/8 hover:border-orange'
            : 'border-ink/10 bg-paper/82 hover:border-target/50'
      }`}
      onClick={onToggle}
      data-testid={`pca-component-toggle-${index}`}
    >
      {recommended && (
        <span
          className="absolute -right-1 -top-1 rounded-full border border-orange/55 bg-orange/15 px-1 text-[8px] font-black uppercase text-orange"
          data-testid={`pca-component-next-${index}`}
        >
          next
        </span>
      )}
      <div className="mb-1 flex items-center justify-between gap-2">
        <span className="text-[10px] font-black uppercase tracking-wide text-ink/55">c{index + 1}</span>
        <span className="text-[10px] tabular-nums text-ink/55">s={formatCompressionNumber(sigma)}</span>
      </div>
      <div
        className="grid aspect-square overflow-hidden rounded border border-ink/10"
        style={{ gridTemplateColumns: `repeat(${shape(normalized)[1]}, minmax(0, 1fr))` }}
      >
        {normalized.flatMap((row, rowIndex) =>
          row.map((value, colIndex) => (
            <span
              key={`${rowIndex}-${colIndex}`}
              className="border-r border-b border-bg/70"
              style={{ backgroundColor: cellTone(value, 1, true) }}
            />
          )),
        )}
      </div>
    </button>
  )
}

function ChoiceButton({
  active,
  label,
  testId,
  onClick,
}: {
  active: boolean
  label: string
  testId: string
  onClick: () => void
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded border px-2.5 py-1.5 text-xs font-semibold transition ${
        active
          ? 'border-target bg-target text-bg'
          : 'border-ink/10 bg-paper text-ink hover:border-target/50'
      }`}
      data-testid={testId}
    >
      {label}
    </button>
  )
}

function componentMatrix(component: ReturnType<typeof svdSmallMatrix>[number], rows: number, cols: number): MatrixData {
  return Array.from({ length: rows }, (_, row) =>
    Array.from({ length: cols }, (_, col) => component.sigma * component.left[row] * component.right[col]),
  )
}

function separationScore(featureDimensions: 1 | 2, centered: boolean): number {
  if (!centered) return 0.38
  return featureDimensions === 2 ? 0.82 : 0.52
}

export function PcaCompressionMission() {
  const definition = pcaCompressionMission
  const runtime = useMissionRuntime(definition)
  const activeLevel = runtime.activeLevel
  const { completeActiveLevel, setActiveLevelId } = runtime
  const [dataset, setDataset] = useState<MatrixData>(presets[activeLevel.id].dataset)
  const [selectedIndexes, setSelectedIndexes] = useState<number[]>(presets[activeLevel.id].selectedIndexes)
  const [centered, setCentered] = useState(presets[activeLevel.id].centered)
  const [featureDimensions, setFeatureDimensions] = useState<1 | 2>(presets[activeLevel.id].featureDimensions)
  const [budget, setBudget] = useState(presets[activeLevel.id].budget)
  const [touched, setTouched] = useState(false)

  const resetToPreset = (levelId = activeLevel.id) => {
    const preset = presets[levelId]
    setDataset(preset.dataset)
    setSelectedIndexes(preset.selectedIndexes)
    setCentered(preset.centered)
    setFeatureDimensions(preset.featureDimensions)
    setBudget(preset.budget)
    setTouched(false)
  }

  const selectLevel = (levelId: string) => {
    resetToPreset(levelId)
    setActiveLevelId(levelId)
  }

  const workingMatrix = useMemo(() => (centered ? centerColumns(dataset).centered : dataset), [centered, dataset])
  const components = useMemo(() => svdSmallMatrix(workingMatrix), [workingMatrix])
  const [rows, cols] = shape(workingMatrix)
  const result = useMemo(() => compressionResult(workingMatrix, selectedIndexes), [selectedIndexes, workingMatrix])
  const displayReconstruction = centered
    ? centerColumns(dataset).means.length > 0
      ? reconstructionErrorForCenteredRank(dataset, selectedIndexes.length, true).reconstruction
      : result.reconstruction
    : result.reconstruction
  const displayResidual = centered
    ? reconstructionErrorForCenteredRank(dataset, selectedIndexes.length, true).residual
    : result.residual
  const residualHotspot = worstResidualCell(displayResidual)
  const showResidualHotspot = Math.abs(residualHotspot.value) > 0.12
  const nextComponentIndex =
    components.find((component) => !selectedIndexes.includes(component.index))?.index ?? null
  const rankBudgetDiagnosis = diagnoseCompressionBudget(result, qualityByLevel['rank-budget'])
  const componentDiagnosis = diagnoseCompressionBudget(result, qualityByLevel['component-detective'])
  const qualityDiagnosis = diagnoseCompressionBudget(result, qualityByLevel['quality-gate'])
  const centeringDiagnosis = diagnoseCentering(dataset, centered)
  const separation = separationScore(featureDimensions, centered)

  const levelSuccess = useMemo(() => {
    if (activeLevel.id === 'rank-budget') return rankBudgetDiagnosis.kind === 'ready'
    if (activeLevel.id === 'component-detective') {
      return selectedIndexes.includes(1) && componentDiagnosis.kind === 'ready'
    }
    if (activeLevel.id === 'center-before-pca') {
      const raw = reconstructionErrorForCenteredRank(dataset, 1, false)
      const centeredResult = reconstructionErrorForCenteredRank(dataset, 1, true)
      return centered && centeredResult.frobeniusError < raw.frobeniusError
    }
    if (activeLevel.id === 'quality-gate') return selectedIndexes.length === 3 && qualityDiagnosis.kind === 'ready'
    if (activeLevel.id === 'transfer-to-features') return centered && featureDimensions === 2 && separation > 0.75
    return false
  }, [
    activeLevel.id,
    centered,
    componentDiagnosis.kind,
    dataset,
    featureDimensions,
    qualityDiagnosis.kind,
    rankBudgetDiagnosis.kind,
    selectedIndexes,
    separation,
  ])

  useEffect(() => {
    if (levelSuccess) completeActiveLevel()
  }, [completeActiveLevel, levelSuccess])

  const activeDiagnosis: CompressionDiagnosis =
    activeLevel.id === 'rank-budget'
      ? rankBudgetDiagnosis
      : activeLevel.id === 'component-detective'
        ? componentDiagnosis.kind === 'ready' && !selectedIndexes.includes(1)
          ? {
              kind: 'component-mismatch',
              message: 'Quality is close, but target detail component is not selected.',
              repairHint: 'Включи c2: она гасит локальную ошибку в residual map.',
            }
          : componentDiagnosis
        : activeLevel.id === 'center-before-pca'
          ? centeringDiagnosis
          : activeLevel.id === 'quality-gate'
            ? qualityDiagnosis
            : separation > 0.75
              ? { kind: 'ready', message: 'Feature separation is preserved.', repairHint: 'Можно переносить признаки в ML.' }
              : {
                  kind: 'underfit',
                  message: 'Compressed features mix the two pattern families.',
                  repairHint: 'Включи centering and keep 2D PCA coordinates.',
                }

  const repairLabelByKind: Record<string, string> = {
    'over-budget': 'over budget',
    underfit: 'мало компонент',
    'local-artifact': 'локальный артефакт',
    'mean-not-centered': 'не центрировано',
    'component-mismatch': 'не та компонента',
  }
  const repairLabel = repairLabelByKind[activeDiagnosis.kind] ?? 'почини сжатие'
  const showRepairMarker = touched && !levelSuccess && activeDiagnosis.kind !== 'ready'

  const mascotState = chooseMascotState({
    success: levelSuccess,
    warning: touched && activeDiagnosis.kind !== 'ready',
    hint: result.retainedEnergy > 0.82 || centered,
    thinking: activeLevel.id === 'component-detective' || activeLevel.id === 'quality-gate',
  })
  const mascotMessage = missionMessage(mascotState, {
    success: activeLevel.successText,
    warning: activeLevel.mistakeFeedback?.[0] ?? activeDiagnosis.message,
    hint: activeLevel.hint,
    thinking: 'Я стою на residual map: если одна клетка яркая, общая energy нас не спасла.',
    idle: 'Собери low-rank copy: я буду следить за storage, energy and worst-cell artifact.',
  })

  const badges: MissionBadge[] = [
    {
      id: 'rank',
      label: 'rank',
      value: selectedIndexes.length,
      tone: levelSuccess ? 'success' : 'neutral',
    },
    {
      id: 'storage',
      label: 'storage',
      value: `${result.storageCost}/${budget}`,
      tone: result.storageCost <= budget ? 'success' : 'danger',
    },
    {
      id: 'energy',
      label: 'energy',
      value: `${Math.round(result.retainedEnergy * 100)}%`,
      tone: result.retainedEnergy > 0.9 ? 'success' : 'energy',
    },
    {
      id: 'max-cell',
      label: 'max cell',
      value: formatCompressionNumber(result.maxCellError),
      tone: result.maxCellError < 0.2 ? 'success' : 'warning',
    },
  ]

  const setRank = (rank: number) => {
    setTouched(true)
    setSelectedIndexes(components.slice(0, rank).map((component) => component.index))
  }

  const toggleComponent = (index: number) => {
    setTouched(true)
    setSelectedIndexes((current) =>
      current.includes(index) ? current.filter((item) => item !== index) : [...current, index].sort((a, b) => a - b),
    )
  }

  const fitBudget = () => {
    setTouched(true)
    setSelectedIndexes([0, 1])
    setBudget(26)
  }

  const fixArtifact = () => {
    setTouched(true)
    setSelectedIndexes([0, 1, 2])
    setBudget(39)
  }

  const centerData = () => {
    setTouched(true)
    setCentered(true)
  }

  const useFeature2D = () => {
    setTouched(true)
    setCentered(true)
    setFeatureDimensions(2)
  }

  const showPcaPanel = activeLevel.id === 'center-before-pca' || activeLevel.id === 'transfer-to-features'

  return (
    <MissionShell
      definition={definition}
      activeLevelId={activeLevel.id}
      onLevelSelect={selectLevel}
      mascotState={mascotState}
      mascotMessage={mascotMessage}
      badges={badges}
      sceneViewportClassName="min-h-[660px] pt-[116px] sm:pt-[84px] lg:h-full"
      scene={
        <div
          className="relative grid min-h-full content-start gap-3 bg-[linear-gradient(135deg,#fffdf7_0%,#f3efe2_48%,#eef4ee_100%)] p-3"
          data-testid="pca-compression-canvas"
        >
          <ResultMoment show={levelSuccess} label="low-rank копия принята" />
          {showRepairMarker && (
            <RepairMarker
              tone={activeDiagnosis.kind === 'over-budget' ? 'danger' : 'warning'}
              label={repairLabel}
              xPercent={50}
              yPercent={1}
            />
          )}
          <div className="grid min-h-0 gap-3 lg:grid-cols-[1fr_0.95fr_1fr]">
            <Heatmap title={centered ? 'centered data' : 'original'} matrix={workingMatrix} testId="pca-original-grid" />
            <Heatmap title="reconstruction" matrix={displayReconstruction} testId="pca-reconstruction-grid" />
            <Heatmap
              title="residual error"
              matrix={displayResidual}
              testId="pca-error-grid"
              residual
              hotspot={showResidualHotspot ? residualHotspot : null}
            />
          </div>

          <div className="grid gap-3 rounded-md border border-ink/10 bg-bg/80 p-3 shadow-[0_14px_28px_rgba(20,20,19,0.10)] lg:grid-cols-[1.4fr_0.8fr]">
            <div className="min-w-0">
              <div className="mb-2 flex items-center justify-between gap-2">
                <p className="text-[10px] font-black uppercase tracking-wide text-target">singular component rail</p>
                <p className="text-[10px] text-ink/50">selected: {selectedIndexes.map((item) => `c${item + 1}`).join(', ') || 'none'}</p>
              </div>
              <div className="flex gap-2 overflow-x-auto pb-1">
                {components.slice(0, Math.min(cols, 5)).map((component) => (
                  <ComponentToggle
                    key={component.index}
                    active={selectedIndexes.includes(component.index)}
                    index={component.index}
                    sigma={component.sigma}
                    preview={componentMatrix(component, rows, cols)}
                    onToggle={() => toggleComponent(component.index)}
                    recommended={!levelSuccess && component.index === nextComponentIndex}
                  />
                ))}
              </div>
            </div>

            <div className="grid content-start gap-2 text-xs">
              <div className="grid grid-cols-2 gap-2">
                <div className="rounded border border-ink/10 bg-paper px-2 py-1.5" data-testid="pca-storage-badge">
                  <p className="text-[10px] uppercase tracking-wide text-ink/45">storage</p>
                  <p className="font-black text-ink">{result.storageCost}/{budget}</p>
                </div>
                <div className="rounded border border-ink/10 bg-paper px-2 py-1.5" data-testid="pca-retained-energy-badge">
                  <p className="text-[10px] uppercase tracking-wide text-ink/45">energy</p>
                  <p className="font-black text-ink">{Math.round(result.retainedEnergy * 100)}%</p>
                </div>
                <div className="rounded border border-ink/10 bg-paper px-2 py-1.5" data-testid="pca-error-badge">
                  <p className="text-[10px] uppercase tracking-wide text-ink/45">F error</p>
                  <p className="font-black text-ink">{formatCompressionNumber(result.frobeniusError)}</p>
                </div>
                <div className="rounded border border-ink/10 bg-paper px-2 py-1.5">
                  <p className="text-[10px] uppercase tracking-wide text-ink/45">ratio</p>
                  <p className="font-black text-ink">{formatCompressionNumber(result.compressionRatio)}</p>
                </div>
              </div>
              {showPcaPanel && (
                <div className="rounded border border-target/20 bg-target/8 p-2">
                  <p className="text-[10px] font-black uppercase tracking-wide text-target">PCA feature inspector</p>
                  <p className="mt-1 text-ink/70">
                    centered: {centered ? 'yes' : 'no'}, dims: {featureDimensions}, separation:{' '}
                    {Math.round(separation * 100)}%
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      }
      controls={
        <div className="grid gap-3">
          <div>
            <p className="mb-1 text-[10px] font-black uppercase tracking-wide text-ink/45">rank preset</p>
            <div className="flex flex-wrap gap-2">
              {[0, 1, 2, 3].map((rank) => (
                <ChoiceButton
                  key={rank}
                  active={selectedIndexes.length === rank}
                  label={`${rank}`}
                  testId={`pca-rank-choice-${rank}`}
                  onClick={() => setRank(rank)}
                />
              ))}
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => resetToPreset()}
              className="inline-flex items-center gap-1 rounded border border-ink/10 bg-paper px-2 py-1.5 text-xs font-semibold text-ink hover:border-target/50"
            >
              <RotateCcw size={14} /> reset
            </button>
            <button
              type="button"
              onClick={fitBudget}
              className="inline-flex items-center gap-1 rounded border border-ink/10 bg-paper px-2 py-1.5 text-xs font-semibold text-ink hover:border-target/50"
              data-testid="pca-fit-budget"
            >
              <Check size={14} /> fit budget
            </button>
            <button
              type="button"
              onClick={fixArtifact}
              className="inline-flex items-center gap-1 rounded border border-ink/10 bg-paper px-2 py-1.5 text-xs font-semibold text-ink hover:border-target/50"
              data-testid="pca-fix-artifact"
            >
              <Crosshair size={14} /> fix artifact
            </button>
          </div>

          <div className="grid gap-2 rounded border border-ink/10 bg-bg/60 p-2">
            <label className="flex items-center justify-between gap-2 text-xs font-semibold text-ink">
              center data
              <input
                type="checkbox"
                checked={centered}
                onChange={(event) => {
                  setTouched(true)
                  setCentered(event.target.checked)
                }}
                data-testid="pca-center-toggle"
              />
            </label>
            <div className="flex flex-wrap gap-2">
              <ChoiceButton
                active={featureDimensions === 1}
                label="1D features"
                testId="pca-feature-choice-1"
                onClick={() => {
                  setTouched(true)
                  setFeatureDimensions(1)
                }}
              />
              <ChoiceButton
                active={featureDimensions === 2}
                label="2D features"
                testId="pca-feature-choice-2"
                onClick={useFeature2D}
              />
              <button
                type="button"
                onClick={centerData}
                className="inline-flex items-center gap-1 rounded border border-ink/10 bg-paper px-2 py-1.5 text-xs font-semibold text-ink hover:border-target/50"
              >
                <ScanSearch size={14} /> center snap
              </button>
            </div>
          </div>
        </div>
      }
      feedback={
        <div className="space-y-1" data-testid="pca-diagnosis">
          <p className="font-semibold text-ink">{activeDiagnosis.message}</p>
          <p>{activeDiagnosis.repairHint}</p>
        </div>
      }
    />
  )
}
