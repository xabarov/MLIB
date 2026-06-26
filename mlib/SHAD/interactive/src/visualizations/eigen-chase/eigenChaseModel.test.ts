import { describe, expect, it } from 'vitest'
import {
  applyMatrix,
  crossMagnitude,
  diagnoseEigen,
  eigenLevels,
  eigenLevelSuccess,
  eigenState,
  normalize,
} from './eigenChaseModel'

describe('eigenChaseModel', () => {
  it('applies a 2x2 matrix to a vector', () => {
    expect(applyMatrix({ a: 2, b: 1, c: 1, d: 2 }, [1, 1])).toEqual([3, 3])
  })

  it('measures parallelism with the cross product', () => {
    expect(crossMagnitude([1, 0], [2, 0])).toBeCloseTo(0)
    expect(crossMagnitude([1, 0], [0, 1])).toBeCloseTo(1)
  })

  it('reads lambda along an eigen direction', () => {
    const state = eigenState({ a: 2, b: 1, c: 1, d: 2 }, normalize([1, 1]))
    expect(state.lambda).toBeCloseTo(3)
    expect(state.alignment).toBeCloseTo(0)
  })

  it('accepts the targeted eigenvector for each level', () => {
    expect(eigenLevelSuccess('large-eigen', [1, 1])).toBe(true)
    expect(eigenLevelSuccess('small-eigen', [1, -1])).toBe(true)
    expect(eigenLevelSuccess('flip-eigen', [1, -1])).toBe(true)
  })

  it('rejects the wrong eigenvector by its eigenvalue', () => {
    // (1,-1) is an eigenvector of the symmetric matrix, but with lambda 1, not 3.
    expect(eigenLevelSuccess('large-eigen', [1, -1])).toBe(false)
    expect(diagnoseEigen({ levelId: 'large-eigen', direction: [1, -1], touched: true }).kind).toBe(
      'wrong-eigenvalue',
    )
  })

  it('flags a non-eigen direction as not aligned', () => {
    expect(eigenLevelSuccess('large-eigen', [1, 0])).toBe(false)
    expect(diagnoseEigen({ levelId: 'large-eigen', direction: [1, 0], touched: true }).kind).toBe(
      'not-aligned',
    )
  })

  it('does not punish the untouched state', () => {
    expect(diagnoseEigen({ levelId: 'large-eigen', direction: [1, 0], touched: false }).kind).toBe(
      'idle',
    )
  })

  it('captures the flip matrix negative eigenvalue', () => {
    const state = eigenState(eigenLevels['flip-eigen'].matrix, normalize([1, -1]))
    expect(state.lambda).toBeCloseTo(-1)
  })
})
