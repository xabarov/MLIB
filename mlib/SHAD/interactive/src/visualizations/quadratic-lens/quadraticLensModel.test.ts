import { describe, expect, it } from 'vitest'
import {
  classifyQuadraticForm,
  determinantOfForm,
  eigenPairsSymmetric2x2,
  levelSetSample,
  principalAxisAngle,
  quadraticLevelSuccess,
  quadraticValue,
  rotateForm,
  rotatePoint,
  signatureLabel,
  type Symmetric2x2,
} from './quadraticLensModel'

function dot(a: [number, number], b: [number, number]) {
  return a[0] * b[0] + a[1] * b[1]
}

describe('quadraticLensModel', () => {
  it('classifies positive definite diagonal forms', () => {
    const form: Symmetric2x2 = { a: 1, b: 0, c: 4 }

    expect(classifyQuadraticForm(form)).toBe('positive-definite')
    expect(signatureLabel(form)).toBe('(+,+)')
    expect(determinantOfForm(form)).toBe(4)
  })

  it('classifies indefinite forms', () => {
    const form: Symmetric2x2 = { a: 1, b: 0, c: -1 }

    expect(classifyQuadraticForm(form)).toBe('indefinite')
    expect(signatureLabel(form)).toBe('(+,-)')
    expect(determinantOfForm(form)).toBe(-1)
  })

  it('classifies semidefinite and negative definite forms', () => {
    expect(classifyQuadraticForm({ a: 1, b: 0, c: 0 })).toBe('positive-semidefinite')
    expect(classifyQuadraticForm({ a: -1, b: 0, c: -2 })).toBe('negative-definite')
    expect(signatureLabel({ a: 0, b: 0, c: 0 })).toBe('(0,0)')
  })

  it('returns orthogonal eigenvectors for symmetric forms', () => {
    const [first, second] = eigenPairsSymmetric2x2({ a: 3, b: 1, c: 2 })

    expect(dot(first.vector, second.vector)).toBeCloseTo(0, 8)
    expect(quadraticValue({ a: 3, b: 1, c: 2 }, first.vector)).toBeCloseTo(first.lambda, 8)
    expect(quadraticValue({ a: 3, b: 1, c: 2 }, second.vector)).toBeCloseTo(second.lambda, 8)
  })

  it('removes the cross-term at the principal axis angle', () => {
    const form: Symmetric2x2 = { a: 3, b: 1, c: 2 }
    const rotated = rotateForm(form, principalAxisAngle(form))

    expect(rotated.b).toBeCloseTo(0, 8)
  })

  it('preserves quadratic values under coordinated rotation', () => {
    const form: Symmetric2x2 = { a: 2.5, b: -0.75, c: 1.2 }
    const theta = Math.PI / 7
    const point: [number, number] = [1.3, -0.4]
    const rotatedForm = rotateForm(form, theta)
    const rotatedPoint = rotatePoint(point, -theta)

    expect(quadraticValue(form, point)).toBeCloseTo(quadraticValue(rotatedForm, rotatedPoint), 8)
  })

  it('samples ellipse and hyperbola level sets', () => {
    const ellipse = levelSetSample({ a: 1, b: 0, c: 4 })
    const hyperbola = levelSetSample({ a: 1, b: 0, c: -1 })

    expect(ellipse).toHaveLength(1)
    expect(ellipse[0].points.length).toBeGreaterThan(16)
    expect(hyperbola.length).toBeGreaterThanOrEqual(2)
    expect(hyperbola.flatMap((branch) => branch.points).length).toBeGreaterThan(16)
  })

  it('keeps near-degenerate samples finite', () => {
    const branches = levelSetSample({ a: 1, b: 0, c: 0.0001 })
    const points = branches.flatMap((branch) => branch.points)

    expect(points.length).toBeGreaterThan(0)
    expect(points.every(([x, y]) => Number.isFinite(x) && Number.isFinite(y))).toBe(true)
  })

  it('checks level success conditions', () => {
    expect(
      quadraticLevelSuccess({
        levelId: 'positive-energy',
        form: { a: 2, b: 0.2, c: 1 },
        rotationAngle: 0,
        positiveDirection: [1, 0],
        negativeDirection: [0, 1],
        nullDirection: [0, 1],
        touched: true,
      }),
    ).toBe(true)

    expect(
      quadraticLevelSuccess({
        levelId: 'saddle-signature',
        form: { a: 1, b: 0, c: -1 },
        rotationAngle: 0,
        positiveDirection: [1, 0],
        negativeDirection: [0, 1],
        nullDirection: [1, 1],
        touched: true,
      }),
    ).toBe(true)
  })
})
