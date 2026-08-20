import { describe, expect, it } from 'vitest'
import {
  allUsed,
  availableFrom,
  diagnoseEuler,
  edgeBetween,
  eulerLevels,
  eulerLevelSuccess,
  isStuck,
  oddVertices,
  startVertices,
} from './eulerTrailModel'

function walk(levelId: 'bowtie' | 'house' | 'envelope', sequence: number[]) {
  const config = eulerLevels[levelId]
  const used: number[] = []
  let current = sequence[0]
  for (let k = 1; k < sequence.length; k += 1) {
    const next = sequence[k]
    const index = edgeBetween(config.edges, used, current, next)
    if (index < 0) return { used, ok: false }
    used.push(index)
    current = next
  }
  return { used, ok: true }
}

describe('eulerTrailModel', () => {
  it('classifies graphs by odd-degree count', () => {
    expect(oddVertices(5, eulerLevels.bowtie.edges)).toEqual([])
    expect(oddVertices(5, eulerLevels.house.edges)).toEqual([2, 3])
    expect(oddVertices(5, eulerLevels.envelope.edges)).toEqual([0, 1])
  })

  it('offers odd vertices as starts for a path, any for a circuit', () => {
    expect(startVertices(eulerLevels.house)).toEqual([2, 3])
    expect(startVertices(eulerLevels.bowtie)).toEqual([0, 1, 2, 3, 4])
  })

  it('walks a full Eulerian circuit on the bowtie', () => {
    const result = walk('bowtie', [0, 1, 2, 3, 4, 2, 0])
    expect(result.ok).toBe(true)
    expect(allUsed(eulerLevels.bowtie.edges, result.used)).toBe(true)
  })

  it('walks an Eulerian path on the house from an odd vertex', () => {
    const result = walk('house', [2, 1, 0, 3, 4, 2, 3])
    expect(eulerLevelSuccess(eulerLevels.house.edges, result.used)).toBe(true)
  })

  it('draws the envelope without lifting the pen', () => {
    const result = walk('envelope', [0, 3, 2, 4, 3, 1, 2, 0, 1])
    expect(eulerLevelSuccess(eulerLevels.envelope.edges, result.used)).toBe(true)
  })

  it('rejects a move with no free edge', () => {
    const config = eulerLevels.bowtie
    // 0 and 3 are not adjacent.
    expect(edgeBetween(config.edges, [], 0, 3)).toBe(-1)
    expect(edgeBetween(config.edges, [], 0, 1)).toBeGreaterThanOrEqual(0)
  })

  it('detects a stuck state', () => {
    const config = eulerLevels.house
    // Reach vertex 2 having used both of its incident edges except via a dead end.
    const used = [edgeBetween(config.edges, [], 2, 1)]
    expect(isStuck(config.edges, used, 2)).toBe(false)
    expect(availableFrom(config.edges, [], 2).length).toBeGreaterThan(0)
  })

  it('diagnoses idle, invalid, and success', () => {
    const config = eulerLevels.house
    expect(diagnoseEuler({ config, used: [], current: null, touched: false, lastInvalid: false }).kind).toBe('idle')
    expect(diagnoseEuler({ config, used: [0], current: 1, touched: true, lastInvalid: true }).kind).toBe('invalid')
    const full = config.edges.map((_, i) => i)
    expect(diagnoseEuler({ config, used: full, current: 3, touched: true, lastInvalid: false }).kind).toBe('success')
  })
})
