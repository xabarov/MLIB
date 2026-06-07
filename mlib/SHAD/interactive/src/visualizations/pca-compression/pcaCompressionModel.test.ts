import { describe, expect, it } from 'vitest'
import {
  centerColumns,
  compressionResult,
  compressionRatio,
  detailMatrix,
  diagnoseCompressionBudget,
  diagnoseCentering,
  frobeniusNorm,
  glyphMatrix,
  rankKReconstruction,
  reconstructionErrorForCenteredRank,
  shiftedCloudMatrix,
  storageCost,
  svdSmallMatrix,
} from './pcaCompressionModel'

describe('pcaCompressionModel', () => {
  it('rank-0 reconstruction starts from zero matrix', () => {
    const result = rankKReconstruction(glyphMatrix, 0)

    expect(result.rank).toBe(0)
    expect(frobeniusNorm(result.reconstruction)).toBeCloseTo(0, 8)
    expect(result.frobeniusError).toBeCloseTo(frobeniusNorm(glyphMatrix), 8)
  })

  it('rank-1 reconstruction reduces Frobenius error on a structured matrix', () => {
    const rank0 = rankKReconstruction(glyphMatrix, 0)
    const rank1 = rankKReconstruction(glyphMatrix, 1)

    expect(rank1.frobeniusError).toBeLessThan(rank0.frobeniusError)
    expect(rank1.retainedEnergy).toBeGreaterThan(0.65)
  })

  it('retained energy is monotone as rank increases', () => {
    const rank1 = rankKReconstruction(glyphMatrix, 1)
    const rank2 = rankKReconstruction(glyphMatrix, 2)
    const rank3 = rankKReconstruction(glyphMatrix, 3)

    expect(rank2.retainedEnergy).toBeGreaterThanOrEqual(rank1.retainedEnergy)
    expect(rank3.retainedEnergy).toBeGreaterThanOrEqual(rank2.retainedEnergy)
    expect(rank3.frobeniusError).toBeLessThanOrEqual(rank2.frobeniusError)
  })

  it('storage cost grows as k times rows plus cols plus sigma', () => {
    expect(storageCost(6, 6, 0)).toBe(0)
    expect(storageCost(6, 6, 2)).toBe(26)
    expect(storageCost(8, 2, 3)).toBe(33)
  })

  it('compression ratio can be worse than raw storage for too-large rank', () => {
    expect(compressionRatio(6, 6, 3)).toBeGreaterThan(1)
    expect(compressionRatio(6, 6, 2)).toBeLessThan(1)
  })

  it('max-cell gate catches a local artifact even with acceptable energy', () => {
    const result = rankKReconstruction(detailMatrix, 2)
    const diagnosis = diagnoseCompressionBudget(result, {
      maxStorage: 26,
      minRetainedEnergy: 0.85,
      maxCellError: 0.18,
    })

    expect(result.retainedEnergy).toBeGreaterThan(0.85)
    expect(diagnosis.kind).toBe('local-artifact')
  })

  it('centering beats raw rank-1 reconstruction on shifted data', () => {
    const raw = reconstructionErrorForCenteredRank(shiftedCloudMatrix, 1, false)
    const centered = reconstructionErrorForCenteredRank(shiftedCloudMatrix, 1, true)

    expect(centered.frobeniusError).toBeLessThan(raw.frobeniusError)
    expect(diagnoseCentering(shiftedCloudMatrix, false).kind).toBe('mean-not-centered')
    expect(diagnoseCentering(shiftedCloudMatrix, true).kind).toBe('ready')
  })

  it('selected component reconstruction matches full reconstruction when all components are selected', () => {
    const components = svdSmallMatrix(glyphMatrix)
    const allSelected = compressionResult(glyphMatrix, components.map((component) => component.index))

    expect(allSelected.frobeniusError).toBeLessThan(1e-6)
    expect(allSelected.retainedEnergy).toBeCloseTo(1, 8)
  })

  it('centering removes column means', () => {
    const { centered } = centerColumns(shiftedCloudMatrix)
    const means = centered[0].map((_, col) =>
      centered.reduce((sum, row) => sum + row[col], 0) / centered.length,
    )

    expect(means[0]).toBeCloseTo(0, 8)
    expect(means[1]).toBeCloseTo(0, 8)
  })

  it('fixtures and decompositions do not produce NaN', () => {
    const components = svdSmallMatrix(glyphMatrix)
    const result = rankKReconstruction(glyphMatrix, 2)
    const values = [
      ...components.flatMap((component) => [
        component.sigma,
        component.energy,
        ...component.left,
        ...component.right,
      ]),
      result.frobeniusError,
      result.retainedEnergy,
      result.storageCost,
      result.compressionRatio,
      result.maxCellError,
    ]

    expect(values.every(Number.isFinite)).toBe(true)
  })
})
