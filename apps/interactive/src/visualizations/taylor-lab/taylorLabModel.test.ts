import { describe, expect, it } from 'vitest'
import {
  coeffStops,
  curveError,
  diagnoseTaylor,
  evaluatePolynomial,
  matchTolerance,
  taylorLevels,
  taylorLevelSuccess,
  worstCoefficient,
} from './taylorLabModel'

describe('taylorLabModel', () => {
  it('evaluates a polynomial by ascending powers', () => {
    // 1 + 2x + 3x^2 at x = 2 -> 1 + 4 + 12 = 17.
    expect(evaluatePolynomial([1, 2, 3], 2)).toBeCloseTo(17)
    expect(evaluatePolynomial([0, 1, 0, -1 / 6], Math.PI / 2)).toBeCloseTo(
      Math.PI / 2 - (Math.PI / 2) ** 3 / 6,
    )
  })

  it('encodes the known Taylor coefficients of e^x and sin x', () => {
    expect(taylorLevels.curvature.target[2]).toBeCloseTo(0.5) // x^2 / 2!
    expect(taylorLevels.sine.target[3]).toBeCloseTo(-1 / 6) // -x^3 / 3!
    expect(taylorLevels.sine.target[0]).toBeCloseTo(0)
    expect(taylorLevels.sine.target[2]).toBeCloseTo(0)
  })

  it('shrinks the residual as more Taylor terms are added for e^x', () => {
    const tangent = curveError(taylorLevels.tangent.target, taylorLevels.tangent)
    const quadratic = curveError(taylorLevels.curvature.target, taylorLevels.curvature)
    expect(quadratic).toBeLessThan(tangent)
  })

  it('every target coefficient is reachable on the slider grid within tolerance', () => {
    for (const level of Object.values(taylorLevels)) {
      for (const target of level.target) {
        const snapped = Math.round(target / coeffStops.step) * coeffStops.step
        expect(Math.abs(snapped - target)).toBeLessThanOrEqual(matchTolerance)
        expect(snapped).toBeGreaterThanOrEqual(coeffStops.min - 1e-9)
        expect(snapped).toBeLessThanOrEqual(coeffStops.max + 1e-9)
      }
    }
  })

  it('accepts coefficients within tolerance and rejects an off term', () => {
    const target = taylorLevels.curvature.target
    expect(taylorLevelSuccess([1.05, 0.95, 0.45, 0.05, -0.05], target)).toBe(true)
    expect(taylorLevelSuccess([1, 1, 0.5, 0.5, 0], target)).toBe(false)
  })

  it('finds the worst-matched coefficient', () => {
    expect(worstCoefficient([1, 1, 0.5, 0, 0], [1, 1, 0.5, 0, 0])).toBeNull()
    expect(worstCoefficient([1, 1, 0.5, 0.9, 0], [1, 1, 0.5, 0, 0])).toBe(3)
  })

  it('diagnoses the untouched, off, and solved states', () => {
    const target = taylorLevels.sine.target
    expect(diagnoseTaylor({ coeffs: [0, 0, 0, 0, 0], target, touched: false }).kind).toBe('idle')
    const off = diagnoseTaylor({ coeffs: [0, 1, 0, 0.9, 0], target, touched: true })
    expect(off.kind).toBe('coefficient-off')
    expect(off.worstCoeff).toBe(3)
    expect(diagnoseTaylor({ coeffs: target, target, touched: true }).kind).toBe('success')
  })
})
