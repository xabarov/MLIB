export type Vec2 = [number, number]

export type GradientLevelId = 'roll-to-min' | 'tame-the-step' | 'narrow-valley'

export type GradientDiagnosisKind =
  | 'idle'
  | 'success'
  | 'exploded'
  | 'oscillating'
  | 'too-slow'

export type GradientDiagnosis = {
  kind: GradientDiagnosisKind
  message: string
  repairHint: string
}

/** Bowl f(x, y) = a x^2 + b y^2 with minimum at the origin. */
export type Surface = { a: number; b: number }

export type GradientLevelConfig = {
  id: GradientLevelId
  surface: Surface
  start: Vec2
  steps: number
  tolerance: number
  seed?: never
}

export const gradientLevels: Record<GradientLevelId, GradientLevelConfig> = {
  'roll-to-min': {
    id: 'roll-to-min',
    surface: { a: 1, b: 1 },
    start: [2.4, 1.8],
    steps: 26,
    tolerance: 0.12,
  },
  'tame-the-step': {
    id: 'tame-the-step',
    surface: { a: 2, b: 2 },
    start: [2.8, 2.4],
    steps: 26,
    tolerance: 0.12,
  },
  'narrow-valley': {
    id: 'narrow-valley',
    surface: { a: 1, b: 8 },
    start: [2.5, 1.4],
    steps: 34,
    tolerance: 0.16,
  },
}

export const DIVERGE_LIMIT = 1e3
export const learningRateStops = { min: 0.02, max: 0.8, step: 0.01 }

export function surfaceValue(s: Surface, [x, y]: Vec2): number {
  return s.a * x * x + s.b * y * y
}

export function gradient(s: Surface, [x, y]: Vec2): Vec2 {
  return [2 * s.a * x, 2 * s.b * y]
}

export function gradientStep(s: Surface, point: Vec2, lr: number): Vec2 {
  const g = gradient(s, point)
  return [point[0] - lr * g[0], point[1] - lr * g[1]]
}

/** Trajectory of gradient descent, length steps + 1 (including the start). */
export function runDescent(s: Surface, start: Vec2, lr: number, steps: number): Vec2[] {
  const path: Vec2[] = [start]
  let point = start
  for (let i = 0; i < steps; i += 1) {
    point = gradientStep(s, point, lr)
    path.push(point)
    if (!Number.isFinite(point[0]) || Math.max(Math.abs(point[0]), Math.abs(point[1])) > DIVERGE_LIMIT) {
      break
    }
  }
  return path
}

export function distanceToMin(point: Vec2): number {
  return Math.hypot(point[0], point[1])
}

export function hasDiverged(path: Vec2[]): boolean {
  const last = path[path.length - 1]
  return (
    !Number.isFinite(last[0]) ||
    !Number.isFinite(last[1]) ||
    Math.max(Math.abs(last[0]), Math.abs(last[1])) > DIVERGE_LIMIT
  )
}

/** True if some coordinate changes sign between consecutive steps (overshoot). */
export function isOscillating(path: Vec2[]): boolean {
  for (let i = 1; i < path.length; i += 1) {
    for (let axis = 0; axis < 2; axis += 1) {
      const prev = path[i - 1][axis]
      const curr = path[i][axis]
      if (prev * curr < 0 && Math.abs(prev) > 1e-6) return true
    }
  }
  return false
}

export function gradientLevelSuccess({
  levelId,
  lr,
}: {
  levelId: GradientLevelId
  lr: number
}): boolean {
  const config = gradientLevels[levelId]
  const path = runDescent(config.surface, config.start, lr, config.steps)
  if (hasDiverged(path)) return false
  return distanceToMin(path[path.length - 1]) <= config.tolerance
}

export function diagnoseGradient({
  levelId,
  lr,
  touched,
}: {
  levelId: GradientLevelId
  lr: number
  touched: boolean
}): GradientDiagnosis {
  const config = gradientLevels[levelId]
  if (!touched) {
    return {
      kind: 'idle',
      message: 'Запусти спуск: выбери шаг и смотри, как точка катится к минимуму.',
      repairHint: 'Двигай learning rate и наблюдай траекторию.',
    }
  }
  const path = runDescent(config.surface, config.start, lr, config.steps)
  if (gradientLevelSuccess({ levelId, lr })) {
    return {
      kind: 'success',
      message: 'Точка устойчиво скатилась в минимум.',
      repairHint: 'Шаг попал в окно сходимости.',
    }
  }
  if (hasDiverged(path)) {
    return {
      kind: 'exploded',
      message: 'Шаг слишком большой: траектория улетела в бесконечность.',
      repairHint: 'Уменьши learning rate: большой шаг перепрыгивает минимум всё дальше.',
    }
  }
  if (isOscillating(path)) {
    return {
      kind: 'oscillating',
      message: 'Точка скачет через минимум: шаг великоват для самой крутой оси.',
      repairHint: 'Самая узкая долина задаёт предел шага. Сделай learning rate меньше.',
    }
  }
  return {
    kind: 'too-slow',
    message: 'Спуск не доехал до минимума за отведённые шаги.',
    repairHint: 'Шаг слишком мал: увеличь learning rate, но не до колебаний.',
  }
}

export function formatGradientNumber(value: number): string {
  if (!Number.isFinite(value)) return 'inf'
  return Math.abs(value) < 0.005 ? '0.00' : value.toFixed(2)
}
