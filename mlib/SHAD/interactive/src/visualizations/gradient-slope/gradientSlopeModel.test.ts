import { describe, expect, it } from 'vitest'
import {
  diagnoseGradient,
  gradient,
  gradientLevelSuccess,
  gradientStep,
  hasDiverged,
  isOscillating,
  runDescent,
} from './gradientSlopeModel'

describe('gradientSlopeModel', () => {
  it('computes the gradient of a x^2 + b y^2', () => {
    expect(gradient({ a: 1, b: 1 }, [2, 3])).toEqual([4, 6])
    expect(gradient({ a: 1, b: 8 }, [1, 1])).toEqual([2, 16])
  })

  it('takes one descent step against the gradient', () => {
    expect(gradientStep({ a: 1, b: 1 }, [2, 2], 0.5)).toEqual([0, 0])
  })

  it('builds a trajectory that starts at the start point', () => {
    const path = runDescent({ a: 1, b: 1 }, [2, 2], 0.4, 10)
    expect(path[0]).toEqual([2, 2])
    expect(path.length).toBeLessThanOrEqual(11)
    expect(distance(path[path.length - 1])).toBeLessThan(distance([2, 2]))
  })

  it('flags a diverging run when the step is too large', () => {
    const path = runDescent({ a: 1, b: 1 }, [2, 2], 1.5, 20)
    expect(hasDiverged(path)).toBe(true)
  })

  it('detects oscillation when a coordinate flips sign', () => {
    expect(isOscillating(runDescent({ a: 1, b: 1 }, [2, 2], 0.9, 6))).toBe(true)
    expect(isOscillating(runDescent({ a: 1, b: 1 }, [2, 2], 0.4, 6))).toBe(false)
  })

  it('opens a convergence window for the gentle bowl', () => {
    expect(gradientLevelSuccess({ levelId: 'roll-to-min', lr: 0.5 })).toBe(true)
    expect(gradientLevelSuccess({ levelId: 'roll-to-min', lr: 0.03 })).toBe(false)
  })

  it('explodes the steep bowl when the step is too large', () => {
    expect(gradientLevelSuccess({ levelId: 'tame-the-step', lr: 0.3 })).toBe(true)
    expect(gradientLevelSuccess({ levelId: 'tame-the-step', lr: 0.7 })).toBe(false)
    expect(diagnoseGradient({ levelId: 'tame-the-step', lr: 0.7, touched: true }).kind).toBe('exploded')
  })

  it('caps the step by the narrow direction of the valley', () => {
    expect(gradientLevelSuccess({ levelId: 'narrow-valley', lr: 0.1 })).toBe(true)
    expect(gradientLevelSuccess({ levelId: 'narrow-valley', lr: 0.3 })).toBe(false)
  })

  it('does not punish the untouched state', () => {
    expect(diagnoseGradient({ levelId: 'roll-to-min', lr: 0.5, touched: false }).kind).toBe('idle')
    expect(diagnoseGradient({ levelId: 'roll-to-min', lr: 0.03, touched: true }).kind).toBe('too-slow')
  })
})

function distance(point: [number, number]): number {
  return Math.hypot(point[0], point[1])
}
