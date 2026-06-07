export type MatrixData = number[][]

export type LowRankComponent = {
  index: number
  sigma: number
  left: number[]
  right: number[]
  energy: number
}

export type CompressionResult = {
  rank: number
  selectedIndexes: number[]
  reconstruction: MatrixData
  residual: MatrixData
  frobeniusError: number
  retainedEnergy: number
  storageCost: number
  compressionRatio: number
  maxCellError: number
}

export type CompressionDiagnosisKind =
  | 'ready'
  | 'over-budget'
  | 'underfit'
  | 'local-artifact'
  | 'mean-not-centered'
  | 'component-mismatch'

export type CompressionDiagnosis = {
  kind: CompressionDiagnosisKind
  message: string
  repairHint: string
}

export const compressionTolerance = 1e-8
export const compressionUiTolerance = 0.04

export const glyphMatrix: MatrixData = [
  [0.9, 0.9, 0.2, 0.1, 0.1, 0.1],
  [0.9, 0.7, 0.4, 0.1, 0.1, 0.1],
  [0.9, 0.2, 0.9, 0.4, 0.1, 0.1],
  [0.9, 0.2, 0.4, 0.9, 0.4, 0.1],
  [0.9, 0.2, 0.1, 0.4, 0.9, 0.4],
  [0.9, 0.2, 0.1, 0.1, 0.4, 0.9],
]

export const detailMatrix: MatrixData = [
  [0.9, 0.9, 0.25, 0.1, 0.1, 0.1],
  [0.9, 0.7, 0.45, 0.1, 0.1, 0.1],
  [0.9, 0.2, 1.0, 0.4, 0.1, 0.1],
  [0.9, 0.2, 0.4, 0.95, 0.4, 0.1],
  [0.9, 0.2, 0.1, 0.4, 0.9, 0.75],
  [0.9, 0.2, 0.1, 0.1, 0.75, 0.95],
]

export const shiftedCloudMatrix: MatrixData = [
  [3.2, 1.1],
  [3.55, 1.18],
  [3.85, 1.45],
  [4.2, 1.68],
  [4.55, 1.95],
  [4.9, 2.2],
  [5.25, 2.5],
  [5.55, 2.72],
]

export function shape(matrix: MatrixData): [number, number] {
  return [matrix.length, matrix[0]?.length ?? 0]
}

export function cloneMatrix(matrix: MatrixData): MatrixData {
  return matrix.map((row) => [...row])
}

export function zeroMatrix(rows: number, cols: number): MatrixData {
  return Array.from({ length: rows }, () => Array.from({ length: cols }, () => 0))
}

export function matrixMeans(matrix: MatrixData): number[] {
  const [rows, cols] = shape(matrix)
  if (rows === 0) return []
  return Array.from({ length: cols }, (_, col) =>
    matrix.reduce((sum, row) => sum + (row[col] ?? 0), 0) / rows,
  )
}

export function centerColumns(matrix: MatrixData): { centered: MatrixData; means: number[] } {
  const means = matrixMeans(matrix)
  return {
    means,
    centered: matrix.map((row) => row.map((value, col) => value - means[col])),
  }
}

export function uncenterColumns(matrix: MatrixData, means: number[]): MatrixData {
  return matrix.map((row) => row.map((value, col) => value + (means[col] ?? 0)))
}

export function subtractMatrices(left: MatrixData, right: MatrixData): MatrixData {
  return left.map((row, rowIndex) =>
    row.map((value, colIndex) => value - (right[rowIndex]?.[colIndex] ?? 0)),
  )
}

export function addMatrices(left: MatrixData, right: MatrixData): MatrixData {
  return left.map((row, rowIndex) =>
    row.map((value, colIndex) => value + (right[rowIndex]?.[colIndex] ?? 0)),
  )
}

export function scaleMatrix(matrix: MatrixData, scale: number): MatrixData {
  return matrix.map((row) => row.map((value) => value * scale))
}

export function frobeniusNorm(matrix: MatrixData): number {
  return Math.sqrt(matrix.reduce((sum, row) => sum + row.reduce((inner, value) => inner + value * value, 0), 0))
}

export function maxAbsCell(matrix: MatrixData): number {
  return matrix.reduce(
    (max, row) => Math.max(max, ...row.map((value) => Math.abs(value))),
    0,
  )
}

export function normalizeMatrixForHeatmap(matrix: MatrixData): MatrixData {
  const max = maxAbsCell(matrix)
  if (max < compressionTolerance) return cloneMatrix(matrix)
  return scaleMatrix(matrix, 1 / max)
}

export function transpose(matrix: MatrixData): MatrixData {
  const [rows, cols] = shape(matrix)
  return Array.from({ length: cols }, (_, col) =>
    Array.from({ length: rows }, (_, row) => matrix[row]?.[col] ?? 0),
  )
}

export function multiplyMatrices(left: MatrixData, right: MatrixData): MatrixData {
  const [leftRows, shared] = shape(left)
  const [, rightCols] = shape(right)
  return Array.from({ length: leftRows }, (_, row) =>
    Array.from({ length: rightCols }, (_, col) => {
      let sum = 0
      for (let index = 0; index < shared; index += 1) {
        sum += (left[row]?.[index] ?? 0) * (right[index]?.[col] ?? 0)
      }
      return sum
    }),
  )
}

function dot(left: number[], right: number[]): number {
  return left.reduce((sum, value, index) => sum + value * (right[index] ?? 0), 0)
}

function vectorNorm(vector: number[]): number {
  return Math.sqrt(dot(vector, vector))
}

function normalizeVector(vector: number[]): number[] {
  const length = vectorNorm(vector)
  if (length < compressionTolerance) {
    return vector.map((_, index) => (index === 0 ? 1 : 0))
  }
  return vector.map((value) => value / length)
}

function matrixVectorMultiply(matrix: MatrixData, vector: number[]): number[] {
  return matrix.map((row) => dot(row, vector))
}

function outerProduct(left: number[], right: number[], scale: number): MatrixData {
  return left.map((leftValue) => right.map((rightValue) => scale * leftValue * rightValue))
}

function identity(size: number): MatrixData {
  return Array.from({ length: size }, (_, row) =>
    Array.from({ length: size }, (_, col) => (row === col ? 1 : 0)),
  )
}

function jacobiEigenSymmetric(matrix: MatrixData): { values: number[]; vectors: MatrixData } {
  const size = matrix.length
  const a = cloneMatrix(matrix)
  const vectors = identity(size)
  const maxIterations = size * size * 24

  for (let iteration = 0; iteration < maxIterations; iteration += 1) {
    let p = 0
    let q = 1
    let max = 0
    for (let row = 0; row < size; row += 1) {
      for (let col = row + 1; col < size; col += 1) {
        const value = Math.abs(a[row][col])
        if (value > max) {
          max = value
          p = row
          q = col
        }
      }
    }

    if (max < compressionTolerance) break

    const app = a[p][p]
    const aqq = a[q][q]
    const apq = a[p][q]
    const angle = 0.5 * Math.atan2(2 * apq, aqq - app)
    const c = Math.cos(angle)
    const s = Math.sin(angle)

    for (let row = 0; row < size; row += 1) {
      if (row !== p && row !== q) {
        const arp = a[row][p]
        const arq = a[row][q]
        a[row][p] = c * arp - s * arq
        a[p][row] = a[row][p]
        a[row][q] = s * arp + c * arq
        a[q][row] = a[row][q]
      }
    }

    a[p][p] = c * c * app - 2 * s * c * apq + s * s * aqq
    a[q][q] = s * s * app + 2 * s * c * apq + c * c * aqq
    a[p][q] = 0
    a[q][p] = 0

    for (let row = 0; row < size; row += 1) {
      const vrp = vectors[row][p]
      const vrq = vectors[row][q]
      vectors[row][p] = c * vrp - s * vrq
      vectors[row][q] = s * vrp + c * vrq
    }
  }

  return {
    values: a.map((row, index) => Math.max(0, row[index])),
    vectors,
  }
}

export function svdSmallMatrix(matrix: MatrixData): LowRankComponent[] {
  const [rows, cols] = shape(matrix)
  if (rows === 0 || cols === 0) return []
  const ata = multiplyMatrices(transpose(matrix), matrix)
  const eigen = jacobiEigenSymmetric(ata)

  return eigen.values
    .map((lambda, index) => {
      const right = normalizeVector(eigen.vectors.map((row) => row[index]))
      const sigma = Math.sqrt(Math.max(0, lambda))
      const left =
        sigma > compressionTolerance
          ? matrixVectorMultiply(matrix, right).map((value) => value / sigma)
          : Array.from({ length: rows }, (_, row) => (row === index ? 1 : 0))
      return {
        index,
        sigma,
        left: normalizeVector(left),
        right,
        energy: sigma * sigma,
      }
    })
    .sort((left, right) => right.sigma - left.sigma)
    .map((component, index) => ({ ...component, index }))
}

export function reconstructFromComponents(
  components: LowRankComponent[],
  selectedIndexes: number[],
  rows: number,
  cols: number,
): MatrixData {
  const selected = new Set(selectedIndexes)
  return components.reduce((sum, component) => {
    if (!selected.has(component.index)) return sum
    return addMatrices(sum, outerProduct(component.left, component.right, component.sigma))
  }, zeroMatrix(rows, cols))
}

export function storageCost(rows: number, cols: number, k: number): number {
  return k * (rows + cols + 1)
}

export function compressionRatio(rows: number, cols: number, k: number): number {
  const raw = rows * cols
  if (raw === 0) return 1
  return storageCost(rows, cols, k) / raw
}

export function compressionResult(
  matrix: MatrixData,
  selectedIndexes: number[],
): CompressionResult {
  const [rows, cols] = shape(matrix)
  const components = svdSmallMatrix(matrix)
  const selected = selectedIndexes.filter((index) => index >= 0 && index < components.length)
  const reconstruction = reconstructFromComponents(components, selected, rows, cols)
  const residual = subtractMatrices(matrix, reconstruction)
  const totalEnergy = components.reduce((sum, component) => sum + component.energy, 0)
  const retained = selected.reduce((sum, index) => sum + (components[index]?.energy ?? 0), 0)

  return {
    rank: selected.length,
    selectedIndexes: selected,
    reconstruction,
    residual,
    frobeniusError: frobeniusNorm(residual),
    retainedEnergy: totalEnergy < compressionTolerance ? 1 : retained / totalEnergy,
    storageCost: storageCost(rows, cols, selected.length),
    compressionRatio: compressionRatio(rows, cols, selected.length),
    maxCellError: maxAbsCell(residual),
  }
}

export function rankKReconstruction(matrix: MatrixData, k: number): CompressionResult {
  const components = svdSmallMatrix(matrix)
  const selected = components.slice(0, Math.max(0, k)).map((component) => component.index)
  return compressionResult(matrix, selected)
}

export function diagnoseCompressionBudget(
  result: CompressionResult,
  {
    maxStorage,
    minRetainedEnergy,
    maxCellError,
  }: {
    maxStorage: number
    minRetainedEnergy: number
    maxCellError: number
  },
): CompressionDiagnosis {
  if (result.storageCost > maxStorage) {
    return {
      kind: 'over-budget',
      message: 'Storage budget exceeded.',
      repairHint: 'Сними лишнюю компоненту или уменьши rank.',
    }
  }
  if (result.retainedEnergy < minRetainedEnergy) {
    return {
      kind: 'underfit',
      message: 'Too much energy was removed.',
      repairHint: 'Верни компоненту, которая держит основной stroke.',
    }
  }
  if (result.maxCellError > maxCellError) {
    return {
      kind: 'local-artifact',
      message: 'Total energy is acceptable, but one cell artifact is too high.',
      repairHint: 'Проверь residual map и верни компоненту, которая чинит яркую клетку.',
    }
  }
  return {
    kind: 'ready',
    message: 'Compression fits the quality gate.',
    repairHint: 'Можно переходить дальше.',
  }
}

export function diagnoseCentering(raw: MatrixData, centered: boolean): CompressionDiagnosis {
  if (!centered) {
    const means = matrixMeans(raw)
    const meanEnergy = means.reduce((sum, value) => sum + value * value, 0)
    if (meanEnergy > 1) {
      return {
        kind: 'mean-not-centered',
        message: 'Mean shift dominates the first component.',
        repairHint: 'Включи centering, чтобы PCA ловила разброс вокруг среднего.',
      }
    }
  }
  return {
    kind: 'ready',
    message: 'Centered PCA can track variance instead of mean shift.',
    repairHint: 'Оцени retained variance after projection.',
  }
}

export function projectRowsToComponents(matrix: MatrixData, components: LowRankComponent[], k: number): MatrixData {
  const selected = components.slice(0, Math.max(0, k))
  return matrix.map((row) => selected.map((component) => dot(row, component.right)))
}

export function reconstructionErrorForCenteredRank(raw: MatrixData, k: number, centered: boolean): CompressionResult {
  if (!centered) return rankKReconstruction(raw, k)
  const { centered: centeredMatrix, means } = centerColumns(raw)
  const centeredResult = rankKReconstruction(centeredMatrix, k)
  const reconstruction = uncenterColumns(centeredResult.reconstruction, means)
  const residual = subtractMatrices(raw, reconstruction)
  return {
    ...centeredResult,
    reconstruction,
    residual,
    frobeniusError: frobeniusNorm(residual),
    maxCellError: maxAbsCell(residual),
  }
}

export function formatCompressionNumber(value: number): string {
  if (!Number.isFinite(value)) return 'inf'
  if (Math.abs(value) < 0.005) return '0.00'
  return value.toFixed(2)
}
