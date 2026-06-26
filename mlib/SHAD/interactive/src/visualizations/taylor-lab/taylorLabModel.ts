export type TaylorLevelId = 'tangent' | 'curvature' | 'sine'

export type TaylorDiagnosisKind = 'idle' | 'success' | 'coefficient-off'

export type TaylorDiagnosis = {
  kind: TaylorDiagnosisKind
  message: string
  repairHint: string
  worstCoeff: number | null
}

export type TaylorView = { xMin: number; xMax: number; yMin: number; yMax: number }

export type TaylorLevelConfig = {
  id: TaylorLevelId
  /** Target function being approximated. */
  fn: (x: number) => number
  /** Taylor coefficients c0..c4 of fn at 0. */
  target: number[]
  /** Plot window. */
  view: TaylorView
  /** Display label for the function. */
  label: string
}

/** Number of polynomial coefficients c0..c4 (degrees 0..4). */
export const DEGREE = 5
export const coeffStops = { min: -1.5, max: 1.5, step: 0.05 }
export const matchTolerance = 0.12

const EXP_VIEW: TaylorView = { xMin: -1.2, xMax: 1.2, yMin: -0.5, yMax: 3.6 }

export const taylorLevels: Record<TaylorLevelId, TaylorLevelConfig> = {
  // Tangent line of e^x at 0: 1 + x.
  tangent: {
    id: 'tangent',
    fn: Math.exp,
    target: [1, 1, 0, 0, 0],
    view: EXP_VIEW,
    label: 'eˣ',
  },
  // Quadratic Taylor of e^x: 1 + x + x^2/2.
  curvature: {
    id: 'curvature',
    fn: Math.exp,
    target: [1, 1, 0.5, 0, 0],
    view: EXP_VIEW,
    label: 'eˣ',
  },
  // Taylor of sin x: x - x^3/6 (odd terms only).
  sine: {
    id: 'sine',
    fn: Math.sin,
    target: [0, 1, 0, -1 / 6, 0],
    view: { xMin: -3, xMax: 3, yMin: -1.6, yMax: 1.6 },
    label: 'sin x',
  },
}

export function evaluatePolynomial(coeffs: number[], x: number): number {
  let sum = 0
  let power = 1
  for (let k = 0; k < coeffs.length; k += 1) {
    sum += coeffs[k] * power
    power *= x
  }
  return sum
}

/** RMS residual between the polynomial and the true function over the view. */
export function curveError(coeffs: number[], config: TaylorLevelConfig, samples = 120): number {
  const { xMin, xMax } = config.view
  let sum = 0
  for (let i = 0; i <= samples; i += 1) {
    const x = xMin + ((xMax - xMin) * i) / samples
    const diff = evaluatePolynomial(coeffs, x) - config.fn(x)
    sum += diff * diff
  }
  return Math.sqrt(sum / (samples + 1))
}

export function worstCoefficient(coeffs: number[], target: number[]): number | null {
  let worst = -1
  let worstGap = 0
  for (let k = 0; k < target.length; k += 1) {
    const gap = Math.abs((coeffs[k] ?? 0) - target[k])
    if (gap > worstGap) {
      worstGap = gap
      worst = k
    }
  }
  return worst >= 0 ? worst : null
}

export function taylorLevelSuccess(coeffs: number[], target: number[]): boolean {
  for (let k = 0; k < target.length; k += 1) {
    if (Math.abs((coeffs[k] ?? 0) - target[k]) > matchTolerance) return false
  }
  return true
}

export function diagnoseTaylor({
  coeffs,
  target,
  touched,
}: {
  coeffs: number[]
  target: number[]
  touched: boolean
}): TaylorDiagnosis {
  if (!touched) {
    return {
      kind: 'idle',
      message: 'Каждая ручка — коэффициент при x^k. Подгони полином под функцию у нуля.',
      repairHint: 'Совмести оранжевую кривую с бледной у начала координат.',
      worstCoeff: null,
    }
  }
  if (taylorLevelSuccess(coeffs, target)) {
    return {
      kind: 'success',
      message: 'Полином совпал с рядом Тейлора: функция и её производные сошлись в нуле.',
      repairHint: 'Коэффициенты совпали с производными функции в нуле.',
      worstCoeff: null,
    }
  }
  const worst = worstCoefficient(coeffs, target)
  return {
    kind: 'coefficient-off',
    message:
      worst !== null
        ? `Коэффициент при x^${worst} ещё далеко: нужно ${target[worst].toFixed(2)}.`
        : 'Коэффициенты ещё не совпали.',
    repairHint: 'Двигай самую далёкую от цели ручку к нужному значению.',
    worstCoeff: worst,
  }
}

export function formatCoefficient(value: number): string {
  return value.toFixed(2)
}
