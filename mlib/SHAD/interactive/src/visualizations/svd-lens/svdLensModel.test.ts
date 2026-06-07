import { describe, expect, it } from 'vitest'
import { eigenPairsSymmetric2x2 } from '../quadratic-lens/quadraticLensModel'
import {
  applyMatrix,
  centerPointCloud,
  dot,
  frobeniusError,
  matrixFromColumns,
  pcaCloud,
  principalComponent2D,
  projectionError,
  rankKApprox,
  retainedVariance,
  signedAxisDistance,
  svd2x2,
  svdTargetMatrix,
  transformedCircleSample,
  transposeTimesMatrix,
  type Matrix2x2,
} from './svdLensModel'

describe('svdLensModel', () => {
  it('finds obvious singular values for diagonal matrices', () => {
    const svd = svd2x2({ a: 3, b: 0, c: 0, d: 2 })

    expect(svd.sigma1).toBeCloseTo(3, 8)
    expect(svd.sigma2).toBeCloseTo(2, 8)
    expect(svd.rank).toBe(2)
  })

  it('keeps rotation matrices at unit singular values', () => {
    const theta = Math.PI / 5
    const matrix: Matrix2x2 = {
      a: Math.cos(theta),
      b: -Math.sin(theta),
      c: Math.sin(theta),
      d: Math.cos(theta),
    }
    const svd = svd2x2(matrix)

    expect(svd.sigma1).toBeCloseTo(1, 8)
    expect(svd.sigma2).toBeCloseTo(1, 8)
    expect(svd.condition).toBeCloseTo(1, 8)
  })

  it('returns nonnegative singular values and orthogonal axes for shear matrices', () => {
    const svd = svd2x2({ a: 1, b: 1.5, c: 0, d: 1 })

    expect(svd.sigma1).toBeGreaterThanOrEqual(svd.sigma2)
    expect(svd.sigma2).toBeGreaterThan(0)
    expect(dot(svd.v1, svd.v2)).toBeCloseTo(0, 6)
    expect(dot(svd.u1, svd.u2)).toBeCloseTo(0, 6)
  })

  it('handles rank-one matrices without NaN', () => {
    const svd = svd2x2(matrixFromColumns([2, 1], [4, 2]))

    expect(svd.rank).toBe(1)
    expect(svd.sigma1).toBeGreaterThan(0)
    expect(svd.sigma2).toBeCloseTo(0, 6)
    expect([svd.u1, svd.u2, svd.v1, svd.v2].flat().every(Number.isFinite)).toBe(true)
  })

  it('connects singular values to eigenvalues of A^T A', () => {
    const svd = svd2x2(svdTargetMatrix)
    const eigenvalues = eigenPairsSymmetric2x2(transposeTimesMatrix(svdTargetMatrix))
      .map((pair) => pair.lambda)
      .sort((a, b) => b - a)

    expect(svd.sigma1 ** 2).toBeCloseTo(eigenvalues[0], 6)
    expect(svd.sigma2 ** 2).toBeCloseTo(eigenvalues[1], 6)
  })

  it('maps unit circle extrema to singular values', () => {
    const svd = svd2x2(svdTargetMatrix)
    const radii = transformedCircleSample(svdTargetMatrix, 360).map((point) => Math.hypot(point[0], point[1]))

    expect(Math.max(...radii)).toBeCloseTo(svd.sigma1, 2)
    expect(Math.min(...radii)).toBeCloseTo(svd.sigma2, 2)
  })

  it('builds a rank-one approximation from the dominant singular component', () => {
    const matrix: Matrix2x2 = { a: 2, b: 0.5, c: 0.5, d: 0.3 }
    const rankOne = rankKApprox(matrix, 1)
    const arbitraryColumnDrop: Matrix2x2 = { ...matrix, b: 0, d: 0 }

    expect(frobeniusError(matrix, rankOne)).toBeLessThan(frobeniusError(matrix, arbitraryColumnDrop))
  })

  it('finds the principal component of centered data', () => {
    const centered = centerPointCloud(pcaCloud)
    const pc = principalComponent2D(pcaCloud)
    const offAxis: [number, number] = [0, 1]

    expect(signedAxisDistance(pc, [1, 0.58])).toBeLessThan(0.18)
    expect(projectionError(centered, pc)).toBeLessThan(projectionError(centered, offAxis))
    expect(retainedVariance(pcaCloud, pc)).toBeGreaterThan(0.95)
  })

  it('applies matrix columns in the expected orientation', () => {
    const matrix = matrixFromColumns([2, 1], [-1, 3])

    expect(applyMatrix(matrix, [1, 0])).toEqual([2, 1])
    expect(applyMatrix(matrix, [0, 1])).toEqual([-1, 3])
  })
})
