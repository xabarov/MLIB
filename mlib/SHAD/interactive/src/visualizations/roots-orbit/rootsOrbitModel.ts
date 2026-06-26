export type Complex = [number, number] // [re, im]

export type RootsLevelId = 'triangle' | 'square' | 'pentagon'

export type RootsDiagnosisKind =
  | 'idle'
  | 'success'
  | 'modulus-off'
  | 'angle-off'
  | 'not-primitive'

export type RootsDiagnosis = {
  kind: RootsDiagnosisKind
  message: string
  repairHint: string
}

export type RootsLevelConfig = {
  id: RootsLevelId
  n: number
  start: Complex
}

export const rootsLevels: Record<RootsLevelId, RootsLevelConfig> = {
  triangle: { id: 'triangle', n: 3, start: [1.18, 0.28] },
  square: { id: 'square', n: 4, start: [1.12, -0.2] },
  pentagon: { id: 'pentagon', n: 5, start: [0.82, 0.34] },
}

export const modulusTolerance = 0.06
export const closeTolerance = 0.08
export const distinctTolerance = 0.08

export function cmul(a: Complex, b: Complex): Complex {
  return [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]]
}

export function cabs(z: Complex): number {
  return Math.hypot(z[0], z[1])
}

export function csub(a: Complex, b: Complex): Complex {
  return [a[0] - b[0], a[1] - b[1]]
}

/** z to the power k (k >= 0). */
export function cpow(z: Complex, k: number): Complex {
  let result: Complex = [1, 0]
  for (let i = 0; i < k; i += 1) {
    result = cmul(result, z)
  }
  return result
}

/** The n polygon vertices z^0, z^1, ..., z^(n-1). */
export function orbit(z: Complex, n: number): Complex[] {
  const points: Complex[] = []
  for (let k = 0; k < n; k += 1) {
    points.push(cpow(z, k))
  }
  return points
}

/** How far z^n lands from 1: zero means the orbit closes on itself. */
export function closureError(z: Complex, n: number): number {
  return cabs(csub(cpow(z, n), [1, 0]))
}

/** Count of geometrically distinct points (greedy clustering by tolerance). */
export function distinctCount(points: Complex[], tolerance = distinctTolerance): number {
  const kept: Complex[] = []
  for (const point of points) {
    if (!kept.some((other) => cabs(csub(point, other)) < tolerance)) {
      kept.push(point)
    }
  }
  return kept.length
}

export function rootsLevelSuccess({
  levelId,
  z,
}: {
  levelId: RootsLevelId
  z: Complex
}): boolean {
  const { n } = rootsLevels[levelId]
  if (Math.abs(cabs(z) - 1) > modulusTolerance) return false
  if (closureError(z, n) > closeTolerance) return false
  return distinctCount(orbit(z, n)) === n
}

export function diagnoseRoots({
  levelId,
  z,
  touched,
}: {
  levelId: RootsLevelId
  z: Complex
  touched: boolean
}): RootsDiagnosis {
  const { n } = rootsLevels[levelId]
  if (!touched) {
    return {
      kind: 'idle',
      message: 'Двигай число z: его степени z, z², ... обходят окружность.',
      repairHint: 'Поставь z на единичную окружность под нужным углом.',
    }
  }
  if (rootsLevelSuccess({ levelId, z })) {
    return {
      kind: 'success',
      message: `Орбита замкнулась: z^${n} = 1, и степени образуют правильный ${n}-угольник.`,
      repairHint: 'Это первообразный корень степени n из единицы.',
    }
  }
  const modulus = cabs(z)
  if (Math.abs(modulus - 1) > modulusTolerance) {
    return {
      kind: 'modulus-off',
      message:
        modulus > 1
          ? `|z| = ${modulus.toFixed(2)} > 1: степени уходят по спирали наружу.`
          : `|z| = ${modulus.toFixed(2)} < 1: степени сходятся по спирали к нулю.`,
      repairHint: 'Верни z на единичную окружность: |z| = 1.',
    }
  }
  if (closureError(z, n) > closeTolerance) {
    return {
      kind: 'angle-off',
      message: `z^${n} ещё не равно 1: орбита не замыкается.`,
      repairHint: `Поставь z под углом 2π/${n}: тогда n-й степени хватит ровно на круг.`,
    }
  }
  return {
    kind: 'not-primitive',
    message: 'Орбита замыкается, но обходит меньше n вершин: многоугольник вырожден.',
    repairHint: `Возьми первообразный корень (угол 2π/${n}), а не его кратный.`,
  }
}

export function formatComplex(z: Complex): string {
  const re = Math.abs(z[0]) < 0.005 ? '0.00' : z[0].toFixed(2)
  const imAbs = Math.abs(z[1])
  const imStr = (imAbs < 0.005 ? 0 : imAbs).toFixed(2)
  const sign = z[1] < 0 ? '-' : '+'
  return `${re} ${sign} ${imStr}i`
}
