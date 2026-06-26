export type MonteCarloLevelId = 'circle-pi' | 'triangle' | 'parabola'

export type MonteCarloDiagnosisKind = 'idle' | 'success' | 'too-few-samples' | 'estimate-off'

export type MonteCarloDiagnosis = {
  kind: MonteCarloDiagnosisKind
  message: string
  repairHint: string
}

export type SamplePoint = { x: number; y: number; inside: boolean }

export type MonteCarloLevelConfig = {
  id: MonteCarloLevelId
  /** Whether a point of the unit square is inside the target region. */
  inside: (x: number, y: number) => boolean
  /** True value the estimator should converge to. */
  target: number
  /** Whether the estimator is the area fraction or 4x the fraction (pi). */
  estimator: 'fraction' | 'pi'
  tolerance: number
  minSamples: number
  seed: number
}

export const monteCarloLevels: Record<MonteCarloLevelId, MonteCarloLevelConfig> = {
  // Quarter disk in the unit square: fraction inside -> pi / 4, so pi = 4 * frac.
  'circle-pi': {
    id: 'circle-pi',
    inside: (x, y) => x * x + y * y <= 1,
    target: Math.PI,
    estimator: 'pi',
    tolerance: 0.12,
    minSamples: 1000,
    seed: 12345,
  },
  // Triangle y < x: area 1/2.
  triangle: {
    id: 'triangle',
    inside: (x, y) => y < x,
    target: 0.5,
    estimator: 'fraction',
    tolerance: 0.04,
    minSamples: 1000,
    seed: 777,
  },
  // Region under the parabola y < x^2: area 1/3.
  parabola: {
    id: 'parabola',
    inside: (x, y) => y < x * x,
    target: 1 / 3,
    estimator: 'fraction',
    tolerance: 0.04,
    minSamples: 1000,
    seed: 2024,
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

export type MonteCarloRun = {
  points: SamplePoint[]
  hits: number
  fraction: number
}

/**
 * Draw `n` deterministic points in the unit square. `pointCap` limits how many
 * are returned for rendering, but the hit count always uses the full `n`.
 */
export function runMonteCarlo(
  levelId: MonteCarloLevelId,
  n: number,
  pointCap = 600,
): MonteCarloRun {
  const config = monteCarloLevels[levelId]
  const next = mulberry32(config.seed)
  const points: SamplePoint[] = []
  let hits = 0
  for (let i = 0; i < n; i += 1) {
    const x = next()
    const y = next()
    const inside = config.inside(x, y)
    if (inside) hits += 1
    if (points.length < pointCap) points.push({ x, y, inside })
  }
  return { points, hits, fraction: n > 0 ? hits / n : 0 }
}

export function estimateValue(levelId: MonteCarloLevelId, run: MonteCarloRun): number {
  return monteCarloLevels[levelId].estimator === 'pi' ? 4 * run.fraction : run.fraction
}

export function monteCarloLevelSuccess({
  levelId,
  sampleSize,
}: {
  levelId: MonteCarloLevelId
  sampleSize: number
}): boolean {
  const config = monteCarloLevels[levelId]
  if (sampleSize < config.minSamples) return false
  const run = runMonteCarlo(levelId, sampleSize)
  return Math.abs(estimateValue(levelId, run) - config.target) <= config.tolerance
}

export function diagnoseMonteCarlo({
  levelId,
  sampleSize,
  touched,
}: {
  levelId: MonteCarloLevelId
  sampleSize: number
  touched: boolean
}): MonteCarloDiagnosis {
  const config = monteCarloLevels[levelId]
  if (!touched) {
    return {
      kind: 'idle',
      message: 'Бросай точки в квадрат: доля попавших в область оценивает её площадь.',
      repairHint: 'Увеличивай число точек и следи за оценкой.',
    }
  }
  if (monteCarloLevelSuccess({ levelId, sampleSize })) {
    return {
      kind: 'success',
      message: 'Оценка устойчиво совпала с истинным значением.',
      repairHint: 'Геометрическая вероятность = отношение площадей.',
    }
  }
  if (sampleSize < config.minSamples) {
    return {
      kind: 'too-few-samples',
      message: `Мало точек: ${sampleSize} < ${config.minSamples}. Оценка площади шумит.`,
      repairHint: 'Добавь точек: разброс оценки падает как 1/sqrt(n).',
    }
  }
  return {
    kind: 'estimate-off',
    message: 'Оценка ещё за пределами допуска.',
    repairHint: 'Набери ещё точек, чтобы доля стабилизировалась.',
  }
}

export function formatEstimate(value: number): string {
  return value.toFixed(3)
}
