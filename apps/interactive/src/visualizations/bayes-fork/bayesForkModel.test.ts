import { describe, expect, it } from 'vitest'
import {
  bayesLevels,
  bayesLevelSuccess,
  diagnoseBayes,
  empiricalQuantity,
  falsePositiveRate,
  mulberry32,
  posteriorAfterPositives,
  runBayes,
} from './bayesForkModel'

describe('bayesForkModel', () => {
  it('is deterministic for a fixed seed', () => {
    const a = runBayes('base-rate', 3000)
    const b = runBayes('base-rate', 3000)
    expect(a).toEqual(b)
    expect(a.a + a.b + a.c + a.d).toBe(3000)
  })

  it('keeps the PRNG output in the unit interval', () => {
    const next = mulberry32(11)
    for (let i = 0; i < 200; i += 1) {
      const value = next()
      expect(value).toBeGreaterThanOrEqual(0)
      expect(value).toBeLessThan(1)
    }
  })

  it('computes the base-rate posterior as a sharp inversion of sensitivity', () => {
    const fp = falsePositiveRate(0.94)
    const posterior = posteriorAfterPositives(0.02, 0.95, fp, 1)
    // High sensitivity (0.95) but the posterior collapses far below it.
    expect(posterior).toBeGreaterThan(0.2)
    expect(posterior).toBeLessThan(0.3)
    expect(bayesLevels['base-rate'].target).toBeCloseTo(posterior, 10)
  })

  it('sharpens the posterior with a second independent positive test', () => {
    expect(bayesLevels['two-tests'].target).toBeGreaterThan(bayesLevels['base-rate'].target)
    expect(bayesLevels['two-tests'].target).toBeGreaterThan(0.8)
  })

  it('reads the empirical quantity off the right margin of the table', () => {
    // conditionOn 'row' -> P(positive | D) = a / (a + b).
    expect(empiricalQuantity('conditional-frequency', { a: 90, b: 10, c: 5, d: 95, total: 200 })).toBeCloseTo(0.9)
    // conditionOn 'col' -> P(D | positive) = a / (a + c).
    expect(empiricalQuantity('base-rate', { a: 19, b: 1, c: 58, d: 922, total: 1000 })).toBeCloseTo(19 / 77)
  })

  it('lets the empirical estimate reach the analytic target at minSamples', () => {
    for (const level of Object.values(bayesLevels)) {
      const run = runBayes(level.id, level.minSamples)
      const empirical = empiricalQuantity(level.id, run)
      expect(Math.abs(empirical - level.target)).toBeLessThanOrEqual(level.tolerance)
    }
  })

  it('requires enough samples and an accurate estimate to succeed', () => {
    const target = bayesLevels['base-rate'].target
    expect(bayesLevelSuccess({ levelId: 'base-rate', sampleSize: 2000, estimate: target })).toBe(false)
    expect(bayesLevelSuccess({ levelId: 'base-rate', sampleSize: 8000, estimate: target })).toBe(true)
    expect(bayesLevelSuccess({ levelId: 'base-rate', sampleSize: 8000, estimate: 0.95 })).toBe(false)
  })

  it('diagnoses base-rate neglect when the estimate equals the sensitivity', () => {
    const sens = bayesLevels['base-rate'].sensitivity
    expect(
      diagnoseBayes({ levelId: 'base-rate', sampleSize: 8000, estimate: sens, touched: true }).kind,
    ).toBe('base-rate-neglect')
  })

  it('does not punish the initial state and explains a thin sample', () => {
    expect(
      diagnoseBayes({ levelId: 'base-rate', sampleSize: 500, estimate: 0.2, touched: false }).kind,
    ).toBe('idle')
    expect(
      diagnoseBayes({ levelId: 'base-rate', sampleSize: 2000, estimate: 0.2, touched: true }).kind,
    ).toBe('too-few-samples')
  })
})
