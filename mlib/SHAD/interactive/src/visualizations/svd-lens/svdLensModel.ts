import {
  eigenPairsSymmetric2x2,
  type Symmetric2x2,
  type Vec2,
} from '../quadratic-lens/quadraticLensModel'

export type { Vec2 }

export type Matrix2x2 = {
  a: number
  b: number
  c: number
  d: number
}

export type Svd2D = {
  sigma1: number
  sigma2: number
  v1: Vec2
  v2: Vec2
  u1: Vec2
  u2: Vec2
  ata: Symmetric2x2
  condition: number
  rank: 0 | 1 | 2
}

export type SvdDiagnosisKind =
  | 'success'
  | 'in-progress'
  | 'wrong-ellipse'
  | 'wrong-directions'
  | 'eigenvalue-trap'
  | 'signed-sigma'
  | 'wrong-rank'
  | 'weak-component-kept'
  | 'pca-axis-off'
  | 'not-centered'

export type SvdDiagnosis = {
  kind: SvdDiagnosisKind
  message: string
  repairHint: string
}

export const svdTolerance = 1e-7
export const svdUiTolerance = 0.08
export const svdSnap = 0.1
export const svdGridLimit = 3

const unitCircleSamples = 96

export const svdTargetMatrix: Matrix2x2 = { a: 1.73, b: -0.5, c: 1, d: 0.87 }
export const svdTrapMatrix: Matrix2x2 = { a: 1, b: 2, c: 0, d: 1 }
export const pcaCloud: Vec2[] = [
  [-2.1, -1.25],
  [-1.7, -1.05],
  [-1.2, -0.58],
  [-0.7, -0.45],
  [-0.2, -0.05],
  [0.35, 0.18],
  [0.8, 0.48],
  [1.15, 0.68],
  [1.55, 0.92],
  [2.05, 1.18],
]

export function snapSvdValue(value: number): number {
  return Math.max(
    -svdGridLimit,
    Math.min(svdGridLimit, Math.round(value / svdSnap) * svdSnap),
  )
}

export function formatSvdNumber(value: number): string {
  return Math.abs(value) < 0.005 ? '0.00' : value.toFixed(2)
}

export function dot(a: Vec2, b: Vec2): number {
  return a[0] * b[0] + a[1] * b[1]
}

export function vectorLength(vector: Vec2): number {
  return Math.hypot(vector[0], vector[1])
}

export function normalize(vector: Vec2): Vec2 {
  const length = vectorLength(vector)
  if (length < svdTolerance) return [1, 0]
  return [vector[0] / length, vector[1] / length]
}

export function signedAxisDistance(a: Vec2, b: Vec2): number {
  const na = normalize(a)
  const nb = normalize(b)
  return Math.min(
    Math.hypot(na[0] - nb[0], na[1] - nb[1]),
    Math.hypot(na[0] + nb[0], na[1] + nb[1]),
  )
}

export function angleToVector(theta: number): Vec2 {
  return [Math.cos(theta), Math.sin(theta)]
}

export function applyMatrix(matrix: Matrix2x2, point: Vec2): Vec2 {
  return [matrix.a * point[0] + matrix.b * point[1], matrix.c * point[0] + matrix.d * point[1]]
}

export function matrixFromColumns(u: Vec2, v: Vec2): Matrix2x2 {
  return { a: u[0], b: v[0], c: u[1], d: v[1] }
}

export function matrixColumns(matrix: Matrix2x2): [Vec2, Vec2] {
  return [
    [matrix.a, matrix.c],
    [matrix.b, matrix.d],
  ]
}

export function determinant(matrix: Matrix2x2): number {
  return matrix.a * matrix.d - matrix.b * matrix.c
}

export function transposeTimesMatrix(matrix: Matrix2x2): Symmetric2x2 {
  return {
    a: matrix.a * matrix.a + matrix.c * matrix.c,
    b: matrix.a * matrix.b + matrix.c * matrix.d,
    c: matrix.b * matrix.b + matrix.d * matrix.d,
  }
}

export function multiplyMatrices(left: Matrix2x2, right: Matrix2x2): Matrix2x2 {
  return {
    a: left.a * right.a + left.b * right.c,
    b: left.a * right.b + left.b * right.d,
    c: left.c * right.a + left.d * right.c,
    d: left.c * right.b + left.d * right.d,
  }
}

export function outerProduct(scale: number, u: Vec2, v: Vec2): Matrix2x2 {
  return {
    a: scale * u[0] * v[0],
    b: scale * u[0] * v[1],
    c: scale * u[1] * v[0],
    d: scale * u[1] * v[1],
  }
}

export function addMatrices(left: Matrix2x2, right: Matrix2x2): Matrix2x2 {
  return {
    a: left.a + right.a,
    b: left.b + right.b,
    c: left.c + right.c,
    d: left.d + right.d,
  }
}

function fallbackOrthogonal(vector: Vec2): Vec2 {
  return [-vector[1], vector[0]]
}

export function svd2x2(matrix: Matrix2x2): Svd2D {
  const ata = transposeTimesMatrix(matrix)
  const eigenPairs = eigenPairsSymmetric2x2(ata).sort((left, right) => right.lambda - left.lambda)
  const sigma1 = Math.sqrt(Math.max(0, eigenPairs[0].lambda))
  const sigma2 = Math.sqrt(Math.max(0, eigenPairs[1].lambda))
  const v1 = normalize(eigenPairs[0].vector)
  const v2 = normalize(fallbackOrthogonal(v1))
  const av1 = applyMatrix(matrix, v1)
  const av2 = applyMatrix(matrix, v2)
  const u1: Vec2 = sigma1 > svdUiTolerance ? normalize(av1) : [1, 0]
  let u2: Vec2 = sigma2 > svdUiTolerance ? normalize(av2) : fallbackOrthogonal(u1)
  if (Math.abs(dot(u1, u2)) > 0.2) {
    u2 = fallbackOrthogonal(u1)
  }
  const rank = sigma1 <= svdUiTolerance ? 0 : sigma2 <= svdUiTolerance ? 1 : 2
  const condition = sigma2 <= svdUiTolerance ? Number.POSITIVE_INFINITY : sigma1 / sigma2

  return {
    sigma1,
    sigma2,
    v1,
    v2,
    u1,
    u2: normalize(u2),
    ata,
    condition,
    rank,
  }
}

export function unitCircleSample(samples = unitCircleSamples): Vec2[] {
  return Array.from({ length: samples + 1 }, (_, index) => {
    const angle = (index / samples) * Math.PI * 2
    return [Math.cos(angle), Math.sin(angle)]
  })
}

export function transformedCircleSample(matrix: Matrix2x2, samples = unitCircleSamples): Vec2[] {
  return unitCircleSample(samples).map((point) => applyMatrix(matrix, point))
}

export function rankKApprox(matrix: Matrix2x2, k: 0 | 1 | 2): Matrix2x2 {
  const svd = svd2x2(matrix)
  if (k === 0) return { a: 0, b: 0, c: 0, d: 0 }
  const first = outerProduct(svd.sigma1, svd.u1, svd.v1)
  if (k === 1) return first
  return addMatrices(first, outerProduct(svd.sigma2, svd.u2, svd.v2))
}

export function frobeniusError(left: Matrix2x2, right: Matrix2x2): number {
  return Math.hypot(left.a - right.a, left.b - right.b, left.c - right.c, left.d - right.d)
}

export function centerPointCloud(points: Vec2[]): Vec2[] {
  if (points.length === 0) return []
  const mean: Vec2 = [
    points.reduce((sum, point) => sum + point[0], 0) / points.length,
    points.reduce((sum, point) => sum + point[1], 0) / points.length,
  ]
  return points.map((point) => [point[0] - mean[0], point[1] - mean[1]])
}

export function covarianceForm(points: Vec2[]): Symmetric2x2 {
  const centered = centerPointCloud(points)
  if (centered.length === 0) return { a: 0, b: 0, c: 0 }
  const scale = 1 / centered.length
  return {
    a: centered.reduce((sum, point) => sum + point[0] * point[0], 0) * scale,
    b: centered.reduce((sum, point) => sum + point[0] * point[1], 0) * scale,
    c: centered.reduce((sum, point) => sum + point[1] * point[1], 0) * scale,
  }
}

export function principalComponent2D(points: Vec2[]): Vec2 {
  return normalize(eigenPairsSymmetric2x2(covarianceForm(points))[0].vector)
}

export function projectPoint(point: Vec2, direction: Vec2): Vec2 {
  const axis = normalize(direction)
  const amount = dot(point, axis)
  return [axis[0] * amount, axis[1] * amount]
}

export function projectionError(points: Vec2[], direction: Vec2): number {
  const axis = normalize(direction)
  return points.reduce((sum, point) => {
    const projected = projectPoint(point, axis)
    return sum + Math.hypot(point[0] - projected[0], point[1] - projected[1]) ** 2
  }, 0)
}

export function retainedVariance(points: Vec2[], direction: Vec2): number {
  const centered = centerPointCloud(points)
  const total = centered.reduce((sum, point) => sum + dot(point, point), 0)
  if (total < svdTolerance) return 1
  const axis = normalize(direction)
  const retained = centered.reduce((sum, point) => sum + dot(point, axis) ** 2, 0)
  return retained / total
}

export function matrixMatchesSvdTarget(matrix: Matrix2x2): boolean {
  const current = svd2x2(matrix)
  const target = svd2x2(svdTargetMatrix)
  return (
    Math.abs(current.sigma1 - target.sigma1) < 0.12 &&
    Math.abs(current.sigma2 - target.sigma2) < 0.12 &&
    signedAxisDistance(current.u1, target.u1) < 0.16
  )
}

export type SingularChoice = 'singular-values' | 'eigenvalues-a' | 'signed-values'

export function svdLevelSuccess({
  levelId,
  matrix,
  rightDirection,
  rightDirectionSecond,
  singularChoice,
  keepSigma2,
  pcaAngle,
  touched,
}: {
  levelId: string
  matrix: Matrix2x2
  rightDirection: Vec2
  rightDirectionSecond: Vec2
  singularChoice: SingularChoice
  keepSigma2: boolean
  pcaAngle: number
  touched: boolean
}): boolean {
  const svd = svd2x2(matrix)
  if (levelId === 'circle-to-ellipse') return touched && matrixMatchesSvdTarget(matrix)
  if (levelId === 'right-directions') {
    return (
      signedAxisDistance(rightDirection, svd.v1) < 0.18 &&
      signedAxisDistance(rightDirectionSecond, svd.v2) < 0.18 &&
      Math.abs(dot(normalize(rightDirection), normalize(rightDirectionSecond))) < 0.18
    )
  }
  if (levelId === 'singular-vs-eigen') return singularChoice === 'singular-values'
  if (levelId === 'rank-one-shadow') return !keepSigma2 && svd.rank >= 1
  if (levelId === 'pca-cloud') {
    return signedAxisDistance(angleToVector(pcaAngle), principalComponent2D(pcaCloud)) < 0.18
  }
  return false
}

export function diagnoseSvdState({
  levelId,
  matrix,
  rightDirection,
  rightDirectionSecond,
  singularChoice,
  keepSigma2,
  pcaAngle,
  touched,
}: {
  levelId: string
  matrix: Matrix2x2
  rightDirection: Vec2
  rightDirectionSecond: Vec2
  singularChoice: SingularChoice
  keepSigma2: boolean
  pcaAngle: number
  touched: boolean
}): SvdDiagnosis {
  const success = svdLevelSuccess({
    levelId,
    matrix,
    rightDirection,
    rightDirectionSecond,
    singularChoice,
    keepSigma2,
    pcaAngle,
    touched,
  })

  if (success) {
    return {
      kind: 'success',
      message: 'SVD-условие уровня выполнено.',
      repairHint: 'Можно переходить дальше.',
    }
  }

  if (!touched && levelId === 'circle-to-ellipse') {
    return {
      kind: 'in-progress',
      message: 'Матрица еще не собрана под целевой эллипс.',
      repairHint: 'Начни с preset lens или настрой столбцы так, чтобы круг стал нужным эллипсом.',
    }
  }

  if (levelId === 'circle-to-ellipse') {
    return {
      kind: 'wrong-ellipse',
      message: 'Круг пока превращается не в тот эллипс.',
      repairHint: 'Сравни sigma и направление длинной полуоси с ghost-эллипсом.',
    }
  }

  if (levelId === 'right-directions') {
    return {
      kind: 'wrong-directions',
      message: 'Входные направления еще не стали полуосями выходного эллипса.',
      repairHint: 'Ищи направления v1 и v2 на входном круге; их образы Av должны лечь на оси эллипса.',
    }
  }

  if (levelId === 'singular-vs-eigen') {
    if (singularChoice === 'eigenvalues-a') {
      return {
        kind: 'eigenvalue-trap',
        message: 'Это собственные значения A, а не сингулярные числа.',
        repairHint: 'Для SVD бери квадратные корни из собственных значений A^T A.',
      }
    }
    return {
      kind: 'signed-sigma',
      message: 'Сингулярные числа не имеют знака.',
      repairHint: 'Sigma - это длины полуосей эллипса, поэтому они неотрицательны.',
    }
  }

  if (levelId === 'rank-one-shadow') {
    return {
      kind: keepSigma2 ? 'wrong-rank' : 'weak-component-kept',
      message: keepSigma2
        ? 'Rank все еще 2: слабая ось не отброшена.'
        : 'Нужно оставить сильную сингулярную ось, а не произвольную координату.',
      repairHint: 'Отключи sigma2 и сохрани направление sigma1.',
    }
  }

  if (levelId === 'pca-cloud') {
    return {
      kind: 'pca-axis-off',
      message: 'Ось PCA еще не совпала с направлением максимальной дисперсии.',
      repairHint: 'Поверни ось вдоль вытянутого облака, а не вдоль координатной сетки.',
    }
  }

  return {
    kind: 'in-progress',
    message: 'Цель уровня еще не достигнута.',
    repairHint: 'Смотри на sigma, оси и ошибку реконструкции.',
  }
}

export function svgPointToSvdCoord({
  clientX,
  clientY,
  rect,
}: {
  clientX: number
  clientY: number
  rect: Pick<DOMRect, 'left' | 'top' | 'width' | 'height'>
}): Vec2 {
  const x = ((clientX - rect.left) / rect.width) * 8 - 4
  const y = 4 - ((clientY - rect.top) / rect.height) * 8
  return [snapSvdValue(x), snapSvdValue(y)]
}
