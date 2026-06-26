import { describe, expect, it } from 'vitest'
import {
  diagnoseFourier,
  fourierLevels,
  fourierLevelSuccess,
  reconstruct,
  spectralError,
  worstHarmonic,
} from './fourierSynthModel'

describe('fourierSynthModel', () => {
  it('reconstructs a sum of sine harmonics', () => {
    // a1 sin(x): at x = pi/2 equals a1.
    expect(reconstruct([1, 0, 0, 0, 0], Math.PI / 2)).toBeCloseTo(1)
    // a2 sin(2x): at x = pi/4 equals a2.
    expect(reconstruct([0, 0.5, 0, 0, 0], Math.PI / 4)).toBeCloseTo(0.5)
  })

  it('measures spectral error as amplitude distance', () => {
    expect(spectralError([1, 0.5, 0, 0, 0], [1, 0.5, 0, 0, 0])).toBeCloseTo(0)
    expect(spectralError([0, 0, 0, 0, 0], [1, 0, 0, 0, 0])).toBeCloseTo(Math.sqrt(0.5))
  })

  it('finds the worst-matched harmonic', () => {
    expect(worstHarmonic([1, 0.5, 0, 0, 0], [1, 0.5, 0, 0, 0])).toBeNull()
    expect(worstHarmonic([1, 0.5, 0.9, 0, 0], [1, 0.5, 0, 0, 0])).toBe(2)
  })

  it('accepts a spectrum within tolerance and rejects an off harmonic', () => {
    const target = fourierLevels['two-harmonics'].target
    expect(fourierLevelSuccess([1.05, 0.45, 0.05, -0.05, 0.0], target)).toBe(true)
    expect(fourierLevelSuccess([1.0, 0.5, 0.5, 0, 0], target)).toBe(false)
  })

  it('matches the square wave target (odd harmonics only)', () => {
    const square = fourierLevels['square-wave'].target
    expect(square[1]).toBeCloseTo(0)
    expect(square[3]).toBeCloseTo(0)
    expect(fourierLevelSuccess(square, square)).toBe(true)
  })

  it('diagnoses the untouched, off, and solved states', () => {
    const target = fourierLevels['two-harmonics'].target
    expect(diagnoseFourier({ amplitudes: [0, 0, 0, 0, 0], target, touched: false }).kind).toBe('idle')
    const off = diagnoseFourier({ amplitudes: [1, 0.5, 0.8, 0, 0], target, touched: true })
    expect(off.kind).toBe('harmonic-off')
    expect(off.worstHarmonic).toBe(2)
    expect(diagnoseFourier({ amplitudes: target, target, touched: true }).kind).toBe('success')
  })
})
