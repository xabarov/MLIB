export type Vec3 = [number, number, number]
export type Vec2 = [number, number]

export const kernelDirection: Vec3 = [-1, 1, -1]
export const kernelEpsilon = 0.08

const directionNormSq = 3

export function residual(candidate: Vec3): Vec2 {
  const [x, y, z] = candidate
  return [x + y, x - z]
}

export function norm(values: readonly number[]): number {
  return Math.sqrt(values.reduce((sum, value) => sum + value * value, 0))
}

export function projectionToKernel(candidate: Vec3): Vec3 {
  const dot =
    candidate[0] * kernelDirection[0] +
    candidate[1] * kernelDirection[1] +
    candidate[2] * kernelDirection[2]
  const t = dot / directionNormSq
  return [kernelDirection[0] * t, kernelDirection[1] * t, kernelDirection[2] * t]
}

export function kernelParameter(candidate: Vec3): number {
  return projectionToKernel(candidate)[0] / kernelDirection[0]
}

export function isZeroVector(candidate: Vec3, epsilon = kernelEpsilon): boolean {
  return norm(candidate) <= epsilon
}

export function errorToKernel(candidate: Vec3): number {
  return norm(residual(candidate))
}

export function isOnKernel(candidate: Vec3, epsilon = kernelEpsilon): boolean {
  return errorToKernel(candidate) < epsilon && !isZeroVector(candidate, epsilon)
}

export function isBasisAligned(candidate: Vec3): boolean {
  return (
    isOnKernel(candidate) &&
    Math.abs(Math.abs(candidate[0]) - 1) < 0.12 &&
    Math.abs(Math.abs(candidate[1]) - 1) < 0.12 &&
    Math.abs(Math.abs(candidate[2]) - 1) < 0.12
  )
}

export function kernelLevelSuccess({
  levelId,
  candidate,
  completedLevelIds,
}: {
  levelId: string
  candidate: Vec3
  completedLevelIds: readonly string[]
}): boolean {
  const onKernel = isOnKernel(candidate)
  if (levelId === 'nonzero-zero') return onKernel
  if (levelId === 'solution-line') return onKernel && Math.abs(kernelParameter(candidate)) > 1.4
  if (levelId === 'kernel-basis') return isBasisAligned(candidate)
  if (levelId === 'rank-nullity') {
    return (
      completedLevelIds.includes('nonzero-zero') &&
      completedLevelIds.includes('solution-line') &&
      completedLevelIds.includes('kernel-basis') &&
      onKernel
    )
  }
  return false
}

export function formatKernelNumber(value: number): string {
  return Math.abs(value) < 0.005 ? '0.00' : value.toFixed(2)
}
