import { describe, expect, it } from 'vitest'
import {
  allFilled,
  diagnoseDp,
  dpLevels,
  editDistance,
  editTable,
  fillCell,
  initialFilled,
  isReady,
  readyCells,
} from './dpStationModel'

describe('dpStationModel', () => {
  it('computes the Levenshtein distance', () => {
    expect(editDistance('COT', 'CAT')).toBe(1)
    expect(editDistance('CAT', 'CART')).toBe(1)
    expect(editDistance('FOOD', 'GOLD')).toBe(2)
    expect(editDistance('CAT', 'CAT')).toBe(0)
  })

  it('fills the base row and column with indices', () => {
    const table = editTable('COT', 'CAT')
    expect(table[0]).toEqual([0, 1, 2, 3])
    expect(table.map((row) => row[0])).toEqual([0, 1, 2, 3])
  })

  it('starts with only the base case filled', () => {
    const filled = initialFilled(3, 3)
    expect(filled[0].every(Boolean)).toBe(true)
    expect(filled.map((row) => row[0]).every(Boolean)).toBe(true)
    expect(filled[1][1]).toBe(false)
    expect(allFilled(filled)).toBe(false)
  })

  it('only marks a cell ready when its three predecessors are filled', () => {
    const filled = initialFilled(3, 3)
    expect(isReady(filled, 1, 1)).toBe(true)
    expect(isReady(filled, 2, 2)).toBe(false)
    const after = fillCell(filled, 1, 1)
    // (2,2) still needs (2,1) and (1,2).
    expect(isReady(after, 2, 2)).toBe(false)
    expect(isReady(after, 1, 2)).toBe(true)
    expect(isReady(after, 2, 1)).toBe(true)
  })

  it('fills the whole table by always taking a ready cell', () => {
    let filled = initialFilled(3, 4)
    let guard = 0
    while (!allFilled(filled) && guard < 100) {
      const cells = readyCells(filled)
      expect(cells.length).toBeGreaterThan(0)
      filled = fillCell(filled, cells[0].row, cells[0].col)
      guard += 1
    }
    expect(allFilled(filled)).toBe(true)
  })

  it('diagnoses idle, not-ready, and success', () => {
    const start = initialFilled(3, 3)
    expect(diagnoseDp({ filled: start, touched: false, lastNotReady: false }).kind).toBe('idle')
    expect(diagnoseDp({ filled: start, touched: true, lastNotReady: true }).kind).toBe('not-ready')
    const full = initialFilled(1, 1)
    const done = fillCell(full, 1, 1)
    expect(diagnoseDp({ filled: done, touched: true, lastNotReady: false }).kind).toBe('success')
  })

  it('exposes the configured level words', () => {
    expect(dpLevels['food-gold'].rowWord).toBe('FOOD')
    expect(dpLevels['food-gold'].colWord).toBe('GOLD')
  })
})
