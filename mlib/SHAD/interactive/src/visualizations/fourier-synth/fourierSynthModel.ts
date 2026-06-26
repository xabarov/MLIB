export type FourierLevelId = 'two-harmonics' | 'square-wave' | 'sawtooth'

export type FourierDiagnosisKind = 'idle' | 'success' | 'harmonic-off'

export type FourierDiagnosis = {
  kind: FourierDiagnosisKind
  message: string
  repairHint: string
  worstHarmonic: number | null
}

export type FourierLevelConfig = {
  id: FourierLevelId
  /** Target amplitude for sin(k x), k = 1..HARMONICS. */
  target: number[]
}

export const HARMONICS = 5
export const amplitudeStops = { min: -1.5, max: 1.5, step: 0.05 }
export const matchTolerance = 0.12

const FOUR_OVER_PI = 4 / Math.PI
const TWO_OVER_PI = 2 / Math.PI

export const fourierLevels: Record<FourierLevelId, FourierLevelConfig> = {
  'two-harmonics': {
    id: 'two-harmonics',
    target: [1.0, 0.5, 0, 0, 0],
  },
  // Square wave: odd harmonics with 1/k decay, even harmonics vanish.
  'square-wave': {
    id: 'square-wave',
    target: [FOUR_OVER_PI, 0, FOUR_OVER_PI / 3, 0, FOUR_OVER_PI / 5],
  },
  // Sawtooth: every harmonic, alternating sign, 1/k decay.
  sawtooth: {
    id: 'sawtooth',
    target: [TWO_OVER_PI, -TWO_OVER_PI / 2, TWO_OVER_PI / 3, -TWO_OVER_PI / 4, TWO_OVER_PI / 5],
  },
}

export function reconstruct(amplitudes: number[], x: number): number {
  let sum = 0
  for (let k = 0; k < amplitudes.length; k += 1) {
    sum += amplitudes[k] * Math.sin((k + 1) * x)
  }
  return sum
}

/**
 * L2 / RMS distance between two sine spectra. Over [0, 2pi] the cross terms
 * vanish, so the energy reduces exactly to the amplitude differences.
 */
export function spectralError(amplitudes: number[], target: number[]): number {
  let sum = 0
  for (let k = 0; k < target.length; k += 1) {
    const diff = (amplitudes[k] ?? 0) - target[k]
    sum += diff * diff
  }
  return Math.sqrt(0.5 * sum)
}

export function worstHarmonic(amplitudes: number[], target: number[]): number | null {
  let worst = -1
  let worstGap = 0
  for (let k = 0; k < target.length; k += 1) {
    const gap = Math.abs((amplitudes[k] ?? 0) - target[k])
    if (gap > worstGap) {
      worstGap = gap
      worst = k
    }
  }
  return worst >= 0 ? worst : null
}

export function fourierLevelSuccess(amplitudes: number[], target: number[]): boolean {
  for (let k = 0; k < target.length; k += 1) {
    if (Math.abs((amplitudes[k] ?? 0) - target[k]) > matchTolerance) return false
  }
  return true
}

export function diagnoseFourier({
  amplitudes,
  target,
  touched,
}: {
  amplitudes: number[]
  target: number[]
  touched: boolean
}): FourierDiagnosis {
  if (!touched) {
    return {
      kind: 'idle',
      message: 'Складывай гармоники: каждая ручка — амплитуда sin(k·x).',
      repairHint: 'Подгони синюю кривую под бледную целевую.',
      worstHarmonic: null,
    }
  }
  if (fourierLevelSuccess(amplitudes, target)) {
    return {
      kind: 'success',
      message: 'Сигнал собран: гармоники совпали с целевым спектром.',
      repairHint: 'Энергия ошибки упала почти до нуля.',
      worstHarmonic: null,
    }
  }
  const worst = worstHarmonic(amplitudes, target)
  return {
    kind: 'harmonic-off',
    message:
      worst !== null
        ? `Гармоника ${worst + 1} ещё далеко: нужно ${target[worst].toFixed(2)}.`
        : 'Спектр ещё не совпал.',
    repairHint: 'Двигай самую далёкую ручку к целевой амплитуде.',
    worstHarmonic: worst,
  }
}

export function formatAmplitude(value: number): string {
  return value.toFixed(2)
}
