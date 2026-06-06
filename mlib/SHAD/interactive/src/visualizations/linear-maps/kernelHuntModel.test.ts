import { describe, expect, it } from 'vitest'
import {
  errorToKernel,
  isBasisAligned,
  isOnKernel,
  isZeroVector,
  kernelLevelSuccess,
  projectionToKernel,
  residual,
} from './kernelHuntModel'

describe('kernelHuntModel', () => {
  it('recognizes the nonzero kernel vector (-1, 1, -1)', () => {
    expect(residual([-1, 1, -1])).toEqual([0, 0])
    expect(errorToKernel([-1, 1, -1])).toBeCloseTo(0)
    expect(isOnKernel([-1, 1, -1])).toBe(true)
  })

  it('does not accept the zero vector as a meaningful kernel answer', () => {
    expect(isZeroVector([0, 0, 0])).toBe(true)
    expect(isOnKernel([0, 0, 0])).toBe(false)
  })

  it('projects arbitrary candidates to the kernel line', () => {
    expect(projectionToKernel([1, 2, 1])).toEqual([-0, 0, -0])
    const projected = projectionToKernel([-2, 2, -2])
    expect(projected[0]).toBeCloseTo(-2)
    expect(projected[1]).toBeCloseTo(2)
    expect(projected[2]).toBeCloseTo(-2)
  })

  it('checks level-specific success predicates', () => {
    expect(
      kernelLevelSuccess({
        levelId: 'solution-line',
        candidate: [-2, 2, -2],
        completedLevelIds: ['nonzero-zero'],
      }),
    ).toBe(true)
    expect(isBasisAligned([1, -1, 1])).toBe(true)
    expect(
      kernelLevelSuccess({
        levelId: 'rank-nullity',
        candidate: [-1, 1, -1],
        completedLevelIds: ['nonzero-zero', 'solution-line', 'kernel-basis'],
      }),
    ).toBe(true)
  })
})
