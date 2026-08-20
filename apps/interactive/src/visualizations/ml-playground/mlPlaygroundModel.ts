import type {
  ConfusionCounts,
  DatasetColumn,
  DatasetRow,
  DatasetSplit,
  ModelMetric,
  ThresholdModel,
} from '../../game/dataTypes'

export type MlLevelId =
  | 'simple-threshold'
  | 'test-control'
  | 'f1-threshold'
  | 'leakage-trap'

export type MlDiagnosisKind =
  | 'good-fit'
  | 'bad-threshold'
  | 'train-test-gap'
  | 'accuracy-trap'
  | 'leakage-used'
  | 'underfit'
  | 'wrong-feature'

export type MlDiagnosis = {
  kind: MlDiagnosisKind
  message: string
  repairHint: string
  invariantOk: boolean
}

export type MlLevelConfig = {
  id: MlLevelId
  title: string
  model: ThresholdModel
  allowedFeatures: string[]
  goal: string
  leakageEnabled?: boolean
}

export const mlColumns: DatasetColumn[] = [
  { id: 'signal', label: 'signal', kind: 'number' },
  { id: 'noise', label: 'noise', kind: 'number' },
  { id: 'leakage_score', label: 'leak', kind: 'number' },
]

export const mlFeatureLabels: Record<string, string> = {
  signal: 'signal',
  noise: 'noise',
  leakage_score: 'leakage',
}

export const mlBaseRows: DatasetRow[] = [
  { id: 'tr-01', split: 'train', label: 0, values: { signal: 18, noise: 72, leakage_score: 0.04 } },
  { id: 'tr-02', split: 'train', label: 0, values: { signal: 25, noise: 64, leakage_score: 0.08 } },
  { id: 'tr-03', split: 'train', label: 0, values: { signal: 31, noise: 35, leakage_score: 0.11 } },
  { id: 'tr-04', split: 'train', label: 0, values: { signal: 38, noise: 51, leakage_score: 0.13 } },
  { id: 'tr-05', split: 'train', label: 0, values: { signal: 44, noise: 28, leakage_score: 0.18 } },
  { id: 'tr-06', split: 'train', label: 1, values: { signal: 52, noise: 61, leakage_score: 0.91 } },
  { id: 'tr-07', split: 'train', label: 1, values: { signal: 58, noise: 42, leakage_score: 0.94 } },
  { id: 'tr-08', split: 'train', label: 1, values: { signal: 63, noise: 79, leakage_score: 0.96 } },
  { id: 'tr-09', split: 'train', label: 1, values: { signal: 70, noise: 33, leakage_score: 0.98 } },
  { id: 'tr-10', split: 'train', label: 1, values: { signal: 82, noise: 55, leakage_score: 0.99 } },
  { id: 'te-01', split: 'test', label: 0, values: { signal: 42, noise: 68, leakage_score: 0.58 } },
  { id: 'te-02', split: 'test', label: 0, values: { signal: 48, noise: 31, leakage_score: 0.62 } },
  { id: 'te-03', split: 'test', label: 0, values: { signal: 55, noise: 74, leakage_score: 0.57 } },
  { id: 'te-04', split: 'test', label: 1, values: { signal: 61, noise: 47, leakage_score: 0.53 } },
  { id: 'te-05', split: 'test', label: 1, values: { signal: 67, noise: 26, leakage_score: 0.45 } },
  { id: 'te-06', split: 'test', label: 1, values: { signal: 74, noise: 83, leakage_score: 0.49 } },
]

export const imbalancedRows: DatasetRow[] = [
  { id: 'imb-01', split: 'train', label: 0, values: { signal: 16, noise: 40, leakage_score: 0.08 } },
  { id: 'imb-02', split: 'train', label: 0, values: { signal: 21, noise: 45, leakage_score: 0.12 } },
  { id: 'imb-03', split: 'train', label: 0, values: { signal: 27, noise: 52, leakage_score: 0.15 } },
  { id: 'imb-04', split: 'train', label: 0, values: { signal: 33, noise: 34, leakage_score: 0.18 } },
  { id: 'imb-05', split: 'train', label: 0, values: { signal: 39, noise: 77, leakage_score: 0.21 } },
  { id: 'imb-06', split: 'train', label: 0, values: { signal: 46, noise: 59, leakage_score: 0.25 } },
  { id: 'imb-07', split: 'train', label: 0, values: { signal: 52, noise: 48, leakage_score: 0.29 } },
  { id: 'imb-08', split: 'train', label: 1, values: { signal: 59, noise: 64, leakage_score: 0.91 } },
  { id: 'imb-09', split: 'train', label: 1, values: { signal: 71, noise: 38, leakage_score: 0.95 } },
  { id: 'imb-10', split: 'test', label: 0, values: { signal: 30, noise: 57, leakage_score: 0.51 } },
  { id: 'imb-11', split: 'test', label: 0, values: { signal: 43, noise: 62, leakage_score: 0.54 } },
  { id: 'imb-12', split: 'test', label: 0, values: { signal: 56, noise: 43, leakage_score: 0.48 } },
  { id: 'imb-13', split: 'test', label: 1, values: { signal: 62, noise: 51, leakage_score: 0.47 } },
  { id: 'imb-14', split: 'test', label: 1, values: { signal: 78, noise: 69, leakage_score: 0.46 } },
]

export const mlLevelConfigs: Record<MlLevelId, MlLevelConfig> = {
  'simple-threshold': {
    id: 'simple-threshold',
    title: 'Простой порог',
    model: { featureId: 'signal', threshold: 35, direction: 'gte' },
    allowedFeatures: ['signal', 'noise'],
    goal: 'Поставь порог так, чтобы train accuracy стала высокой.',
  },
  'test-control': {
    id: 'test-control',
    title: 'Test-контроль',
    model: { featureId: 'signal', threshold: 45, direction: 'gte' },
    allowedFeatures: ['signal', 'noise'],
    goal: 'Не довольствуйся train: test тоже должен пройти.',
  },
  'f1-threshold': {
    id: 'f1-threshold',
    title: 'Порог против F1',
    model: { featureId: 'signal', threshold: 75, direction: 'gte' },
    allowedFeatures: ['signal', 'noise'],
    goal: 'На несбалансированном наборе accuracy может обмануть.',
  },
  'leakage-trap': {
    id: 'leakage-trap',
    title: 'Утечка признака',
    model: { featureId: 'leakage_score', threshold: 0.5, direction: 'gte' },
    allowedFeatures: ['signal', 'leakage_score'],
    goal: 'Отключи подозрительный признак и сохрани честную test-метрику.',
    leakageEnabled: true,
  },
}

export function rowsForLevel(levelId: MlLevelId): DatasetRow[] {
  return levelId === 'f1-threshold' ? imbalancedRows : mlBaseRows
}

export function featureValue(row: DatasetRow, featureId: string): number {
  const value = row.values[featureId]
  return typeof value === 'number' && Number.isFinite(value) ? value : 0
}

export function predictThreshold(row: DatasetRow, model: ThresholdModel): 0 | 1 {
  const value = featureValue(row, model.featureId)
  return model.direction === 'gte'
    ? value >= model.threshold
      ? 1
      : 0
    : value < model.threshold
      ? 1
      : 0
}

export function applyModel(rows: DatasetRow[], model: ThresholdModel): DatasetRow[] {
  return rows.map((row) => {
    const prediction = predictThreshold(row, model)
    const flags = new Set(row.flags ?? [])
    if (prediction !== row.label) flags.add('misclassified')
    else flags.delete('misclassified')
    if (model.featureId === 'leakage_score') flags.add('leakage')
    return { ...row, prediction, flags: Array.from(flags) }
  })
}

export function splitRows(rows: DatasetRow[], split: DatasetSplit): DatasetRow[] {
  return rows.filter((row) => row.split === split)
}

export function confusionCounts(rows: DatasetRow[]): ConfusionCounts {
  return rows.reduce<ConfusionCounts>(
    (counts, row) => {
      if (row.label === 1 && row.prediction === 1) counts.tp += 1
      if (row.label === 0 && row.prediction === 1) counts.fp += 1
      if (row.label === 0 && row.prediction === 0) counts.tn += 1
      if (row.label === 1 && row.prediction === 0) counts.fn += 1
      return counts
    },
    { tp: 0, fp: 0, tn: 0, fn: 0 },
  )
}

function ratio(numerator: number, denominator: number): number {
  return denominator === 0 ? 0 : numerator / denominator
}

export function accuracy(rows: DatasetRow[]): number {
  return ratio(rows.filter((row) => row.prediction === row.label).length, rows.length)
}

export function precisionRecallF1(rows: DatasetRow[]) {
  const counts = confusionCounts(rows)
  const precision = ratio(counts.tp, counts.tp + counts.fp)
  const recall = ratio(counts.tp, counts.tp + counts.fn)
  const f1 = ratio(2 * precision * recall, precision + recall)
  return { precision, recall, f1 }
}

export function trainTestMetrics(rows: DatasetRow[]): ModelMetric[] {
  const train = splitRows(rows, 'train')
  const test = splitRows(rows, 'test')
  const trainPrf = precisionRecallF1(train)
  const testPrf = precisionRecallF1(test)
  return [
    { id: 'accuracy', label: 'Accuracy', train: accuracy(train), test: accuracy(test), format: 'percent' },
    { id: 'precision', label: 'Precision', train: trainPrf.precision, test: testPrf.precision, format: 'percent' },
    { id: 'recall', label: 'Recall', train: trainPrf.recall, test: testPrf.recall, format: 'percent' },
    { id: 'f1', label: 'F1', train: trainPrf.f1, test: testPrf.f1, format: 'percent' },
  ]
}

export function metricValue(metrics: ModelMetric[], metricId: string, split: DatasetSplit): number {
  const metric = metrics.find((item) => item.id === metricId)
  return metric ? metric[split] : 0
}

export function diagnoseModel(
  levelId: MlLevelId,
  rows: DatasetRow[],
  model: ThresholdModel,
): MlDiagnosis {
  const predicted = applyModel(rows, model)
  const metrics = trainTestMetrics(predicted)
  const trainAcc = metricValue(metrics, 'accuracy', 'train')
  const testAcc = metricValue(metrics, 'accuracy', 'test')
  const testF1 = metricValue(metrics, 'f1', 'test')
  const testRecall = metricValue(metrics, 'recall', 'test')

  if (!mlLevelConfigs[levelId].allowedFeatures.includes(model.featureId)) {
    return {
      kind: 'wrong-feature',
      message: 'Этот уровень проверяет другой признак: выбранная ось не решает задачу.',
      repairHint: 'Переключись на разрешенный признак и снова настрой порог.',
      invariantOk: false,
    }
  }

  if (model.featureId === 'leakage_score') {
    return {
      kind: 'leakage-used',
      message: 'Метрика выглядит слишком красиво: признак leak знает ответ и ломает честный test.',
      repairHint: 'Отключи leakage-признак и вернись к signal.',
      invariantOk: false,
    }
  }

  if (levelId === 'simple-threshold') {
    if (trainAcc >= 0.9) {
      return {
        kind: 'good-fit',
        message: 'Train-порог пойман: почти все обучающие точки по правильную сторону.',
        repairHint: 'Теперь проверь, выдержит ли тот же порог test.',
        invariantOk: true,
      }
    }
    return {
      kind: trainAcc < 0.65 ? 'underfit' : 'bad-threshold',
      message: 'Порог пока режет train-облако слишком грубо.',
      repairHint: 'Двигай границу ближе к промежутку между 44 и 52.',
      invariantOk: false,
    }
  }

  if (levelId === 'test-control') {
    if (trainAcc >= 0.95 && testAcc < 0.8) {
      return {
        kind: 'train-test-gap',
        message: 'Train выглядит идеально, но test уже спорит: граница слишком низкая.',
        repairHint: 'Подними порог так, чтобы точки test около 48-55 не стали ложными плюсами.',
        invariantOk: false,
      }
    }
    if (testAcc >= 0.83 && trainAcc >= 0.8) {
      return {
        kind: 'good-fit',
        message: 'Порог выдержал test-контроль: модель не просто запомнила train.',
        repairHint: 'Смотри на обе колонки метрик, не только на train.',
        invariantOk: true,
      }
    }
    return {
      kind: 'bad-threshold',
      message: 'Test еще не согласен с выбранным порогом.',
      repairHint: 'Ищи границу около 58-60.',
      invariantOk: false,
    }
  }

  if (levelId === 'f1-threshold') {
    if (testAcc >= 0.6 && testRecall < 0.7) {
      return {
        kind: 'accuracy-trap',
        message: 'Accuracy терпимая, но recall положительного класса провалился.',
        repairHint: 'Опусти порог, чтобы не терять редкие положительные точки.',
        invariantOk: false,
      }
    }
    if (testF1 >= 0.8 && testRecall >= 0.8) {
      return {
        kind: 'good-fit',
        message: 'F1 сбалансирован: редкий класс больше не потерян за красивой accuracy.',
        repairHint: 'На несбалансированных данных следи за precision и recall вместе.',
        invariantOk: true,
      }
    }
    return {
      kind: 'bad-threshold',
      message: 'Порог еще не держит precision/recall trade-off.',
      repairHint: 'Ищи границу около первой положительной точки.',
      invariantOk: false,
    }
  }

  if (testAcc >= 0.83 && trainAcc >= 0.8) {
    return {
      kind: 'good-fit',
      message: 'Утечка отключена: честный signal дает устойчивый test.',
      repairHint: 'Идеальная метрика хуже честной, если она получена через leakage.',
      invariantOk: true,
    }
  }
  return {
    kind: 'bad-threshold',
    message: 'После отключения leakage порог signal еще нужно настроить.',
    repairHint: 'Подними порог к честной границе около 58-60.',
    invariantOk: false,
  }
}

export function formatPercent(value: number): string {
  return `${Math.round(value * 100)}%`
}
