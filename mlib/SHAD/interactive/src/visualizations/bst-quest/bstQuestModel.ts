export type BstNode = { value: number; left: number | null; right: number | null }
export type BstTree = BstNode[]

export type BstLevelId = 'find-leaf' | 'find-deep' | 'not-found'

export type BstDiagnosisKind = 'idle' | 'success' | 'wrong-branch' | 'in-progress'

export type BstDiagnosis = {
  kind: BstDiagnosisKind
  message: string
  repairHint: string
}

export type BstLevelConfig = {
  id: BstLevelId
  tree: BstTree
  positions: Array<[number, number]>
  target: number
}

// Shared balanced tree built from inserting 5,3,8,2,4,7,9.
const TREE: BstTree = [
  { value: 5, left: 1, right: 2 },
  { value: 3, left: 3, right: 4 },
  { value: 8, left: 5, right: 6 },
  { value: 2, left: null, right: null },
  { value: 4, left: null, right: null },
  { value: 7, left: null, right: null },
  { value: 9, left: null, right: null },
]

const POSITIONS: Array<[number, number]> = [
  [50, 14],
  [28, 45],
  [72, 45],
  [16, 78],
  [40, 78],
  [60, 78],
  [84, 78],
]

export const bstLevels: Record<BstLevelId, BstLevelConfig> = {
  'find-leaf': { id: 'find-leaf', tree: TREE, positions: POSITIONS, target: 7 },
  'find-deep': { id: 'find-deep', tree: TREE, positions: POSITIONS, target: 2 },
  'not-found': { id: 'not-found', tree: TREE, positions: POSITIONS, target: 6 },
}

/** The BST-correct child index to visit next, or null at a terminal node. */
export function correctChild(tree: BstTree, index: number, target: number): number | null {
  const node = tree[index]
  if (target === node.value) return null
  return target < node.value ? node.left : node.right
}

export type SearchOutcome = {
  path: number[]
  terminal: number
  found: boolean
}

export function bstSearch(tree: BstTree, target: number): SearchOutcome {
  const path: number[] = []
  let current = 0
  for (let guard = 0; guard < tree.length + 1; guard += 1) {
    path.push(current)
    if (tree[current].value === target) {
      return { path, terminal: current, found: true }
    }
    const next = correctChild(tree, current, target)
    if (next === null) {
      return { path, terminal: current, found: false }
    }
    current = next
  }
  return { path, terminal: current, found: tree[current].value === target }
}

/** Children that exist and can be clicked from a node. */
export function childrenOf(tree: BstTree, index: number): number[] {
  const node = tree[index]
  return [node.left, node.right].filter((child): child is number => child !== null)
}

export function bstLevelSuccess(levelId: BstLevelId, current: number): boolean {
  const config = bstLevels[levelId]
  return current === bstSearch(config.tree, config.target).terminal
}

export function diagnoseBst({
  levelId,
  current,
  touched,
  lastWrong,
}: {
  levelId: BstLevelId
  current: number
  touched: boolean
  lastWrong: boolean
}): BstDiagnosis {
  const config = bstLevels[levelId]
  const outcome = bstSearch(config.tree, config.target)
  if (current === outcome.terminal) {
    return {
      kind: touched ? 'success' : 'idle',
      message: outcome.found
        ? `Число ${config.target} найдено за ${outcome.path.length} шага(ов).`
        : `Лист достигнут: ${config.target} в дереве нет, поиск закончился здесь.`,
      repairHint: 'BST-поиск идёт по сравнениям: меньше - влево, больше - вправо.',
    }
  }
  if (!touched) {
    return {
      kind: 'idle',
      message: `Найди ${config.target}: на каждом узле иди влево, если число меньше, и вправо, если больше.`,
      repairHint: 'Кликай ребёнка в нужную сторону по сравнению с узлом.',
    }
  }
  if (lastWrong) {
    return {
      kind: 'wrong-branch',
      message: 'Не та ветка: сравни цель с числом в узле и выбери верное направление.',
      repairHint: `${config.target} меньше - влево, больше - вправо.`,
    }
  }
  return {
    kind: 'in-progress',
    message: `Спускайся к ${config.target} по сравнениям.`,
    repairHint: 'Меньше текущего узла - левый ребёнок, больше - правый.',
  }
}
