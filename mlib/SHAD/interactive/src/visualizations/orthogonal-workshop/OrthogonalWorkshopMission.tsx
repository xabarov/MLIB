import { useEffect, useMemo, useState } from 'react'
import { Orbit, RotateCcw, Target } from 'lucide-react'
import { MissionShell } from '../../game/components/MissionShell'
import { chooseMascotState, missionMessage } from '../../game/missionFeedback'
import { orthogonalWorkshopMission } from '../../game/missions'
import type { MissionBadge } from '../../game/missionTypes'
import { useMissionRuntime } from '../../game/useMissionRuntime'
import {
  applyMatrix2,
  determinant2,
  dot2,
  formatOrthogonalNumber,
  gramSchmidt2,
  isOrthogonalMatrix2,
  lineDirection,
  matrixColumns,
  norm2,
  orthogonalOperatorDiagnosis,
  orthogonalPairDiagnosis,
  projectOntoLine2,
  projectionDiagnosis,
  rawGramVectors,
  safeNormalize2,
  scale2,
  shearTrapMatrix,
  signedAxisDistance,
  snapOrthogonalValue,
  subtract2,
  targetRotation,
  transposeTimesMatrix2,
  type Matrix2x2,
  type OrthogonalDiagnosis,
  type Vec2,
} from './orthogonalWorkshopModel'

type LevelPreset = {
  point: Vec2
  projection: Vec2
  vectorA: Vec2
  vectorB: Vec2
  normalizeVector: Vec2
  matrix: Matrix2x2
  gramSolved: boolean
}

const presets: Record<string, LevelPreset> = {
  'shadow-on-line': {
    point: [2.1, 1.4],
    projection: [0.4, 0],
    vectorA: [1.4, 0.4],
    vectorB: [0.9, 1.5],
    normalizeVector: [1.7, 0.9],
    matrix: shearTrapMatrix,
    gramSolved: false,
  },
  'independent-is-not-orthogonal': {
    point: [2.1, 1.4],
    projection: [2.1, 0],
    vectorA: [1.4, 0.4],
    vectorB: [0.9, 1.5],
    normalizeVector: [1.7, 0.9],
    matrix: shearTrapMatrix,
    gramSolved: false,
  },
  'normalize-without-turning': {
    point: [2.1, 1.4],
    projection: [2.1, 0],
    vectorA: [1.4, 0.4],
    vectorB: [-0.4, 1.4],
    normalizeVector: [1.7, 0.9],
    matrix: shearTrapMatrix,
    gramSolved: false,
  },
  'gram-schmidt-two': {
    point: [2.1, 1.4],
    projection: [2.1, 0],
    vectorA: rawGramVectors[0],
    vectorB: rawGramVectors[1],
    normalizeVector: [0.88, 0.47],
    matrix: shearTrapMatrix,
    gramSolved: false,
  },
  'orthogonal-operator': {
    point: [2.1, 1.4],
    projection: [2.1, 0],
    vectorA: [1.4, 0.4],
    vectorB: [-0.4, 1.4],
    normalizeVector: [0.88, 0.47],
    matrix: shearTrapMatrix,
    gramSolved: false,
  },
}

const gridLines = Array.from({ length: 9 }, (_, index) => index - 4)
const unitCircle = Array.from({ length: 97 }, (_, index) => {
  const angle = (index / 96) * Math.PI * 2
  return [Math.cos(angle), Math.sin(angle)] as Vec2
})

function pointsToSvg(points: Vec2[]): string {
  return points.map(([x, y]) => `${formatOrthogonalNumber(x)},${formatOrthogonalNumber(y)}`).join(' ')
}

function SliderField({
  label,
  value,
  testId,
  onChange,
  min = -3,
  max = 3,
}: {
  label: string
  value: number
  testId: string
  onChange: (value: number) => void
  min?: number
  max?: number
}) {
  return (
    <label className="grid gap-1 text-xs text-ink/70">
      <span className="flex items-center justify-between gap-2">
        <span className="font-semibold text-ink">{label}</span>
        <span className="tabular-nums">{formatOrthogonalNumber(value)}</span>
      </span>
      <div className="grid grid-cols-[minmax(0,1fr)_3.75rem] items-center gap-2">
        <input
          type="range"
          min={min}
          max={max}
          step={0.1}
          value={value}
          onChange={(event) => onChange(Number(event.target.value))}
          className="min-w-0 accent-target"
          data-testid={`${testId}-range`}
        />
        <input
          type="number"
          min={min}
          max={max}
          step={0.1}
          value={formatOrthogonalNumber(value)}
          onChange={(event) => onChange(Number(event.target.value))}
          className="w-full min-w-0 rounded border border-ink/10 bg-paper px-1.5 py-1 text-right tabular-nums text-ink"
          data-testid={testId}
        />
      </div>
    </label>
  )
}

function MatrixReadout({ matrix }: { matrix: Matrix2x2 }) {
  return (
    <div className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5 text-xs text-ink">
      Q = [[{formatOrthogonalNumber(matrix.a)}, {formatOrthogonalNumber(matrix.b)}], [
      {formatOrthogonalNumber(matrix.c)}, {formatOrthogonalNumber(matrix.d)}]]
    </div>
  )
}

function vectorLine(vector: Vec2, className: string, testId?: string) {
  return (
    <line
      x1={0}
      y1={0}
      x2={vector[0]}
      y2={vector[1]}
      className={className}
      strokeWidth="0.07"
      strokeLinecap="round"
      markerEnd="url(#arrow)"
      data-testid={testId}
    />
  )
}

export function OrthogonalWorkshopMission() {
  const definition = orthogonalWorkshopMission
  const runtime = useMissionRuntime(definition)
  const activeLevel = runtime.activeLevel
  const { completeActiveLevel, setActiveLevelId } = runtime
  const [point, setPoint] = useState<Vec2>(presets[activeLevel.id].point)
  const [projection, setProjection] = useState<Vec2>(presets[activeLevel.id].projection)
  const [vectorA, setVectorA] = useState<Vec2>(presets[activeLevel.id].vectorA)
  const [vectorB, setVectorB] = useState<Vec2>(presets[activeLevel.id].vectorB)
  const [normalizeVector, setNormalizeVector] = useState<Vec2>(presets[activeLevel.id].normalizeVector)
  const [matrix, setMatrix] = useState<Matrix2x2>(presets[activeLevel.id].matrix)
  const [gramSolved, setGramSolved] = useState(presets[activeLevel.id].gramSolved)
  const [touched, setTouched] = useState(false)

  const resetToPreset = (levelId = activeLevel.id) => {
    const preset = presets[levelId]
    setPoint(preset.point)
    setProjection(preset.projection)
    setVectorA(preset.vectorA)
    setVectorB(preset.vectorB)
    setNormalizeVector(preset.normalizeVector)
    setMatrix(preset.matrix)
    setGramSolved(preset.gramSolved)
    setTouched(false)
  }

  const selectLevel = (levelId: string) => {
    resetToPreset(levelId)
    setActiveLevelId(levelId)
  }

  const residual = subtract2(point, projection)
  const pairDiagnosis = orthogonalPairDiagnosis(vectorA, vectorB)
  const projectionState = projectionDiagnosis(point, projection, lineDirection)
  const initialNormalizeRay = safeNormalize2(presets['normalize-without-turning'].normalizeVector)
  const normalizedDirectionDistance = signedAxisDistance(normalizeVector, initialNormalizeRay)
  const gram = useMemo(() => gramSchmidt2(rawGramVectors), [])
  const displayedGram = gramSolved ? gram.orthonormal : [safeNormalize2(vectorA), safeNormalize2(vectorB)]
  const qtq = transposeTimesMatrix2(matrix)
  const matrixDiagnosis = orthogonalOperatorDiagnosis(matrix, { requireRotation: true })
  const transformedCircle = unitCircle.map((circlePoint) => applyMatrix2(matrix, circlePoint))

  const levelSuccess = (() => {
    if (activeLevel.id === 'shadow-on-line') return projectionState.kind === 'ready' && touched
    if (activeLevel.id === 'independent-is-not-orthogonal') return pairDiagnosis.kind === 'ready' && touched
    if (activeLevel.id === 'normalize-without-turning') {
      return Math.abs(norm2(normalizeVector) - 1) < 0.04 && normalizedDirectionDistance < 0.08 && touched
    }
    if (activeLevel.id === 'gram-schmidt-two') {
      return gramSolved && gram.dependentIndex === null && Math.abs(dot2(displayedGram[0], displayedGram[1])) < 0.04
    }
    return matrixDiagnosis.kind === 'ready' && determinant2(matrix) > 0.8 && touched
  })()

  const diagnosis: OrthogonalDiagnosis = (() => {
    if (levelSuccess) {
      return {
        kind: 'ready',
        message: activeLevel.successText,
        repairHint: activeLevel.takeaway,
      }
    }
    if (activeLevel.id === 'shadow-on-line') return projectionState
    if (activeLevel.id === 'independent-is-not-orthogonal') return pairDiagnosis
    if (activeLevel.id === 'normalize-without-turning') {
      if (norm2(normalizeVector) < 0.08) {
        return {
          kind: 'zero-vector',
          message: 'Вектор почти нулевой: направление потеряно.',
          repairHint: 'Верни длину и потом нормируй до единицы.',
        }
      }
      if (normalizedDirectionDistance >= 0.08) {
        return {
          kind: 'not-normalized',
          message: 'Нормировка повернула направление.',
          repairHint: 'Меняй только длину вдоль ghost-луча.',
        }
      }
      return {
        kind: 'not-normalized',
        message: `Длина еще не единичная: norm = ${formatOrthogonalNumber(norm2(normalizeVector))}.`,
        repairHint: 'Растяни или сожми вектор до norm = 1.',
      }
    }
    if (activeLevel.id === 'gram-schmidt-two') {
      return {
        kind: 'not-orthogonal',
        message: 'Остаток Грама-Шмидта еще не собран.',
        repairHint: 'Вычти проекцию второго вектора на первый и нормируй остаток.',
      }
    }
    return matrixDiagnosis
  })()

  useEffect(() => {
    if (levelSuccess) completeActiveLevel()
  }, [completeActiveLevel, levelSuccess])

  const mascotState = chooseMascotState({
    success: levelSuccess,
    warning: touched && diagnosis.kind !== 'ready',
    hint: activeLevel.id === 'gram-schmidt-two' && !gramSolved,
    thinking: !touched,
  })
  const mascotMessage = missionMessage(mascotState, {
    idle: 'Меби держит остаток: двигай тень так, чтобы ошибка стала перпендикулярной.',
    thinking: 'Смотри не только на красивую картинку: главный индикатор здесь dot product.',
    hint: 'Ортогонализация не заменяет вектор произвольно, а вычитает уже объясненную проекцию.',
    warning: diagnosis.repairHint,
    success: activeLevel.takeaway,
  })

  const badges: MissionBadge[] = [
    {
      id: 'dot',
      label: 'DOT',
      value: formatOrthogonalNumber(activeLevel.id === 'shadow-on-line' ? dot2(residual, lineDirection) : dot2(vectorA, vectorB)),
      tone: Math.abs(activeLevel.id === 'shadow-on-line' ? dot2(residual, lineDirection) : dot2(vectorA, vectorB)) < 0.08 ? 'success' : 'warning',
    },
    {
      id: 'norm',
      label: 'NORM',
      value: formatOrthogonalNumber(norm2(normalizeVector)),
      tone: Math.abs(norm2(normalizeVector) - 1) < 0.08 ? 'success' : 'neutral',
    },
    {
      id: 'det',
      label: 'DET',
      value: formatOrthogonalNumber(determinant2(matrix)),
      tone: determinant2(matrix) > 0.8 ? 'success' : 'neutral',
    },
    {
      id: 'qtq',
      label: 'Q^T Q',
      value: `${formatOrthogonalNumber(qtq.a)}, ${formatOrthogonalNumber(qtq.b)}, ${formatOrthogonalNumber(qtq.c)}`,
      tone: isOrthogonalMatrix2(matrix) ? 'success' : 'warning',
    },
  ]

  const setVectorCoord = (
    setter: (value: Vec2) => void,
    vector: Vec2,
    index: 0 | 1,
    value: number,
  ) => {
    const next: Vec2 = index === 0 ? [snapOrthogonalValue(value), vector[1]] : [vector[0], snapOrthogonalValue(value)]
    setter(next)
    setTouched(true)
  }

  const setMatrixCoord = (coord: keyof Matrix2x2, value: number) => {
    setMatrix((current) => ({ ...current, [coord]: snapOrthogonalValue(value) }))
    setTouched(true)
  }

  const snapProjection = () => {
    setProjection(projectOntoLine2(point, lineDirection))
    setTouched(true)
  }

  const snapOrthogonalPair = () => {
    const first = vectorA
    const second = scale2([-first[1], first[0]], norm2(vectorB) / Math.max(norm2(first), 0.1))
    setVectorB(second)
    setTouched(true)
  }

  const snapNormalize = () => {
    setNormalizeVector(initialNormalizeRay)
    setTouched(true)
  }

  const snapGramSchmidt = () => {
    setGramSolved(true)
    setTouched(true)
  }

  const snapMatrix = () => {
    setMatrix(targetRotation)
    setTouched(true)
  }

  const makeShear = () => {
    setMatrix(shearTrapMatrix)
    setTouched(true)
  }

  return (
    <MissionShell
      definition={definition}
      activeLevelId={activeLevel.id}
      onLevelSelect={selectLevel}
      mascotState={mascotState}
      mascotMessage={mascotMessage}
      badges={badges}
      sceneViewportClassName="min-h-[620px] pt-[112px] sm:pt-[82px] lg:h-full lg:min-h-0"
      scene={
        <div className="grid h-full min-h-[620px] gap-3 bg-[radial-gradient(circle_at_18%_18%,rgba(95,141,99,0.13),transparent_30%),linear-gradient(180deg,#fffdf7,#f5f2e8)] p-3 lg:grid-cols-[1.1fr_0.9fr]">
          <svg
            viewBox="-4 -4 8 8"
            className="min-h-[300px] w-full rounded border border-ink/10 bg-paper shadow-soft"
            data-testid="orthogonal-workshop-canvas"
            aria-label="Orthogonal workshop geometry"
          >
            <defs>
              <marker id="arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
                <path d="M0,0 L6,3 L0,6 Z" className="fill-ink" />
              </marker>
            </defs>
            <g transform="scale(1 -1)">
              {gridLines.map((line) => (
                <g key={line}>
                  <line x1={-4} y1={line} x2={4} y2={line} className="stroke-grid" strokeWidth="0.018" />
                  <line x1={line} y1={-4} x2={line} y2={4} className="stroke-grid" strokeWidth="0.018" />
                </g>
              ))}
              <line x1={-4} y1={0} x2={4} y2={0} className="stroke-ink/35" strokeWidth="0.03" />
              <line x1={0} y1={-4} x2={0} y2={4} className="stroke-ink/35" strokeWidth="0.03" />
              {activeLevel.id === 'orthogonal-operator' && (
                <>
                  <polyline points={pointsToSvg(unitCircle)} className="fill-none stroke-target/35" strokeWidth="0.045" strokeDasharray="0.14 0.1" />
                  <polyline points={pointsToSvg(transformedCircle)} className="fill-none stroke-success" strokeWidth="0.055" data-testid="orthogonal-operator-circle" />
                  {vectorLine(matrixColumns(matrix)[0], 'stroke-orange', 'orthogonal-matrix-column-1')}
                  {vectorLine(matrixColumns(matrix)[1], 'stroke-target', 'orthogonal-matrix-column-2')}
                </>
              )}
              {activeLevel.id !== 'orthogonal-operator' && (
                <>
                  <line
                    x1={-3.7}
                    y1={0}
                    x2={3.7}
                    y2={0}
                    className="stroke-success"
                    strokeWidth="0.045"
                    strokeDasharray="0.16 0.1"
                    data-testid="orthogonal-line"
                  />
                  {activeLevel.id === 'shadow-on-line' && (
                    <>
                      {vectorLine(point, 'stroke-orange', 'orthogonal-vector-x')}
                      <line
                        x1={projection[0]}
                        y1={projection[1]}
                        x2={point[0]}
                        y2={point[1]}
                        className="stroke-target"
                        strokeWidth="0.06"
                        strokeDasharray="0.14 0.08"
                        data-testid="orthogonal-residual"
                      />
                      <circle
                        cx={projection[0]}
                        cy={projection[1]}
                        r={0.12}
                        className="fill-success stroke-ink"
                        strokeWidth="0.03"
                        data-testid="orthogonal-projection"
                      />
                      <circle
                        cx={point[0]}
                        cy={point[1]}
                        r={0.12}
                        className="fill-orange stroke-ink"
                        strokeWidth="0.03"
                      />
                    </>
                  )}
                  {activeLevel.id === 'independent-is-not-orthogonal' && (
                    <>
                      {vectorLine(vectorA, 'stroke-orange')}
                      {vectorLine(vectorB, 'stroke-target')}
                      <polygon points={`0,0 ${vectorA[0]},${vectorA[1]} ${vectorA[0] + vectorB[0]},${vectorA[1] + vectorB[1]} ${vectorB[0]},${vectorB[1]}`} className="fill-orange/10 stroke-orange/30" strokeWidth="0.035" />
                    </>
                  )}
                  {activeLevel.id === 'normalize-without-turning' && (
                    <>
                      <line x1={-initialNormalizeRay[0] * 3.2} y1={-initialNormalizeRay[1] * 3.2} x2={initialNormalizeRay[0] * 3.2} y2={initialNormalizeRay[1] * 3.2} className="stroke-success/50" strokeWidth="0.04" strokeDasharray="0.12 0.1" />
                      <circle cx={0} cy={0} r={1} className="fill-none stroke-target/40" strokeWidth="0.04" />
                      {vectorLine(normalizeVector, 'stroke-orange')}
                    </>
                  )}
                  {activeLevel.id === 'gram-schmidt-two' && (
                    <>
                      {vectorLine(rawGramVectors[0], 'stroke-ink/35')}
                      {vectorLine(rawGramVectors[1], 'stroke-ink/35')}
                      {vectorLine(displayedGram[0], 'stroke-orange', 'orthogonal-gram-e1')}
                      {vectorLine(displayedGram[1], 'stroke-target', 'orthogonal-gram-e2')}
                      <line x1={0} y1={0} x2={gram.residuals[1][0]} y2={gram.residuals[1][1]} className="stroke-success/60" strokeWidth="0.05" strokeDasharray="0.12 0.08" />
                    </>
                  )}
                  {(levelSuccess || Math.abs(dot2(residual, lineDirection)) < 0.08) && activeLevel.id === 'shadow-on-line' && (
                    <path d={`M${projection[0] + 0.22},${projection[1]} L${projection[0] + 0.22},${projection[1] + 0.22} L${projection[0]},${projection[1] + 0.22}`} className="fill-none stroke-success" strokeWidth="0.035" data-testid="orthogonal-angle-marker" />
                  )}
                </>
              )}
            </g>
          </svg>

          <div className="grid content-start gap-3">
            <div className="rounded border border-ink/10 bg-bg/80 p-3">
              <p className="text-[10px] font-semibold uppercase tracking-wide text-orange">Residual lab</p>
              <p className="mt-1 text-sm font-semibold text-ink">x = projection + residual</p>
              <p className="mt-1 text-xs leading-relaxed text-ink/65">
                Ортогональность засчитывается только когда видимая ошибка действительно перпендикулярна уже построенному направлению.
              </p>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div className="rounded border border-ink/10 bg-paper px-2 py-1.5 text-xs" data-testid="orthogonal-dot-badge">
                <p className="text-[10px] font-semibold uppercase text-ink/45">dot</p>
                <p className="font-semibold text-ink">{formatOrthogonalNumber(dot2(residual, lineDirection))}</p>
              </div>
              <div className="rounded border border-ink/10 bg-paper px-2 py-1.5 text-xs" data-testid="orthogonal-norm-badge">
                <p className="text-[10px] font-semibold uppercase text-ink/45">norm</p>
                <p className="font-semibold text-ink">{formatOrthogonalNumber(norm2(normalizeVector))}</p>
              </div>
              <div className="rounded border border-ink/10 bg-paper px-2 py-1.5 text-xs" data-testid="orthogonal-det-badge">
                <p className="text-[10px] font-semibold uppercase text-ink/45">det</p>
                <p className="font-semibold text-ink">{formatOrthogonalNumber(determinant2(matrix))}</p>
              </div>
              <div className="rounded border border-ink/10 bg-paper px-2 py-1.5 text-xs" data-testid="orthogonal-qtq-badge">
                <p className="text-[10px] font-semibold uppercase text-ink/45">Q^T Q</p>
                <p className="font-semibold text-ink">{formatOrthogonalNumber(qtq.a)}, {formatOrthogonalNumber(qtq.b)}, {formatOrthogonalNumber(qtq.c)}</p>
              </div>
            </div>
          </div>
        </div>
      }
      controls={
        <div className="space-y-3">
          {activeLevel.id === 'shadow-on-line' && (
            <div className="grid gap-2 md:grid-cols-2">
              <SliderField label="x1" value={point[0]} testId="orthogonal-vector-x-x" onChange={(value) => setVectorCoord(setPoint, point, 0, value)} />
              <SliderField label="x2" value={point[1]} testId="orthogonal-vector-x-y" onChange={(value) => setVectorCoord(setPoint, point, 1, value)} />
              <SliderField label="p1" value={projection[0]} testId="orthogonal-projection-x" onChange={(value) => setVectorCoord(setProjection, projection, 0, value)} />
              <SliderField label="p2" value={projection[1]} testId="orthogonal-projection-y" onChange={(value) => setVectorCoord(setProjection, projection, 1, value)} />
            </div>
          )}
          {activeLevel.id === 'independent-is-not-orthogonal' && (
            <div className="grid gap-2 md:grid-cols-2">
              <SliderField label="a1" value={vectorA[0]} testId="orthogonal-vector-a-x" onChange={(value) => setVectorCoord(setVectorA, vectorA, 0, value)} />
              <SliderField label="a2" value={vectorA[1]} testId="orthogonal-vector-a-y" onChange={(value) => setVectorCoord(setVectorA, vectorA, 1, value)} />
              <SliderField label="b1" value={vectorB[0]} testId="orthogonal-vector-b-x" onChange={(value) => setVectorCoord(setVectorB, vectorB, 0, value)} />
              <SliderField label="b2" value={vectorB[1]} testId="orthogonal-vector-b-y" onChange={(value) => setVectorCoord(setVectorB, vectorB, 1, value)} />
            </div>
          )}
          {activeLevel.id === 'normalize-without-turning' && (
            <div className="grid gap-2 md:grid-cols-2">
              <SliderField label="v1" value={normalizeVector[0]} testId="orthogonal-normalize-x" onChange={(value) => setVectorCoord(setNormalizeVector, normalizeVector, 0, value)} />
              <SliderField label="v2" value={normalizeVector[1]} testId="orthogonal-normalize-y" onChange={(value) => setVectorCoord(setNormalizeVector, normalizeVector, 1, value)} />
            </div>
          )}
          {activeLevel.id === 'orthogonal-operator' && (
            <>
              <MatrixReadout matrix={matrix} />
              <div className="grid gap-2 md:grid-cols-2">
                <SliderField label="a" value={matrix.a} testId="orthogonal-matrix-a" onChange={(value) => setMatrixCoord('a', value)} />
                <SliderField label="b" value={matrix.b} testId="orthogonal-matrix-b" onChange={(value) => setMatrixCoord('b', value)} />
                <SliderField label="c" value={matrix.c} testId="orthogonal-matrix-c" onChange={(value) => setMatrixCoord('c', value)} />
                <SliderField label="d" value={matrix.d} testId="orthogonal-matrix-d" onChange={(value) => setMatrixCoord('d', value)} />
              </div>
            </>
          )}
          <div className="flex flex-wrap gap-2">
            <button type="button" onClick={() => resetToPreset()} className="inline-flex items-center gap-1 rounded border border-ink/10 bg-paper px-2 py-1 text-xs font-semibold text-ink transition hover:border-orange/40 hover:text-orange">
              <RotateCcw size={14} /> reset
            </button>
            {activeLevel.id === 'shadow-on-line' && (
              <button type="button" onClick={snapProjection} className="inline-flex items-center gap-1 rounded border border-target/25 bg-target/10 px-2 py-1 text-xs font-semibold text-ink transition hover:border-target">
                <Target size={14} /> project
              </button>
            )}
            {activeLevel.id === 'independent-is-not-orthogonal' && (
              <button type="button" onClick={snapOrthogonalPair} className="inline-flex items-center gap-1 rounded border border-success/25 bg-success/10 px-2 py-1 text-xs font-semibold text-ink transition hover:border-success">
                <Target size={14} /> orthogonalize
              </button>
            )}
            {activeLevel.id === 'normalize-without-turning' && (
              <button type="button" onClick={snapNormalize} className="inline-flex items-center gap-1 rounded border border-target/25 bg-target/10 px-2 py-1 text-xs font-semibold text-ink transition hover:border-target">
                <Target size={14} /> normalize
              </button>
            )}
            {activeLevel.id === 'gram-schmidt-two' && (
              <button type="button" onClick={snapGramSchmidt} className="inline-flex items-center gap-1 rounded border border-success/25 bg-success/10 px-2 py-1 text-xs font-semibold text-ink transition hover:border-success">
                <Orbit size={14} /> gram-schmidt
              </button>
            )}
            {activeLevel.id === 'orthogonal-operator' && (
              <>
                <button type="button" onClick={makeShear} className="inline-flex items-center gap-1 rounded border border-orange/25 bg-orange/10 px-2 py-1 text-xs font-semibold text-ink transition hover:border-orange">
                  shear trap
                </button>
                <button type="button" onClick={snapMatrix} className="inline-flex items-center gap-1 rounded border border-target/25 bg-target/10 px-2 py-1 text-xs font-semibold text-ink transition hover:border-target">
                  <Target size={14} /> snap Q
                </button>
              </>
            )}
          </div>
        </div>
      }
      feedback={
        <div className="space-y-1" data-testid="orthogonal-diagnosis">
          <p className="font-semibold text-ink">{diagnosis.message}</p>
          <p>{diagnosis.repairHint}</p>
        </div>
      }
    />
  )
}
