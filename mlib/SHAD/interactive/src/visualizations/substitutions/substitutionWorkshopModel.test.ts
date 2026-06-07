import { describe, expect, it } from 'vitest'
import {
  cycleNotation,
  cycles,
  diagnoseSubstitutionState,
  identity,
  inversions,
  isSamePermutation,
  mismatchPositions,
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

  it('diagnoses target mismatches and near-target repair hints', () => {
    expect(
      diagnoseSubstitutionState({
        levelId: 'make-cycle',
        permutation: [1, 2, 3, 4, 5],
        swapCount: 0,
      }).kind,
    ).toBe('in-progress')

    expect(mismatchPositions([2, 1, 4, 5, 3], [2, 3, 4, 5, 1])).toEqual([2, 5])

    const diagnosis = diagnoseSubstitutionState({
      levelId: 'repair',
      permutation: [2, 1, 4, 5, 3],
      swapCount: 1,
    })

    expect(diagnosis.kind).toBe('near-target')
    expect(diagnosis.mismatchPositions).toEqual([2, 5])
    expect(diagnosis.message).toContain('2, 5')
  })

  it('diagnoses parity and swap-budget mistakes', () => {
    expect(
      diagnoseSubstitutionState({
        levelId: 'flip-parity',
        permutation: [1, 2, 3, 4, 5],
        swapCount: 0,
      }).kind,
    ).toBe('wrong-parity')

    const overBudget = diagnoseSubstitutionState({
      levelId: 'make-cycle',
      permutation: [2, 3, 4, 5, 1],
      swapCount: 5,
    })

    expect(overBudget.kind).toBe('over-budget')
    expect(overBudget.message).toContain('5/4')
  })
})
