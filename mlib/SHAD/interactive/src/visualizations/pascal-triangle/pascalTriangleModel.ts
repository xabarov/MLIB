export type PascalLevelId = 'triangle-5' | 'triangle-6' | 'triangle-7'

export type PascalDiagnosisKind = 'idle' | 'success' | 'not-ready' | 'in-progress'

export type PascalDiagnosis = {
  kind: PascalDiagnosisKind
  message: string
  repairHint: string
}

export type PascalCell = { row: number; col: number }

export type PascalLevelConfig = {
  id: PascalLevelId
  /** Number of triangle rows (indices 0..rows-1). */
  rows: number
}

export const pascalLevels: Record<PascalLevelId, PascalLevelConfig> = {
  'triangle-5': { id: 'triangle-5', rows: 5 },
  'triangle-6': { id: 'triangle-6', rows: 6 },
  'triangle-7': { id: 'triangle-7', rows: 7 },
}

/** Pascal's triangle: row i has i+1 binomial coefficients C(i, j). */
export function buildPascalTable(rows: number): number[][] {
  const table: number[][] = []
  for (let i = 0; i < rows; i += 1) {
    const row: number[] = []
    for (let j = 0; j <= i; j += 1) {
      row.push(j === 0 || j === i ? 1 : table[i - 1][j - 1] + table[i - 1][j])
    }
    table.push(row)
  }
  return table
}

/** Sum of row i equals 2^i. */
export function rowSum(table: number[][], i: number): number {
  return table[i].reduce((sum, value) => sum + value, 0)
}

/** The edges of the triangle (j = 0 and j = i) start filled with 1. */
export function initialFilled(rows: number): boolean[][] {
  const filled: boolean[][] = []
  for (let i = 0; i < rows; i += 1) {
    const row: boolean[] = []
    for (let j = 0; j <= i; j += 1) row.push(j === 0 || j === i)
    filled.push(row)
  }
  return filled
}

/** An interior cell can be computed once both parents above it are filled. */
export function isReady(filled: boolean[][], i: number, j: number): boolean {
  if (j <= 0 || j >= i) return false
  if (filled[i][j]) return false
  return filled[i - 1][j - 1] && filled[i - 1][j]
}

export function readyCells(filled: boolean[][]): PascalCell[] {
  const cells: PascalCell[] = []
  for (let i = 2; i < filled.length; i += 1) {
    for (let j = 1; j < i; j += 1) {
      if (isReady(filled, i, j)) cells.push({ row: i, col: j })
    }
  }
  return cells
}

export function fillCell(filled: boolean[][], i: number, j: number): boolean[][] {
  const next = filled.map((row) => row.slice())
  next[i][j] = true
  return next
}

export function allFilled(filled: boolean[][]): boolean {
  return filled.every((row) => row.every((cell) => cell))
}

export function pascalLevelSuccess(filled: boolean[][]): boolean {
  return allFilled(filled)
}

export function diagnosePascal({
  filled,
  touched,
  lastNotReady,
}: {
  filled: boolean[][]
  touched: boolean
  lastNotReady: boolean
}): PascalDiagnosis {
  if (allFilled(filled)) {
    return {
      kind: touched ? 'success' : 'idle',
      message: touched
        ? 'Треугольник собран: каждая клетка — сумма двух соседок сверху.'
        : 'Треугольник уже заполнен.',
      repairHint: 'Это и есть биномиальные коэффициенты C(n, k).',
    }
  }
  if (!touched) {
    return {
      kind: 'idle',
      message: 'Заполняй внутренние клетки: каждая равна сумме двух клеток над ней.',
      repairHint: 'Подсвечены клетки, у которых обе верхние соседки уже посчитаны.',
    }
  }
  if (lastNotReady) {
    return {
      kind: 'not-ready',
      message: 'Эту клетку рано считать: одна из верхних соседок ещё не готова.',
      repairHint: 'Иди по строкам сверху вниз: сначала заполни строку выше.',
    }
  }
  return {
    kind: 'in-progress',
    message: 'Ещё не все клетки посчитаны.',
    repairHint: 'Кликай подсвеченные клетки: сумма двух соседок сверху.',
  }
}
