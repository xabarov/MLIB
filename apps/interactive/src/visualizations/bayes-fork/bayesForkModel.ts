export type BayesLevelId = 'conditional-frequency' | 'base-rate' | 'two-tests'

export type BayesDiagnosisKind =
  | 'idle'
  | 'success'
  | 'too-few-samples'
  | 'base-rate-neglect'
  | 'estimate-off'

export type BayesDiagnosis = {
  kind: BayesDiagnosisKind
  message: string
  repairHint: string
}

/** Which event counts as "positive" and which margin the answer conditions on. */
export type BayesLevelConfig = {
  id: BayesLevelId
  /** P(D): base rate of the hidden condition. */
  baseRate: number
  /** P(+ | D): test sensitivity. */
  sensitivity: number
  /** P(- | not D): test specificity, so false positive rate is 1 - specificity. */
  specificity: number
  /** Positive event uses two independent tests instead of one. */
  doubleTest: boolean
  /** 'row' = condition on D (asks P(positive|D)); 'col' = condition on positive (asks P(D|positive)). */
  conditionOn: 'row' | 'col'
  /** Analytic value the estimate must match. */
  target: number
  tolerance: number
  minSamples: number
  seed: number
}

export function falsePositiveRate(specificity: number): number {
  return 1 - specificity
}

/**
 * Bayes posterior P(D | k positive tests) for `k` independent tests, each with
 * the given sensitivity and false-positive rate.
 */
export function posteriorAfterPositives(
  baseRate: number,
  sensitivity: number,
  falsePos: number,
  positives: number,
): number {
  const like = baseRate * sensitivity ** positives
  const likeNeg = (1 - baseRate) * falsePos ** positives
  const denom = like + likeNeg
  return denom > 0 ? like / denom : 0
}

const RARE = { baseRate: 0.02, sensitivity: 0.95, specificity: 0.94 }
const RARE_FP = falsePositiveRate(RARE.specificity)

export const bayesLevels: Record<BayesLevelId, BayesLevelConfig> = {
  // Balanced base rate: read the test's hit rate among the sick subgroup.
  'conditional-frequency': {
    id: 'conditional-frequency',
    baseRate: 0.5,
    sensitivity: 0.9,
    specificity: 0.85,
    doubleTest: false,
    conditionOn: 'row',
    target: 0.9,
    tolerance: 0.05,
    minSamples: 2000,
    seed: 4242,
  },
  // Rare disease + one positive test: the famous base-rate inversion.
  'base-rate': {
    id: 'base-rate',
    baseRate: RARE.baseRate,
    sensitivity: RARE.sensitivity,
    specificity: RARE.specificity,
    doubleTest: false,
    conditionOn: 'col',
    target: posteriorAfterPositives(RARE.baseRate, RARE.sensitivity, RARE_FP, 1),
    tolerance: 0.06,
    minSamples: 8000,
    seed: 9001,
  },
  // Two independent positives sharpen the posterior far past one test.
  'two-tests': {
    id: 'two-tests',
    baseRate: RARE.baseRate,
    sensitivity: RARE.sensitivity,
    specificity: RARE.specificity,
    doubleTest: true,
    conditionOn: 'col',
    target: posteriorAfterPositives(RARE.baseRate, RARE.sensitivity, RARE_FP, 2),
    tolerance: 0.07,
    minSamples: 8000,
    seed: 31337,
  },
}

export const sampleSizeStops = [500, 2000, 8000, 20000]

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

/**
 * 2x2 contingency table for a level's positive event.
 *   a = #(D, positive)   b = #(D, negative)
 *   c = #(not D, positive)   d = #(not D, negative)
 */
export type BayesRun = {
  a: number
  b: number
  c: number
  d: number
  total: number
}

export function runBayes(levelId: BayesLevelId, n: number): BayesRun {
  const config = bayesLevels[levelId]
  const falsePos = falsePositiveRate(config.specificity)
  const next = mulberry32(config.seed)
  let a = 0
  let b = 0
  let c = 0
  let d = 0
  for (let i = 0; i < n; i += 1) {
    const disease = next() < config.baseRate
    const pHit = disease ? config.sensitivity : falsePos
    const test1 = next() < pHit
    // Always draw the second test so the stream stays aligned across levels.
    const test2 = next() < pHit
    const positive = config.doubleTest ? test1 && test2 : test1
    if (disease) {
      if (positive) a += 1
      else b += 1
    } else if (positive) c += 1
    else d += 1
  }
  return { a, b, c, d, total: n }
}

/** Empirical estimate of the quantity the level asks for, read off the table. */
export function empiricalQuantity(levelId: BayesLevelId, run: BayesRun): number {
  const config = bayesLevels[levelId]
  if (config.conditionOn === 'row') {
    const row = run.a + run.b
    return row > 0 ? run.a / row : 0
  }
  const col = run.a + run.c
  return col > 0 ? run.a / col : 0
}

export function bayesLevelSuccess({
  levelId,
  sampleSize,
  estimate,
}: {
  levelId: BayesLevelId
  sampleSize: number
  estimate: number
}): boolean {
  const config = bayesLevels[levelId]
  if (sampleSize < config.minSamples) return false
  return Math.abs(estimate - config.target) <= config.tolerance
}

export function diagnoseBayes({
  levelId,
  sampleSize,
  estimate,
  touched,
}: {
  levelId: BayesLevelId
  sampleSize: number
  estimate: number
  touched: boolean
}): BayesDiagnosis {
  const config = bayesLevels[levelId]
  if (!touched) {
    return {
      kind: 'idle',
      message: 'Набери выборку и читай таблицу: где условие, а где ответ.',
      repairHint: 'Сначала собери данные, потом подведи оценку под нужную долю.',
    }
  }
  if (bayesLevelSuccess({ levelId, sampleSize, estimate })) {
    return {
      kind: 'success',
      message: 'Оценка совпала с условной вероятностью.',
      repairHint: 'Ты прочитал долю по правильному срезу таблицы.',
    }
  }
  if (sampleSize < config.minSamples) {
    return {
      kind: 'too-few-samples',
      message: `Мало наблюдений: ${sampleSize} < ${config.minSamples}. Редкий срез почти пуст и шумит.`,
      repairHint: 'Добавь выборки: нужная клетка таблицы наберёт достаточно случаев.',
    }
  }
  // Confusing P(+|D) with P(D|+): the estimate sits near the sensitivity.
  if (config.conditionOn === 'col' && Math.abs(estimate - config.sensitivity) <= config.tolerance) {
    return {
      kind: 'base-rate-neglect',
      message: 'Похоже, ты взял чувствительность P(+|D), а спрашивают P(D|+).',
      repairHint: 'Учти базовую частоту: дели больных-с-плюсом на всех-с-плюсом, а не на всех больных.',
    }
  }
  return {
    kind: 'estimate-off',
    message: 'Оценка ещё за пределами допуска вокруг истинной вероятности.',
    repairHint: 'Читай долю по нужному срезу: условие сужает таблицу до одной строки или столбца.',
  }
}

export function formatProbability(value: number): string {
  return value.toFixed(3)
}
