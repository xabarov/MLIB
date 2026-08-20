export type ExpectationLevelId = 'sample-mean' | 'sample-variance' | 'estimate-mean'

export type ExpectationDiagnosisKind =
  | 'idle'
  | 'success'
  | 'too-few-samples'
  | 'std-not-variance'
  | 'estimate-off'

export type ExpectationDiagnosis = {
  kind: ExpectationDiagnosisKind
  message: string
  repairHint: string
}

/** Faces of the die the level samples (values are 1..6). */
export const DIE_FACES = [1, 2, 3, 4, 5, 6] as const

export type ExpectationLevelConfig = {
  id: ExpectationLevelId
  /** Probability weights for faces 1..6 (need not be normalized). */
  weights: number[]
  /** Whether the weighting is shown to the player. */
  knownWeights: boolean
  /** Quantity to estimate: the mean E[X] or the variance Var[X]. */
  quantity: 'mean' | 'variance'
  /** Analytic value the estimate must match. */
  target: number
  tolerance: number
  minSamples: number
  seed: number
}

function normalize(weights: number[]): number[] {
  const total = weights.reduce((sum, w) => sum + w, 0)
  return weights.map((w) => w / total)
}

export function distributionMean(weights: number[]): number {
  const probs = normalize(weights)
  return DIE_FACES.reduce((sum, face, index) => sum + face * probs[index], 0)
}

export function distributionVariance(weights: number[]): number {
  const probs = normalize(weights)
  const mean = distributionMean(weights)
  return DIE_FACES.reduce((sum, face, index) => sum + probs[index] * (face - mean) ** 2, 0)
}

const FAIR = [1, 1, 1, 1, 1, 1]
const LOADED = [3, 3, 2, 1, 1, 2]

export const expectationLevels: Record<ExpectationLevelId, ExpectationLevelConfig> = {
  // Fair die: the running average settles at E[X] = 3.5.
  'sample-mean': {
    id: 'sample-mean',
    weights: FAIR,
    knownWeights: true,
    quantity: 'mean',
    target: distributionMean(FAIR),
    tolerance: 0.15,
    minSamples: 1000,
    seed: 5151,
  },
  // Fair die: the spread of values is Var[X] = 35/12, not its square root.
  'sample-variance': {
    id: 'sample-variance',
    weights: FAIR,
    knownWeights: true,
    quantity: 'variance',
    target: distributionVariance(FAIR),
    tolerance: 0.3,
    minSamples: 5000,
    seed: 2718,
  },
  // Hidden loaded die: the mean is an estimator that needs data.
  'estimate-mean': {
    id: 'estimate-mean',
    weights: LOADED,
    knownWeights: false,
    quantity: 'mean',
    target: distributionMean(LOADED),
    tolerance: 0.15,
    minSamples: 1000,
    seed: 9091,
  },
}

export const sampleSizeStops = [50, 200, 1000, 5000]

export function mulberry32(seed: number): () => number {
  let state = seed >>> 0
  return function next() {
    state = (state + 0x6d2b79f5) >>> 0
    let t = state
    t = Math.imul(t ^ (t >>> 15), t | 1)
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

export type ExpectationRun = {
  counts: number[]
  sum: number
  sumSquares: number
  n: number
}

export function runExpectation(levelId: ExpectationLevelId, n: number): ExpectationRun {
  const config = expectationLevels[levelId]
  const probs = normalize(config.weights)
  const cumulative: number[] = []
  probs.reduce((acc, p, index) => {
    cumulative[index] = acc + p
    return cumulative[index]
  }, 0)
  const next = mulberry32(config.seed)
  const counts = [0, 0, 0, 0, 0, 0]
  let sum = 0
  let sumSquares = 0
  for (let i = 0; i < n; i += 1) {
    const u = next()
    let face = cumulative.findIndex((c) => u < c)
    if (face < 0) face = DIE_FACES.length - 1
    const value = DIE_FACES[face]
    counts[face] += 1
    sum += value
    sumSquares += value * value
  }
  return { counts, sum, sumSquares, n }
}

export function empiricalMean(run: ExpectationRun): number {
  return run.n > 0 ? run.sum / run.n : 0
}

export function empiricalVariance(run: ExpectationRun): number {
  if (run.n === 0) return 0
  const mean = run.sum / run.n
  return run.sumSquares / run.n - mean * mean
}

export function empiricalQuantity(levelId: ExpectationLevelId, run: ExpectationRun): number {
  return expectationLevels[levelId].quantity === 'mean'
    ? empiricalMean(run)
    : empiricalVariance(run)
}

export function expectationLevelSuccess({
  levelId,
  sampleSize,
  estimate,
}: {
  levelId: ExpectationLevelId
  sampleSize: number
  estimate: number
}): boolean {
  const config = expectationLevels[levelId]
  if (sampleSize < config.minSamples) return false
  return Math.abs(estimate - config.target) <= config.tolerance
}

export function diagnoseExpectation({
  levelId,
  sampleSize,
  estimate,
  touched,
}: {
  levelId: ExpectationLevelId
  sampleSize: number
  estimate: number
  touched: boolean
}): ExpectationDiagnosis {
  const config = expectationLevels[levelId]
  if (!touched) {
    return {
      kind: 'idle',
      message: 'Бросай кость и смотри, к чему сходится среднее значение.',
      repairHint: 'Сначала собери выборку, потом подведи оценку под нужную величину.',
    }
  }
  if (expectationLevelSuccess({ levelId, sampleSize, estimate })) {
    return {
      kind: 'success',
      message: 'Оценка совпала с истинной величиной распределения.',
      repairHint: 'Выборочная оценка сошлась к теоретическому значению.',
    }
  }
  if (sampleSize < config.minSamples) {
    return {
      kind: 'too-few-samples',
      message: `Мало бросков: ${sampleSize} < ${config.minSamples}. Оценка ещё шумит.`,
      repairHint: 'Добавь бросков: выборочная оценка стабилизируется на большом n.',
    }
  }
  // Confusing the variance with the standard deviation (its square root).
  if (
    config.quantity === 'variance' &&
    Math.abs(estimate - Math.sqrt(config.target)) <= config.tolerance
  ) {
    return {
      kind: 'std-not-variance',
      message: 'Похоже, ты оценил стандартное отклонение, а просят дисперсию.',
      repairHint: 'Дисперсия — это средний квадрат отклонения; возведи разброс в квадрат.',
    }
  }
  return {
    kind: 'estimate-off',
    message: 'Оценка ещё за пределами допуска вокруг истинной величины.',
    repairHint: 'Набери ещё бросков и подведи оценку к выборочному значению.',
  }
}

export function formatExpectation(value: number): string {
  return value.toFixed(2)
}
