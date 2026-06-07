import { useEffect, useMemo, useRef, useState, type PointerEvent } from 'react'
import { RotateCcw, Target } from 'lucide-react'
import { MissionShell } from '../../game/components/MissionShell'
import { chooseMascotState, missionMessage } from '../../game/missionFeedback'
import { svdLensMission } from '../../game/missions'
import type { MissionBadge } from '../../game/missionTypes'
import { useMissionRuntime } from '../../game/useMissionRuntime'
import {
  angleToVector,
  applyMatrix,
  centerPointCloud,
  determinant,
  diagnoseSvdState,
  formatSvdNumber,
  frobeniusError,
  matrixMatchesSvdTarget,
  pcaCloud,
  principalComponent2D,
  projectionError,
  rankKApprox,
  retainedVariance,
  signedAxisDistance,
  snapSvdValue,
  svd2x2,
  svdLevelSuccess,
  svdTargetMatrix,
  transformedCircleSample,
  transposeTimesMatrix,
  type Matrix2x2,
  type SingularChoice,
  type Vec2,
} from './svdLensModel'

type DragTarget = 'right1' | 'right2' | null

type LevelPreset = {
  matrix: Matrix2x2
  rightDirection: Vec2
  rightDirectionSecond: Vec2
  singularChoice: SingularChoice
  keepSigma2: boolean
  pcaAngle: number
}

const presets: Record<string, LevelPreset> = {
  'circle-to-ellipse': {
    matrix: { a: 1, b: 0, c: 0, d: 1 },
    rightDirection: [1, 0],
    rightDirectionSecond: [0, 1],
    singularChoice: 'eigenvalues-a',
    keepSigma2: true,
    pcaAngle: 0,
  },
  'right-directions': {
    matrix: svdTargetMatrix,
    rightDirection: [1, 0],
    rightDirectionSecond: [0, 1],
    singularChoice: 'eigenvalues-a',
    keepSigma2: true,
    pcaAngle: 0,
  },
  'singular-vs-eigen': {
    matrix: { a: 1, b: 2, c: 0, d: 1 },
    rightDirection: [1, 0],
    rightDirectionSecond: [0, 1],
    singularChoice: 'eigenvalues-a',
    keepSigma2: true,
    pcaAngle: 0,
  },
  'rank-one-shadow': {
    matrix: svdTargetMatrix,
    rightDirection: [1, 0],
    rightDirectionSecond: [0, 1],
    singularChoice: 'singular-values',
    keepSigma2: true,
    pcaAngle: 0,
  },
  'pca-cloud': {
    matrix: svdTargetMatrix,
    rightDirection: [1, 0],
    rightDirectionSecond: [0, 1],
    singularChoice: 'singular-values',
    keepSigma2: false,
    pcaAngle: 0,
  },
}

const gridLines = Array.from({ length: 9 }, (_, index) => index - 4)

function pointsToSvg(points: Vec2[]): string {
  return points.map(([x, y]) => `${formatSvdNumber(x)},${formatSvdNumber(y)}`).join(' ')
}

function AxisLine({ vector, className, width = 0.04 }: { vector: Vec2; className: string; width?: number }) {
  return (
    <line
      x1={-vector[0] * 3.7}
      y1={-vector[1] * 3.7}
      x2={vector[0] * 3.7}
      y2={vector[1] * 3.7}
      className={className}
      strokeWidth={width}
      strokeLinecap="round"
      strokeDasharray="0.16 0.12"
    />
  )
}

function SliderField({
  label,
  value,
  min = -3,
  max = 3,
  step = 0.1,
  testId,
  onChange,
}: {
  label: string
  value: number
  min?: number
  max?: number
  step?: number
  testId: string
  onChange: (value: number) => void
}) {
  return (
    <label className="grid gap-1 text-xs text-ink/70">
      <span className="flex items-center justify-between gap-2">
        <span className="font-semibold text-ink">{label}</span>
        <span className="tabular-nums">{formatSvdNumber(value)}</span>
      </span>
      <div className="grid grid-cols-[minmax(0,1fr)_3.75rem] items-center gap-2">
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(event) => onChange(Number(event.target.value))}
          className="min-w-0 accent-target"
          data-testid={`${testId}-range`}
        />
        <input
          type="number"
          min={min}
          max={max}
          step={step}
          value={formatSvdNumber(value)}
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
      A = [[{formatSvdNumber(matrix.a)}, {formatSvdNumber(matrix.b)}], [
      {formatSvdNumber(matrix.c)}, {formatSvdNumber(matrix.d)}]]
    </div>
  )
}

function ChoiceButton({
  active,
  label,
  testId,
  onClick,
}: {
  active: boolean
  label: string
  testId: string
  onClick: () => void
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded border px-2 py-1.5 text-xs font-semibold transition ${
        active
          ? 'border-target bg-target text-bg'
          : 'border-ink/10 bg-paper text-ink hover:border-target/50'
      }`}
      data-testid={testId}
    >
      {label}
    </button>
  )
}

export function SvdLensMission() {
  const definition = svdLensMission
  const runtime = useMissionRuntime(definition)
  const activeLevel = runtime.activeLevel
  const { completeActiveLevel, setActiveLevelId } = runtime
  const [matrix, setMatrix] = useState<Matrix2x2>(presets[activeLevel.id].matrix)
  const [rightDirection, setRightDirection] = useState<Vec2>(presets[activeLevel.id].rightDirection)
  const [rightDirectionSecond, setRightDirectionSecond] = useState<Vec2>(
    presets[activeLevel.id].rightDirectionSecond,
  )
  const [singularChoice, setSingularChoice] = useState<SingularChoice>(
    presets[activeLevel.id].singularChoice,
  )
  const [keepSigma2, setKeepSigma2] = useState(presets[activeLevel.id].keepSigma2)
  const [pcaAngle, setPcaAngle] = useState(presets[activeLevel.id].pcaAngle)
  const [touched, setTouched] = useState(false)
  const svgRef = useRef<SVGSVGElement>(null)
  const dragTarget = useRef<DragTarget>(null)

  const resetToPreset = (levelId = activeLevel.id) => {
    const preset = presets[levelId]
    setMatrix(preset.matrix)
    setRightDirection(preset.rightDirection)
    setRightDirectionSecond(preset.rightDirectionSecond)
    setSingularChoice(preset.singularChoice)
    setKeepSigma2(preset.keepSigma2)
    setPcaAngle(preset.pcaAngle)
    setTouched(false)
  }

  const selectLevel = (levelId: string) => {
    resetToPreset(levelId)
    setActiveLevelId(levelId)
  }

  const svd = useMemo(() => svd2x2(matrix), [matrix])
  const ata = transposeTimesMatrix(matrix)
  const currentEllipse = useMemo(() => transformedCircleSample(matrix, 120), [matrix])
  const targetEllipse = useMemo(() => transformedCircleSample(svdTargetMatrix, 120), [])
  const rankOne = useMemo(() => rankKApprox(matrix, keepSigma2 ? 2 : 1), [keepSigma2, matrix])
  const rankEllipse = useMemo(() => transformedCircleSample(rankOne, 80), [rankOne])
  const centeredCloud = useMemo(() => centerPointCloud(pcaCloud), [])
  const pcaAxis = angleToVector(pcaAngle)
  const truePc = useMemo(() => principalComponent2D(pcaCloud), [])
  const variance = retainedVariance(pcaCloud, pcaAxis)
  const pcaError = projectionError(centeredCloud, pcaAxis)
  const levelSuccess = useMemo(
    () =>
      svdLevelSuccess({
        levelId: activeLevel.id,
        matrix,
        rightDirection,
        rightDirectionSecond,
        singularChoice,
        keepSigma2,
        pcaAngle,
        touched,
      }),
    [activeLevel.id, keepSigma2, matrix, pcaAngle, rightDirection, rightDirectionSecond, singularChoice, touched],
  )
  const diagnosis = diagnoseSvdState({
    levelId: activeLevel.id,
    matrix,
    rightDirection,
    rightDirectionSecond,
    singularChoice,
    keepSigma2,
    pcaAngle,
    touched,
  })

  useEffect(() => {
    if (!levelSuccess) return
    completeActiveLevel()
  }, [completeActiveLevel, levelSuccess])

  const mascotState = chooseMascotState({
    success: levelSuccess,
    warning:
      touched &&
      [
        'wrong-ellipse',
        'wrong-directions',
        'eigenvalue-trap',
        'signed-sigma',
        'wrong-rank',
        'weak-component-kept',
        'pca-axis-off',
      ].includes(diagnosis.kind),
    hint:
      Math.abs(svd.sigma1 - svd2x2(svdTargetMatrix).sigma1) < 0.3 ||
      signedAxisDistance(rightDirection, svd.v1) < 0.35 ||
      variance > 0.85,
    thinking: activeLevel.id === 'singular-vs-eigen',
  })
  const mascotMessage = missionMessage(mascotState, {
    success: activeLevel.successText,
    warning: activeLevel.mistakeFeedback?.[0] ?? diagnosis.message,
    hint: activeLevel.hint,
    thinking: 'Я смотрю не на знак det, а на длины полуосей: sigma всегда неотрицательны.',
    idle: 'Пропусти круг через матрицу. Я буду сравнивать входные оси, output ellipse и PCA-тень.',
  })

  const badges: MissionBadge[] = [
    {
      id: 'sigma1',
      label: 'sigma1',
      value: formatSvdNumber(svd.sigma1),
      tone: levelSuccess ? 'success' : 'energy',
    },
    {
      id: 'sigma2',
      label: 'sigma2',
      value: keepSigma2 ? formatSvdNumber(svd.sigma2) : 'off',
      tone: keepSigma2 ? 'target' : 'warning',
    },
    {
      id: 'rank',
      label: 'rank',
      value: keepSigma2 ? svd.rank : Math.min(svd.rank, 1),
      tone: activeLevel.id === 'rank-one-shadow' && !keepSigma2 ? 'success' : 'neutral',
    },
    {
      id: 'variance',
      label: 'PCA var',
      value: `${Math.round(variance * 100)}%`,
      tone: activeLevel.id === 'pca-cloud' && levelSuccess ? 'success' : 'neutral',
    },
  ]

  const setMatrixCoord = (key: keyof Matrix2x2, value: number) => {
    setTouched(true)
    setMatrix((current) => ({ ...current, [key]: Number.isFinite(value) ? snapSvdValue(value) : 0 }))
  }

  const eventToPoint = (event: PointerEvent<SVGSVGElement>): Vec2 => {
    const svg = svgRef.current
    if (!svg) return [0, 0]
    const rect = svg.getBoundingClientRect()
    const x = ((event.clientX - rect.left) / rect.width) * 8 - 4
    const y = 4 - ((event.clientY - rect.top) / rect.height) * 8
    return [x, y]
  }

  const startDrag = (event: PointerEvent<SVGCircleElement>, target: DragTarget) => {
    dragTarget.current = target
    event.currentTarget.setPointerCapture(event.pointerId)
  }

  const handlePointerMove = (event: PointerEvent<SVGSVGElement>) => {
    if (!dragTarget.current) return
    const point = eventToPoint(event)
    const unit = Math.hypot(point[0], point[1]) < 0.1 ? [1, 0] : ([point[0], point[1]] as Vec2)
    const length = Math.hypot(unit[0], unit[1])
    const next: Vec2 = [unit[0] / length, unit[1] / length]
    setTouched(true)
    if (dragTarget.current === 'right1') setRightDirection(next)
    if (dragTarget.current === 'right2') setRightDirectionSecond(next)
  }

  const stopDrag = () => {
    dragTarget.current = null
  }

  const snapMatrix = () => {
    setTouched(true)
    setMatrix(svdTargetMatrix)
  }

  const snapDirections = () => {
    setTouched(true)
    setRightDirection(svd.v1)
    setRightDirectionSecond(svd.v2)
  }

  const chooseSingular = (choice: SingularChoice) => {
    setTouched(true)
    setSingularChoice(choice)
  }

  const chooseRankOne = () => {
    setTouched(true)
    setKeepSigma2(false)
  }

  const snapPca = () => {
    setTouched(true)
    setPcaAngle(Math.atan2(truePc[1], truePc[0]))
  }

  const showDirections = activeLevel.id === 'right-directions'
  const showPca = activeLevel.id === 'pca-cloud'
  const showRank = activeLevel.id === 'rank-one-shadow'
  const av1 = applyMatrix(matrix, rightDirection)
  const av2 = applyMatrix(matrix, rightDirectionSecond)
  const approxError = frobeniusError(matrix, rankOne)

  return (
    <MissionShell
      definition={definition}
      activeLevelId={activeLevel.id}
      onLevelSelect={selectLevel}
      mascotState={mascotState}
      mascotMessage={mascotMessage}
      badges={badges}
      sceneViewportClassName="min-h-[640px] pt-[116px] sm:pt-[84px] lg:h-full"
      scene={
        <div className="grid h-full grid-rows-[1fr_auto] gap-3 bg-[radial-gradient(circle_at_18%_14%,rgba(106,155,204,0.15),transparent_30%),radial-gradient(circle_at_82%_78%,rgba(95,141,99,0.14),transparent_28%),linear-gradient(180deg,#fffdf7,#f5f2e8)] p-3">
          <div className="grid min-h-0 gap-3 lg:grid-cols-[1fr_130px_1fr]">
            <svg
              ref={svgRef}
              viewBox="-4 -4 8 8"
              className="min-h-[260px] w-full touch-none rounded-md border border-ink/10 bg-paper shadow-[0_16px_36px_rgba(20,20,19,0.12)]"
              onPointerMove={handlePointerMove}
              onPointerUp={stopDrag}
              onPointerCancel={stopDrag}
              aria-label="SVD input space"
              data-testid="svd-lens-canvas"
            >
              <g transform="scale(1,-1)">
                {gridLines.map((line) => (
                  <g key={line}>
                    <line x1={-4} y1={line} x2={4} y2={line} className="stroke-grid" strokeWidth="0.018" />
                    <line x1={line} y1={-4} x2={line} y2={4} className="stroke-grid" strokeWidth="0.018" />
                  </g>
                ))}
                <line x1={-4} y1={0} x2={4} y2={0} className="stroke-ink/40" strokeWidth="0.035" />
                <line x1={0} y1={-4} x2={0} y2={4} className="stroke-ink/40" strokeWidth="0.035" />
                <circle
                  cx={0}
                  cy={0}
                  r={1}
                  className="fill-target/8 stroke-target"
                  strokeWidth="0.045"
                  data-testid="svd-input-circle"
                />
                <AxisLine vector={svd.v1} className="stroke-success/70" width={0.045} />
                <AxisLine vector={svd.v2} className="stroke-success/40" width={0.035} />
                {showDirections && (
                  <>
                    <line x1={0} y1={0} x2={rightDirection[0]} y2={rightDirection[1]} className="stroke-orange" strokeWidth="0.06" />
                    <line x1={0} y1={0} x2={rightDirectionSecond[0]} y2={rightDirectionSecond[1]} className="stroke-target" strokeWidth="0.06" />
                    <circle
                      cx={rightDirection[0]}
                      cy={rightDirection[1]}
                      r={0.17}
                      className="cursor-grab fill-orange stroke-ink"
                      strokeWidth="0.03"
                      data-testid="svd-right-vector-1"
                      onPointerDown={(event) => startDrag(event, 'right1')}
                    />
                    <circle
                      cx={rightDirectionSecond[0]}
                      cy={rightDirectionSecond[1]}
                      r={0.17}
                      className="cursor-grab fill-target stroke-ink"
                      strokeWidth="0.03"
                      data-testid="svd-right-vector-2"
                      onPointerDown={(event) => startDrag(event, 'right2')}
                    />
                  </>
                )}
              </g>
            </svg>

            <div className="flex min-h-[120px] flex-col items-center justify-center rounded-md border border-ink/10 bg-bg/75 px-3 text-center shadow-[inset_0_0_0_1px_rgba(106,155,204,0.12)]">
              <p className="text-[10px] font-semibold uppercase tracking-wide text-target">matrix lens</p>
              <p className="mt-2 text-2xl font-black text-ink">A</p>
              <p className="mt-1 text-xs text-ink/55">A^T A to sigma</p>
              <div className="mt-3 rounded bg-paper px-2 py-1 text-xs font-semibold text-ink" data-testid="svd-sigma-badge">
                {formatSvdNumber(svd.sigma1)} / {formatSvdNumber(svd.sigma2)}
              </div>
            </div>

            <svg
              viewBox="-4 -4 8 8"
              className="min-h-[260px] w-full rounded-md border border-ink/10 bg-paper shadow-[0_16px_36px_rgba(20,20,19,0.12)]"
              aria-label="SVD output space"
            >
              <g transform="scale(1,-1)">
                {gridLines.map((line) => (
                  <g key={line}>
                    <line x1={-4} y1={line} x2={4} y2={line} className="stroke-grid" strokeWidth="0.018" />
                    <line x1={line} y1={-4} x2={line} y2={4} className="stroke-grid" strokeWidth="0.018" />
                  </g>
                ))}
                <line x1={-4} y1={0} x2={4} y2={0} className="stroke-ink/40" strokeWidth="0.035" />
                <line x1={0} y1={-4} x2={0} y2={4} className="stroke-ink/40" strokeWidth="0.035" />
                <polyline
                  points={pointsToSvg(targetEllipse)}
                  className="fill-none stroke-target/30"
                  strokeWidth="0.08"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeDasharray="0.16 0.12"
                />
                <polyline
                  points={pointsToSvg(showRank ? rankEllipse : currentEllipse)}
                  className="fill-none stroke-success"
                  strokeWidth="0.075"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  data-testid="svd-output-ellipse"
                />
                <AxisLine vector={svd.u1} className="stroke-success/70" width={0.045} />
                <AxisLine vector={svd.u2} className="stroke-success/40" width={0.035} />
                {showDirections && (
                  <>
                    <line x1={0} y1={0} x2={av1[0]} y2={av1[1]} className="stroke-orange" strokeWidth="0.06" />
                    <line x1={0} y1={0} x2={av2[0]} y2={av2[1]} className="stroke-target" strokeWidth="0.06" />
                    <circle cx={av1[0]} cy={av1[1]} r={0.14} className="fill-orange stroke-ink" strokeWidth="0.03" data-testid="svd-left-vector-1" />
                    <circle cx={av2[0]} cy={av2[1]} r={0.14} className="fill-target stroke-ink" strokeWidth="0.03" />
                  </>
                )}
              </g>
            </svg>
          </div>

          {showPca && (
            <svg
              viewBox="-4 -2.4 8 4.8"
              className="min-h-[180px] w-full rounded-md border border-ink/10 bg-paper shadow-[0_14px_30px_rgba(20,20,19,0.10)]"
              aria-label="PCA cloud"
              data-testid="svd-pca-cloud"
            >
              <g transform="scale(1,-1)">
                <line x1={-4} y1={0} x2={4} y2={0} className="stroke-ink/30" strokeWidth="0.03" />
                <line x1={0} y1={-2.4} x2={0} y2={2.4} className="stroke-ink/30" strokeWidth="0.03" />
                <AxisLine vector={pcaAxis} className="stroke-target" width={0.055} />
                <AxisLine vector={truePc} className="stroke-success/50" width={0.035} />
                {centeredCloud.map((point) => (
                  <circle key={`${point[0]}:${point[1]}`} cx={point[0]} cy={point[1]} r={0.1} className="fill-orange stroke-ink" strokeWidth="0.02" />
                ))}
              </g>
            </svg>
          )}
        </div>
      }
      controls={
        <div className="space-y-3">
          <div className="grid grid-cols-3 gap-2">
            <div className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5">
              <p className="text-[10px] font-semibold uppercase tracking-wide text-ink/45">det</p>
              <p className="truncate text-xs font-semibold text-ink">{formatSvdNumber(determinant(matrix))}</p>
            </div>
            <div className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5">
              <p className="text-[10px] font-semibold uppercase tracking-wide text-ink/45">rank</p>
              <p className="truncate text-xs font-semibold text-ink">{keepSigma2 ? svd.rank : Math.min(svd.rank, 1)}</p>
            </div>
            <div className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5">
              <p className="text-[10px] font-semibold uppercase tracking-wide text-ink/45">A^T A</p>
              <p className="truncate text-xs font-semibold text-ink">
                {formatSvdNumber(ata.a)}, {formatSvdNumber(ata.b)}, {formatSvdNumber(ata.c)}
              </p>
            </div>
          </div>
          <MatrixReadout matrix={matrix} />
          <div className="grid gap-2 md:grid-cols-2">
            <SliderField label="a" value={matrix.a} testId="svd-matrix-a" onChange={(value) => setMatrixCoord('a', value)} />
            <SliderField label="b" value={matrix.b} testId="svd-matrix-b" onChange={(value) => setMatrixCoord('b', value)} />
            <SliderField label="c" value={matrix.c} testId="svd-matrix-c" onChange={(value) => setMatrixCoord('c', value)} />
            <SliderField label="d" value={matrix.d} testId="svd-matrix-d" onChange={(value) => setMatrixCoord('d', value)} />
          </div>

          {activeLevel.id === 'singular-vs-eigen' && (
            <div className="grid gap-2">
              <ChoiceButton active={singularChoice === 'eigenvalues-a'} label="eigenvalues A" testId="svd-choice-eigenvalues-a" onClick={() => chooseSingular('eigenvalues-a')} />
              <ChoiceButton active={singularChoice === 'signed-values'} label="signed axes" testId="svd-choice-signed-values" onClick={() => chooseSingular('signed-values')} />
              <ChoiceButton active={singularChoice === 'singular-values'} label="sqrt eigenvalues A^T A" testId="svd-choice-singular-values" onClick={() => chooseSingular('singular-values')} />
            </div>
          )}

          {showRank && (
            <div className="rounded border border-ink/10 bg-paper/80 p-2 text-xs text-ink">
              <p className="font-semibold">Rank approximation</p>
              <p className="mt-1 text-ink/65">error = {formatSvdNumber(approxError)}</p>
              <button
                type="button"
                onClick={chooseRankOne}
                className={`mt-2 rounded border px-2 py-1 font-semibold ${
                  keepSigma2 ? 'border-orange/30 bg-orange/10 text-ink' : 'border-success/40 bg-success/15 text-ink'
                }`}
                data-testid="svd-rank-toggle-sigma-2"
              >
                {keepSigma2 ? 'turn off sigma2' : 'sigma2 off'}
              </button>
            </div>
          )}

          {showPca && (
            <div className="space-y-2">
              <SliderField
                label="PCA angle"
                value={pcaAngle}
                min={-1.57}
                max={1.57}
                step={0.01}
                testId="svd-pca-axis"
                onChange={(value) => {
                  setTouched(true)
                  setPcaAngle(Number.isFinite(value) ? value : 0)
                }}
              />
              <div className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5 text-xs text-ink">
                retained variance = {Math.round(variance * 100)}%, error = {formatSvdNumber(pcaError)}
              </div>
            </div>
          )}

          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => resetToPreset()}
              className="inline-flex items-center gap-1 rounded border border-ink/10 bg-paper px-2 py-1 text-xs font-semibold text-ink transition hover:border-orange/40 hover:text-orange"
            >
              <RotateCcw size={14} /> reset
            </button>
            {activeLevel.id === 'circle-to-ellipse' && (
              <button
                type="button"
                onClick={snapMatrix}
                className="inline-flex items-center gap-1 rounded border border-target/25 bg-target/10 px-2 py-1 text-xs font-semibold text-ink transition hover:border-target"
              >
                <Target size={14} /> lens
              </button>
            )}
            {activeLevel.id === 'right-directions' && (
              <button
                type="button"
                onClick={snapDirections}
                className="inline-flex items-center gap-1 rounded border border-success/25 bg-success/10 px-2 py-1 text-xs font-semibold text-ink transition hover:border-success"
              >
                <Target size={14} /> snap v
              </button>
            )}
            {activeLevel.id === 'pca-cloud' && (
              <button
                type="button"
                onClick={snapPca}
                className="inline-flex items-center gap-1 rounded border border-target/25 bg-target/10 px-2 py-1 text-xs font-semibold text-ink transition hover:border-target"
              >
                <Target size={14} /> PCA axis
              </button>
            )}
          </div>
          <div className="sr-only" data-testid="svd-target-match">
            {matrixMatchesSvdTarget(matrix) ? 'target' : 'not-target'}
          </div>
        </div>
      }
      feedback={
        <div className="space-y-1" data-testid="svd-diagnosis">
          <p className="font-semibold text-ink">{diagnosis.message}</p>
          <p>{diagnosis.repairHint}</p>
          <p className="text-xs text-ink/55">
            sigma = ({formatSvdNumber(svd.sigma1)}, {formatSvdNumber(svd.sigma2)}), condition ={' '}
            {Number.isFinite(svd.condition) ? formatSvdNumber(svd.condition) : 'inf'}
          </p>
        </div>
      }
    />
  )
}
