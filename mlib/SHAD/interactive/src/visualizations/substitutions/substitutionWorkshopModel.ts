export type Permutation = number[]

export type SubstitutionLevelSpec = {
  id: string
  size: number
  start: Permutation
  target?: Permutation
  maxSwaps?: number
  requiredParity?: 'even' | 'odd'
}

export const substitutionLevels: Record<string, SubstitutionLevelSpec> = {
  'make-cycle': {
    id: 'make-cycle',
    size: 5,
    start: [1, 2, 3, 4, 5],
    target: [2, 3, 4, 5, 1],
    maxSwaps: 4,
  },
  'flip-parity': {
    id: 'flip-parity',
    size: 5,
    start: [1, 2, 3, 4, 5],
    requiredParity: 'odd',
    maxSwaps: 1,
  },
  'two-cycles': {
    id: 'two-cycles',
    size: 6,
    start: [1, 2, 3, 4, 5, 6],
    target: [2, 1, 4, 3, 6, 5],
    maxSwaps: 3,
  },
  repair: {
    id: 'repair',
    size: 5,
    start: [2, 1, 3, 5, 4],
    target: [2, 3, 4, 5, 1],
    maxSwaps: 3,
  },
}

export function identity(size: number): Permutation {
  return Array.from({ length: size }, (_, index) => index + 1)
}

export function swapImages(permutation: Permutation, a: number, b: number): Permutation {
  if (a === b) return permutation
  const next = [...permutation]
  const tmp = next[a]
  next[a] = next[b]
  next[b] = tmp
  return next
}

export function isSamePermutation(a: Permutation, b: Permutation): boolean {
  return a.length === b.length && a.every((value, index) => value === b[index])
}

export function inversions(permutation: Permutation): number {
  let count = 0
  for (let i = 0; i < permutation.length; i += 1) {
    for (let j = i + 1; j < permutation.length; j += 1) {
      if (permutation[i] > permutation[j]) count += 1
    }
  }
  return count
}

export function parity(permutation: Permutation): 'even' | 'odd' {
  return inversions(permutation) % 2 === 0 ? 'even' : 'odd'
}

export function cycles(permutation: Permutation): number[][] {
  const seen = new Set<number>()
  const result: number[][] = []

  for (let start = 1; start <= permutation.length; start += 1) {
    if (seen.has(start)) continue
    const cycle: number[] = []
    let current = start
    while (!seen.has(current)) {
      seen.add(current)
      cycle.push(current)
      current = permutation[current - 1]
    }
    if (cycle.length > 1) result.push(cycle)
  }

  return result
}

export function cycleNotation(permutation: Permutation): string {
  const nonTrivial = cycles(permutation)
  if (nonTrivial.length === 0) return 'id'
  return nonTrivial.map((cycle) => `(${cycle.join(' ')})`).join('')
}

export function substitutionLevelSuccess({
  levelId,
  permutation,
  swapCount,
}: {
  levelId: string
  permutation: Permutation
  swapCount: number
}): boolean {
  const level = substitutionLevels[levelId]
  if (!level) return false
  if (level.maxSwaps !== undefined && swapCount > level.maxSwaps) return false
  if (level.target && !isSamePermutation(permutation, level.target)) return false
  if (level.requiredParity && parity(permutation) !== level.requiredParity) return false
  return Boolean(level.target || level.requiredParity)
}

export function targetDistance(permutation: Permutation, target?: Permutation): number {
  if (!target) return 0
  return permutation.reduce((count, value, index) => count + (target[index] === value ? 0 : 1), 0)
}
