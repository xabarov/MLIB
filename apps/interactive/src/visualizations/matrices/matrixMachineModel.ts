export type Vec2 = [number, number]

export type Matrix2 = {
  u: Vec2
  v: Vec2
}

export type MatrixMachineTarget = Matrix2 & {
  id: string
  /**
   * Challenge levels hide the per-column guide dots and the inline numeric
   * target. The goal becomes matching the image of the unit square, so both
   * columns must be reconstructed instead of dragged onto a visible marker.
   */
  challenge?: boolean
}

export type MatrixMachineDiagnosisKind =
  | 'success'
  | 'in-progress'
  | 'swapped-columns'
  | 'wrong-first-column'
  | 'wrong-second-column'
  | 'wrong-direction'
  | 'wrong-length'

export type MatrixMachineDiagnosis = {
  kind: MatrixMachineDiagnosisKind
  message: string
  repairHint: string
}

export const matrixMachineTargets: Record<string, MatrixMachineTarget> = {
  'stretch-x': { id: 'stretch-x', u: [2, 0], v: [0, 1] },
  'shear-y': { id: 'shear-y', u: [1, 0], v: [1, 1] },
  'flip-x': { id: 'flip-x', u: [-1, 0], v: [0, 1] },
  'quarter-turn': { id: 'quarter-turn', u: [0, 1], v: [-1, 0] },
  // Challenge levels: both columns are off-axis, so no level can be solved by
  // nudging a single handle onto an identity default.
  parallelogram: { id: 'parallelogram', u: [2, 1], v: [1, 2], challenge: true },
  'rotate-stretch': { id: 'rotate-stretch', u: [1, 1], v: [-1, 1], challenge: true },
}

const snap = 0.25
const gridLimit = 3
const epsilon = 0.08

export function snapMatrixCoord(value: number): number {
  return Math.max(-gridLimit, Math.min(gridLimit, Math.round(value / snap) * snap))
}

export function matrixFromColumns(u: Vec2, v: Vec2): [[number, number], [number, number]] {
  return [
    [u[0], v[0]],
    [u[1], v[1]],
  ]
}

/**
 * Image of the unit square under the matrix with columns u, v: the polygon
 * 0 -> u -> u+v -> v. Used to show "matrix as a machine acting on a shape".
 */
export function unitSquareImage(u: Vec2, v: Vec2): Vec2[] {
  return [
    [0, 0],
    [u[0], u[1]],
    [u[0] + v[0], u[1] + v[1]],
    [v[0], v[1]],
  ]
}

export function distance(a: Vec2, b: Vec2): number {
  return Math.hypot(a[0] - b[0], a[1] - b[1])
}

export function targetError(levelId: string, u: Vec2, v: Vec2): number {
  const target = matrixMachineTargets[levelId]
  if (!target) return Number.POSITIVE_INFINITY
  return Math.max(distance(u, target.u), distance(v, target.v))
}

export function matrixMachineLevelSuccess(levelId: string, u: Vec2, v: Vec2): boolean {
  return targetError(levelId, u, v) < epsilon
}

export function sameDirection(a: Vec2, b: Vec2): boolean {
  const cross = Math.abs(a[0] * b[1] - a[1] * b[0])
  const dot = a[0] * b[0] + a[1] * b[1]
  return cross < epsilon && dot > 0
}

export function diagnoseMatrixMachineState({
  levelId,
  u,
  v,
  touched,
}: {
  levelId: string
  u: Vec2
  v: Vec2
  touched: boolean
}): MatrixMachineDiagnosis {
  const target = matrixMachineTargets[levelId]
  if (!target) {
    return {
      kind: 'in-progress',
      message: 'Цель уровня не найдена.',
      repairHint: 'Вернись на карту курса и открой миссию заново.',
    }
  }

  if (matrixMachineLevelSuccess(levelId, u, v)) {
    return {
      kind: 'success',
      message: 'Оба образа базиса совпали с целевой матрицей.',
      repairHint: 'Можно переходить к следующему уровню.',
    }
  }

  if (!touched) {
    return {
      kind: 'in-progress',
      message: 'Матрица еще не настроена: двигай образы e1 и e2.',
      repairHint: 'Начни с того столбца, который отличается от бледной направляющей.',
    }
  }

  const uError = distance(u, target.u)
  const vError = distance(v, target.v)
  const swapped = distance(u, target.v) < epsilon && distance(v, target.u) < epsilon

  if (swapped) {
    return {
      kind: 'swapped-columns',
      message: 'Образы e1 и e2 перепутаны местами.',
      repairHint: 'Оранжевый вектор отвечает за первый столбец, синий - за второй.',
    }
  }

  if (sameDirection(u, target.u) && uError >= epsilon) {
    return {
      kind: 'wrong-length',
      message: 'Направление A e1 верное, но длина первого столбца еще не совпала.',
      repairHint: 'Дотяни оранжевую ручку вдоль той же прямой до целевой отметки.',
    }
  }

  if (sameDirection(v, target.v) && vError >= epsilon) {
    return {
      kind: 'wrong-length',
      message: 'Направление A e2 верное, но длина второго столбца еще не совпала.',
      repairHint: 'Дотяни синюю ручку вдоль той же прямой до целевой отметки.',
    }
  }

  if (uError >= epsilon && vError < epsilon) {
    return {
      kind: 'wrong-first-column',
      message: 'Второй столбец уже собран, ошибка осталась в A e1.',
      repairHint: 'Исправляй оранжевую ручку: это образ первого базисного вектора.',
    }
  }

  if (vError >= epsilon && uError < epsilon) {
    return {
      kind: 'wrong-second-column',
      message: 'Первый столбец уже собран, ошибка осталась в A e2.',
      repairHint: 'Исправляй синюю ручку: это образ второго базисного вектора.',
    }
  }

  return {
    kind: 'wrong-direction',
    message: 'Хотя бы один образ базиса смотрит не в целевом направлении.',
    repairHint: 'Сначала совмести направление с бледной направляющей, потом длину.',
  }
}

export function formatMatrixNumber(value: number): string {
  return Math.abs(value) < 0.005 ? '0.00' : value.toFixed(2)
}

export function svgPointToMatrixCoord({
  clientX,
  clientY,
  rect,
}: {
  clientX: number
  clientY: number
  rect: Pick<DOMRect, 'left' | 'top' | 'width' | 'height'>
}): Vec2 {
  const x = ((clientX - rect.left) / rect.width) * 8 - 4
  const y = 4 - ((clientY - rect.top) / rect.height) * 8
  return [snapMatrixCoord(x), snapMatrixCoord(y)]
}
