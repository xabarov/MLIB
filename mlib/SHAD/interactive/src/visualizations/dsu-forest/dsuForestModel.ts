export type DsuLevelId = 'connect-all' | 'spanning-tree' | 'two-groups'

export type EdgeStatus = 'tree' | 'cycle' | null

export type DsuDiagnosisKind = 'idle' | 'success' | 'over-merged' | 'in-progress'

export type DsuDiagnosis = {
  kind: DsuDiagnosisKind
  message: string
  repairHint: string
}

export type DsuLevelConfig = {
  id: DsuLevelId
  n: number
  positions: Array<[number, number]>
  edges: Array<[number, number]>
  /** Target number of connected components. */
  target: number
}

const GRID: Array<[number, number]> = [
  [22, 26],
  [50, 26],
  [78, 26],
  [22, 74],
  [50, 74],
  [78, 74],
]

export const dsuLevels: Record<DsuLevelId, DsuLevelConfig> = {
  // Connect everything into a single component (one redundant edge closes a loop).
  'connect-all': {
    id: 'connect-all',
    n: 6,
    positions: GRID,
    edges: [
      [0, 1],
      [1, 3],
      [0, 3],
      [1, 2],
      [3, 4],
      [4, 5],
    ],
    target: 1,
  },
  // Several loops: build a spanning tree and recognize the redundant cycle edges.
  'spanning-tree': {
    id: 'spanning-tree',
    n: 6,
    positions: GRID,
    edges: [
      [0, 1],
      [1, 2],
      [0, 3],
      [1, 4],
      [2, 5],
      [3, 4],
      [4, 5],
    ],
    target: 1,
  },
  // Two clusters joined by a single bridge: leave exactly two groups, skip the bridge.
  'two-groups': {
    id: 'two-groups',
    n: 6,
    positions: GRID,
    edges: [
      [0, 1],
      [1, 2],
      [3, 4],
      [4, 5],
      [2, 3],
    ],
    target: 2,
  },
}

export function makeParent(n: number): number[] {
  return Array.from({ length: n }, (_, i) => i)
}

export function find(parent: number[], x: number): number {
  let current = x
  while (parent[current] !== current) {
    current = parent[current]
  }
  return current
}

export type UnionResult = { parent: number[]; merged: boolean }

export function union(parent: number[], a: number, b: number): UnionResult {
  const rootA = find(parent, a)
  const rootB = find(parent, b)
  if (rootA === rootB) {
    return { parent, merged: false }
  }
  const next = parent.slice()
  next[rootB] = rootA
  return { parent: next, merged: true }
}

export function componentCount(parent: number[]): number {
  const roots = new Set<number>()
  for (let i = 0; i < parent.length; i += 1) {
    roots.add(find(parent, i))
  }
  return roots.size
}

export function sameComponent(parent: number[], a: number, b: number): boolean {
  return find(parent, a) === find(parent, b)
}

export function dsuLevelSuccess(levelId: DsuLevelId, parent: number[]): boolean {
  return componentCount(parent) === dsuLevels[levelId].target
}

export function diagnoseDsu({
  levelId,
  parent,
  touched,
}: {
  levelId: DsuLevelId
  parent: number[]
  touched: boolean
}): DsuDiagnosis {
  const target = dsuLevels[levelId].target
  const count = componentCount(parent)
  if (!touched) {
    return {
      kind: 'idle',
      message: 'Кликай рёбра: каждое объединяет две компоненты в одну.',
      repairHint: 'Ребро между уже связанными вершинами — цикл, оно ничего не меняет.',
    }
  }
  if (count === target) {
    return {
      kind: 'success',
      message: target === 1 ? 'Всё связано в одну компоненту.' : `Получилось ровно ${target} компоненты.`,
      repairHint: 'Союз непересекающихся множеств собран.',
    }
  }
  if (count < target) {
    return {
      kind: 'over-merged',
      message: `Слишком связали: компонент ${count}, нужно ${target}. Лишнее ребро-мост склеило группы.`,
      repairHint: 'Сбрось уровень и не объединяй вершины из разных групп.',
    }
  }
  return {
    kind: 'in-progress',
    message: `Компонент пока ${count}, нужно ${target}. Соедини ещё.`,
    repairHint: 'Объединяй вершины из разных компонент, пропуская циклы.',
  }
}
