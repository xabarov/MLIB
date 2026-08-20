export type Matrix = number[][] // 3 rows x 4 cols (augmented [A | b])

export type GaussLevelId = 'forward' | 'need-swap' | 'fractions'

export type GaussDiagnosisKind = 'idle' | 'success' | 'pivot-zero' | 'in-progress'

export type GaussDiagnosis = {
  kind: GaussDiagnosisKind
  message: string
  repairHint: string
}

export type EliminableCell = { row: number; col: number }

export type GaussLevelConfig = {
  id: GaussLevelId
  start: Matrix
}

export const ROWS = 3
export const COLS = 4
export const GAUSS_TOL = 1e-7

export const gaussLevels: Record<GaussLevelId, GaussLevelConfig> = {
  forward: {
    id: 'forward',
    start: [
      [1, 1, 1, 6],
      [1, 2, 3, 14],
      [1, 4, 9, 36],
    ],
  },
  'need-swap': {
    id: 'need-swap',
    start: [
      [0, 2, 1, 4],
      [1, 1, 1, 6],
      [2, 1, -1, 1],
    ],
  },
  fractions: {
    id: 'fractions',
    start: [
      [2, 1, -1, 8],
      [-3, -1, 2, -11],
      [-2, 1, 2, -3],
    ],
  },
}

function cloneMatrix(matrix: Matrix): Matrix {
  return matrix.map((row) => row.slice())
}

/** A pivot row j is ready when everything left of column j is already zero. */
export function isPivotReady(matrix: Matrix, j: number): boolean {
  if (Math.abs(matrix[j][j]) <= GAUSS_TOL) return false
  for (let k = 0; k < j; k += 1) {
    if (Math.abs(matrix[j][k]) > GAUSS_TOL) return false
  }
  return true
}

/**
 * A below-diagonal entry can be eliminated only with a ready pivot, which keeps
 * the order Gaussian and never re-introduces a cleared zero.
 */
export function canEliminate(matrix: Matrix, i: number, j: number): boolean {
  if (i <= j) return false
  if (Math.abs(matrix[i][j]) <= GAUSS_TOL) return false
  return isPivotReady(matrix, j)
}

export function eliminableCells(matrix: Matrix): EliminableCell[] {
  const cells: EliminableCell[] = []
  for (let i = 1; i < ROWS; i += 1) {
    for (let j = 0; j < i; j += 1) {
      if (canEliminate(matrix, i, j)) cells.push({ row: i, col: j })
    }
  }
  return cells
}

export function eliminate(matrix: Matrix, i: number, j: number): Matrix {
  const next = cloneMatrix(matrix)
  const multiplier = next[i][j] / next[j][j]
  for (let k = 0; k < COLS; k += 1) {
    next[i][k] -= multiplier * next[j][k]
  }
  next[i][j] = 0 // guard against floating dust on the eliminated entry
  return next
}

export function swapRows(matrix: Matrix, i: number, k: number): Matrix {
  const next = cloneMatrix(matrix)
  ;[next[i], next[k]] = [next[k], next[i]]
  return next
}

export function isUpperTriangular(matrix: Matrix): boolean {
  for (let i = 1; i < ROWS; i += 1) {
    for (let j = 0; j < i; j += 1) {
      if (Math.abs(matrix[i][j]) > GAUSS_TOL) return false
    }
  }
  return true
}

/** Back-substitution solution once the matrix is upper triangular. */
export function backSubstitution(matrix: Matrix): number[] | null {
  const x = [0, 0, 0]
  for (let i = ROWS - 1; i >= 0; i -= 1) {
    if (Math.abs(matrix[i][i]) <= GAUSS_TOL) return null
    let sum = matrix[i][COLS - 1]
    for (let j = i + 1; j < ROWS; j += 1) {
      sum -= matrix[i][j] * x[j]
    }
    x[i] = sum / matrix[i][i]
  }
  return x
}

export function gaussLevelSuccess(matrix: Matrix): boolean {
  return isUpperTriangular(matrix)
}

export function diagnoseGauss({
  matrix,
  touched,
}: {
  matrix: Matrix
  touched: boolean
}): GaussDiagnosis {
  if (isUpperTriangular(matrix)) {
    return {
      kind: touched ? 'success' : 'idle',
      message: touched
        ? 'Ступенчатый вид получен: под диагональю одни нули.'
        : 'Матрица уже в ступенчатом виде.',
      repairHint: 'Решение читается обратным ходом снизу вверх.',
    }
  }
  if (!touched) {
    return {
      kind: 'idle',
      message: 'Обнуляй элементы под диагональю, чтобы привести систему к ступенчатому виду.',
      repairHint: 'Кликни подсвеченный элемент — он вычтется через опорную строку.',
    }
  }
  if (eliminableCells(matrix).length === 0) {
    return {
      kind: 'pivot-zero',
      message: 'Опорный элемент на диагонали равен нулю: занулять нечем.',
      repairHint: 'Поменяй строки местами, чтобы под опорой встало ненулевое число.',
    }
  }
  return {
    kind: 'in-progress',
    message: 'Под диагональю ещё остались ненулевые элементы.',
    repairHint: 'Обнули подсвеченный элемент опорной строкой.',
  }
}

export function formatGaussNumber(value: number): string {
  if (Math.abs(value) < 0.005) return '0'
  const rounded = Math.round(value)
  return Math.abs(value - rounded) < 0.005 ? String(rounded) : value.toFixed(2)
}
