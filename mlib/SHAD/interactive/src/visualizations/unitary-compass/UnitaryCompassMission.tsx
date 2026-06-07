import { useEffect, useMemo, useState } from 'react'
import { RotateCcw, Sparkles, Target } from 'lucide-react'
import { MissionShell } from '../../game/components/MissionShell'
import { chooseMascotState, missionMessage } from '../../game/missionFeedback'
import { unitaryCompassMission } from '../../game/missions'
import type { MissionBadge } from '../../game/missionTypes'
import { useMissionRuntime } from '../../game/useMissionRuntime'
import {
  adjointMatrix,
  baseVector,
  complex,
  complexDotBilinear,
  diagnoseAStarABridge,
  diagnoseHermitianMatrix,
  diagnoseHermitianSlot,
  diagnoseUnitaryMatrix,
  fakeHermitianMatrix,
  formatComplex,
  formatUnitaryNumber,
  hermitianNormSquared,
  hermitianTargetMatrix,
  innerByMode,
  isHermitianMatrix,
  isUnitaryMatrix,
  matrixByAStarChoice,
  matrixStarMatrix,
  nonUnitaryMatrix,
  phaseRotateVector,
  phaseRotationMatrix,
  snapUnitaryValue,
  type AStarChoice,
  type Complex,
  type ComplexMatrix2x2,
  type ComplexVec2,
  type HermitianSlotMode,
  type UnitaryDiagnosis,
} from './unitaryCompassModel'

type LevelPreset = {
  innerMode: HermitianSlotMode
  phaseAngle: number
  hermitianMatrix: ComplexMatrix2x2
  unitaryMatrix: ComplexMatrix2x2
  bridgeChoice: AStarChoice
}

const presets: Record<string, LevelPreset> = {
  'i-scale-trap': {
    innerMode: 'bilinear',
    phaseAngle: 0,
    hermitianMatrix: fakeHermitianMatrix,
    unitaryMatrix: nonUnitaryMatrix,
    bridgeChoice: 'ata',
  },
  'conjugate-slot': {
    innerMode: 'bilinear',
    phaseAngle: 0,
    hermitianMatrix: fakeHermitianMatrix,
    unitaryMatrix: nonUnitaryMatrix,
    bridgeChoice: 'ata',
  },
  'phase-preserve': {
    innerMode: 'conjugate-second',
    phaseAngle: 0,
    hermitianMatrix: fakeHermitianMatrix,
    unitaryMatrix: nonUnitaryMatrix,
    bridgeChoice: 'ata',
  },
  'fake-hermitian': {
    innerMode: 'conjugate-second',
    phaseAngle: Math.PI / 2,
    hermitianMatrix: fakeHermitianMatrix,
    unitaryMatrix: nonUnitaryMatrix,
    bridgeChoice: 'ata',
  },
  'unitary-motion': {
    innerMode: 'conjugate-second',
    phaseAngle: Math.PI / 2,
    hermitianMatrix: hermitianTargetMatrix,
    unitaryMatrix: nonUnitaryMatrix,
    bridgeChoice: 'ata',
  },
  'a-star-a-bridge': {
    innerMode: 'conjugate-second',
    phaseAngle: Math.PI / 2,
    hermitianMatrix: hermitianTargetMatrix,
    unitaryMatrix: phaseRotationMatrix(Math.PI / 2),
    bridgeChoice: 'ata',
  },
}

const planeGrid = [-1, 0, 1]

function toPlanePoint(value: Complex, scale = 1.35): [number, number] {
  return [value.re * scale, value.im * scale]
}

function complexPoint(value: Complex, className: string, testId?: string) {
  const [x, y] = toPlanePoint(value)
  return (
    <>
      <line x1={0} y1={0} x2={x} y2={y} className={className} strokeWidth="0.055" strokeLinecap="round" />
      <circle cx={x} cy={y} r={0.075} className={`${className.replace('stroke-', 'fill-')} stroke-ink`} strokeWidth="0.025" data-testid={testId} />
    </>
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
        active ? 'border-target bg-target text-bg' : 'border-ink/10 bg-paper text-ink hover:border-target/50'
      }`}
      data-testid={testId}
    >
      {label}
    </button>
  )
}

function ComplexInput({
  label,
  value,
  reTestId,
  imTestId,
  onChange,
}: {
  label: string
  value: Complex
  reTestId: string
  imTestId: string
  onChange: (value: Complex) => void
}) {
  return (
    <div className="rounded border border-ink/10 bg-paper/80 p-2">
      <p className="text-[10px] font-semibold uppercase tracking-wide text-ink/45">{label}</p>
      <div className="mt-1 grid grid-cols-2 gap-2">
        <label className="grid gap-1 text-[11px] text-ink/60">
          re
          <input
            type="number"
            step={0.1}
            value={formatUnitaryNumber(value.re)}
            onChange={(event) => onChange({ ...value, re: snapUnitaryValue(Number(event.target.value)) })}
            className="min-w-0 rounded border border-ink/10 bg-bg px-1.5 py-1 text-right text-xs text-ink"
            data-testid={reTestId}
          />
        </label>
        <label className="grid gap-1 text-[11px] text-ink/60">
          im
          <input
            type="number"
            step={0.1}
            value={formatUnitaryNumber(value.im)}
            onChange={(event) => onChange({ ...value, im: snapUnitaryValue(Number(event.target.value)) })}
            className="min-w-0 rounded border border-ink/10 bg-bg px-1.5 py-1 text-right text-xs text-ink"
            data-testid={imTestId}
          />
        </label>
      </div>
    </div>
  )
}

function MatrixReadout({ matrix, label = 'A' }: { matrix: ComplexMatrix2x2; label?: string }) {
  return (
    <div className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5 text-xs text-ink">
      <p className="text-[10px] font-semibold uppercase tracking-wide text-ink/45">{label}</p>
      <p className="mt-1 leading-relaxed">
        [{formatComplex(matrix.a)}, {formatComplex(matrix.b)}; {formatComplex(matrix.c)},{' '}
        {formatComplex(matrix.d)}]
      </p>
    </div>
  )
}

export function UnitaryCompassMission() {
  const definition = unitaryCompassMission
  const runtime = useMissionRuntime(definition)
  const activeLevel = runtime.activeLevel
  const { completeActiveLevel, setActiveLevelId } = runtime
  const [innerMode, setInnerMode] = useState<HermitianSlotMode>(presets[activeLevel.id].innerMode)
  const [phaseAngle, setPhaseAngle] = useState(presets[activeLevel.id].phaseAngle)
  const [hermitianMatrix, setHermitianMatrix] = useState<ComplexMatrix2x2>(presets[activeLevel.id].hermitianMatrix)
  const [unitaryMatrix, setUnitaryMatrix] = useState<ComplexMatrix2x2>(presets[activeLevel.id].unitaryMatrix)
  const [bridgeChoice, setBridgeChoice] = useState<AStarChoice>(presets[activeLevel.id].bridgeChoice)
  const [touched, setTouched] = useState(false)

  const resetToPreset = (levelId = activeLevel.id) => {
    const preset = presets[levelId]
    setInnerMode(preset.innerMode)
    setPhaseAngle(preset.phaseAngle)
    setHermitianMatrix(preset.hermitianMatrix)
    setUnitaryMatrix(preset.unitaryMatrix)
    setBridgeChoice(preset.bridgeChoice)
    setTouched(false)
  }

  const selectLevel = (levelId: string) => {
    resetToPreset(levelId)
    setActiveLevelId(levelId)
  }

  const ixVector = phaseRotateVector(baseVector, Math.PI / 2)
  const phaseVector = phaseRotateVector(baseVector, phaseAngle)
  const modeDiagnosis = diagnoseHermitianSlot(innerMode)
  const hermitianDiagnosis = diagnoseHermitianMatrix(hermitianMatrix)
  const unitaryDiagnosis = diagnoseUnitaryMatrix(unitaryMatrix)
  const bridgeDiagnosis = diagnoseAStarABridge(bridgeChoice, nonUnitaryMatrix)
  const selectedInner = innerByMode(ixVector, ixVector, innerMode)
  const bilinearTrap = complexDotBilinear(ixVector, ixVector)
  const hermitianNorm = hermitianNormSquared(ixVector)
  const bridgeMatrix = useMemo(() => matrixByAStarChoice(nonUnitaryMatrix, bridgeChoice), [bridgeChoice])
  const uStarU = useMemo(() => matrixStarMatrix(unitaryMatrix), [unitaryMatrix])
  const unitaryApplied = useMemo(() => phaseRotateVector(applyUnitaryPreview(unitaryMatrix), 0), [unitaryMatrix])

  const levelSuccess = (() => {
    if (activeLevel.id === 'i-scale-trap') return innerMode === 'conjugate-second' && touched
    if (activeLevel.id === 'conjugate-slot') return modeDiagnosis.kind === 'ready' && touched
    if (activeLevel.id === 'phase-preserve') {
      return Math.abs(phaseAngle - Math.PI / 2) < 0.04 && Math.abs(hermitianNormSquared(phaseVector) - hermitianNormSquared(baseVector)) < 0.04 && touched
    }
    if (activeLevel.id === 'fake-hermitian') return hermitianDiagnosis.kind === 'ready' && touched
    if (activeLevel.id === 'unitary-motion') return unitaryDiagnosis.kind === 'ready' && touched
    return bridgeDiagnosis.kind === 'ready' && touched
  })()

  const diagnosis: UnitaryDiagnosis = (() => {
    if (levelSuccess) {
      return { kind: 'ready', message: activeLevel.successText, repairHint: activeLevel.takeaway }
    }
    if (activeLevel.id === 'i-scale-trap' || activeLevel.id === 'conjugate-slot') return modeDiagnosis
    if (activeLevel.id === 'phase-preserve') {
      return {
        kind: 'not-unitary',
        message: `phase = ${formatUnitaryNumber(phaseAngle)}, norm = ${formatUnitaryNumber(hermitianNormSquared(phaseVector))}.`,
        repairHint: 'Поставь phase pi/2: должна измениться фаза, но не Hermitian norm.',
      }
    }
    if (activeLevel.id === 'fake-hermitian') return hermitianDiagnosis
    if (activeLevel.id === 'unitary-motion') return unitaryDiagnosis
    return bridgeDiagnosis
  })()

  useEffect(() => {
    if (levelSuccess) completeActiveLevel()
  }, [completeActiveLevel, levelSuccess])

  const mascotState = chooseMascotState({
    success: levelSuccess,
    warning: touched && diagnosis.kind !== 'ready',
    hint: activeLevel.id === 'a-star-a-bridge' && bridgeChoice !== 'astar-a',
    thinking: !touched,
  })
  const mascotMessage = missionMessage(mascotState, {
    idle: 'Меби смотрит на фазу: комплексная длина должна пережить поворот на i.',
    thinking: 'Здесь главный ход - не новая формула, а правильное место для сопряжения.',
    hint: 'Adjoint - это conjugate transpose. Именно звездочка делает A* A хорошей Hermitian задачей.',
    warning: diagnosis.repairHint,
    success: activeLevel.takeaway,
  })

  const badges: MissionBadge[] = [
    {
      id: 'norm',
      label: 'NORM',
      value: formatUnitaryNumber(hermitianNormSquared(phaseVector)),
      tone: Math.abs(hermitianNormSquared(phaseVector) - hermitianNormSquared(baseVector)) < 0.06 ? 'success' : 'warning',
    },
    {
      id: 'phase',
      label: 'PHASE',
      value: `${formatUnitaryNumber(phaseAngle / Math.PI)}π`,
      tone: Math.abs(phaseAngle - Math.PI / 2) < 0.06 ? 'success' : 'neutral',
    },
    {
      id: 'hermitian',
      label: 'HERMITIAN',
      value: isHermitianMatrix(hermitianMatrix) ? 'yes' : 'no',
      tone: isHermitianMatrix(hermitianMatrix) ? 'success' : 'warning',
    },
    {
      id: 'unitary',
      label: 'U*U',
      value: isUnitaryMatrix(unitaryMatrix) ? 'I' : 'drift',
      tone: isUnitaryMatrix(unitaryMatrix) ? 'success' : 'warning',
    },
  ]

  const chooseMode = (mode: HermitianSlotMode) => {
    setInnerMode(mode)
    setTouched(true)
  }

  const chooseBridge = (choice: AStarChoice) => {
    setBridgeChoice(choice)
    setTouched(true)
  }

  const setHermitianCoord = (key: keyof ComplexMatrix2x2, value: Complex) => {
    setHermitianMatrix((current) => ({ ...current, [key]: value }))
    setTouched(true)
  }

  const setUnitaryCoord = (key: keyof ComplexMatrix2x2, value: Complex) => {
    setUnitaryMatrix((current) => ({ ...current, [key]: value }))
    setTouched(true)
  }

  const makeHermitian = () => {
    setHermitianMatrix(hermitianTargetMatrix)
    setTouched(true)
  }

  const snapU = () => {
    setUnitaryMatrix(phaseRotationMatrix(Math.PI / 2))
    setTouched(true)
  }

  const setPhasePiHalf = () => {
    setPhaseAngle(Math.PI / 2)
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
      sceneViewportClassName="min-h-[650px] pt-[112px] sm:pt-[82px] lg:h-full lg:min-h-0"
      scene={
        <div className="grid h-full min-h-[650px] gap-3 bg-[radial-gradient(circle_at_20%_20%,rgba(84,120,164,0.16),transparent_28%),radial-gradient(circle_at_82%_74%,rgba(207,109,80,0.13),transparent_26%),linear-gradient(180deg,#fffdf7,#f5f2e8)] p-3 lg:grid-cols-[1fr_0.88fr]">
          <div className="grid content-start gap-3">
            <svg
              viewBox="-2.25 -2.25 4.5 4.5"
              className="aspect-square w-full rounded border border-ink/10 bg-paper shadow-soft"
              data-testid="unitary-compass-canvas"
              aria-label="Unitary compass complex plane"
            >
              <g transform="scale(1 -1)" data-testid="complex-vector-plane">
                {planeGrid.map((line) => (
                  <g key={line}>
                    <line x1={-2.1} y1={line} x2={2.1} y2={line} className="stroke-grid" strokeWidth="0.018" />
                    <line x1={line} y1={-2.1} x2={line} y2={2.1} className="stroke-grid" strokeWidth="0.018" />
                  </g>
                ))}
                <circle cx={0} cy={0} r={1.35} className="fill-none stroke-target/35" strokeWidth="0.035" strokeDasharray="0.12 0.09" />
                <line x1={-2.1} y1={0} x2={2.1} y2={0} className="stroke-ink/35" strokeWidth="0.03" />
                <line x1={0} y1={-2.1} x2={0} y2={2.1} className="stroke-ink/35" strokeWidth="0.03" />
                {complexPoint(baseVector[0], 'stroke-orange', 'complex-vector-x')}
                {complexPoint(ixVector[0], 'stroke-target', 'complex-vector-ix')}
                {activeLevel.id === 'phase-preserve' && complexPoint(phaseVector[0], 'stroke-success', 'unitary-phase-vector')}
                {activeLevel.id === 'unitary-motion' && complexPoint(unitaryApplied[0], 'stroke-success', 'unitary-applied-vector')}
              </g>
            </svg>
            <div className="grid grid-cols-2 gap-2">
              <div className="rounded border border-ink/10 bg-paper px-2 py-1.5 text-xs" data-testid="unitary-norm-badge">
                <p className="text-[10px] font-semibold uppercase text-ink/45">Hermitian norm</p>
                <p className="font-semibold text-ink">{formatUnitaryNumber(hermitianNorm)}</p>
              </div>
              <div className="rounded border border-ink/10 bg-paper px-2 py-1.5 text-xs">
                <p className="text-[10px] font-semibold uppercase text-ink/45">Bilinear B(ix,ix)</p>
                <p className="font-semibold text-ink">{formatComplex(bilinearTrap)}</p>
              </div>
              <div className="rounded border border-ink/10 bg-paper px-2 py-1.5 text-xs">
                <p className="text-[10px] font-semibold uppercase text-ink/45">Selected</p>
                <p className="font-semibold text-ink">{formatComplex(selectedInner)}</p>
              </div>
              <div className="rounded border border-ink/10 bg-paper px-2 py-1.5 text-xs" data-testid="unitary-ustaru-badge">
                <p className="text-[10px] font-semibold uppercase text-ink/45">U*U</p>
                <p className="font-semibold text-ink">{formatComplex(uStarU.a)}, {formatComplex(uStarU.b)}, {formatComplex(uStarU.d)}</p>
              </div>
            </div>
          </div>

          <div className="grid content-start gap-3">
            <div className="rounded border border-ink/10 bg-bg/80 p-3">
              <p className="text-[10px] font-semibold uppercase tracking-wide text-orange">Conjugation mirror</p>
              <p className="mt-1 text-sm font-semibold text-ink">&lt;x,y&gt; = sum x_k overline(y_k)</p>
              <p className="mt-1 text-xs leading-relaxed text-ink/65">
                Сопряжение отражает фазу через real axis. Без этой звездочки complex length перестает быть длиной.
              </p>
            </div>
            <MatrixReadout matrix={hermitianMatrix} label="Hermitian test" />
            <MatrixReadout matrix={bridgeMatrix} label={bridgeChoice === 'astar-a' ? 'A* A' : bridgeChoice === 'ata' ? 'A^T A' : 'A A*'} />
            <MatrixReadout matrix={adjointMatrix(hermitianMatrix)} label="A*" />
          </div>
        </div>
      }
      controls={
        <div className="space-y-3">
          {(activeLevel.id === 'i-scale-trap' || activeLevel.id === 'conjugate-slot') && (
            <div className="grid gap-2">
              <ChoiceButton active={innerMode === 'bilinear'} label="bilinear" testId="unitary-bilinear-choice" onClick={() => chooseMode('bilinear')} />
              <ChoiceButton active={innerMode === 'conjugate-first'} label="conjugate first" testId="unitary-conjugate-first-choice" onClick={() => chooseMode('conjugate-first')} />
              <ChoiceButton active={innerMode === 'conjugate-second'} label="conjugate second" testId="unitary-conjugate-second-choice" onClick={() => chooseMode('conjugate-second')} />
              <button type="button" onClick={() => chooseMode('conjugate-second')} className="inline-flex items-center gap-1 rounded border border-target/25 bg-target/10 px-2 py-1 text-xs font-semibold text-ink transition hover:border-target" data-testid="unitary-hermitian-choice">
                <Target size={14} /> Hermitian norm
              </button>
            </div>
          )}

          {activeLevel.id === 'phase-preserve' && (
            <div className="space-y-2">
              <label className="grid gap-1 text-xs text-ink/70">
                <span className="flex items-center justify-between">
                  <span className="font-semibold text-ink">phase</span>
                  <span>{formatUnitaryNumber(phaseAngle / Math.PI)}π</span>
                </span>
                <input
                  type="range"
                  min={0}
                  max={Math.PI * 2}
                  step={0.01}
                  value={phaseAngle}
                  onChange={(event) => {
                    setPhaseAngle(Number(event.target.value))
                    setTouched(true)
                  }}
                  className="accent-target"
                  data-testid="unitary-phase-knob"
                />
              </label>
              <button type="button" onClick={setPhasePiHalf} className="inline-flex items-center gap-1 rounded border border-target/25 bg-target/10 px-2 py-1 text-xs font-semibold text-ink transition hover:border-target" data-testid="unitary-phase-pi-half">
                <Target size={14} /> phase pi/2
              </button>
            </div>
          )}

          {activeLevel.id === 'fake-hermitian' && (
            <div className="space-y-2" data-testid="unitary-hermitian-matrix">
              <div className="grid gap-2 sm:grid-cols-2">
                <ComplexInput label="a11" value={hermitianMatrix.a} reTestId="unitary-matrix-a-re" imTestId="unitary-matrix-a-im" onChange={(value) => setHermitianCoord('a', value)} />
                <ComplexInput label="a12" value={hermitianMatrix.b} reTestId="unitary-matrix-b-re" imTestId="unitary-matrix-b-im" onChange={(value) => setHermitianCoord('b', value)} />
                <ComplexInput label="a21" value={hermitianMatrix.c} reTestId="unitary-matrix-c-re" imTestId="unitary-matrix-c-im" onChange={(value) => setHermitianCoord('c', value)} />
                <ComplexInput label="a22" value={hermitianMatrix.d} reTestId="unitary-matrix-d-re" imTestId="unitary-matrix-d-im" onChange={(value) => setHermitianCoord('d', value)} />
              </div>
              <button type="button" onClick={makeHermitian} className="inline-flex items-center gap-1 rounded border border-success/25 bg-success/10 px-2 py-1 text-xs font-semibold text-ink transition hover:border-success" data-testid="unitary-make-hermitian">
                <Sparkles size={14} /> make Hermitian
              </button>
            </div>
          )}

          {activeLevel.id === 'unitary-motion' && (
            <div className="space-y-2">
              <MatrixReadout matrix={unitaryMatrix} label="U" />
              <div className="grid gap-2 sm:grid-cols-2">
                <ComplexInput label="u11" value={unitaryMatrix.a} reTestId="unitary-u-a-re" imTestId="unitary-u-a-im" onChange={(value) => setUnitaryCoord('a', value)} />
                <ComplexInput label="u12" value={unitaryMatrix.b} reTestId="unitary-u-b-re" imTestId="unitary-u-b-im" onChange={(value) => setUnitaryCoord('b', value)} />
                <ComplexInput label="u21" value={unitaryMatrix.c} reTestId="unitary-u-c-re" imTestId="unitary-u-c-im" onChange={(value) => setUnitaryCoord('c', value)} />
                <ComplexInput label="u22" value={unitaryMatrix.d} reTestId="unitary-u-d-re" imTestId="unitary-u-d-im" onChange={(value) => setUnitaryCoord('d', value)} />
              </div>
              <button type="button" onClick={snapU} className="inline-flex items-center gap-1 rounded border border-target/25 bg-target/10 px-2 py-1 text-xs font-semibold text-ink transition hover:border-target" data-testid="unitary-snap-u">
                <Target size={14} /> snap U
              </button>
            </div>
          )}

          {activeLevel.id === 'a-star-a-bridge' && (
            <div className="grid gap-2">
              <ChoiceButton active={bridgeChoice === 'ata'} label="A^T A" testId="unitary-choice-ata" onClick={() => chooseBridge('ata')} />
              <ChoiceButton active={bridgeChoice === 'aat-star'} label="A A*" testId="unitary-choice-aa-star" onClick={() => chooseBridge('aat-star')} />
              <ChoiceButton active={bridgeChoice === 'astar-a'} label="A* A" testId="unitary-choice-astar-a" onClick={() => chooseBridge('astar-a')} />
            </div>
          )}

          <button type="button" onClick={() => resetToPreset()} className="inline-flex items-center gap-1 rounded border border-ink/10 bg-paper px-2 py-1 text-xs font-semibold text-ink transition hover:border-orange/40 hover:text-orange">
            <RotateCcw size={14} /> reset
          </button>
        </div>
      }
      feedback={
        <div className="space-y-1" data-testid="unitary-diagnosis">
          <p className="font-semibold text-ink">{diagnosis.message}</p>
          <p>{diagnosis.repairHint}</p>
        </div>
      }
    />
  )
}

function applyUnitaryPreview(matrix: ComplexMatrix2x2): ComplexVec2 {
  const input: ComplexVec2 = [complex(1, 0), complex(0, 0)]
  return [
    {
      re: matrix.a.re * input[0].re + matrix.b.re * input[1].re - matrix.a.im * input[0].im - matrix.b.im * input[1].im,
      im: matrix.a.re * input[0].im + matrix.a.im * input[0].re + matrix.b.re * input[1].im + matrix.b.im * input[1].re,
    },
    {
      re: matrix.c.re * input[0].re + matrix.d.re * input[1].re - matrix.c.im * input[0].im - matrix.d.im * input[1].im,
      im: matrix.c.re * input[0].im + matrix.c.im * input[0].re + matrix.d.re * input[1].im + matrix.d.im * input[1].re,
    },
  ]
}
