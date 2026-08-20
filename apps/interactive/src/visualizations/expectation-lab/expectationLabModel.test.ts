import { describe, expect, it } from 'vitest'
import {
  diagnoseExpectation,
  distributionMean,
  distributionVariance,
  empiricalQuantity,
  expectationLevels,
  expectationLevelSuccess,
  mulberry32,
  runExpectation,
} from './expectationLabModel'

describe('expectationLabModel', () => {
  it('computes the fair die mean and variance analytically', () => {
    const fair = [1, 1, 1, 1, 1, 1]
    expect(distributionMean(fair)).toBeCloseTo(3.5)
    expect(distributionVariance(fair)).toBeCloseTo(35 / 12)
  })

  it('weights the mean toward heavy faces for a loaded die', () => {
    expect(distributionMean(expectationLevels['estimate-mean'].weights)).toBeCloseTo(3.0)
  })

  it('is deterministic for a fixed seed and conserves the sample count', () => {
    const a = runExpectation('sample-mean', 2000)
    const b = runExpectation('sample-mean', 2000)
    expect(a).toEqual(b)
    expect(a.counts.reduce((s, c) => s + c, 0)).toBe(2000)
  })

  it('keeps the PRNG output in the unit interval', () => {
    const next = mulberry32(3)
    for (let i = 0; i < 200; i += 1) {
      const value = next()
      expect(value).toBeGreaterThanOrEqual(0)
      expect(value).toBeLessThan(1)
    }
  })

  it('lets the empirical estimate reach the analytic target at minSamples', () => {
    for (const level of Object.values(expectationLevels)) {
      const run = runExpectation(level.id, level.minSamples)
      const empirical = empiricalQuantity(level.id, run)
      expect(Math.abs(empirical - level.target)).toBeLessThanOrEqual(level.tolerance)
    }
  })

  it('keeps the variance well separated from its standard deviation', () => {
    const variance = expectationLevels['sample-variance'].target
    const std = Math.sqrt(variance)
    expect(variance - std).toBeGreaterThan(expectationLevels['sample-variance'].tolerance)
  })

  it('requires enough samples and an accurate estimate to succeed', () => {
    const target = expectationLevels['sample-mean'].target
    expect(expectationLevelSuccess({ levelId: 'sample-mean', sampleSize: 200, estimate: target })).toBe(false)
    expect(expectationLevelSuccess({ levelId: 'sample-mean', sampleSize: 1000, estimate: target })).toBe(true)
    expect(expectationLevelSuccess({ levelId: 'sample-mean', sampleSize: 1000, estimate: 4.5 })).toBe(false)
  })

  it('diagnoses standard-deviation-for-variance confusion', () => {
    const std = Math.sqrt(expectationLevels['sample-variance'].target)
    expect(
      diagnoseExpectation({ levelId: 'sample-variance', sampleSize: 5000, estimate: std, touched: true }).kind,
    ).toBe('std-not-variance')
  })

  it('does not punish the initial state and explains a thin sample', () => {
    expect(
      diagnoseExpectation({ levelId: 'sample-mean', sampleSize: 50, estimate: 3.5, touched: false }).kind,
    ).toBe('idle')
    expect(
      diagnoseExpectation({ levelId: 'sample-mean', sampleSize: 200, estimate: 3.5, touched: true }).kind,
    ).toBe('too-few-samples')
  })
})
