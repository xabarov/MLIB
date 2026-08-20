import { describe, expect, it } from 'vitest'
import {
  cabs,
  closureError,
  cmul,
  cpow,
  diagnoseRoots,
  distinctCount,
  orbit,
  rootsLevelSuccess,
  type Complex,
} from './rootsOrbitModel'

function root(n: number, k: number): Complex {
  return [Math.cos((2 * Math.PI * k) / n), Math.sin((2 * Math.PI * k) / n)]
}

describe('rootsOrbitModel', () => {
  it('multiplies complex numbers', () => {
    expect(cmul([0, 1], [0, 1])).toEqual([-1, 0])
    expect(cmul([2, 0], [3, 0])).toEqual([6, 0])
  })

  it('raises i to integer powers around the circle', () => {
    expect(cpow([0, 1], 4)[0]).toBeCloseTo(1)
    expect(cpow([0, 1], 4)[1]).toBeCloseTo(0)
  })

  it('closes the orbit exactly for an nth root of unity', () => {
    expect(closureError(root(5, 1), 5)).toBeCloseTo(0)
    expect(closureError([1.1, 0], 5)).toBeGreaterThan(0.1)
  })

  it('counts geometrically distinct orbit points', () => {
    expect(distinctCount(orbit(root(4, 1), 4))).toBe(4)
    expect(distinctCount(orbit([-1, 0], 4))).toBe(2)
  })

  it('accepts a primitive root and rejects degenerate or off-circle z', () => {
    expect(rootsLevelSuccess({ levelId: 'triangle', z: root(3, 1) })).toBe(true)
    expect(rootsLevelSuccess({ levelId: 'square', z: [0, 1] })).toBe(true)
    expect(rootsLevelSuccess({ levelId: 'pentagon', z: root(5, 1) })).toBe(true)
    // -1 closes for n=4 but only visits a digon, not the square.
    expect(rootsLevelSuccess({ levelId: 'square', z: [-1, 0] })).toBe(false)
    // off the unit circle the orbit spirals.
    expect(rootsLevelSuccess({ levelId: 'triangle', z: [1.18, 0.28] })).toBe(false)
  })

  it('diagnoses the failure modes', () => {
    expect(diagnoseRoots({ levelId: 'triangle', z: [1.18, 0.28], touched: false }).kind).toBe('idle')
    expect(diagnoseRoots({ levelId: 'triangle', z: [1.3, 0], touched: true }).kind).toBe('modulus-off')
    // On the unit circle but the angle does not close the orbit.
    expect(
      diagnoseRoots({ levelId: 'square', z: [Math.cos(0.5), Math.sin(0.5)], touched: true }).kind,
    ).toBe('angle-off')
    // Closes but only visits a digon, not the full square.
    expect(diagnoseRoots({ levelId: 'square', z: [-1, 0], touched: true }).kind).toBe('not-primitive')
    expect(cabs([3, 4])).toBeCloseTo(5)
  })
})
