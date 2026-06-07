export type Vec2 = [number, number]
export type Vec3 = [number, number, number]

export type Matrix2x2 = {
  a: number
  b: number
  c: number
  d: number
}

export type Symmetric2x2 = {
  a: number
  b: number
  c: number
}

export type OrthogonalDiagnosisKind =
  | 'ready'
  | 'zero-vector'
  | 'dependent'
  | 'not-orthogonal'
  | 'not-normalized'
  | 'not-orthogonal-operator'
  | 'reflection-vs-rotation'

export type OrthogonalDiagnosis = {
  kind: OrthogonalDiagnosisKind
  message: string
  repairHint: string
}

export type GramSchmidtResult2 = {
  orthonormal: Vec2[]
  residuals: Vec2[]
  dependentIndex: number | null
}

export type GramSchmidtResult3 = {
  orthonormal: Vec3[]
  residuals: Vec3[]
  dependentIndex: number | null
}

export const orthogonalTolerance = 1e-7
export const orthogonalUiTolerance = 0.06
export const orthogonalSnap = 0.1
export const orthogonalGridLimit = 3

export const lineDirection: Vec2 = [1, 0]
export const rawGramVectors: [Vec2, Vec2] = [
  [1.45, 0.65],
  [0.6, 1.75],
]
export const targetRotation: Matrix2x2 = { a: 0, b: -1, c: 1, d: 0 }
export const shearTrapMatrix: Matrix2x2 = { a: 1, b: 1, c: 0, d: 1 }

export function snapOrthogonalValue(value: number): number {
  return Math.max(
    -orthogonalGridLimit,
    Math.min(orthogonalGridLimit, Math.round(value / orthogonalSnap) * orthogonalSnap),
  )
}

export function formatOrthogonalNumber(value: number): string {
  return Math.abs(value) < 0.005 ? '0.00' : value.toFixed(2)
}

export function dot2(a: Vec2, b: Vec2): number {
  return a[0] * b[0] + a[1] * b[1]
}

export function dot3(a: Vec3, b: Vec3): number {
  return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}

export function norm2(vector: Vec2): number {
  return Math.hypot(vector[0], vector[1])
}

export function norm3(vector: Vec3): number {
  return Math.hypot(vector[0], vector[1], vector[2])
}

export function normalize2(vector: Vec2): Vec2 {
  const length = norm2(vector)
  if (length < orthogonalTolerance) return [Number.NaN, Number.NaN]
  return [vector[0] / length, vector[1] / length]
}

export function normalize3(vector: Vec3): Vec3 {
  const length = norm3(vector)
  if (length < orthogonalTolerance) return [Number.NaN, Number.NaN, Number.NaN]
  return [vector[0] / length, vector[1] / length, vector[2] / length]
}

export function safeNormalize2(vector: Vec2, fallback: Vec2 = [1, 0]): Vec2 {
  const length = norm2(vector)
  if (length < orthogonalTolerance) return fallback
  return [vector[0] / length, vector[1] / length]
}

export function subtract2(a: Vec2, b: Vec2): Vec2 {
  return [a[0] - b[0], a[1] - b[1]]
}

export function subtract3(a: Vec3, b: Vec3): Vec3 {
  return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
}

export function scale2(vector: Vec2, scale: number): Vec2 {
  return [vector[0] * scale, vector[1] * scale]
}

export function scale3(vector: Vec3, scale: number): Vec3 {
  return [vector[0] * scale, vector[1] * scale, vector[2] * scale]
}

export function projectOntoLine2(point: Vec2, direction: Vec2): Vec2 {
  const denominator = dot2(direction, direction)
  if (denominator < orthogonalTolerance) return [Number.NaN, Number.NaN]
  return scale2(direction, dot2(point, direction) / denominator)
}

export function projectOntoPlane3(point: Vec3, basisA: Vec3, basisB: Vec3): Vec3 {
  const basis = gramSchmidt3([basisA, basisB]).orthonormal
  if (basis.length === 0) return [Number.NaN, Number.NaN, Number.NaN]
  return basis.reduce<Vec3>(
    (sum, vector) => {
      const projection = scale3(vector, dot3(point, vector))
      return [sum[0] + projection[0], sum[1] + projection[1], sum[2] + projection[2]]
    },
    [0, 0, 0],
  )
}

export function residual2(point: Vec2, direction: Vec2): Vec2 {
  return subtract2(point, projectOntoLine2(point, direction))
}

export function residual3(point: Vec3, basis: Vec3[]): Vec3 {
  const orthonormal = gramSchmidt3(basis).orthonormal
  const projection = orthonormal.reduce<Vec3>(
    (sum, vector) => {
      const part = scale3(vector, dot3(point, vector))
      return [sum[0] + part[0], sum[1] + part[1], sum[2] + part[2]]
    },
    [0, 0, 0],
  )
  return subtract3(point, projection)
}

export function angleBetween2(a: Vec2, b: Vec2): number {
  const denominator = norm2(a) * norm2(b)
  if (denominator < orthogonalTolerance) return Number.NaN
  const cosine = Math.max(-1, Math.min(1, dot2(a, b) / denominator))
  return Math.acos(cosine)
}

export function signedAxisDistance(a: Vec2, b: Vec2): number {
  const na = safeNormalize2(a)
  const nb = safeNormalize2(b)
  return Math.min(Math.hypot(na[0] - nb[0], na[1] - nb[1]), Math.hypot(na[0] + nb[0], na[1] + nb[1]))
}

export function gramSchmidt2(vectors: Vec2[]): GramSchmidtResult2 {
  const orthonormal: Vec2[] = []
  const residuals: Vec2[] = []
  let dependentIndex: number | null = null

  vectors.forEach((vector, index) => {
    let residual = vector
    for (const basis of orthonormal) {
      residual = subtract2(residual, scale2(basis, dot2(vector, basis)))
    }
    residuals.push(residual)
    const length = norm2(residual)
    if (length < orthogonalUiTolerance) {
      if (dependentIndex === null) dependentIndex = index
      return
    }
    orthonormal.push(scale2(residual, 1 / length))
  })

  return { orthonormal, residuals, dependentIndex }
}

export function gramSchmidt3(vectors: Vec3[]): GramSchmidtResult3 {
  const orthonormal: Vec3[] = []
  const residuals: Vec3[] = []
  let dependentIndex: number | null = null

  vectors.forEach((vector, index) => {
    let residual = vector
    for (const basis of orthonormal) {
      residual = subtract3(residual, scale3(basis, dot3(vector, basis)))
    }
    residuals.push(residual)
    const length = norm3(residual)
    if (length < orthogonalUiTolerance) {
      if (dependentIndex === null) dependentIndex = index
      return
    }
    orthonormal.push(scale3(residual, 1 / length))
  })

  return { orthonormal, residuals, dependentIndex }
}

export function isOrthonormal2(vectors: Vec2[]): boolean {
  return (
    vectors.length > 0 &&
    vectors.every((vector) => Math.abs(norm2(vector) - 1) < orthogonalUiTolerance) &&
    vectors.every((vector, index) =>
      vectors.slice(index + 1).every((other) => Math.abs(dot2(vector, other)) < orthogonalUiTolerance),
    )
  )
}

export function isOrthonormal3(vectors: Vec3[]): boolean {
  return (
    vectors.length > 0 &&
    vectors.every((vector) => Math.abs(norm3(vector) - 1) < orthogonalUiTolerance) &&
    vectors.every((vector, index) =>
      vectors.slice(index + 1).every((other) => Math.abs(dot3(vector, other)) < orthogonalUiTolerance),
    )
  )
}

export function matrixColumns(matrix: Matrix2x2): [Vec2, Vec2] {
  return [
    [matrix.a, matrix.c],
    [matrix.b, matrix.d],
  ]
}

export function transposeTimesMatrix2(matrix: Matrix2x2): Symmetric2x2 {
  return {
    a: matrix.a * matrix.a + matrix.c * matrix.c,
    b: matrix.a * matrix.b + matrix.c * matrix.d,
    c: matrix.b * matrix.b + matrix.d * matrix.d,
  }
}

export function determinant2(matrix: Matrix2x2): number {
  return matrix.a * matrix.d - matrix.b * matrix.c
}

export function isOrthogonalMatrix2(matrix: Matrix2x2): boolean {
  const qtq = transposeTimesMatrix2(matrix)
  return (
    Math.abs(qtq.a - 1) < orthogonalUiTolerance &&
    Math.abs(qtq.b) < orthogonalUiTolerance &&
    Math.abs(qtq.c - 1) < orthogonalUiTolerance
  )
}

export function applyMatrix2(matrix: Matrix2x2, point: Vec2): Vec2 {
  return [matrix.a * point[0] + matrix.b * point[1], matrix.c * point[0] + matrix.d * point[1]]
}

export function orthogonalOperatorDiagnosis(
  matrix: Matrix2x2,
  options: { requireRotation?: boolean } = {},
): OrthogonalDiagnosis {
  const columns = matrixColumns(matrix)
  if (columns.some((column) => norm2(column) < orthogonalUiTolerance)) {
    return {
      kind: 'zero-vector',
      message: 'Один из столбцов почти нулевой: оператор теряет направление.',
      repairHint: 'Верни оба образа базисных векторов ненулевыми.',
    }
  }
  const qtq = transposeTimesMatrix2(matrix)
  if (!isOrthogonalMatrix2(matrix)) {
    return {
      kind: 'not-orthogonal-operator',
      message: 'Это не ортогональный оператор: Q^T Q еще не равно I.',
      repairHint: 'Сделай столбцы единичными и взаимно перпендикулярными.',
    }
  }
  if (options.requireRotation && determinant2(matrix) < 0) {
    return {
      kind: 'reflection-vs-rotation',
      message: 'Длины и углы сохранены, но это отражение: det Q = -1.',
      repairHint: 'Для чистого поворота нужен det Q = 1.',
    }
  }
  return {
    kind: 'ready',
    message: `Оператор сохраняет скалярное произведение: Q^T Q = (${formatOrthogonalNumber(qtq.a)}, ${formatOrthogonalNumber(qtq.b)}, ${formatOrthogonalNumber(qtq.c)}).`,
    repairHint: 'Теперь круг остается кругом, а прямой угол остается прямым.',
  }
}

export function orthogonalPairDiagnosis(a: Vec2, b: Vec2): OrthogonalDiagnosis {
  if (norm2(a) < orthogonalUiTolerance || norm2(b) < orthogonalUiTolerance) {
    return {
      kind: 'zero-vector',
      message: 'Один из векторов почти нулевой: направление не задано.',
      repairHint: 'Сначала сделай оба вектора заметной длины.',
    }
  }
  if (Math.abs(determinant2({ a: a[0], b: b[0], c: a[1], d: b[1] })) < orthogonalUiTolerance) {
    return {
      kind: 'dependent',
      message: 'Векторы схлопнулись в одну прямую.',
      repairHint: 'Оставь площадь параллелограмма заметной.',
    }
  }
  if (Math.abs(dot2(a, b)) > orthogonalUiTolerance) {
    return {
      kind: 'not-orthogonal',
      message: `Векторы независимы, но dot = ${formatOrthogonalNumber(dot2(a, b))}, а нужно 0.`,
      repairHint: 'Поверни один вектор до прямого угла.',
    }
  }
  return {
    kind: 'ready',
    message: 'Векторы ненулевые, независимые и ортогональные.',
    repairHint: 'Теперь их можно нормировать и получить ортонормированный базис.',
  }
}

export function projectionDiagnosis(point: Vec2, projection: Vec2, direction: Vec2): OrthogonalDiagnosis {
  if (norm2(direction) < orthogonalUiTolerance) {
    return {
      kind: 'zero-vector',
      message: 'У прямой нет направления.',
      repairHint: 'Сначала задай ненулевое направление прямой.',
    }
  }
  const residual = subtract2(point, projection)
  const offLine = Math.abs(direction[0] * projection[1] - direction[1] * projection[0])
  if (offLine > orthogonalUiTolerance) {
    return {
      kind: 'not-orthogonal',
      message: 'Тень должна лежать на прямой.',
      repairHint: 'Передвинь projection point обратно на линию.',
    }
  }
  if (Math.abs(dot2(residual, direction)) > orthogonalUiTolerance) {
    return {
      kind: 'not-orthogonal',
      message: `Остаток еще не перпендикулярен: dot = ${formatOrthogonalNumber(dot2(residual, direction))}.`,
      repairHint: 'Двигай тень вдоль прямой, пока остаток не станет под прямым углом.',
    }
  }
  return {
    kind: 'ready',
    message: 'Тень найдена: x = projection + residual, а residual перпендикулярен прямой.',
    repairHint: 'Это и есть ортогональное разложение.',
  }
}
