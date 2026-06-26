export type Vec2 = [number, number]
export type Matrix2 = { a: number; b: number; c: number; d: number }

export type EigenLevelId = 'large-eigen' | 'small-eigen' | 'flip-eigen'

export type EigenDiagnosisKind = 'idle' | 'success' | 'not-aligned' | 'wrong-eigenvalue'

export type EigenDiagnosis = {
  kind: EigenDiagnosisKind
  message: string
  repairHint: string
}

export type EigenLevelConfig = {
  id: EigenLevelId
  matrix: Matrix2
  targetLambda: number
}

export const eigenLevels: Record<EigenLevelId, EigenLevelConfig> = {
  // Symmetric matrix: eigenvectors (1,1) with lambda 3 and (1,-1) with lambda 1.
  'large-eigen': { id: 'large-eigen', matrix: { a: 2, b: 1, c: 1, d: 2 }, targetLambda: 3 },
  'small-eigen': { id: 'small-eigen', matrix: { a: 2, b: 1, c: 1, d: 2 }, targetLambda: 1 },
  // Swap/reflection: eigenvectors (1,1) lambda 1 and (1,-1) lambda -1 (Av flips).
  'flip-eigen': { id: 'flip-eigen', matrix: { a: 0, b: 1, c: 1, d: 0 }, targetLambda: -1 },
}

export const alignTolerance = 0.05
export const lambdaTolerance = 0.18

export function applyMatrix(matrix: Matrix2, v: Vec2): Vec2 {
  return [matrix.a * v[0] + matrix.b * v[1], matrix.c * v[0] + matrix.d * v[1]]
}

export function norm(v: Vec2): number {
  return Math.hypot(v[0], v[1])
}

export function normalize(v: Vec2): Vec2 {
  const length = norm(v)
  if (length < 1e-9) return [1, 0]
  return [v[0] / length, v[1] / length]
}

export function dot(a: Vec2, b: Vec2): number {
  return a[0] * b[0] + a[1] * b[1]
}

/** |sin(angle)| * |Av| via the 2D cross product; zero when Av is parallel to v. */
export function crossMagnitude(v: Vec2, w: Vec2): number {
  return Math.abs(v[0] * w[1] - v[1] * w[0])
}

export type EigenState = {
  unit: Vec2
  image: Vec2
  lambda: number
  alignment: number
}

export function eigenState(matrix: Matrix2, direction: Vec2): EigenState {
  const unit = normalize(direction)
  const image = applyMatrix(matrix, unit)
  return {
    unit,
    image,
    lambda: dot(unit, image), // lambda = v^T A v for a unit eigenvector
    alignment: crossMagnitude(unit, image),
  }
}

export function isAligned(state: EigenState): boolean {
  return state.alignment <= alignTolerance
}

export function eigenLevelSuccess(levelId: EigenLevelId, direction: Vec2): boolean {
  const config = eigenLevels[levelId]
  const state = eigenState(config.matrix, direction)
  return isAligned(state) && Math.abs(state.lambda - config.targetLambda) <= lambdaTolerance
}

export function diagnoseEigen({
  levelId,
  direction,
  touched,
}: {
  levelId: EigenLevelId
  direction: Vec2
  touched: boolean
}): EigenDiagnosis {
  const config = eigenLevels[levelId]
  const state = eigenState(config.matrix, direction)
  if (!touched) {
    return {
      kind: 'idle',
      message: 'Вращай направление v и смотри на A·v: ищем, где они станут параллельны.',
      repairHint: 'Собственный вектор — направление, которое матрица только растягивает.',
    }
  }
  if (eigenLevelSuccess(levelId, direction)) {
    return {
      kind: 'success',
      message: `Собственный вектор найден: A·v = ${state.lambda.toFixed(2)}·v.`,
      repairHint: 'Матрица растягивает это направление, не поворачивая его.',
    }
  }
  if (!isAligned(state)) {
    return {
      kind: 'not-aligned',
      message: `A·v ещё повёрнут относительно v (перекос ${state.alignment.toFixed(2)}).`,
      repairHint: 'Крути v, пока A·v не ляжет на ту же прямую.',
    }
  }
  return {
    kind: 'wrong-eigenvalue',
    message: `Это собственный вектор, но с λ = ${state.lambda.toFixed(2)}, а нужно ${config.targetLambda}.`,
    repairHint: 'Параллельность есть, но не та: поверни к другому собственному направлению.',
  }
}

export function formatEigenNumber(value: number): string {
  return Math.abs(value) < 0.005 ? '0.00' : value.toFixed(2)
}
