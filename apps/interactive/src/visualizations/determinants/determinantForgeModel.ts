export type Vec2 = [number, number]

export const determinantGridLimit = 3
export const determinantSnap = 0.25
const areaTarget = 2
const areaTolerance = 0.05
const nearAreaTolerance = 0.4

export type DeterminantDiagnosisKind =
  | 'in-progress'
  | 'success'
  | 'area-too-small'
  | 'area-too-large'
  | 'wrong-orientation'
  | 'unexpected-degenerate'
  | 'needs-degenerate'
  | 'needs-repair-after-degenerate'

export type DeterminantDiagnosis = {
  kind: DeterminantDiagnosisKind
  message: string
  repairHint: string
}

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

export function diagnoseDeterminantState({
  levelId,
  u,
  v,
  completedLevelIds,
  touched,
}: {
  levelId: string
  u: Vec2
  v: Vec2
  completedLevelIds: readonly string[]
  touched: boolean
}): DeterminantDiagnosis {
  const det = determinant(u, v)
  const area = Math.abs(det)
  const degenerate = area < areaTolerance
  const success = determinantLevelSuccess({ levelId, u, v, completedLevelIds })

  if (success) {
    return {
      kind: 'success',
      message: 'Условие уровня выполнено: det A попал в нужный режим.',
      repairHint: 'Можно переходить к следующему уровню.',
    }
  }

  if (!touched && levelId !== 'repair-matrix') {
    return {
      kind: 'in-progress',
      message: 'Параллелограмм еще не настроен под цель уровня.',
      repairHint: 'Начни с площади: растяни один из столбцов или поменяй ориентацию.',
    }
  }

  if (levelId === 'area-two') {
    if (degenerate) {
      return {
        kind: 'unexpected-degenerate',
        message: 'Площадь исчезла: столбцы стали зависимыми.',
        repairHint: 'Разведи векторы так, чтобы снова появился параллелограмм.',
      }
    }
    if (area < areaTarget - nearAreaTolerance) {
      return {
        kind: 'area-too-small',
        message: 'Площадь меньше цели: |det A| еще не дотянулся до 2.',
        repairHint: 'Увеличь высоту или основание параллелограмма.',
      }
    }
    if (area > areaTarget + nearAreaTolerance) {
      return {
        kind: 'area-too-large',
        message: 'Площадь больше цели: |det A| уже перелетел 2.',
        repairHint: 'Сожми один из векторов или уменьши угол между ними.',
      }
    }
    return {
      kind: 'in-progress',
      message: 'Площадь почти рядом с целью, осталось попасть точнее.',
      repairHint: 'Двигай ручку мелким шагом: координаты притягиваются к 0.25.',
    }
  }

  if (levelId === 'flip-orientation') {
    if (degenerate) {
      return {
        kind: 'unexpected-degenerate',
        message: 'Площадь исчезла, а нужен отрицательный det с заметной площадью.',
        repairHint: 'Сначала разведи векторы, потом переверни порядок обхода.',
      }
    }
    if (det > 0) {
      return {
        kind: 'wrong-orientation',
        message: 'Площадь есть, но ориентация все еще положительная.',
        repairHint: 'Перетащи один вектор через другой, чтобы знак det A стал отрицательным.',
      }
    }
    return {
      kind: 'area-too-small',
      message: 'Знак уже отрицательный, но площадь слишком мала.',
      repairHint: 'Оставь отрицательную ориентацию и увеличь параллелограмм.',
    }
  }

  if (levelId === 'break-invertibility') {
    return {
      kind: 'needs-degenerate',
      message: 'Матрица еще обратима: площадь не схлопнулась в ноль.',
      repairHint: 'Положи оба столбца на одну прямую, чтобы det A стал 0.',
    }
  }

  if (levelId === 'repair-matrix') {
    if (!completedLevelIds.includes('break-invertibility')) {
      return {
        kind: 'needs-repair-after-degenerate',
        message: 'Сначала нужно пройти уровень, где матрица действительно вырождается.',
        repairHint: 'Вернись к уровню "Сломай обратимость" и схлопни площадь.',
      }
    }
    if (degenerate) {
      return {
        kind: 'needs-repair-after-degenerate',
        message: 'Матрица все еще вырождена: det A = 0.',
        repairHint: 'Отведи один столбец от общей прямой, чтобы вернуть ненулевую площадь.',
      }
    }
    return {
      kind: 'area-too-small',
      message: 'Площадь вернулась, но пока слишком мала для уверенной обратимости.',
      repairHint: 'Разведи векторы заметнее: нужен det A с модулем больше 0.5.',
    }
  }

  return {
    kind: 'in-progress',
    message: 'Цель уровня еще не достигнута.',
    repairHint: 'Следи за det A, площадью и ориентацией.',
  }
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
