export type Edge = [number, number]

export type EulerLevelId = 'bowtie' | 'house' | 'envelope'

export type EulerDiagnosisKind = 'idle' | 'success' | 'stuck' | 'invalid' | 'in-progress'

export type EulerDiagnosis = {
  kind: EulerDiagnosisKind
  message: string
  repairHint: string
}

export type EulerLevelConfig = {
  id: EulerLevelId
  n: number
  positions: Array<[number, number]>
  edges: Edge[]
  kind: 'circuit' | 'path'
}

export const eulerLevels: Record<EulerLevelId, EulerLevelConfig> = {
  // All degrees even: an Eulerian circuit (start = end).
  bowtie: {
    id: 'bowtie',
    n: 5,
    positions: [
      [18, 28],
      [18, 72],
      [50, 50],
      [82, 28],
      [82, 72],
    ],
    edges: [
      [0, 1],
      [1, 2],
      [2, 0],
      [2, 3],
      [3, 4],
      [4, 2],
    ],
    kind: 'circuit',
  },
  // Two odd vertices (2 and 3): an Eulerian path between them.
  house: {
    id: 'house',
    n: 5,
    positions: [
      [25, 80],
      [75, 80],
      [75, 42],
      [25, 42],
      [50, 15],
    ],
    edges: [
      [0, 1],
      [1, 2],
      [2, 3],
      [3, 0],
      [3, 4],
      [4, 2],
    ],
    kind: 'path',
  },
  // Classic envelope: two odd vertices (0 and 1), draw without lifting the pen.
  envelope: {
    id: 'envelope',
    n: 5,
    positions: [
      [20, 82],
      [80, 82],
      [80, 42],
      [20, 42],
      [50, 12],
    ],
    edges: [
      [0, 1],
      [1, 2],
      [2, 3],
      [3, 0],
      [3, 4],
      [4, 2],
      [0, 2],
      [1, 3],
    ],
    kind: 'path',
  },
}

export function degrees(n: number, edges: Edge[]): number[] {
  const d = Array(n).fill(0)
  for (const [a, b] of edges) {
    d[a] += 1
    d[b] += 1
  }
  return d
}

export function oddVertices(n: number, edges: Edge[]): number[] {
  return degrees(n, edges)
    .map((deg, vertex) => (deg % 2 === 1 ? vertex : -1))
    .filter((vertex) => vertex >= 0)
}

/** Valid starting vertices: the odd ones for a path, any for a circuit. */
export function startVertices(config: EulerLevelConfig): number[] {
  const odd = oddVertices(config.n, config.edges)
  return odd.length === 0 ? config.positions.map((_, index) => index) : odd
}

export function edgeBetween(edges: Edge[], used: number[], a: number, b: number): number {
  for (let i = 0; i < edges.length; i += 1) {
    if (used.includes(i)) continue
    const [x, y] = edges[i]
    if ((x === a && y === b) || (x === b && y === a)) return i
  }
  return -1
}

export function availableFrom(edges: Edge[], used: number[], current: number): number[] {
  const result: number[] = []
  for (let i = 0; i < edges.length; i += 1) {
    if (used.includes(i)) continue
    const [a, b] = edges[i]
    if (a === current || b === current) result.push(i)
  }
  return result
}

export function allUsed(edges: Edge[], used: number[]): boolean {
  return used.length === edges.length
}

export function isStuck(edges: Edge[], used: number[], current: number | null): boolean {
  if (current === null) return false
  if (allUsed(edges, used)) return false
  return availableFrom(edges, used, current).length === 0
}

export function eulerLevelSuccess(edges: Edge[], used: number[]): boolean {
  return allUsed(edges, used)
}

export function diagnoseEuler({
  config,
  used,
  current,
  touched,
  lastInvalid,
}: {
  config: EulerLevelConfig
  used: number[]
  current: number | null
  touched: boolean
  lastInvalid: boolean
}): EulerDiagnosis {
  const { edges } = config
  if (allUsed(edges, used)) {
    return {
      kind: touched ? 'success' : 'idle',
      message: 'Все рёбра пройдены ровно по разу: эйлеров маршрут построен.',
      repairHint: 'Рисунок получился, не отрывая руки.',
    }
  }
  if (!touched || current === null) {
    return {
      kind: 'idle',
      message:
        config.kind === 'circuit'
          ? 'Все степени чётные: начни с любой вершины и пройди все рёбра.'
          : 'Две вершины нечётной степени подсвечены: эйлеров путь начинается в одной из них.',
      repairHint: 'Кликни вершину для старта, затем соседние, проходя по рёбрам.',
    }
  }
  if (lastInvalid) {
    return {
      kind: 'invalid',
      message: 'Между этими вершинами нет свободного ребра.',
      repairHint: 'Иди в соседнюю вершину по ещё не пройденному ребру.',
    }
  }
  if (isStuck(edges, used, current)) {
    return {
      kind: 'stuck',
      message: `Тупик: рёбер ${edges.length - used.length} осталось, а ходов нет.`,
      repairHint:
        config.kind === 'path'
          ? 'Сбрось и начни с вершины нечётной степени, не сжигая мосты рано.'
          : 'Сбрось и выбери другой порядок обхода рёбер.',
    }
  }
  return {
    kind: 'in-progress',
    message: `Пройдено рёбер ${used.length} из ${edges.length}.`,
    repairHint: 'Продолжай в соседнюю вершину по свободному ребру.',
  }
}
