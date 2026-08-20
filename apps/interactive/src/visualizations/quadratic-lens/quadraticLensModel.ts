export type Vec2 = [number, number]

export type Symmetric2x2 = {
  a: number
  b: number
  c: number
}

export type QuadraticClassification =
  | 'positive-definite'
  | 'negative-definite'
  | 'indefinite'
  | 'positive-semidefinite'
  | 'negative-semidefinite'
  | 'zero'

export type SignatureLabel = '(+,+)' | '(-,-)' | '(+,-)' | '(+,0)' | '(-,0)' | '(0,0)'

export type EigenPair2D = {
  lambda: number
  vector: Vec2
}

export type LevelSetBranch = {
  id: string
  points: Vec2[]
}

export type QuadraticDiagnosisKind =
  | 'success'
  | 'in-progress'
  | 'not-positive'
  | 'needs-rotation'
  | 'manual-zero-cross-term'
  | 'same-sign-directions'
  | 'zero-direction'
  | 'not-degenerate'
  | 'all-zero-form'
  | 'wrong-signature'
  | 'near-boundary'

export type QuadraticDiagnosis = {
  kind: QuadraticDiagnosisKind
  message: string
  repairHint: string
}

export const quadraticTolerance = 1e-6
export const quadraticUiTolerance = 0.08
export const quadraticSnap = 0.1
export const quadraticGridLimit = 3

const twoPi = Math.PI * 2

export function snapQuadraticValue(value: number): number {
  return Math.max(
    -quadraticGridLimit,
    Math.min(quadraticGridLimit, Math.round(value / quadraticSnap) * quadraticSnap),
  )
}

export function clampQuadraticValue(value: number): number {
  return Math.max(-quadraticGridLimit, Math.min(quadraticGridLimit, value))
}

export function quadraticValue(form: Symmetric2x2, point: Vec2): number {
  const [x, y] = point
  return form.a * x * x + 2 * form.b * x * y + form.c * y * y
}

export function determinantOfForm(form: Symmetric2x2): number {
  return form.a * form.c - form.b * form.b
}

export function traceOfForm(form: Symmetric2x2): number {
  return form.a + form.c
}

export function vectorLength(vector: Vec2): number {
  return Math.hypot(vector[0], vector[1])
}

export function normalizeVector(vector: Vec2): Vec2 {
  const length = vectorLength(vector)
  if (length < quadraticTolerance) return [1, 0]
  return [vector[0] / length, vector[1] / length]
}

export function rotatePoint(point: Vec2, theta: number): Vec2 {
  const cos = Math.cos(theta)
  const sin = Math.sin(theta)
  return [cos * point[0] - sin * point[1], sin * point[0] + cos * point[1]]
}

export function rotateForm(form: Symmetric2x2, theta: number): Symmetric2x2 {
  const cos = Math.cos(theta)
  const sin = Math.sin(theta)
  return {
    a: form.a * cos * cos + 2 * form.b * sin * cos + form.c * sin * sin,
    b: form.b * (cos * cos - sin * sin) + (form.c - form.a) * sin * cos,
    c: form.a * sin * sin - 2 * form.b * sin * cos + form.c * cos * cos,
  }
}

export function eigenPairsSymmetric2x2(form: Symmetric2x2): [EigenPair2D, EigenPair2D] {
  const halfTrace = traceOfForm(form) / 2
  const halfDelta = (form.a - form.c) / 2
  const radius = Math.hypot(halfDelta, form.b)
  const lambda1 = halfTrace + radius
  const lambda2 = halfTrace - radius

  if (Math.abs(form.b) < quadraticTolerance && Math.abs(form.a - form.c) < quadraticTolerance) {
    return [
      { lambda: lambda1, vector: [1, 0] },
      { lambda: lambda2, vector: [0, 1] },
    ]
  }

  const vectorFor = (lambda: number): Vec2 => {
    if (Math.abs(form.b) > quadraticTolerance) {
      return normalizeVector([form.b, lambda - form.a])
    }
    return form.a >= form.c ? (lambda === lambda1 ? [1, 0] : [0, 1]) : lambda === lambda1 ? [0, 1] : [1, 0]
  }

  const first = vectorFor(lambda1)
  const second: Vec2 = [-first[1], first[0]]
  return [
    { lambda: lambda1, vector: first },
    { lambda: lambda2, vector: second },
  ]
}

export function principalAxisAngle(form: Symmetric2x2): number {
  const [principal] = eigenPairsSymmetric2x2(form)
  return Math.atan2(principal.vector[1], principal.vector[0])
}

export function classifyQuadraticForm(form: Symmetric2x2): QuadraticClassification {
  const [first, second] = eigenPairsSymmetric2x2(form)
  const values = [first.lambda, second.lambda]
  const positive = values.filter((value) => value > quadraticUiTolerance).length
  const negative = values.filter((value) => value < -quadraticUiTolerance).length

  if (positive === 2) return 'positive-definite'
  if (negative === 2) return 'negative-definite'
  if (positive > 0 && negative > 0) return 'indefinite'
  if (positive > 0) return 'positive-semidefinite'
  if (negative > 0) return 'negative-semidefinite'
  return 'zero'
}

export function signatureLabel(form: Symmetric2x2): SignatureLabel {
  const classification = classifyQuadraticForm(form)
  if (classification === 'positive-definite') return '(+,+)'
  if (classification === 'negative-definite') return '(-,-)'
  if (classification === 'indefinite') return '(+,-)'
  if (classification === 'positive-semidefinite') return '(+,0)'
  if (classification === 'negative-semidefinite') return '(-,0)'
  return '(0,0)'
}

export function formatQuadraticNumber(value: number): string {
  return Math.abs(value) < 0.005 ? '0.00' : value.toFixed(2)
}

export function angleDistance(a: number, b: number): number {
  const raw = Math.abs(((a - b + Math.PI) % twoPi) - Math.PI)
  return Math.min(raw, Math.abs(raw - Math.PI))
}

export function levelSetSample(
  form: Symmetric2x2,
  level = 1,
  options: { samples?: number; radius?: number } = {},
): LevelSetBranch[] {
  const samples = options.samples ?? 144
  const radius = options.radius ?? 3.2
  const pairs = eigenPairsSymmetric2x2(form)
  const angle = Math.atan2(pairs[0].vector[1], pairs[0].vector[0])
  const lambda1 = pairs[0].lambda
  const lambda2 = pairs[1].lambda

  if (Math.abs(lambda1) < quadraticUiTolerance && Math.abs(lambda2) < quadraticUiTolerance) {
    return []
  }

  if (lambda1 * level > quadraticUiTolerance && lambda2 * level > quadraticUiTolerance) {
    const rx = Math.sqrt(Math.abs(level / lambda1))
    const ry = Math.sqrt(Math.abs(level / lambda2))
    const points = Array.from({ length: samples + 1 }, (_, index) => {
      const t = (index / samples) * twoPi
      return rotatePoint([rx * Math.cos(t), ry * Math.sin(t)], angle)
    })
    return [{ id: 'ellipse', points }]
  }

  const branches: LevelSetBranch[] = []
  const sampleRange = Array.from({ length: samples }, (_, index) => {
    return -radius + (2 * radius * index) / (samples - 1)
  })

  const addBranch = (id: string, points: Vec2[]) => {
    const visible = points.filter(([x, y]) => Math.abs(x) <= radius && Math.abs(y) <= radius)
    if (visible.length > 1) branches.push({ id, points: visible })
  }

  if (Math.abs(lambda2) < quadraticUiTolerance && lambda1 * level > 0) {
    const x = Math.sqrt(Math.abs(level / lambda1))
    addBranch(
      'degenerate-positive',
      sampleRange.map((y) => rotatePoint([x, y], angle)),
    )
    addBranch(
      'degenerate-negative',
      sampleRange.map((y) => rotatePoint([-x, y], angle)),
    )
    return branches
  }

  if (Math.abs(lambda1) < quadraticUiTolerance && lambda2 * level > 0) {
    const y = Math.sqrt(Math.abs(level / lambda2))
    addBranch(
      'degenerate-positive',
      sampleRange.map((x) => rotatePoint([x, y], angle)),
    )
    addBranch(
      'degenerate-negative',
      sampleRange.map((x) => rotatePoint([x, -y], angle)),
    )
    return branches
  }

  if (lambda1 * level > 0 && lambda2 * level < 0) {
    const a = Math.sqrt(Math.abs(level / lambda1))
    const b = Math.sqrt(Math.abs(level / lambda2))
    const tValues = sampleRange.map((value) => value / 1.5)
    addBranch(
      'hyperbola-right',
      tValues.map((t) => rotatePoint([a * Math.cosh(t), b * Math.sinh(t)], angle)),
    )
    addBranch(
      'hyperbola-left',
      tValues.map((t) => rotatePoint([-a * Math.cosh(t), b * Math.sinh(t)], angle)),
    )
    return branches
  }

  if (lambda1 * level < 0 && lambda2 * level > 0) {
    const a = Math.sqrt(Math.abs(level / lambda2))
    const b = Math.sqrt(Math.abs(level / lambda1))
    const tValues = sampleRange.map((value) => value / 1.5)
    addBranch(
      'hyperbola-top',
      tValues.map((t) => rotatePoint([b * Math.sinh(t), a * Math.cosh(t)], angle)),
    )
    addBranch(
      'hyperbola-bottom',
      tValues.map((t) => rotatePoint([b * Math.sinh(t), -a * Math.cosh(t)], angle)),
    )
  }

  return branches
}

export function quadraticLevelSuccess({
  levelId,
  form,
  rotationAngle,
  positiveDirection,
  negativeDirection,
  nullDirection,
  touched,
}: {
  levelId: string
  form: Symmetric2x2
  rotationAngle: number
  positiveDirection: Vec2
  negativeDirection: Vec2
  nullDirection: Vec2
  touched: boolean
}): boolean {
  const classification = classifyQuadraticForm(form)
  const det = determinantOfForm(form)
  const rotated = rotateForm(form, rotationAngle)
  const originalHasCrossTerm = Math.abs(form.b) > 0.25

  if (levelId === 'positive-energy') {
    return touched && classification === 'positive-definite' && det > 0.25
  }
  if (levelId === 'cross-term-rotation') {
    return originalHasCrossTerm && Math.abs(rotated.b) < 0.04
  }
  if (levelId === 'saddle-signature') {
    return (
      classification === 'indefinite' &&
      vectorLength(positiveDirection) > 0.5 &&
      vectorLength(negativeDirection) > 0.5 &&
      quadraticValue(form, positiveDirection) > 0.4 &&
      quadraticValue(form, negativeDirection) < -0.4
    )
  }
  if (levelId === 'degenerate-direction') {
    const eigenvalues = eigenPairsSymmetric2x2(form).map((pair) => Math.abs(pair.lambda))
    return (
      classification === 'positive-semidefinite' &&
      Math.abs(det) < 0.08 &&
      Math.min(...eigenvalues) < 0.08 &&
      Math.max(...eigenvalues) > 0.5 &&
      vectorLength(nullDirection) > 0.5 &&
      Math.abs(quadraticValue(form, nullDirection)) < 0.08
    )
  }
  if (levelId === 'signature-repair') {
    return classification === 'indefinite' && signatureLabel(form) === '(+,-)' && Math.abs(det) > 0.4
  }
  return false
}

export function diagnoseQuadraticState({
  levelId,
  form,
  rotationAngle,
  positiveDirection,
  negativeDirection,
  nullDirection,
  touched,
}: {
  levelId: string
  form: Symmetric2x2
  rotationAngle: number
  positiveDirection: Vec2
  negativeDirection: Vec2
  nullDirection: Vec2
  touched: boolean
}): QuadraticDiagnosis {
  const success = quadraticLevelSuccess({
    levelId,
    form,
    rotationAngle,
    positiveDirection,
    negativeDirection,
    nullDirection,
    touched,
  })
  const classification = classifyQuadraticForm(form)
  const det = determinantOfForm(form)
  const rotated = rotateForm(form, rotationAngle)

  if (success) {
    return {
      kind: 'success',
      message: 'Форма попала в нужный геометрический режим.',
      repairHint: 'Можно переходить к следующему уровню.',
    }
  }

  if (!touched && levelId !== 'cross-term-rotation') {
    return {
      kind: 'in-progress',
      message: 'Форма еще не настроена под цель уровня.',
      repairHint: 'Начни с коэффициентов: они меняют эллипс, седло и вырожденные оси.',
    }
  }

  if (levelId === 'positive-energy') {
    if (Math.abs(det) < 0.12) {
      return {
        kind: 'near-boundary',
        message: 'Форма почти схлопнулась: determinant слишком близок к нулю.',
        repairHint: 'Сделай оба главных растяжения положительными и заметными.',
      }
    }
    return {
      kind: 'not-positive',
      message: 'Это еще не положительная энергия во всех направлениях.',
      repairHint: 'Нужны положительные собственные значения: добейся закрытого эллипса.',
    }
  }

  if (levelId === 'cross-term-rotation') {
    if (Math.abs(form.b) < 0.25) {
      return {
        kind: 'manual-zero-cross-term',
        message: 'Смешанный член исчез из самой формы, но уровень про поворот осей.',
        repairHint: 'Верни b заметным и вращай базис до нулевого смешивания.',
      }
    }
    return {
      kind: 'needs-rotation',
      message: `В повернутом базисе смешанный член еще равен ${formatQuadraticNumber(rotated.b)}.`,
      repairHint: 'Поворачивай оси до главного направления: там xy-член пропадает.',
    }
  }

  if (levelId === 'saddle-signature') {
    if (classification !== 'indefinite') {
      return {
        kind: 'wrong-signature',
        message: 'Форма пока не седловая: у нее нет двух знаков энергии.',
        repairHint: 'Сделай determinant отрицательным или выбери неопределенную заготовку.',
      }
    }
    if (vectorLength(positiveDirection) < 0.5 || vectorLength(negativeDirection) < 0.5) {
      return {
        kind: 'zero-direction',
        message: 'Один из маркеров слишком близко к нулю.',
        repairHint: 'Нужны настоящие ненулевые направления, а не начало координат.',
      }
    }
    return {
      kind: 'same-sign-directions',
      message: 'Два выбранных направления еще не показывают разные знаки.',
      repairHint: 'Поставь один маркер в положительную область, второй - в отрицательную.',
    }
  }

  if (levelId === 'degenerate-direction') {
    if (classification === 'zero') {
      return {
        kind: 'all-zero-form',
        message: 'Форма исчезла целиком, а нужен один потерянный измеряемый ход.',
        repairHint: 'Оставь одно ненулевое главное растяжение и занули другое.',
      }
    }
    return {
      kind: 'not-degenerate',
      message: 'Нулевое направление еще не поймано.',
      repairHint: 'Добейся determinant около нуля и поставь маркер вдоль схлопнутой оси.',
    }
  }

  if (levelId === 'signature-repair') {
    return {
      kind: 'wrong-signature',
      message: `Текущая сигнатура ${signatureLabel(form)}, цель уровня - (+,-).`,
      repairHint: 'Сделай одну главную энергию положительной, а другую отрицательной.',
    }
  }

  return {
    kind: 'in-progress',
    message: 'Цель уровня еще не достигнута.',
    repairHint: 'Смотри на сигнатуру, determinant и энергию выбранных направлений.',
  }
}

export function svgPointToQuadraticCoord({
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
  return [snapQuadraticValue(x), snapQuadraticValue(y)]
}
