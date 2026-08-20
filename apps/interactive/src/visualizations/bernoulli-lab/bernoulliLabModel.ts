export type BernoulliLevelId = 'fair-coin' | 'estimate-bias' | 'law-of-large-numbers'

export type BernoulliDiagnosisKind =
  | 'idle'
  | 'success'
  | 'too-few-samples'
  | 'estimate-off'
  | 'band-not-stable'

export type BernoulliDiagnosis = {
  kind: BernoulliDiagnosisKind
  message: string
  repairHint: string
}

export type BernoulliLevelConfig = {
  id: BernoulliLevelId
  /** Actual probability of heads used to draw the toy sample. */
  trueP: number
  /** Whether the true probability is shown to the player. */
  knownP: boolean
  /** Value the frequency should converge to (for fair-coin / LLN). */
  targetFreq: number
  /** Minimum number of trials required to call the result trustworthy. */
  minSamples: number
  /** Allowed gap on frequency / estimate. */
  tolerance: number
  /** Fixed seed: the lab is honest and reproducible, not magic. */
  seed: number
}

export const bernoulliLevels: Record<BernoulliLevelId, BernoulliLevelConfig> = {
  'fair-coin': {
    id: 'fair-coin',
    trueP: 0.5,
    knownP: true,
    targetFreq: 0.5,
    minSamples: 500,
    tolerance: 0.05,
    seed: 1337,
  },
  'estimate-bias': {
    id: 'estimate-bias',
    trueP: 0.7,
    knownP: false,
    targetFreq: 0.7,
    minSamples: 500,
    tolerance: 0.05,
    seed: 4242,
  },
  'law-of-large-numbers': {
    id: 'law-of-large-numbers',
    trueP: 0.5,
    knownP: true,
    targetFreq: 0.5,
    minSamples: 1000,
    tolerance: 0.03,
    seed: 2024,
  },
}

export const sampleSizeStops = [20, 100, 500, 2000]

/**
 * Deterministic PRNG (mulberry32). A fixed seed makes every run reproducible,
 * so a "lucky" or "unlucky" sample is a property of the seed, not hidden state.
 */
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

export type BernoulliRun = {
  sequence: (0 | 1)[]
  heads: number
  tails: number
  frequency: number
}

export function runBernoulli(seed: number, p: number, n: number): BernoulliRun {
  const next = mulberry32(seed)
  const sequence: (0 | 1)[] = []
  let heads = 0
  for (let i = 0; i < n; i += 1) {
    const flip: 0 | 1 = next() < p ? 1 : 0
    sequence.push(flip)
    heads += flip
  }
  return {
    sequence,
    heads,
    tails: n - heads,
    frequency: n > 0 ? heads / n : 0,
  }
}

/** Running estimate of P(heads) after each trial. */
export function runningFrequency(sequence: (0 | 1)[]): number[] {
  const result: number[] = []
  let heads = 0
  sequence.forEach((flip, index) => {
    heads += flip
    result.push(heads / (index + 1))
  })
  return result
}

/** Largest deviation from the target over the final `tailFraction` of the run. */
export function tailDeviation(sequence: (0 | 1)[], target: number, tailFraction = 0.25): number {
  if (sequence.length === 0) return 1
  const freqs = runningFrequency(sequence)
  const start = Math.floor(freqs.length * (1 - tailFraction))
  let maxDeviation = 0
  for (let i = start; i < freqs.length; i += 1) {
    maxDeviation = Math.max(maxDeviation, Math.abs(freqs[i] - target))
  }
  return maxDeviation
}

export function bernoulliLevelSuccess({
  levelId,
  sampleSize,
  estimate,
}: {
  levelId: BernoulliLevelId
  sampleSize: number
  estimate: number
}): boolean {
  const config = bernoulliLevels[levelId]
  if (sampleSize < config.minSamples) return false
  const run = runBernoulli(config.seed, config.trueP, sampleSize)

  if (levelId === 'estimate-bias') {
    return Math.abs(estimate - config.trueP) <= config.tolerance
  }
  if (levelId === 'law-of-large-numbers') {
    return tailDeviation(run.sequence, config.targetFreq) <= config.tolerance
  }
  return Math.abs(run.frequency - config.targetFreq) <= config.tolerance
}

export function diagnoseBernoulli({
  levelId,
  sampleSize,
  estimate,
  touched,
}: {
  levelId: BernoulliLevelId
  sampleSize: number
  estimate: number
  touched: boolean
}): BernoulliDiagnosis {
  const config = bernoulliLevels[levelId]
  if (!touched) {
    return {
      kind: 'idle',
      message: 'Брось монету: набери выборку и смотри, к чему сходится частота.',
      repairHint: 'Увеличивай число бросков и следи за линией частоты.',
    }
  }
  if (bernoulliLevelSuccess({ levelId, sampleSize, estimate })) {
    return {
      kind: 'success',
      message: 'Частота устойчиво держится у вероятности.',
      repairHint: 'Закон больших чисел сработал.',
    }
  }
  if (sampleSize < config.minSamples) {
    return {
      kind: 'too-few-samples',
      message: `Слишком мало бросков: ${sampleSize} < ${config.minSamples}. Малая выборка шумит.`,
      repairHint: 'Добавь бросков: частота стабилизируется только на большом n.',
    }
  }
  if (levelId === 'estimate-bias') {
    return {
      kind: 'estimate-off',
      message: 'Оценка вероятности ещё мимо наблюдаемой частоты.',
      repairHint: 'Подведи ползунок оценки к частоте на большой выборке.',
    }
  }
  return {
    kind: 'band-not-stable',
    message: 'Частота ещё гуляет шире коридора.',
    repairHint: 'Шум падает как 1/sqrt(n): набери больше бросков.',
  }
}

export function formatProbability(value: number): string {
  return value.toFixed(2)
}
