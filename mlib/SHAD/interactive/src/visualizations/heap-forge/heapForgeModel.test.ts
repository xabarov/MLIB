import { describe, expect, it } from 'vitest'
import {
  diagnoseHeap,
  heapLevels,
  heapViolations,
  isMinHeap,
  leftChild,
  parentIndex,
  rightChild,
  siftDown,
  siftUp,
  swapNodes,
} from './heapForgeModel'

describe('heapForgeModel', () => {
  it('navigates the array-encoded tree', () => {
    expect(parentIndex(3)).toBe(1)
    expect(parentIndex(4)).toBe(1)
    expect(leftChild(1)).toBe(3)
    expect(rightChild(1)).toBe(4)
  })

  it('finds every parent > child violation', () => {
    expect(heapViolations([1, 3, 4, 8, 9])).toEqual([])
    expect(heapViolations([7, 3, 4, 8, 9, 5])).toEqual([
      { parent: 0, child: 1 },
      { parent: 0, child: 2 },
    ])
  })

  it('swaps two nodes without mutating the input', () => {
    const heap = [1, 8, 4, 3]
    const swapped = swapNodes(heap, 1, 3)
    expect(swapped).toEqual([1, 3, 4, 8])
    expect(heap).toEqual([1, 8, 4, 3])
  })

  it('recognizes the fixing swap for each level', () => {
    expect(isMinHeap(swapNodes(heapLevels['fix-one-break'].start, 1, 3))).toBe(true)
    // sift-down must swap with the SMALLER child, not just any child.
    expect(isMinHeap(swapNodes(heapLevels['sift-down'].start, 0, 1))).toBe(true)
    expect(isMinHeap(swapNodes(heapLevels['sift-down'].start, 0, 2))).toBe(false)
  })

  it('restores the heap with sift helpers', () => {
    expect(isMinHeap(siftUp(heapLevels['bubble-up'].start, 7))).toBe(true)
    expect(isMinHeap(siftDown(heapLevels['sift-down'].start, 0))).toBe(true)
  })

  it('diagnoses an untouched broken heap without claiming success', () => {
    const broken = heapLevels['sift-down'].start
    expect(diagnoseHeap({ heap: broken, touched: false }).kind).toBe('idle')
    expect(diagnoseHeap({ heap: broken, touched: true }).kind).toBe('has-violation')
    const fixed = swapNodes(broken, 0, 1)
    expect(diagnoseHeap({ heap: fixed, touched: true }).kind).toBe('success')
  })
})
