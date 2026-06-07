import { describe, expect, it } from 'vitest'
import {
  angleBetween2,
  determinant2,
  dot2,
  dot3,
  gramSchmidt2,
  gramSchmidt3,
  isOrthogonalMatrix2,
  isOrthonormal2,
  norm2,
  normalize2,
  orthogonalOperatorDiagnosis,
  orthogonalPairDiagnosis,
  projectOntoLine2,
  projectOntoPlane3,
  residual2,
  residual3,
  shearTrapMatrix,
  targetRotation,
  transposeTimesMatrix2,
  type Vec2,
} from './orthogonalWorkshopModel'

function expectVecClose(actual: Vec2, expected: Vec2) {
  expect(actual[0]).toBeCloseTo(expected[0], 5)
  expect(actual[1]).toBeCloseTo(expected[1], 5)
}

describe('orthogonalWorkshopModel', () => {
  it('projects onto a line with an orthogonal residual', () => {
    const point: Vec2 = [2, 3]
    const direction: Vec2 = [1, 1]
    const projection = projectOntoLine2(point, direction)
    const residual = residual2(point, direction)

    expect(dot2(residual, direction)).toBeCloseTo(0, 5)
    expectVecClose([projection[0] + residual[0], projection[1] + residual[1]], point)
  })

  it('projects onto a plane and leaves a normal residual', () => {
    const point: [number, number, number] = [2, 3, 4]
    const projection = projectOntoPlane3(point, [1, 0, 0], [0, 1, 0])
    const residual = residual3(point, [
      [1, 0, 0],
      [0, 1, 0],
    ])

    expect(projection).toEqual([2, 3, 0])
    expect(residual).toEqual([0, 0, 4])
    expect(dot3(residual, [1, 0, 0])).toBeCloseTo(0)
    expect(dot3(residual, [0, 1, 0])).toBeCloseTo(0)
  })

  it('runs Gram-Schmidt and preserves span in a simple 2D case', () => {
    const result = gramSchmidt2([
      [2, 0],
      [1, 3],
    ])

    expect(result.dependentIndex).toBeNull()
    expect(isOrthonormal2(result.orthonormal)).toBe(true)
    expectVecClose(result.orthonormal[0], [1, 0])
    expectVecClose(result.orthonormal[1], [0, 1])
  })

  it('detects dependent vectors without NaN', () => {
    const result = gramSchmidt2([
      [1, 1],
      [2, 2],
    ])

    expect(result.dependentIndex).toBe(1)
    expect(result.orthonormal).toHaveLength(1)
    expect(result.residuals.flat().every(Number.isFinite)).toBe(true)
  })

  it('normalizes nonzero vectors to length 1', () => {
    const vector = normalize2([3, 4])

    expect(norm2(vector)).toBeCloseTo(1)
  })

  it('rejects independent but non-orthogonal vectors', () => {
    const diagnosis = orthogonalPairDiagnosis([1, 0], [1, 1])

    expect(diagnosis.kind).toBe('not-orthogonal')
    expect(angleBetween2([1, 0], [1, 1])).toBeGreaterThan(0)
  })

  it('recognizes rotation and reflection matrices', () => {
    const reflection = { a: 1, b: 0, c: 0, d: -1 }

    expect(isOrthogonalMatrix2(targetRotation)).toBe(true)
    expect(determinant2(targetRotation)).toBeCloseTo(1)
    expect(isOrthogonalMatrix2(reflection)).toBe(true)
    expect(determinant2(reflection)).toBeCloseTo(-1)
    expect(orthogonalOperatorDiagnosis(reflection, { requireRotation: true }).kind).toBe(
      'reflection-vs-rotation',
    )
  })

  it('rejects shear matrices even when one basis length is preserved', () => {
    const qtq = transposeTimesMatrix2(shearTrapMatrix)

    expect(qtq.a).toBeCloseTo(1)
    expect(isOrthogonalMatrix2(shearTrapMatrix)).toBe(false)
    expect(orthogonalOperatorDiagnosis(shearTrapMatrix).kind).toBe('not-orthogonal-operator')
  })

  it('supports Gram-Schmidt in 3D and detects dependent third vectors', () => {
    const result = gramSchmidt3([
      [1, 0, 0],
      [1, 1, 0],
      [2, 1, 0],
    ])

    expect(result.orthonormal).toHaveLength(2)
    expect(result.dependentIndex).toBe(2)
    expect(result.orthonormal[0]).toEqual([1, 0, 0])
    expect(result.orthonormal[1]).toEqual([0, 1, 0])
  })
})
