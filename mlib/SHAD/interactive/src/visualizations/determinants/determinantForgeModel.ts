export type Vec2 = [number, number]

export const determinantGridLimit = 3
export const determinantSnap = 0.25

export function determinant(u: Vec2, v: Vec2): number {
  return u[0] * v[1] - v[0] * u[1]
}

export function determinantArea(u: Vec2, v: Vec2): number {
  return Math.abs(determinant(u, v))
}

export function isDegenerate(u: Vec2, v: Vec2): boolean {
  return determinantArea(u, v) < 0.05
}

export function snapCoord(value: number): number {
  return Math.max(
    -determinantGridLimit,
    Math.min(determinantGridLimit, Math.round(value / determinantSnap) * determinantSnap),
  )
}

export function determinantLevelSuccess({
  levelId,
  u,
  v,
  completedLevelIds,
}: {
  levelId: string
  u: Vec2
  v: Vec2
  completedLevelIds: readonly string[]
}): boolean {
  const det = determinant(u, v)
  const area = Math.abs(det)
  const degenerate = area < 0.05
  if (levelId === 'area-two') return Math.abs(area - 2) < 0.05
  if (levelId === 'flip-orientation') return det < -0.5 && area > 1
  if (levelId === 'break-invertibility') return degenerate
  if (levelId === 'repair-matrix') {
    return completedLevelIds.includes('break-invertibility') && area > 0.5
  }
  return false
}

export function formatDeterminantNumber(value: number): string {
  return Math.abs(value) < 0.005 ? '0.00' : value.toFixed(2)
}

export function svgPointToCoord({
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
  return [snapCoord(x), snapCoord(y)]
}
