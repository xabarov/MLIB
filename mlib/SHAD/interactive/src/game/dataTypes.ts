export type DatasetSplit = 'train' | 'test'

export type DatasetFlag = 'outlier' | 'missing' | 'leakage' | 'misclassified'

export type DatasetRow = {
  id: string
  split: DatasetSplit
  label: 0 | 1
  prediction?: 0 | 1
  values: Record<string, number | string | null>
  flags?: DatasetFlag[]
}

export type DatasetColumn = {
  id: string
  label: string
  kind?: 'number' | 'category'
}

export type ModelMetric = {
  id: string
  label: string
  train: number
  test: number
  format?: 'percent' | 'number'
  warning?: string
}

export type ConfusionCounts = {
  tp: number
  fp: number
  tn: number
  fn: number
}

export type ThresholdModel = {
  featureId: string
  threshold: number
  direction: 'gte' | 'lt'
}

export type DataActionKind =
  | 'mark-missing'
  | 'impute-median'
  | 'fill-zero'
  | 'drop-missing'
  | 'drop-row'
  | 'mark-outlier'
  | 'disable-feature'
  | 'encode-category'
  | 'keep-raw'
  | 'choose-split'

export type DataPipelineStep = {
  id: string
  kind: DataActionKind
  label: string
  targetId: string
  valid: boolean
}

export type FeatureState = {
  id: string
  label: string
  enabled: boolean
  kind?: DatasetColumn['kind']
  encoded?: boolean
  flaggedAsLeakage?: boolean
}

export type SplitQuality = {
  labelGap: number
  rangeGap: number
  ok: boolean
}
