import { describe, expect, it } from 'vitest'
import {
  bernoulliLevelSuccess,
  diagnoseBernoulli,
  mulberry32,
  runBernoulli,
  runningFrequency,
  tailDeviation,
} from './bernoulliLabModel'

describe('bernoulliLabModel', () => {
  it('is deterministic for a fixed seed', () => {
    const a = runBernoulli(1337, 0.5, 50)
    const b = runBernoulli(1337, 0.5, 50)
    expect(a.sequence).toEqual(b.sequence)
    expect(a.heads + a.tails).toBe(50)
  })

  it('produces a different stream for a different seed', () => {
    const a = runBernoulli(1, 0.5, 64)
    const b = runBernoulli(2, 0.5, 64)
    expect(a.sequence).not.toEqual(b.sequence)
  })

  it('always returns 1 for p = 1 and 0 for p = 0', () => {
    expect(runBernoulli(99, 1, 10).heads).toBe(10)
    expect(runBernoulli(99, 0, 10).heads).toBe(0)
  })

  it('keeps the PRNG output in the unit interval', () => {
    const next = mulberry32(7)
    for (let i = 0; i < 100; i += 1) {
      const value = next()
      expect(value).toBeGreaterThanOrEqual(0)
      expect(value).toBeLessThan(1)
    }
  })

  it('computes a running frequency that ends at the final frequency', () => {
    const freqs = runningFrequency([1, 0, 1, 1])
    expect(freqs[0]).toBe(1)
    expect(freqs[3]).toBeCloseTo(0.75)
  })

  it('reports a shrinking tail deviation as samples grow', () => {
    const small = tailDeviation(runBernoulli(2024, 0.5, 200).sequence, 0.5)
    const large = tailDeviation(runBernoulli(2024, 0.5, 2000).sequence, 0.5)
    expect(large).toBeLessThan(small + 1e-9)
    expect(large).toBeLessThanOrEqual(0.03)
  })

  it('requires enough samples for the fair coin', () => {
    expect(bernoulliLevelSuccess({ levelId: 'fair-coin', sampleSize: 100, estimate: 0.5 })).toBe(false)
    expect(bernoulliLevelSuccess({ levelId: 'fair-coin', sampleSize: 500, estimate: 0.5 })).toBe(true)
  })

  it('checks the estimate against the hidden bias, not just the sample size', () => {
    expect(bernoulliLevelSuccess({ levelId: 'estimate-bias', sampleSize: 500, estimate: 0.7 })).toBe(true)
    expect(bernoulliLevelSuccess({ levelId: 'estimate-bias', sampleSize: 500, estimate: 0.5 })).toBe(false)
    expect(bernoulliLevelSuccess({ levelId: 'estimate-bias', sampleSize: 100, estimate: 0.7 })).toBe(false)
  })

  it('needs a stable tail for the law of large numbers', () => {
    expect(
      bernoulliLevelSuccess({ levelId: 'law-of-large-numbers', sampleSize: 500, estimate: 0.5 }),
    ).toBe(false)
    expect(
      bernoulliLevelSuccess({ levelId: 'law-of-large-numbers', sampleSize: 2000, estimate: 0.5 }),
    ).toBe(true)
  })

  it('does not punish the initial state and explains a small sample', () => {
    expect(
      diagnoseBernoulli({ levelId: 'fair-coin', sampleSize: 20, estimate: 0.5, touched: false }).kind,
    ).toBe('idle')
    expect(
      diagnoseBernoulli({ levelId: 'fair-coin', sampleSize: 100, estimate: 0.5, touched: true }).kind,
    ).toBe('too-few-samples')
    expect(
      diagnoseBernoulli({ levelId: 'estimate-bias', sampleSize: 500, estimate: 0.5, touched: true }).kind,
    ).toBe('estimate-off')
  })
})
