import { describe, expect, it } from 'vitest'
import {
  diagnoseMonteCarlo,
  estimateValue,
  monteCarloLevels,
  monteCarloLevelSuccess,
  mulberry32,
  runMonteCarlo,
} from './monteCarloModel'

describe('monteCarloModel', () => {
  it('is deterministic for a fixed seed', () => {
    const a = runMonteCarlo('circle-pi', 200)
    const b = runMonteCarlo('circle-pi', 200)
    expect(a.hits).toBe(b.hits)
  })

  it('keeps the PRNG output in the unit interval', () => {
    const next = mulberry32(5)
    for (let i = 0; i < 100; i += 1) {
      const value = next()
      expect(value).toBeGreaterThanOrEqual(0)
      expect(value).toBeLessThan(1)
    }
  })

  it('caps rendered points but counts every hit', () => {
    const run = runMonteCarlo('triangle', 5000, 600)
    expect(run.points.length).toBe(600)
    expect(run.hits).toBeGreaterThan(600)
    expect(run.fraction).toBeCloseTo(run.hits / 5000)
  })

  it('estimates pi as four times the hit fraction', () => {
    const run = runMonteCarlo('circle-pi', 1000)
    expect(estimateValue('circle-pi', run)).toBeCloseTo(4 * run.fraction)
  })

  it('requires enough samples to land near the true value', () => {
    expect(monteCarloLevelSuccess({ levelId: 'circle-pi', sampleSize: 200 })).toBe(false)
    expect(monteCarloLevelSuccess({ levelId: 'circle-pi', sampleSize: 1000 })).toBe(true)
    expect(monteCarloLevelSuccess({ levelId: 'triangle', sampleSize: 1000 })).toBe(true)
    expect(monteCarloLevelSuccess({ levelId: 'parabola', sampleSize: 1000 })).toBe(true)
  })

  it('targets the known areas', () => {
    expect(monteCarloLevels.triangle.target).toBeCloseTo(0.5)
    expect(monteCarloLevels.parabola.target).toBeCloseTo(1 / 3)
  })

  it('diagnoses untouched, too-few, and solved states', () => {
    expect(
      diagnoseMonteCarlo({ levelId: 'circle-pi', sampleSize: 50, touched: false }).kind,
    ).toBe('idle')
    expect(
      diagnoseMonteCarlo({ levelId: 'circle-pi', sampleSize: 200, touched: true }).kind,
    ).toBe('too-few-samples')
    expect(
      diagnoseMonteCarlo({ levelId: 'circle-pi', sampleSize: 1000, touched: true }).kind,
    ).toBe('success')
  })
})
