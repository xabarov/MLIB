import { describe, expect, it } from 'vitest'
import {
  backSubstitution,
  canEliminate,
  diagnoseGauss,
  eliminableCells,
  eliminate,
  gaussLevels,
  isUpperTriangular,
  swapRows,
} from './gaussStationModel'

describe('gaussStationModel', () => {
  it('only allows elimination with a ready pivot', () => {
    const m = gaussLevels.forward.start
    expect(canEliminate(m, 1, 0)).toBe(true)
    // column 1 pivot is not ready until column 0 is cleared.
    expect(canEliminate(m, 2, 1)).toBe(false)
  })

  it('eliminates an entry to exactly zero', () => {
    const m = gaussLevels.forward.start
    const next = eliminate(m, 1, 0)
    expect(next[1][0]).toBe(0)
    expect(m[1][0]).toBe(1) // original untouched
  })

  it('reaches upper triangular form for the forward level', () => {
    let m = gaussLevels.forward.start
    m = eliminate(m, 1, 0)
    m = eliminate(m, 2, 0)
    m = eliminate(m, 2, 1)
    expect(isUpperTriangular(m)).toBe(true)
    expect(backSubstitution(m)).toEqual([1, 2, 3])
  })

  it('needs a row swap when the first pivot is zero', () => {
    const m = gaussLevels['need-swap'].start
    expect(eliminableCells(m)).toEqual([])
    let swapped = swapRows(m, 0, 1)
    expect(eliminableCells(swapped).length).toBeGreaterThan(0)
    swapped = eliminate(swapped, 2, 0)
    swapped = eliminate(swapped, 2, 1)
    expect(isUpperTriangular(swapped)).toBe(true)
  })

  it('solves the fractional system by back-substitution', () => {
    let m = gaussLevels.fractions.start
    m = eliminate(m, 1, 0)
    m = eliminate(m, 2, 0)
    m = eliminate(m, 2, 1)
    expect(isUpperTriangular(m)).toBe(true)
    const solution = backSubstitution(m)
    expect(solution).not.toBeNull()
    expect(solution![0]).toBeCloseTo(2)
    expect(solution![1]).toBeCloseTo(3)
    expect(solution![2]).toBeCloseTo(-1)
  })

  it('diagnoses idle, pivot-zero, and success', () => {
    expect(diagnoseGauss({ matrix: gaussLevels.forward.start, touched: false }).kind).toBe('idle')
    expect(diagnoseGauss({ matrix: gaussLevels['need-swap'].start, touched: true }).kind).toBe(
      'pivot-zero',
    )
    let m = gaussLevels.forward.start
    m = eliminate(m, 1, 0)
    m = eliminate(m, 2, 0)
    m = eliminate(m, 2, 1)
    expect(diagnoseGauss({ matrix: m, touched: true }).kind).toBe('success')
  })
})
