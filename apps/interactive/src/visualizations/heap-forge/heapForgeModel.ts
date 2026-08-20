export type Heap = number[]

export type HeapLevelId = 'fix-one-break' | 'bubble-up' | 'sift-down'

export type HeapViolation = { parent: number; child: number }

export type HeapDiagnosisKind = 'idle' | 'success' | 'has-violation'

export type HeapDiagnosis = {
  kind: HeapDiagnosisKind
  message: string
  repairHint: string
  violations: HeapViolation[]
}

export type HeapLevelConfig = {
  id: HeapLevelId
  start: Heap
  /** Index highlighted as the freshly added / moved node, if any. */
  focusIndex?: number
}

export const heapLevels: Record<HeapLevelId, HeapLevelConfig> = {
  // A valid min-heap with one out-of-place pair (indices 1 and 3 swapped).
  'fix-one-break': {
    id: 'fix-one-break',
    start: [1, 8, 4, 3, 9, 5, 7],
  },
  // A valid heap with a small value appended at the end: bubble it up.
  'bubble-up': {
    id: 'bubble-up',
    start: [1, 3, 4, 8, 9, 5, 7, 2],
    focusIndex: 7,
  },
  // After extract-min the last leaf sits at the root: sift it down.
  'sift-down': {
    id: 'sift-down',
    start: [7, 3, 4, 8, 9, 5],
    focusIndex: 0,
  },
}

export function parentIndex(index: number): number {
  return Math.floor((index - 1) / 2)
}

export function leftChild(index: number): number {
  return 2 * index + 1
}

export function rightChild(index: number): number {
  return 2 * index + 2
}

/** All parent->child pairs that break the min-heap order (parent > child). */
export function heapViolations(heap: Heap): HeapViolation[] {
  const violations: HeapViolation[] = []
  for (let i = 1; i < heap.length; i += 1) {
    const parent = parentIndex(i)
    if (heap[parent] > heap[i]) {
      violations.push({ parent, child: i })
    }
  }
  return violations
}

export function isMinHeap(heap: Heap): boolean {
  return heapViolations(heap).length === 0
}

export function swapNodes(heap: Heap, i: number, j: number): Heap {
  const next = heap.slice()
  ;[next[i], next[j]] = [next[j], next[i]]
  return next
}

/** Bubble the node at `index` up to its correct spot (used by the snap helper). */
export function siftUp(heap: Heap, index: number): Heap {
  let current = index
  let next = heap.slice()
  while (current > 0) {
    const parent = parentIndex(current)
    if (next[parent] <= next[current]) break
    next = swapNodes(next, parent, current)
    current = parent
  }
  return next
}

/** Push the node at `index` down past its smaller child (used by the snap helper). */
export function siftDown(heap: Heap, index: number): Heap {
  let current = index
  let next = heap.slice()
  const size = next.length
  for (;;) {
    const left = leftChild(current)
    const right = rightChild(current)
    let smallest = current
    if (left < size && next[left] < next[smallest]) smallest = left
    if (right < size && next[right] < next[smallest]) smallest = right
    if (smallest === current) break
    next = swapNodes(next, current, smallest)
    current = smallest
  }
  return next
}

export function heapLevelSuccess(heap: Heap): boolean {
  return isMinHeap(heap)
}

export function diagnoseHeap({
  heap,
  touched,
}: {
  heap: Heap
  touched: boolean
}): HeapDiagnosis {
  const violations = heapViolations(heap)
  if (violations.length === 0) {
    return {
      kind: touched ? 'success' : 'idle',
      message: touched ? 'Куча корректна: каждый родитель не больше детей.' : 'Куча уже корректна.',
      repairHint: 'Инвариант min-heap восстановлен.',
      violations,
    }
  }
  if (!touched) {
    return {
      kind: 'idle',
      message: `Куча сломана: ${violations.length} нарушени(е/я) parent > child.`,
      repairHint: 'Меняй местами узлы, чтобы родитель стал не больше детей.',
      violations,
    }
  }
  const first = violations[0]
  return {
    kind: 'has-violation',
    message: `Нарушение: узел ${heap[first.parent]} больше потомка ${heap[first.child]}.`,
    repairHint: 'Подними меньшего ребёнка к родителю обменом по красному ребру.',
    violations,
  }
}

export function formatHeapValue(value: number): string {
  return String(value)
}
