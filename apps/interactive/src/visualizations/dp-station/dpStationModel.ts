export type DpLevelId = 'cot-cat' | 'cat-cart' | 'food-gold'

export type DpDiagnosisKind = 'idle' | 'success' | 'not-ready' | 'in-progress'

export type DpDiagnosis = {
  kind: DpDiagnosisKind
  message: string
  repairHint: string
}

export type DpCell = { row: number; col: number }

export type DpLevelConfig = {
  id: DpLevelId
  /** Word along the rows (top to bottom). */
  rowWord: string
  /** Word along the columns (left to right). */
  colWord: string
}

export const dpLevels: Record<DpLevelId, DpLevelConfig> = {
  'cot-cat': { id: 'cot-cat', rowWord: 'COT', colWord: 'CAT' },
  'cat-cart': { id: 'cat-cart', rowWord: 'CAT', colWord: 'CART' },
  'food-gold': { id: 'food-gold', rowWord: 'FOOD', colWord: 'GOLD' },
}

/** Full Levenshtein DP table, sized (m+1) x (n+1). */
export function editTable(rowWord: string, colWord: string): number[][] {
  const m = rowWord.length
  const n = colWord.length
  const table = Array.from({ length: m + 1 }, () => Array(n + 1).fill(0))
  for (let i = 0; i <= m; i += 1) table[i][0] = i
  for (let j = 0; j <= n; j += 1) table[0][j] = j
  for (let i = 1; i <= m; i += 1) {
    for (let j = 1; j <= n; j += 1) {
      table[i][j] =
        rowWord[i - 1] === colWord[j - 1]
          ? table[i - 1][j - 1]
          : 1 + Math.min(table[i - 1][j], table[i][j - 1], table[i - 1][j - 1])
    }
  }
  return table
}

export function editDistance(rowWord: string, colWord: string): number {
  return editTable(rowWord, colWord)[rowWord.length][colWord.length]
}

/** Base case row (i = 0) and column (j = 0) start filled. */
export function initialFilled(m: number, n: number): boolean[][] {
  return Array.from({ length: m + 1 }, (_, i) =>
    Array.from({ length: n + 1 }, (_, j) => i === 0 || j === 0),
  )
}

/** A cell can be computed once its three predecessors are filled. */
export function isReady(filled: boolean[][], i: number, j: number): boolean {
  if (i <= 0 || j <= 0) return false
  if (filled[i][j]) return false
  return filled[i - 1][j] && filled[i][j - 1] && filled[i - 1][j - 1]
}

export function readyCells(filled: boolean[][]): DpCell[] {
  const cells: DpCell[] = []
  for (let i = 1; i < filled.length; i += 1) {
    for (let j = 1; j < filled[i].length; j += 1) {
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

export function dpLevelSuccess(filled: boolean[][]): boolean {
  return allFilled(filled)
}

export function diagnoseDp({
  filled,
  touched,
  lastNotReady,
}: {
  filled: boolean[][]
  touched: boolean
  lastNotReady: boolean
}): DpDiagnosis {
  if (allFilled(filled)) {
    return {
      kind: touched ? 'success' : 'idle',
      message: touched ? 'Таблица заполнена: ответ в правом нижнем углу.' : 'Таблица уже заполнена.',
      repairHint: 'Редакционное расстояние — это число в правом нижнем углу.',
    }
  }
  if (!touched) {
    return {
      kind: 'idle',
      message: 'Заполняй ячейки: каждая зависит от левой, верхней и диагональной соседок.',
      repairHint: 'Доступные клетки подсвечены — у них все три соседки уже посчитаны.',
    }
  }
  if (lastNotReady) {
    return {
      kind: 'not-ready',
      message: 'Эту клетку рано считать: соседки слева, сверху и по диагонали ещё не готовы.',
      repairHint: 'Иди по порядку: заполняй подсвеченные клетки слева направо, сверху вниз.',
    }
  }
  return {
    kind: 'in-progress',
    message: 'Ещё не все клетки посчитаны.',
    repairHint: 'Кликай подсвеченные клетки, у которых готовы все три соседки.',
  }
}
