export type Complex = {
  re: number
  im: number
}

export type ComplexVec2 = [Complex, Complex]

export type ComplexMatrix2x2 = {
  a: Complex
  b: Complex
  c: Complex
  d: Complex
}

export type HermitianSlotMode = 'bilinear' | 'conjugate-first' | 'conjugate-second'
export type AStarChoice = 'ata' | 'aat-star' | 'astar-a'

export type UnitaryDiagnosisKind =
  | 'ready'
  | 'zero-vector'
  | 'bilinear-trap'
  | 'wrong-conjugate-slot'
  | 'not-hermitian'
  | 'not-unitary'
  | 'not-positive-semidefinite'

export type UnitaryDiagnosis = {
  kind: UnitaryDiagnosisKind
  message: string
  repairHint: string
}

export const unitaryTolerance = 1e-7
export const unitaryUiTolerance = 0.06
export const unitarySnap = 0.1
export const unitaryGridLimit = 2.5

export const zeroComplex = complex(0, 0)
export const oneComplex = complex(1, 0)
export const iComplex = complex(0, 1)
export const minusIComplex = complex(0, -1)

export const baseVector: ComplexVec2 = [complex(1, 0), complex(0.6, 0.8)]
export const testVectorY: ComplexVec2 = [complex(0.2, 0.9), complex(1, -0.4)]
export const fakeHermitianMatrix: ComplexMatrix2x2 = {
  a: complex(2, 0),
  b: iComplex,
  c: iComplex,
  d: complex(3, 0),
}
export const hermitianTargetMatrix: ComplexMatrix2x2 = {
  a: complex(2, 0),
  b: iComplex,
  c: minusIComplex,
  d: complex(3, 0),
}
export const nonUnitaryMatrix: ComplexMatrix2x2 = {
  a: complex(1, 0),
  b: complex(0.5, 0),
  c: zeroComplex,
  d: oneComplex,
}

export function complex(re: number, im = 0): Complex {
  return { re, im }
}

export function snapUnitaryValue(value: number): number {
  return Math.max(
    -unitaryGridLimit,
    Math.min(unitaryGridLimit, Math.round(value / unitarySnap) * unitarySnap),
  )
}

export function addComplex(left: Complex, right: Complex): Complex {
  return complex(left.re + right.re, left.im + right.im)
}

export function subtractComplex(left: Complex, right: Complex): Complex {
  return complex(left.re - right.re, left.im - right.im)
}

export function multiplyComplex(left: Complex, right: Complex): Complex {
  return complex(left.re * right.re - left.im * right.im, left.re * right.im + left.im * right.re)
}

export function scaleComplex(value: Complex, scale: number): Complex {
  return complex(value.re * scale, value.im * scale)
}

export function conjugate(value: Complex): Complex {
  return complex(value.re, -value.im)
}

export function absSquared(value: Complex): number {
  return value.re * value.re + value.im * value.im
}

export function complexMagnitude(value: Complex): number {
  return Math.hypot(value.re, value.im)
}

export function complexDistance(left: Complex, right: Complex): number {
  return complexMagnitude(subtractComplex(left, right))
}

export function complexClose(left: Complex, right: Complex, tolerance = unitaryUiTolerance): boolean {
  return complexDistance(left, right) < tolerance
}

export function formatUnitaryNumber(value: number): string {
  return Math.abs(value) < 0.005 ? '0.00' : value.toFixed(2)
}

export function formatComplex(value: Complex): string {
  const re = Math.abs(value.re) < 0.005 ? 0 : value.re
  const im = Math.abs(value.im) < 0.005 ? 0 : value.im
  if (im === 0) return formatUnitaryNumber(re)
  if (re === 0) return `${formatUnitaryNumber(im)}i`
  const sign = im >= 0 ? '+' : '-'
  return `${formatUnitaryNumber(re)} ${sign} ${formatUnitaryNumber(Math.abs(im))}i`
}

export function addVec2(left: ComplexVec2, right: ComplexVec2): ComplexVec2 {
  return [addComplex(left[0], right[0]), addComplex(left[1], right[1])]
}

export function scaleVec2(vector: ComplexVec2, scale: Complex): ComplexVec2 {
  return [multiplyComplex(vector[0], scale), multiplyComplex(vector[1], scale)]
}

export function complexDotBilinear(x: ComplexVec2, y: ComplexVec2): Complex {
  return addComplex(multiplyComplex(x[0], y[0]), multiplyComplex(x[1], y[1]))
}

export function hermitianInner(x: ComplexVec2, y: ComplexVec2): Complex {
  return addComplex(multiplyComplex(x[0], conjugate(y[0])), multiplyComplex(x[1], conjugate(y[1])))
}

export function innerByMode(x: ComplexVec2, y: ComplexVec2, mode: HermitianSlotMode): Complex {
  if (mode === 'bilinear') return complexDotBilinear(x, y)
  if (mode === 'conjugate-first') {
    return addComplex(multiplyComplex(conjugate(x[0]), y[0]), multiplyComplex(conjugate(x[1]), y[1]))
  }
  return hermitianInner(x, y)
}

export function hermitianNormSquared(x: ComplexVec2): number {
  return hermitianInner(x, x).re
}

export function complexVectorNorm(x: ComplexVec2): number {
  return Math.sqrt(Math.max(0, hermitianNormSquared(x)))
}

export function normalizeComplexVec2(vector: ComplexVec2): ComplexVec2 {
  const norm = complexVectorNorm(vector)
  if (norm < unitaryTolerance) return [zeroComplex, zeroComplex]
  return [scaleComplex(vector[0], 1 / norm), scaleComplex(vector[1], 1 / norm)]
}

export function phase(theta: number): Complex {
  return complex(Math.cos(theta), Math.sin(theta))
}

export function phaseRotateVector(vector: ComplexVec2, theta: number): ComplexVec2 {
  return scaleVec2(vector, phase(theta))
}

export function applyComplexMatrix(matrix: ComplexMatrix2x2, vector: ComplexVec2): ComplexVec2 {
  return [
    addComplex(multiplyComplex(matrix.a, vector[0]), multiplyComplex(matrix.b, vector[1])),
    addComplex(multiplyComplex(matrix.c, vector[0]), multiplyComplex(matrix.d, vector[1])),
  ]
}

export function adjointMatrix(matrix: ComplexMatrix2x2): ComplexMatrix2x2 {
  return {
    a: conjugate(matrix.a),
    b: conjugate(matrix.c),
    c: conjugate(matrix.b),
    d: conjugate(matrix.d),
  }
}

export function multiplyComplexMatrices(
  left: ComplexMatrix2x2,
  right: ComplexMatrix2x2,
): ComplexMatrix2x2 {
  return {
    a: addComplex(multiplyComplex(left.a, right.a), multiplyComplex(left.b, right.c)),
    b: addComplex(multiplyComplex(left.a, right.b), multiplyComplex(left.b, right.d)),
    c: addComplex(multiplyComplex(left.c, right.a), multiplyComplex(left.d, right.c)),
    d: addComplex(multiplyComplex(left.c, right.b), multiplyComplex(left.d, right.d)),
  }
}

export function identityComplexMatrix(): ComplexMatrix2x2 {
  return { a: oneComplex, b: zeroComplex, c: zeroComplex, d: oneComplex }
}

export function phaseRotationMatrix(theta: number): ComplexMatrix2x2 {
  const value = phase(theta)
  return { a: value, b: zeroComplex, c: zeroComplex, d: value }
}

export function unitarySwapMatrix(theta = 0): ComplexMatrix2x2 {
  const value = phase(theta)
  return { a: zeroComplex, b: value, c: value, d: zeroComplex }
}

export function matrixDistance(left: ComplexMatrix2x2, right: ComplexMatrix2x2): number {
  return Math.hypot(
    complexDistance(left.a, right.a),
    complexDistance(left.b, right.b),
    complexDistance(left.c, right.c),
    complexDistance(left.d, right.d),
  )
}

export function isHermitianMatrix(matrix: ComplexMatrix2x2): boolean {
  return matrixDistance(matrix, adjointMatrix(matrix)) < unitaryUiTolerance
}

export function isUnitaryMatrix(matrix: ComplexMatrix2x2): boolean {
  return matrixDistance(multiplyComplexMatrices(adjointMatrix(matrix), matrix), identityComplexMatrix()) < unitaryUiTolerance
}

export function matrixStarMatrix(matrix: ComplexMatrix2x2): ComplexMatrix2x2 {
  return multiplyComplexMatrices(adjointMatrix(matrix), matrix)
}

export function transposeTimesMatrixNoConjugate(matrix: ComplexMatrix2x2): ComplexMatrix2x2 {
  return {
    a: addComplex(multiplyComplex(matrix.a, matrix.a), multiplyComplex(matrix.c, matrix.c)),
    b: addComplex(multiplyComplex(matrix.a, matrix.b), multiplyComplex(matrix.c, matrix.d)),
    c: addComplex(multiplyComplex(matrix.b, matrix.a), multiplyComplex(matrix.d, matrix.c)),
    d: addComplex(multiplyComplex(matrix.b, matrix.b), multiplyComplex(matrix.d, matrix.d)),
  }
}

export function matrixByAStarChoice(matrix: ComplexMatrix2x2, choice: AStarChoice): ComplexMatrix2x2 {
  if (choice === 'ata') return transposeTimesMatrixNoConjugate(matrix)
  if (choice === 'aat-star') return multiplyComplexMatrices(matrix, adjointMatrix(matrix))
  return matrixStarMatrix(matrix)
}

export function hermitianMatrixEigenvalues2(matrix: ComplexMatrix2x2): [number, number] {
  const a = matrix.a.re
  const d = matrix.d.re
  const offDiagonalEnergy = absSquared(matrix.b)
  const halfTrace = (a + d) / 2
  const radius = Math.sqrt(((a - d) / 2) ** 2 + offDiagonalEnergy)
  return [halfTrace + radius, halfTrace - radius]
}

export function isPositiveSemidefiniteHermitian(matrix: ComplexMatrix2x2): boolean {
  if (!isHermitianMatrix(matrix)) return false
  const [lambda1, lambda2] = hermitianMatrixEigenvalues2(matrix)
  return lambda1 > -unitaryUiTolerance && lambda2 > -unitaryUiTolerance
}

export function diagnoseHermitianSlot(mode: HermitianSlotMode): UnitaryDiagnosis {
  const ix = phaseRotateVector(baseVector, Math.PI / 2)
  const baseValue = innerByMode(baseVector, baseVector, mode)
  const rotatedValue = innerByMode(ix, ix, mode)
  const symmetryLeft = innerByMode(baseVector, testVectorY, mode)
  const symmetryRight = conjugate(innerByMode(testVectorY, baseVector, mode))

  if (mode === 'bilinear') {
    return {
      kind: 'bilinear-trap',
      message: `B(ix, ix) = ${formatComplex(rotatedValue)}, а B(x, x) = ${formatComplex(baseValue)}.`,
      repairHint: 'Обычная билинейность меняет знак под умножением на i: это не длина.',
    }
  }
  if (mode !== 'conjugate-second') {
    return {
      kind: 'wrong-conjugate-slot',
      message: 'Сопряжение есть, но оно стоит не в соглашении этой лекции.',
      repairHint: 'В этих конспектах форма линейна по первому аргументу и сопряженна по второму.',
    }
  }
  if (!complexClose(symmetryLeft, symmetryRight)) {
    return {
      kind: 'wrong-conjugate-slot',
      message: '<x,y> не совпало с conjugate(<y,x>).',
      repairHint: 'Проверь conjugate slot и порядок аргументов.',
    }
  }
  return {
    kind: 'ready',
    message: 'Hermitian inner product выбран: норма стабильна, conjugate symmetry работает.',
    repairHint: 'Теперь умножение на i меняет фазу, но не длину.',
  }
}

export function diagnoseHermitianMatrix(matrix: ComplexMatrix2x2): UnitaryDiagnosis {
  if (isHermitianMatrix(matrix)) {
    return {
      kind: 'ready',
      message: 'Матрица Hermitian: A = A*.',
      repairHint: 'Off-diagonal entries стали комплексными сопряжениями.',
    }
  }
  return {
    kind: 'not-hermitian',
    message: 'Матрица выглядит симметричной, но A != A*: не хватает conjugate transpose.',
    repairHint: 'Поставь off-diagonal элементы как i и -i, а диагональ оставь вещественной.',
  }
}

export function diagnoseUnitaryMatrix(matrix: ComplexMatrix2x2): UnitaryDiagnosis {
  const columns = [
    [matrix.a, matrix.c] as ComplexVec2,
    [matrix.b, matrix.d] as ComplexVec2,
  ]
  if (columns.some((column) => complexVectorNorm(column) < unitaryUiTolerance)) {
    return {
      kind: 'zero-vector',
      message: 'Один из столбцов почти нулевой: unitary basis потерян.',
      repairHint: 'Верни оба столбца ненулевыми.',
    }
  }
  if (!isUnitaryMatrix(matrix)) {
    return {
      kind: 'not-unitary',
      message: 'Матрица не unitary: U*U еще не равно I.',
      repairHint: 'Сохраняй не одну длину, а весь Hermitian inner product.',
    }
  }
  return {
    kind: 'ready',
    message: 'U*U = I: унитарное движение сохраняет Hermitian geometry.',
    repairHint: 'Фаза может меняться, но норма и углы остаются.',
  }
}

export function diagnoseAStarABridge(choice: AStarChoice, matrix: ComplexMatrix2x2): UnitaryDiagnosis {
  const result = matrixByAStarChoice(matrix, choice)
  if (choice !== 'astar-a') {
    return {
      kind: choice === 'ata' ? 'not-hermitian' : 'not-positive-semidefinite',
      message: choice === 'ata' ? 'A^T A использует transpose без сопряжения.' : 'AA* живет на выходе, а здесь нужны правые сингулярные направления.',
      repairHint: 'Для SVD-входных направлений выбери A* A.',
    }
  }
  if (!isPositiveSemidefiniteHermitian(result)) {
    return {
      kind: 'not-positive-semidefinite',
      message: 'A* A должен быть Hermitian positive semidefinite, но проверка не прошла.',
      repairHint: 'Проверь adjoint: нужен conjugate transpose.',
    }
  }
  const [lambda1, lambda2] = hermitianMatrixEigenvalues2(result)
  return {
    kind: 'ready',
    message: `A* A готов: eigenvalues = ${formatUnitaryNumber(lambda1)}, ${formatUnitaryNumber(lambda2)}.`,
    repairHint: 'Их корни становятся singular values в SVD.',
  }
}
