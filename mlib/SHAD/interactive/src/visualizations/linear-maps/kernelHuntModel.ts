export type Vec3 = [number, number, number]
export type Vec2 = [number, number]

export const kernelDirection: Vec3 = [-1, 1, -1]
export const kernelEpsilon = 0.08
const residualEpsilon = 0.08

export type KernelDiagnosisKind =
  | 'in-progress'
  | 'success'
  | 'zero-vector'
  | 'first-equation-error'
  | 'second-equation-error'
  | 'both-equations-error'
  | 'same-solution-scale-needed'
  | 'basis-scale-error'
  | 'rank-nullity-not-ready'

export type KernelDiagnosis = {
  kind: KernelDiagnosisKind
  message: string
  repairHint: string
  residual: Vec2
  parameter: number
}

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

export function diagnoseKernelState({
  levelId,
  candidate,
  completedLevelIds,
  touched,
}: {
  levelId: string
  candidate: Vec3
  completedLevelIds: readonly string[]
  touched: boolean
}): KernelDiagnosis {
  const currentResidual = residual(candidate)
  const firstOk = Math.abs(currentResidual[0]) < residualEpsilon
  const secondOk = Math.abs(currentResidual[1]) < residualEpsilon
  const zero = isZeroVector(candidate)
  const onKernel = isOnKernel(candidate)
  const parameter = kernelParameter(candidate)
  const success = kernelLevelSuccess({ levelId, candidate, completedLevelIds })

  if (success) {
    return {
      kind: 'success',
      message: `Вектор лежит в ядре: x = ${formatKernelNumber(parameter)}(-1, 1, -1).`,
      repairHint: 'Можно переходить к следующему уровню.',
      residual: currentResidual,
      parameter,
    }
  }

  if (!touched) {
    return {
      kind: 'in-progress',
      message: 'Вектор еще не проверен: нужно занулить обе строки Ax.',
      repairHint: 'Начни с уравнений x + y = 0 и x - z = 0.',
      residual: currentResidual,
      parameter,
    }
  }

  if (zero) {
    return {
      kind: 'zero-vector',
      message: 'Нулевой вектор зануляет Ax, но не задает направление ядра.',
      repairHint: 'Сохрани оба остатка нулевыми, но сделай координаты ненулевыми.',
      residual: currentResidual,
      parameter,
    }
  }

  if (!firstOk && !secondOk) {
    return {
      kind: 'both-equations-error',
      message: 'Обе строки Ax еще ненулевые: нарушены x + y и x - z.',
      repairHint: 'Подбирай y = -x и z = x одновременно.',
      residual: currentResidual,
      parameter,
    }
  }

  if (!firstOk) {
    return {
      kind: 'first-equation-error',
      message: 'Первое уравнение еще не занулено: x + y ≠ 0.',
      repairHint: 'Исправь y так, чтобы он стал равен -x.',
      residual: currentResidual,
      parameter,
    }
  }

  if (!secondOk) {
    return {
      kind: 'second-equation-error',
      message: 'Второе уравнение еще не занулено: x - z ≠ 0.',
      repairHint: 'Исправь z так, чтобы он стал равен x.',
      residual: currentResidual,
      parameter,
    }
  }

  if (levelId === 'solution-line' && Math.abs(parameter) <= 1.4) {
    return {
      kind: 'same-solution-scale-needed',
      message: 'Ты снова попал в ядро, но нужен другой масштаб того же направления.',
      repairHint: 'Умножь найденное направление на число с модулем больше 1.4.',
      residual: currentResidual,
      parameter,
    }
  }

  if (levelId === 'kernel-basis' && onKernel) {
    return {
      kind: 'basis-scale-error',
      message: 'Направление верное, но для базиса нужен масштаб с координатами ±1.',
      repairHint: 'Приведи вектор к (-1, 1, -1) или противоположному.',
      residual: currentResidual,
      parameter,
    }
  }

  if (levelId === 'rank-nullity') {
    return {
      kind: 'rank-nullity-not-ready',
      message: 'Финальное равенство откроется после трех предыдущих уровней.',
      repairHint: 'Собери ненулевой вектор, второй масштаб и базис ядра.',
      residual: currentResidual,
      parameter,
    }
  }

  return {
    kind: 'in-progress',
    message: 'Обе строки почти занулены, но условие уровня еще не выполнено.',
    repairHint: 'Проверь масштаб и ненулевость вектора.',
    residual: currentResidual,
    parameter,
  }
}

export function formatKernelNumber(value: number): string {
  return Math.abs(value) < 0.005 ? '0.00' : value.toFixed(2)
}
