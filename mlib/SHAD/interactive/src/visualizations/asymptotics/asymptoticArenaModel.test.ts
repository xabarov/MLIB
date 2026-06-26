import { describe, expect, it } from 'vitest'
import {
  asymptoticScenarios,
  bestStrategyForScenario,
  diagnoseStrategyChoice,
  estimateCost,
  growthPoints,
  strategyRaceEntries,
} from './asymptoticArenaModel'

describe('asymptoticArenaModel', () => {
  it('prefers simple work on small inputs and n log n on large inputs', () => {
    expect(bestStrategyForScenario(asymptoticScenarios['small-random'])).toBe('linear-scan')
    expect(bestStrategyForScenario(asymptoticScenarios['large-random'])).toBe('merge-sort')
  })

  it('recognizes nearly sorted and many lookup scenarios', () => {
    expect(bestStrategyForScenario(asymptoticScenarios['nearly-sorted'])).toBe('insertion-sort')
    expect(bestStrategyForScenario(asymptoticScenarios['many-lookups'])).toBe('hash-index')
  })

  it('computes setup, comparisons and memory costs', () => {
    const hash = estimateCost('hash-index', asymptoticScenarios['many-lookups'])
    expect(hash.setup).toBe(500)
    expect(hash.comparisons).toBe(80)
    expect(hash.memory).toBe(500)

    const insertion = estimateCost('insertion-sort', asymptoticScenarios['large-random'])
    const merge = estimateCost('merge-sort', asymptoticScenarios['large-random'])
    expect(insertion.total).toBeGreaterThan(merge.total)
  })

  it('diagnoses common strategy mistakes', () => {
    expect(diagnoseStrategyChoice('insertion-sort', asymptoticScenarios['large-random']).kind).toBe(
      'quadratic-explodes',
    )
    expect(
      diagnoseStrategyChoice('binary-search-after-sort', asymptoticScenarios['small-random']).kind,
    ).toBe('setup-not-worth-it')
    expect(diagnoseStrategyChoice('linear-scan', asymptoticScenarios['many-lookups']).kind).toBe(
      'preprocessing-pays-off',
    )
    expect(diagnoseStrategyChoice('merge-sort', asymptoticScenarios['nearly-sorted']).kind).toBe(
      'memory-tradeoff',
    )
  })

  it('returns monotonic growth points', () => {
    const points = growthPoints('merge-sort', asymptoticScenarios['large-random'])
    expect(points).toHaveLength(5)
    expect(points[0].cost).toBeLessThan(points[4].cost)
  })

  it('ranks strategies for the visible race replay', () => {
    const smallRace = strategyRaceEntries(asymptoticScenarios['small-random'])
    const largeRace = strategyRaceEntries(asymptoticScenarios['large-random'])

    expect(smallRace[0].strategyId).toBe('linear-scan')
    expect(largeRace[0].strategyId).toBe('merge-sort')
    expect(largeRace.find((entry) => entry.strategyId === 'insertion-sort')?.rank).toBeGreaterThan(
      1,
    )
  })
})
