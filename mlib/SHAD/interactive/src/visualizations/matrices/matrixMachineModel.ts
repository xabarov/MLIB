export type Vec2 = [number, number]

export type Matrix2 = {
  u: Vec2
  v: Vec2
}

export type MatrixMachineTarget = Matrix2 & {
  id: string
}

export const matrixMachineTargets: Record<string, MatrixMachineTarget> = {
  'stretch-x': { id: 'stretch-x', u: [2, 0], v: [0, 1] },
  'shear-y': { id: 'shear-y', u: [1, 0], v: [1, 1] },
  'flip-x': { id: 'flip-x', u: [-1, 0], v: [0, 1] },
  'quarter-turn': { id: 'quarter-turn', u: [0, 1], v: [-1, 0] },
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
