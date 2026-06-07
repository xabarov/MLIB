import { describe, expect, it } from 'vitest'
import {
  diagnoseMatrixMachineState,
  matrixFromColumns,
  matrixMachineLevelSuccess,
  snapMatrixCoord,
  targetError,
} from './matrixMachineModel'

describe('matrixMachineModel', () => {
  it('builds a matrix from basis images as columns', () => {
    expect(matrixFromColumns([2, 0], [0, 1])).toEqual([
      [2, 0],
      [0, 1],
    ])
  })

  it('recognizes target transforms', () => {
    expect(matrixMachineLevelSuccess('stretch-x', [2, 0], [0, 1])).toBe(true)
    expect(matrixMachineLevelSuccess('shear-y', [1, 0], [1, 1])).toBe(true)
    expect(matrixMachineLevelSuccess('flip-x', [-1, 0], [0, 1])).toBe(true)
    expect(matrixMachineLevelSuccess('quarter-turn', [0, 1], [-1, 0])).toBe(true)
  })

  it('reports target error and snapped coordinates', () => {
    expect(targetError('stretch-x', [1, 0], [0, 1])).toBeCloseTo(1)
    expect(snapMatrixCoord(0.62)).toBe(0.5)
    expect(snapMatrixCoord(9)).toBe(3)
  })

  it('diagnoses matrix machine mistakes without punishing the initial state', () => {
    expect(
      diagnoseMatrixMachineState({
        levelId: 'stretch-x',
        u: [1, 0],
        v: [0, 1],
        touched: false,
      }).kind,
    ).toBe('in-progress')

    expect(
      diagnoseMatrixMachineState({
        levelId: 'quarter-turn',
        u: [-1, 0],
        v: [0, 1],
        touched: true,
      }).kind,
    ).toBe('swapped-columns')

    expect(
      diagnoseMatrixMachineState({
        levelId: 'stretch-x',
        u: [1, 0],
        v: [0, 1],
        touched: true,
      }).kind,
    ).toBe('wrong-length')
  })
})
