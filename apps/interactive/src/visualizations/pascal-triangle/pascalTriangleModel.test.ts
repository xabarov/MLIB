import { describe, expect, it } from 'vitest'
import {
  allFilled,
  buildPascalTable,
  diagnosePascal,
  fillCell,
  initialFilled,
  isReady,
  pascalLevels,
  readyCells,
  rowSum,
} from './pascalTriangleModel'

describe('pascalTriangleModel', () => {
  it('builds Pascal rows from the binomial recurrence', () => {
    const table = buildPascalTable(5)
    expect(table[0]).toEqual([1])
    expect(table[1]).toEqual([1, 1])
    expect(table[2]).toEqual([1, 2, 1])
    expect(table[3]).toEqual([1, 3, 3, 1])
    expect(table[4]).toEqual([1, 4, 6, 4, 1])
  })

  it('has row sums equal to powers of two', () => {
    const table = buildPascalTable(7)
    for (let i = 0; i < 7; i += 1) {
      expect(rowSum(table, i)).toBe(2 ** i)
    }
  })

  it('starts with only the triangle edges filled', () => {
    const filled = initialFilled(5)
    expect(filled[2]).toEqual([true, false, true])
    expect(filled[4]).toEqual([true, false, false, false, true])
    expect(allFilled(filled)).toBe(false)
  })

  it('marks an interior cell ready only when both parents are filled', () => {
    const filled = initialFilled(5)
    expect(isReady(filled, 2, 1)).toBe(true)
    // (3,1) needs (2,0) edge and (2,1) interior — not ready yet.
    expect(isReady(filled, 3, 1)).toBe(false)
    const after = fillCell(filled, 2, 1)
    expect(isReady(after, 3, 1)).toBe(true)
    expect(isReady(after, 3, 2)).toBe(true)
  })

  it('never reports edge cells as ready', () => {
    const filled = initialFilled(5)
    expect(isReady(filled, 3, 0)).toBe(false)
    expect(isReady(filled, 3, 3)).toBe(false)
  })

  it('fills the whole triangle by always taking a ready cell', () => {
    let filled = initialFilled(6)
    let guard = 0
    while (!allFilled(filled) && guard < 200) {
      const cells = readyCells(filled)
      expect(cells.length).toBeGreaterThan(0)
      filled = fillCell(filled, cells[0].row, cells[0].col)
      guard += 1
    }
    expect(allFilled(filled)).toBe(true)
  })

  it('diagnoses idle, not-ready, and success', () => {
    const start = initialFilled(5)
    expect(diagnosePascal({ filled: start, touched: false, lastNotReady: false }).kind).toBe('idle')
    expect(diagnosePascal({ filled: start, touched: true, lastNotReady: true }).kind).toBe('not-ready')
    const done = fillCell(initialFilled(3), 2, 1)
    expect(diagnosePascal({ filled: done, touched: true, lastNotReady: false }).kind).toBe('success')
  })

  it('exposes the configured level sizes', () => {
    expect(pascalLevels['triangle-7'].rows).toBe(7)
  })
})
