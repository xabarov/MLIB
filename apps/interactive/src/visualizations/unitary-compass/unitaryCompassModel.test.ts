import { describe, expect, it } from 'vitest'
import {
  absSquared,
  adjointMatrix,
  baseVector,
  complex,
  complexClose,
  complexDotBilinear,
  conjugate,
  diagnoseAStarABridge,
  diagnoseHermitianMatrix,
  diagnoseHermitianSlot,
  diagnoseUnitaryMatrix,
  fakeHermitianMatrix,
  type ComplexVec2,
  hermitianInner,
  hermitianMatrixEigenvalues2,
  hermitianNormSquared,
  hermitianTargetMatrix,
  isHermitianMatrix,
  isPositiveSemidefiniteHermitian,
  isUnitaryMatrix,
  matrixStarMatrix,
  multiplyComplex,
  nonUnitaryMatrix,
  phaseRotateVector,
  phaseRotationMatrix,
  unitarySwapMatrix,
} from './unitaryCompassModel'

describe('unitaryCompassModel', () => {
  it('shows the bilinear trap under multiplication by i', () => {
    const realVector: ComplexVec2 = [complex(1), complex(0)]
    const iVector = phaseRotateVector(realVector, Math.PI / 2)

    expect(complexDotBilinear(realVector, realVector).re).toBeCloseTo(1)
    expect(complexDotBilinear(iVector, iVector).re).toBeCloseTo(-1)
    expect(diagnoseHermitianSlot('bilinear').kind).toBe('bilinear-trap')
  })

  it('keeps Hermitian norm positive and stable under phase rotation', () => {
    const rotated = phaseRotateVector(baseVector, Math.PI / 2)

    expect(hermitianNormSquared(rotated)).toBeCloseTo(hermitianNormSquared(baseVector))
    expect(hermitianInner(rotated, rotated).im).toBeCloseTo(0)
  })

  it('satisfies Hermitian conjugate symmetry with the lecture convention', () => {
    const x: ComplexVec2 = [complex(1, 1), complex(0, 2)]
    const y: ComplexVec2 = [complex(2, -1), complex(0.5, 0.25)]

    expect(complexClose(hermitianInner(x, y), conjugate(hermitianInner(y, x)))).toBe(true)
    expect(diagnoseHermitianSlot('conjugate-second').kind).toBe('ready')
    expect(diagnoseHermitianSlot('conjugate-first').kind).toBe('wrong-conjugate-slot')
  })

  it('recognizes standard phase rotations and swaps as unitary', () => {
    const rotation = phaseRotationMatrix(Math.PI / 3)
    const swap = unitarySwapMatrix(Math.PI / 2)

    expect(isUnitaryMatrix(rotation)).toBe(true)
    expect(isUnitaryMatrix(swap)).toBe(true)
    expect(diagnoseUnitaryMatrix(rotation).kind).toBe('ready')
  })

  it('rejects non-unitary matrices that preserve only one simple length', () => {
    expect(isUnitaryMatrix(nonUnitaryMatrix)).toBe(false)
    expect(diagnoseUnitaryMatrix(nonUnitaryMatrix).kind).toBe('not-unitary')
  })

  it('distinguishes fake symmetric complex matrices from Hermitian matrices', () => {
    expect(isHermitianMatrix(fakeHermitianMatrix)).toBe(false)
    expect(isHermitianMatrix(hermitianTargetMatrix)).toBe(true)
    expect(diagnoseHermitianMatrix(fakeHermitianMatrix).kind).toBe('not-hermitian')
    expect(diagnoseHermitianMatrix(hermitianTargetMatrix).kind).toBe('ready')
  })

  it('makes A star A Hermitian positive semidefinite for non-unitary matrices', () => {
    const astarA = matrixStarMatrix(nonUnitaryMatrix)
    const eigenvalues = hermitianMatrixEigenvalues2(astarA)

    expect(isHermitianMatrix(astarA)).toBe(true)
    expect(isPositiveSemidefiniteHermitian(astarA)).toBe(true)
    expect(eigenvalues[0]).toBeGreaterThanOrEqual(eigenvalues[1])
    expect(eigenvalues[1]).toBeGreaterThan(-1e-6)
    expect(diagnoseAStarABridge('astar-a', nonUnitaryMatrix).kind).toBe('ready')
  })

  it('catches transpose instead of adjoint in the SVD bridge', () => {
    expect(diagnoseAStarABridge('ata', nonUnitaryMatrix).kind).toBe('not-hermitian')
    expect(diagnoseAStarABridge('aat-star', nonUnitaryMatrix).kind).toBe(
      'not-positive-semidefinite',
    )
  })

  it('implements adjoint as conjugate transpose', () => {
    const matrix = {
      a: complex(1, 2),
      b: complex(0, 1),
      c: complex(3, -2),
      d: complex(4),
    }
    const adjoint = adjointMatrix(matrix)

    expect(adjoint.a).toEqual(complex(1, -2))
    expect(adjoint.b).toEqual(complex(3, 2))
    expect(adjoint.c).toEqual(complex(0, -1))
    expect(adjoint.d).toEqual(complex(4, -0))
  })

  it('keeps primitive complex multiplication and squared magnitude stable', () => {
    const value = multiplyComplex(complex(0, 1), complex(0, 1))

    expect(value.re).toBeCloseTo(-1)
    expect(value.im).toBeCloseTo(0)
    expect(absSquared(complex(3, 4))).toBeCloseTo(25)
  })
})
