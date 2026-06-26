import { useEffect, useMemo, useRef, useState, type PointerEvent } from 'react'
import { RotateCcw, Target } from 'lucide-react'
import { MissionShell } from '../../game/components/MissionShell'
import { RepairMarker } from '../../game/components/RepairMarker'
import { ResultMoment } from '../../game/components/ResultMoment'
import { chooseMascotState, missionMessage } from '../../game/missionFeedback'
import { quadraticLensMission } from '../../game/missions'
import type { MissionBadge } from '../../game/missionTypes'
import { useMissionRuntime } from '../../game/useMissionRuntime'
import {
  classifyQuadraticForm,
  determinantOfForm,
  diagnoseQuadraticState,
  eigenPairsSymmetric2x2,
  formatQuadraticNumber,
  levelSetSample,
  principalAxisAngle,
  quadraticLevelSuccess,
  quadraticValue,
  rotateForm,
  signatureLabel,
  snapQuadraticValue,
  svgPointToQuadraticCoord,
  type Symmetric2x2,
  type Vec2,
} from './quadraticLensModel'

type DragTarget = 'positive' | 'negative' | 'null' | null

type LevelPreset = {
  form: Symmetric2x2
  rotationAngle: number
  positiveDirection: Vec2
  negativeDirection: Vec2
  nullDirection: Vec2
}

const presets: Record<string, LevelPreset> = {
  'positive-energy': {
    form: { a: 1, b: 1, c: 0 },
    rotationAngle: 0,
    positiveDirection: [1, 0],
    negativeDirection: [0, 1],
    nullDirection: [0, 1],
  },
  'cross-term-rotation': {
    form: { a: 3, b: 1, c: 1 },
    rotationAngle: 0,
    positiveDirection: [1, 0],
    negativeDirection: [0, 1],
    nullDirection: [0, 1],
  },
  'saddle-signature': {
    form: { a: 1, b: 0, c: -1 },
    rotationAngle: 0,
    positiveDirection: [0.3, 0.3],
    negativeDirection: [0.3, 0.3],
    nullDirection: [1, 1],
  },
  'degenerate-direction': {
    form: { a: 1, b: 0, c: 0.6 },
    rotationAngle: 0,
    positiveDirection: [1, 0],
    negativeDirection: [0, 1],
    nullDirection: [1, 1],
  },
  'signature-repair': {
    form: { a: 1, b: 0.2, c: 1 },
    rotationAngle: 0,
    positiveDirection: [1, 0],
    negativeDirection: [0, 1],
    nullDirection: [1, 1],
  },
}

const gridLines = Array.from({ length: 9 }, (_, index) => index - 4)

function AxisLine({ vector, className, width = 0.04 }: { vector: Vec2; className: string; width?: number }) {
  return (
    <line
      x1={-vector[0] * 4}
      y1={-vector[1] * 4}
      x2={vector[0] * 4}
      y2={vector[1] * 4}
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
  disabled = false,
  testId,
  onChange,
}: {
  label: string
  value: number
  min?: number
  max?: number
  step?: number
  disabled?: boolean
  testId: string
  onChange: (value: number) => void
}) {
  return (
    <label className="grid gap-1 text-xs text-ink/70">
      <span className="flex items-center justify-between gap-2">
        <span className="font-semibold text-ink">{label}</span>
        <span className="tabular-nums">{formatQuadraticNumber(value)}</span>
      </span>
      <div className="grid grid-cols-[1fr_70px] items-center gap-2">
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          disabled={disabled}
          onChange={(event) => onChange(Number(event.target.value))}
          className="accent-orange disabled:opacity-45"
          data-testid={`${testId}-range`}
        />
        <input
          type="number"
          min={min}
          max={max}
          step={step}
          value={formatQuadraticNumber(value)}
          disabled={disabled}
          onChange={(event) => onChange(Number(event.target.value))}
          className="w-full rounded border border-ink/10 bg-paper px-2 py-1 text-right tabular-nums text-ink disabled:opacity-45"
          data-testid={testId}
        />
      </div>
    </label>
  )
}

function DirectionReadout({ label, value, form }: { label: string; value: Vec2; form: Symmetric2x2 }) {
  const energy = quadraticValue(form, value)
  const tone = energy > 0.08 ? 'text-success' : energy < -0.08 ? 'text-danger' : 'text-ink/55'
  return (
    <p className="text-xs text-ink/65">
      <span className="font-semibold text-ink">{label}</span> = ({formatQuadraticNumber(value[0])},{' '}
      {formatQuadraticNumber(value[1])}), <span className={tone}>q = {formatQuadraticNumber(energy)}</span>
    </p>
  )
}

function pointsToSvg(points: Vec2[]): string {
  return points.map(([x, y]) => `${formatQuadraticNumber(x)},${formatQuadraticNumber(y)}`).join(' ')
}

export function QuadraticLensMission() {
  const definition = quadraticLensMission
  const runtime = useMissionRuntime(definition)
  const activeLevel = runtime.activeLevel
  const { completeActiveLevel, setActiveLevelId } = runtime
  const [form, setForm] = useState<Symmetric2x2>(presets[activeLevel.id].form)
  const [rotationAngle, setRotationAngle] = useState(presets[activeLevel.id].rotationAngle)
  const [positiveDirection, setPositiveDirection] = useState<Vec2>(presets[activeLevel.id].positiveDirection)
  const [negativeDirection, setNegativeDirection] = useState<Vec2>(presets[activeLevel.id].negativeDirection)
  const [nullDirection, setNullDirection] = useState<Vec2>(presets[activeLevel.id].nullDirection)
  const [touched, setTouched] = useState(false)
  const svgRef = useRef<SVGSVGElement>(null)
  const dragTarget = useRef<DragTarget>(null)

  const resetLevel = () => {
    const preset = presets[activeLevel.id]
    setForm(preset.form)
    setRotationAngle(preset.rotationAngle)
    setPositiveDirection(preset.positiveDirection)
    setNegativeDirection(preset.negativeDirection)
    setNullDirection(preset.nullDirection)
    setTouched(false)
  }

  const selectLevel = (levelId: string) => {
    const preset = presets[levelId]
    if (preset) {
      setForm(preset.form)
      setRotationAngle(preset.rotationAngle)
      setPositiveDirection(preset.positiveDirection)
      setNegativeDirection(preset.negativeDirection)
      setNullDirection(preset.nullDirection)
      setTouched(false)
    }
    setActiveLevelId(levelId)
  }

  const classification = classifyQuadraticForm(form)
  const signature = signatureLabel(form)
  const det = determinantOfForm(form)
  const eigenPairs = useMemo(() => eigenPairsSymmetric2x2(form), [form])
  const principalAngle = useMemo(() => principalAxisAngle(form), [form])
  const rotatedForm = useMemo(() => rotateForm(form, rotationAngle), [form, rotationAngle])
  const contourBranches = useMemo(() => levelSetSample(form, 1, { radius: 3.8 }), [form])

  const levelSuccess = useMemo(
    () =>
      quadraticLevelSuccess({
        levelId: activeLevel.id,
        form,
        rotationAngle,
        positiveDirection,
        negativeDirection,
        nullDirection,
        touched,
      }),
    [activeLevel.id, form, negativeDirection, nullDirection, positiveDirection, rotationAngle, touched],
  )

  const diagnosis = diagnoseQuadraticState({
    levelId: activeLevel.id,
    form,
    rotationAngle,
    positiveDirection,
    negativeDirection,
    nullDirection,
    touched,
  })

  const repairLabelByKind: Record<string, string> = {
    'not-positive': 'не эллипс',
    'manual-zero-cross-term': 'крути базис, не b',
    'same-sign-directions': 'оси одного знака',
    'zero-direction': 'нулевое направление',
    'not-degenerate': 'не вырождено',
    'all-zero-form': 'форма нулевая',
    'wrong-signature': 'не та сигнатура',
  }
  const repairLabel = repairLabelByKind[diagnosis.kind] ?? 'почини форму'
  const showRepairMarker = touched && !levelSuccess && diagnosis.kind in repairLabelByKind

  useEffect(() => {
    if (!levelSuccess) return
    completeActiveLevel()
  }, [completeActiveLevel, levelSuccess])

  const mascotState = chooseMascotState({
    success: levelSuccess,
    warning:
      touched &&
      [
        'not-positive',
        'manual-zero-cross-term',
        'same-sign-directions',
        'zero-direction',
        'not-degenerate',
        'all-zero-form',
        'wrong-signature',
      ].includes(diagnosis.kind),
    hint:
      Math.abs(rotatedForm.b) < 0.22 ||
      Math.abs(det) < 0.18 ||
      classification.includes('semidefinite'),
    thinking: activeLevel.id === 'cross-term-rotation',
  })
  const mascotMessage = missionMessage(mascotState, {
    success: activeLevel.successText,
    warning: activeLevel.mistakeFeedback?.[0] ?? diagnosis.message,
    hint: activeLevel.hint,
    thinking:
      'Я стою рядом с главными осями: когда базис повернут правильно, смешанный член исчезает.',
    idle: 'Меняй форму и направления. Я буду подсвечивать энергию, сигнатуру и схлопнутые оси.',
  })

  const badges: MissionBadge[] = [
    {
      id: 'signature',
      label: 'signature',
      value: signature,
      tone: levelSuccess ? 'success' : signature === '(+,-)' ? 'target' : 'energy',
    },
    {
      id: 'det',
      label: 'det',
      value: formatQuadraticNumber(det),
      tone: Math.abs(det) < 0.08 ? 'warning' : det < 0 ? 'target' : 'energy',
    },
    {
      id: 'cross-term',
      label: 'b rotated',
      value: formatQuadraticNumber(rotatedForm.b),
      tone: Math.abs(rotatedForm.b) < 0.04 ? 'success' : 'neutral',
    },
  ]

  const setFormCoord = (key: keyof Symmetric2x2, value: number) => {
    const safeValue = Number.isFinite(value) ? snapQuadraticValue(value) : 0
    setTouched(true)
    setForm((current) => ({ ...current, [key]: safeValue }))
  }

  const setDirection = (target: DragTarget, next: Vec2) => {
    setTouched(true)
    if (target === 'positive') setPositiveDirection(next)
    if (target === 'negative') setNegativeDirection(next)
    if (target === 'null') setNullDirection(next)
  }

  const eventToPoint = (event: PointerEvent<SVGSVGElement>): Vec2 => {
    const svg = svgRef.current
    if (!svg) return [0, 0]
    return svgPointToQuadraticCoord({
      clientX: event.clientX,
      clientY: event.clientY,
      rect: svg.getBoundingClientRect(),
    })
  }

  const handlePointerMove = (event: PointerEvent<SVGSVGElement>) => {
    if (!dragTarget.current) return
    setDirection(dragTarget.current, eventToPoint(event))
  }

  const startDrag = (event: PointerEvent<SVGCircleElement>, target: DragTarget) => {
    dragTarget.current = target
    event.currentTarget.setPointerCapture(event.pointerId)
  }

  const stopDrag = () => {
    dragTarget.current = null
  }

  const setDirectionCoord = (target: 'positive' | 'negative' | 'null', coord: 0 | 1, value: number) => {
    const safeValue = Number.isFinite(value) ? snapQuadraticValue(value) : 0
    setTouched(true)
    const setter =
      target === 'positive' ? setPositiveDirection : target === 'negative' ? setNegativeDirection : setNullDirection
    setter((current) => {
      const next = [...current] as Vec2
      next[coord] = safeValue
      return next
    })
  }

  const useCrossTermLock = activeLevel.id === 'cross-term-rotation'
  const showPositiveMarker = activeLevel.id === 'saddle-signature' || activeLevel.id === 'signature-repair'
  const showNegativeMarker = activeLevel.id === 'saddle-signature' || activeLevel.id === 'signature-repair'
  const showNullMarker = activeLevel.id === 'degenerate-direction'
  const axisVector: Vec2 = [Math.cos(rotationAngle), Math.sin(rotationAngle)]
  const axisSecond: Vec2 = [-Math.sin(rotationAngle), Math.cos(rotationAngle)]
  const eigenFirst = eigenPairs[0].vector
  const eigenSecond: Vec2 = [-eigenFirst[1], eigenFirst[0]]
  const contourClass =
    classification === 'positive-definite'
      ? 'stroke-success'
      : classification === 'indefinite'
        ? 'stroke-danger'
        : classification.includes('semidefinite')
          ? 'stroke-orange'
          : 'stroke-ink/35'

  const quickSetPositive = () => {
    setTouched(true)
    setForm({ a: 2, b: 0.2, c: 1 })
  }

  const quickSetSaddle = () => {
    setTouched(true)
    setForm({ a: 1, b: 0, c: -1 })
    setPositiveDirection([1, 0])
    setNegativeDirection([0, 1])
  }

  const quickSetDegenerate = () => {
    setTouched(true)
    setForm({ a: 1, b: 0, c: 0 })
    setNullDirection([0, 1])
  }

  const snapToAxis = () => {
    setTouched(true)
    setRotationAngle(principalAngle)
  }

  return (
    <MissionShell
      definition={definition}
      activeLevelId={activeLevel.id}
      onLevelSelect={selectLevel}
      mascotState={mascotState}
      mascotMessage={mascotMessage}
      badges={badges}
      sceneViewportClassName="h-[560px] pt-[108px] sm:pt-[78px] lg:h-full"
      scene={
        <div className="relative flex h-full items-center justify-center bg-[radial-gradient(circle_at_22%_16%,rgba(95,141,99,0.16),transparent_30%),radial-gradient(circle_at_82%_74%,rgba(106,155,204,0.18),transparent_28%),linear-gradient(180deg,#fffdf7,#f6f3e8)] p-4">
          <ResultMoment show={levelSuccess} label="главные оси найдены" />
          {showRepairMarker && (
            <RepairMarker tone="warning" label={repairLabel} xPercent={50} yPercent={3} />
          )}
          <svg
            ref={svgRef}
            viewBox="-4 -4 8 8"
            className="aspect-square max-h-full w-full max-w-[720px] touch-none rounded-md border border-ink/10 bg-paper shadow-[0_20px_48px_rgba(20,20,19,0.14)]"
            onPointerMove={handlePointerMove}
            onPointerUp={stopDrag}
            onPointerCancel={stopDrag}
            aria-label="Квадратичная линза"
            data-testid="quadratic-lens-canvas"
          >
            <g transform="scale(1,-1)">
              {gridLines.map((line) => (
                <g key={line}>
                  <line x1={-4} y1={line} x2={4} y2={line} className="stroke-grid" strokeWidth="0.018" />
                  <line x1={line} y1={-4} x2={line} y2={4} className="stroke-grid" strokeWidth="0.018" />
                </g>
              ))}
              <line x1={-4} y1={0} x2={4} y2={0} className="stroke-ink/45" strokeWidth="0.035" />
              <line x1={0} y1={-4} x2={0} y2={4} className="stroke-ink/45" strokeWidth="0.035" />

              <AxisLine vector={eigenFirst} className="stroke-target/75" width={0.05} />
              <AxisLine vector={eigenSecond} className="stroke-target/45" width={0.04} />
              <AxisLine vector={axisVector} className="stroke-ink/55" width={0.032} />
              <AxisLine vector={axisSecond} className="stroke-ink/35" width={0.03} />

              {contourBranches.map((branch) => (
                <polyline
                  key={branch.id}
                  points={pointsToSvg(branch.points)}
                  className={`${contourClass} fill-none`}
                  strokeWidth="0.07"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  data-testid="quadratic-contour"
                />
              ))}

              {showPositiveMarker && (
                <>
                  <line
                    x1={0}
                    y1={0}
                    x2={positiveDirection[0]}
                    y2={positiveDirection[1]}
                    className="stroke-success"
                    strokeWidth="0.055"
                    strokeLinecap="round"
                  />
                  <circle
                    cx={positiveDirection[0]}
                    cy={positiveDirection[1]}
                    r={0.18}
                    className="cursor-grab fill-success stroke-ink"
                    strokeWidth="0.035"
                    data-testid="quadratic-positive-marker"
                    onPointerDown={(event) => startDrag(event, 'positive')}
                  />
                </>
              )}
              {showNegativeMarker && (
                <>
                  <line
                    x1={0}
                    y1={0}
                    x2={negativeDirection[0]}
                    y2={negativeDirection[1]}
                    className="stroke-danger"
                    strokeWidth="0.055"
                    strokeLinecap="round"
                  />
                  <circle
                    cx={negativeDirection[0]}
                    cy={negativeDirection[1]}
                    r={0.18}
                    className="cursor-grab fill-danger stroke-ink"
                    strokeWidth="0.035"
                    data-testid="quadratic-negative-marker"
                    onPointerDown={(event) => startDrag(event, 'negative')}
                  />
                </>
              )}
              {showNullMarker && (
                <>
                  <line
                    x1={0}
                    y1={0}
                    x2={nullDirection[0]}
                    y2={nullDirection[1]}
                    className="stroke-orange"
                    strokeWidth="0.055"
                    strokeLinecap="round"
                  />
                  <circle
                    cx={nullDirection[0]}
                    cy={nullDirection[1]}
                    r={0.18}
                    className="cursor-grab fill-orange stroke-ink"
                    strokeWidth="0.035"
                    data-testid="quadratic-null-marker"
                    onPointerDown={(event) => startDrag(event, 'null')}
                  />
                </>
              )}
            </g>
          </svg>
        </div>
      }
      controls={
        <div className="space-y-3">
          <div className="grid grid-cols-3 gap-2" data-testid="signature-badge">
            <div className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5">
              <p className="text-[10px] font-semibold uppercase tracking-wide text-ink/45">class</p>
              <p className="truncate text-xs font-semibold text-ink">{classification}</p>
            </div>
            <div className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5">
              <p className="text-[10px] font-semibold uppercase tracking-wide text-ink/45">lambda</p>
              <p className="truncate text-xs font-semibold text-ink">
                {formatQuadraticNumber(eigenPairs[0].lambda)}, {formatQuadraticNumber(eigenPairs[1].lambda)}
              </p>
            </div>
            <div className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5">
              <p className="text-[10px] font-semibold uppercase tracking-wide text-ink/45">q axes</p>
              <p className="truncate text-xs font-semibold text-ink">{formatQuadraticNumber(rotatedForm.b)}</p>
            </div>
          </div>

          <div className="space-y-2">
            <SliderField
              label="a в ax²"
              value={form.a}
              disabled={useCrossTermLock}
              testId="coefficient-a"
              onChange={(value) => setFormCoord('a', value)}
            />
            <SliderField
              label="b в 2bxy"
              value={form.b}
              disabled={useCrossTermLock}
              testId="coefficient-b"
              onChange={(value) => setFormCoord('b', value)}
            />
            <SliderField
              label="c в cy²"
              value={form.c}
              disabled={useCrossTermLock}
              testId="coefficient-c"
              onChange={(value) => setFormCoord('c', value)}
            />
            <SliderField
              label="поворот базиса"
              value={rotationAngle}
              min={-1.57}
              max={1.57}
              step={0.01}
              testId="basis-rotation"
              onChange={(value) => {
                setTouched(true)
                setRotationAngle(Number.isFinite(value) ? value : 0)
              }}
            />
          </div>

          {(showPositiveMarker || showNegativeMarker || showNullMarker) && (
            <div className="rounded border border-ink/10 bg-paper/75 p-2" data-testid="energy-marker">
              <p className="mb-2 text-xs font-semibold text-ink">Маркеры направлений</p>
              {showPositiveMarker && <DirectionReadout label="plus" value={positiveDirection} form={form} />}
              {showNegativeMarker && <DirectionReadout label="minus" value={negativeDirection} form={form} />}
              {showNullMarker && <DirectionReadout label="zero" value={nullDirection} form={form} />}
              <div className="mt-2 grid grid-cols-2 gap-2">
                {showPositiveMarker && (
                  <>
                    <SliderField
                      label="plus x"
                      value={positiveDirection[0]}
                      testId="positive-x"
                      onChange={(value) => setDirectionCoord('positive', 0, value)}
                    />
                    <SliderField
                      label="plus y"
                      value={positiveDirection[1]}
                      testId="positive-y"
                      onChange={(value) => setDirectionCoord('positive', 1, value)}
                    />
                  </>
                )}
                {showNegativeMarker && (
                  <>
                    <SliderField
                      label="minus x"
                      value={negativeDirection[0]}
                      testId="negative-x"
                      onChange={(value) => setDirectionCoord('negative', 0, value)}
                    />
                    <SliderField
                      label="minus y"
                      value={negativeDirection[1]}
                      testId="negative-y"
                      onChange={(value) => setDirectionCoord('negative', 1, value)}
                    />
                  </>
                )}
                {showNullMarker && (
                  <>
                    <SliderField
                      label="zero x"
                      value={nullDirection[0]}
                      testId="null-x"
                      onChange={(value) => setDirectionCoord('null', 0, value)}
                    />
                    <SliderField
                      label="zero y"
                      value={nullDirection[1]}
                      testId="null-y"
                      onChange={(value) => setDirectionCoord('null', 1, value)}
                    />
                  </>
                )}
              </div>
            </div>
          )}

          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={resetLevel}
              className="inline-flex items-center gap-1 rounded border border-ink/10 bg-paper px-2 py-1 text-xs font-semibold text-ink transition hover:border-orange/40 hover:text-orange"
            >
              <RotateCcw size={14} /> reset
            </button>
            {activeLevel.id === 'positive-energy' && (
              <button
                type="button"
                onClick={quickSetPositive}
                className="inline-flex items-center gap-1 rounded border border-success/25 bg-success/10 px-2 py-1 text-xs font-semibold text-ink transition hover:border-success"
              >
                <Target size={14} /> ellipse
              </button>
            )}
            {activeLevel.id === 'cross-term-rotation' && (
              <button
                type="button"
                onClick={snapToAxis}
                className="inline-flex items-center gap-1 rounded border border-target/25 bg-target/10 px-2 py-1 text-xs font-semibold text-ink transition hover:border-target"
              >
                <Target size={14} /> snap axes
              </button>
            )}
            {activeLevel.id === 'saddle-signature' && (
              <button
                type="button"
                onClick={quickSetSaddle}
                className="inline-flex items-center gap-1 rounded border border-danger/25 bg-danger/10 px-2 py-1 text-xs font-semibold text-ink transition hover:border-danger"
              >
                <Target size={14} /> saddle
              </button>
            )}
            {activeLevel.id === 'degenerate-direction' && (
              <button
                type="button"
                onClick={quickSetDegenerate}
                className="inline-flex items-center gap-1 rounded border border-orange/25 bg-orange/10 px-2 py-1 text-xs font-semibold text-ink transition hover:border-orange"
              >
                <Target size={14} /> collapse
              </button>
            )}
          </div>
        </div>
      }
      feedback={
        <div className="space-y-1" data-testid="quadratic-diagnosis">
          <p className="font-semibold text-ink">{diagnosis.message}</p>
          <p>{diagnosis.repairHint}</p>
          <p className="text-xs text-ink/55">
            q(x,y) = {formatQuadraticNumber(form.a)}x² + {formatQuadraticNumber(2 * form.b)}xy +{' '}
            {formatQuadraticNumber(form.c)}y²
          </p>
        </div>
      }
    />
  )
}
