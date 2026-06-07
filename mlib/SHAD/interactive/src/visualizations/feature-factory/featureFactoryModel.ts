import type {
  DataActionKind,
  DataPipelineStep,
  DatasetColumn,
  DatasetRow,
  FeatureState,
  ModelMetric,
  SplitQuality,
} from '../../game/dataTypes'

export type FeatureFactoryLevelId =
  | 'missing-values'
  | 'outlier-repair'
  | 'leakage-off'
  | 'encode-category'

export type FeatureFactoryDiagnosisKind =
  | 'missing-left'
  | 'outlier-left'
  | 'leakage-enabled'
  | 'category-raw'
  | 'over-cleaned'
  | 'ready'

export type FeatureFactoryDiagnosis = {
  kind: FeatureFactoryDiagnosisKind
  message: string
  repairHint: string
  invariantOk: boolean
}

export type FeatureFactoryState = {
  rows: DatasetRow[]
  features: FeatureState[]
  steps: DataPipelineStep[]
}

export const factoryColumns: DatasetColumn[] = [
  { id: 'signal', label: 'signal', kind: 'number' },
  { id: 'temperature', label: 'temp', kind: 'number' },
  { id: 'segment', label: 'segment', kind: 'category' },
  { id: 'leakage_code', label: 'leak', kind: 'number' },
]

export const factoryBaseRows: DatasetRow[] = [
  { id: 'ff-01', split: 'train', label: 0, values: { signal: 18, temperature: 42, segment: 'A', leakage_code: 0.04 } },
  { id: 'ff-02', split: 'train', label: 0, values: { signal: 24, temperature: null, segment: 'A', leakage_code: 0.08 }, flags: ['missing'] },
  { id: 'ff-03', split: 'train', label: 0, values: { signal: 31, temperature: 39, segment: 'B', leakage_code: 0.1 } },
  { id: 'ff-04', split: 'train', label: 1, values: { signal: 55, temperature: 55, segment: 'B', leakage_code: 0.91 } },
  { id: 'ff-05', split: 'train', label: 1, values: { signal: 63, temperature: 59, segment: 'C', leakage_code: 0.95 } },
  { id: 'ff-06', split: 'train', label: 1, values: { signal: 70, temperature: 62, segment: 'C', leakage_code: 0.98 } },
  { id: 'ff-07', split: 'train', label: 0, values: { signal: 94, temperature: 96, segment: 'C', leakage_code: 0.12 }, flags: ['outlier'] },
  { id: 'ff-08', split: 'test', label: 0, values: { signal: 35, temperature: 41, segment: 'A', leakage_code: 0.61 } },
  { id: 'ff-09', split: 'test', label: 0, values: { signal: 43, temperature: null, segment: 'B', leakage_code: 0.59 }, flags: ['missing'] },
  { id: 'ff-10', split: 'test', label: 1, values: { signal: 59, temperature: 57, segment: 'B', leakage_code: 0.48 } },
  { id: 'ff-11', split: 'test', label: 1, values: { signal: 67, temperature: 64, segment: 'C', leakage_code: 0.44 } },
  { id: 'ff-12', split: 'test', label: 1, values: { signal: 74, temperature: 68, segment: 'C', leakage_code: 0.41 } },
]

const featureLabels: Record<string, string> = {
  signal: 'signal',
  temperature: 'temperature',
  segment: 'segment',
  leakage_code: 'leakage code',
}

export const factoryFeatureLabels = featureLabels

export function initialFactoryFeatures(levelId: FeatureFactoryLevelId): FeatureState[] {
  const leakageEnabled = levelId === 'leakage-off'
  const segmentEncoded = levelId !== 'encode-category'
  return [
    { id: 'signal', label: featureLabels.signal, kind: 'number', enabled: true },
    { id: 'temperature', label: featureLabels.temperature, kind: 'number', enabled: true },
    {
      id: 'segment',
      label: featureLabels.segment,
      kind: 'category',
      enabled: true,
      encoded: segmentEncoded,
    },
    {
      id: 'leakage_code',
      label: featureLabels.leakage_code,
      kind: 'number',
      enabled: leakageEnabled,
      flaggedAsLeakage: true,
    },
  ]
}

export function initialFactoryState(levelId: FeatureFactoryLevelId): FeatureFactoryState {
  return {
    rows: factoryBaseRows,
    features: initialFactoryFeatures(levelId),
    steps: [],
  }
}

function pipelineStep(kind: DataActionKind, targetId: string, valid: boolean): DataPipelineStep {
  const labels: Record<DataActionKind, string> = {
    'mark-missing': 'mark missing',
    'impute-median': 'median impute',
    'drop-row': 'drop row',
    'mark-outlier': 'mark outlier',
    'disable-feature': 'disable feature',
    'encode-category': 'encode category',
    'choose-split': 'choose split',
  }
  return {
    id: `${kind}:${targetId}:${valid ? 'ok' : 'bad'}`,
    kind,
    label: `${labels[kind]} ${targetId}`,
    targetId,
    valid,
  }
}

function appendStep(
  steps: DataPipelineStep[],
  kind: DataActionKind,
  targetId: string,
  valid: boolean,
) {
  const next = pipelineStep(kind, targetId, valid)
  return [...steps.filter((step) => !(step.kind === kind && step.targetId === targetId)), next]
}

export function medianOfColumn(rows: DatasetRow[], columnId: string): number {
  const values = rows
    .map((row) => row.values[columnId])
    .filter((value): value is number => typeof value === 'number' && Number.isFinite(value))
    .sort((a, b) => a - b)
  if (values.length === 0) return 0
  const middle = Math.floor(values.length / 2)
  return values.length % 2 === 0 ? (values[middle - 1] + values[middle]) / 2 : values[middle]
}

export function imputeMedian(state: FeatureFactoryState, columnId: string): FeatureFactoryState {
  const median = medianOfColumn(state.rows, columnId)
  const rows = state.rows.map((row) => {
    if (row.values[columnId] !== null) return row
    return {
      ...row,
      values: { ...row.values, [columnId]: median },
      flags: row.flags?.filter((flag) => flag !== 'missing'),
    }
  })
  return {
    ...state,
    rows,
    steps: appendStep(state.steps, 'impute-median', columnId, columnId === 'temperature'),
  }
}

export function dropRow(state: FeatureFactoryState, rowId: string): FeatureFactoryState {
  const row = state.rows.find((item) => item.id === rowId)
  return {
    ...state,
    rows: state.rows.filter((item) => item.id !== rowId),
    steps: appendStep(state.steps, 'drop-row', rowId, row?.flags?.includes('outlier') ?? false),
  }
}

export function toggleFeature(state: FeatureFactoryState, featureId: string): FeatureFactoryState {
  const feature = state.features.find((item) => item.id === featureId)
  const nextEnabled = !feature?.enabled
  return {
    ...state,
    features: state.features.map((item) =>
      item.id === featureId ? { ...item, enabled: nextEnabled } : item,
    ),
    steps: appendStep(
      state.steps,
      'disable-feature',
      featureId,
      featureId === 'leakage_code' && nextEnabled === false,
    ),
  }
}

export function encodeCategory(state: FeatureFactoryState, featureId: string): FeatureFactoryState {
  const feature = state.features.find((item) => item.id === featureId)
  return {
    ...state,
    features: state.features.map((item) =>
      item.id === featureId ? { ...item, encoded: true } : item,
    ),
    steps: appendStep(
      state.steps,
      'encode-category',
      featureId,
      featureId === 'segment' && feature?.kind === 'category' && feature.enabled,
    ),
  }
}

function hasMissing(rows: DatasetRow[]) {
  return rows.some((row) => Object.values(row.values).some((value) => value === null))
}

function hasOutlier(rows: DatasetRow[]) {
  return rows.some((row) => row.flags?.includes('outlier'))
}

function featureById(features: FeatureState[], featureId: string) {
  return features.find((feature) => feature.id === featureId)
}

export function splitQuality(rows: DatasetRow[]): SplitQuality {
  const train = rows.filter((row) => row.split === 'train')
  const test = rows.filter((row) => row.split === 'test')
  const labelRate = (items: DatasetRow[]) =>
    items.length === 0 ? 0 : items.filter((row) => row.label === 1).length / items.length
  const range = (items: DatasetRow[]) => {
    const signals = items
      .map((row) => row.values.signal)
      .filter((value): value is number => typeof value === 'number')
    return Math.max(...signals) - Math.min(...signals)
  }
  const trainRange = range(train)
  const testRange = range(test)
  const rangeGap = Math.abs(trainRange - testRange) / Math.max(trainRange, testRange, 1)
  const labelGap = Math.abs(labelRate(train) - labelRate(test))
  return {
    labelGap,
    rangeGap,
    ok: labelGap <= 0.2 && rangeGap <= 0.45,
  }
}

export function factoryMetrics(state: FeatureFactoryState): ModelMetric[] {
  const missingFixed = !hasMissing(state.rows)
  const outlierFixed = !hasOutlier(state.rows)
  const leakageOff = featureById(state.features, 'leakage_code')?.enabled === false
  const segmentEncoded = featureById(state.features, 'segment')?.encoded === true
  let train = 0.7
  let test = 0.6
  if (missingFixed) {
    train += 0.04
    test += 0.08
  }
  if (outlierFixed) {
    train -= 0.01
    test += 0.1
  }
  if (segmentEncoded) {
    train += 0.05
    test += 0.07
  }
  if (!leakageOff) {
    train += 0.17
    test -= 0.14
  }
  const clip = (value: number) => Math.max(0, Math.min(0.99, value))
  return [
    {
      id: 'stability',
      label: 'Stability',
      train: clip(train),
      test: clip(test),
      format: 'percent',
      warning: leakageOff ? undefined : 'leakage inflates train',
    },
    {
      id: 'coverage',
      label: 'Coverage',
      train: state.rows.filter((row) => row.split === 'train').length / 7,
      test: state.rows.filter((row) => row.split === 'test').length / 5,
      format: 'percent',
    },
  ]
}

export function diagnoseFactory(
  levelId: FeatureFactoryLevelId,
  state: FeatureFactoryState,
): FeatureFactoryDiagnosis {
  const leakage = featureById(state.features, 'leakage_code')
  const segment = featureById(state.features, 'segment')
  if (state.rows.length < factoryBaseRows.length - 2) {
    return {
      kind: 'over-cleaned',
      message: 'Pipeline слишком агрессивен: полезные строки исчезают вместе с шумом.',
      repairHint: 'Удаляй только строку с явным outlier-флагом.',
      invariantOk: false,
    }
  }
  if (levelId === 'missing-values' && hasMissing(state.rows)) {
    return {
      kind: 'missing-left',
      message: 'В таблице остались NA: модель будет учиться на дырках.',
      repairHint: 'Заполни temperature медианой, не удаляя весь test.',
      invariantOk: false,
    }
  }
  if (levelId === 'outlier-repair' && hasOutlier(state.rows)) {
    return {
      kind: 'outlier-left',
      message: 'Выброс ff-07 все еще тянет границу к себе.',
      repairHint: 'Удаляй только outlier-строку, а не весь хвост распределения.',
      invariantOk: false,
    }
  }
  if (levelId === 'leakage-off' && leakage?.enabled) {
    return {
      kind: 'leakage-enabled',
      message: 'Leakage-признак включен: train выглядит слишком красиво.',
      repairHint: 'Отключи leakage code и смотри на честные признаки.',
      invariantOk: false,
    }
  }
  if (levelId === 'encode-category' && !segment?.encoded) {
    return {
      kind: 'category-raw',
      message: 'Категория segment пока сырая: модель не понимает буквы как числа.',
      repairHint: 'Закодируй segment и сохрани признак включенным.',
      invariantOk: false,
    }
  }
  return {
    kind: 'ready',
    message: 'Pipeline выглядит честно: данные очищены без утечки и потери смысла.',
    repairHint: 'Теперь этот прием можно переносить в ML-полигон.',
    invariantOk: true,
  }
}

export function formatPercent(value: number) {
  return `${Math.round(value * 100)}%`
}
