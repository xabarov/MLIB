import { describe, expect, it } from 'vitest'
import {
  cycleNotation,
  cycles,
  identity,
  inversions,
  isSamePermutation,
  parity,
  substitutionLevelSuccess,
  swapImages,
  targetDistance,
} from './substitutionWorkshopModel'

describe('substitutionWorkshopModel', () => {
  it('builds identity and swaps images', () => {
    expect(identity(4)).toEqual([1, 2, 3, 4])
    expect(swapImages([1, 2, 3, 4], 0, 2)).toEqual([3, 2, 1, 4])
  })

  it('computes inversions and parity', () => {
    expect(inversions([2, 1, 3])).toBe(1)
    expect(parity([2, 1, 3])).toBe('odd')
    expect(parity([2, 3, 1])).toBe('even')
  })

  it('extracts cycle notation', () => {
    expect(cycles([2, 3, 1, 4])).toEqual([[1, 2, 3]])
    expect(cycleNotation([2, 1, 4, 3])).toBe('(1 2)(3 4)')
    expect(cycleNotation([1, 2, 3])).toBe('id')
  })

  it('checks level success and target distance', () => {
    expect(isSamePermutation([2, 3, 4, 5, 1], [2, 3, 4, 5, 1])).toBe(true)
    expect(targetDistance([2, 1, 3], [2, 3, 1])).toBe(2)
    expect(
      substitutionLevelSuccess({
        levelId: 'make-cycle',
        permutation: [2, 3, 4, 5, 1],
        swapCount: 4,
      }),
    ).toBe(true)
    expect(
      substitutionLevelSuccess({
        levelId: 'flip-parity',
        permutation: [2, 1, 3, 4, 5],
        swapCount: 1,
      }),
    ).toBe(true)
  })
})
