import { useEffect, useMemo, useState } from 'react'
import { MissionShell } from '../../game/components/MissionShell'
import { chooseMascotState, missionMessage } from '../../game/missionFeedback'
import { kernelHuntMission } from '../../game/missions'
import type { MissionBadge } from '../../game/missionTypes'
import { useMissionRuntime } from '../../game/useMissionRuntime'
import { KernelLineViz } from './KernelLineViz'
import {
  diagnoseKernelState,
  errorToKernel,
  formatKernelNumber,
  kernelLevelSuccess,
  projectionToKernel,
  residual,
  type Vec3,
} from './kernelHuntModel'

function SliderControl({
  label,
  value,
  onChange,
}: {
  label: string
  value: number
  onChange: (value: number) => void
}) {
  return (
    <label className="grid grid-cols-[24px_1fr_52px] items-center gap-2 text-sm text-ink">
      <span className="font-semibold">{label}</span>
      <input
        type="range"
        min={-3}
        max={3}
        step={0.25}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
        className="accent-orange"
        data-testid={`kernel-range-${label}`}
      />
      <input
        type="number"
        min={-3}
        max={3}
        step={0.25}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
        className="w-full rounded border border-ink/10 bg-paper px-2 py-1 text-right tabular-nums"
        data-testid={`kernel-input-${label}`}
      />
    </label>
  )
}

export function KernelHuntMission() {
  const definition = kernelHuntMission
  const [candidate, setCandidate] = useState<Vec3>([1, 0, 0])
  const [touched, setTouched] = useState(false)
  const runtime = useMissionRuntime(definition)
  const activeLevel = runtime.activeLevel
  const ax = residual(candidate)
  const error = errorToKernel(candidate)
  const projection = projectionToKernel(candidate)
  const { completeActiveLevel, completedLevelIds, setActiveLevelId } = runtime
  const diagnosis = diagnoseKernelState({
    levelId: activeLevel.id,
    candidate,
    completedLevelIds,
    touched,
  })

  const levelSuccess = useMemo(() => {
    return kernelLevelSuccess({
      levelId: activeLevel.id,
      candidate,
      completedLevelIds,
    })
  }, [activeLevel.id, candidate, completedLevelIds])

  useEffect(() => {
    if (!levelSuccess) return
    completeActiveLevel()
  }, [completeActiveLevel, levelSuccess])

  const mascotState = chooseMascotState({
    success: levelSuccess,
    warning:
      touched &&
      [
        'zero-vector',
        'first-equation-error',
        'second-equation-error',
        'both-equations-error',
        'rank-nullity-not-ready',
      ].includes(diagnosis.kind),
    hint: error < 0.7,
  })
  const mascotMessage = missionMessage(mascotState, {
    success: activeLevel.successText,
    warning: activeLevel.mistakeFeedback?.[0] ?? diagnosis.message,
    hint: activeLevel.hint,
    thinking: 'Сравни две ошибки: x + y и x - z. Обе должны стать нулем.',
    idle: 'Двигай координаты. Я буду следить, насколько близко Ax к нулю.',
  })

  const badges: MissionBadge[] = [
    {
      id: 'residual',
      label: '||Ax||',
      value: formatKernelNumber(error),
      tone: levelSuccess ? 'success' : error < 0.7 ? 'warning' : 'energy',
    },
    {
      id: 'ax',
      label: 'Ax',
      value: `(${formatKernelNumber(ax[0])}, ${formatKernelNumber(ax[1])})`,
      tone: 'neutral',
    },
    {
      id: 'rank',
      label: 'rank + dim ker',
      value: '2 + 1 = 3',
      tone: activeLevel.id === 'rank-nullity' && levelSuccess ? 'success' : 'target',
    },
  ]

  const setCoord = (index: number, value: number) => {
    setTouched(true)
    setCandidate((current) => {
      const next = [...current] as Vec3
      next[index] = Number.isFinite(value) ? value : 0
      return next
    })
  }

  return (
    <MissionShell
      definition={definition}
      activeLevelId={activeLevel.id}
      onLevelSelect={setActiveLevelId}
      mascotState={mascotState}
      mascotMessage={mascotMessage}
      badges={badges}
      sceneViewportClassName="h-[300px] pt-[88px] sm:h-[480px] sm:pt-[74px] lg:h-full"
      scene={
        <KernelLineViz
          candidate={candidate}
          projection={projection}
          onCandidateChange={(next) => {
            setTouched(true)
            setCandidate(next)
          }}
        />
      }
      controls={
        <div className="space-y-3">
          <SliderControl label="x" value={candidate[0]} onChange={(value) => setCoord(0, value)} />
          <SliderControl label="y" value={candidate[1]} onChange={(value) => setCoord(1, value)} />
          <SliderControl label="z" value={candidate[2]} onChange={(value) => setCoord(2, value)} />
          <div
            className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5 text-xs leading-relaxed text-ink/70"
            data-testid="kernel-diagnosis"
          >
            <p className="font-semibold text-ink">{diagnosis.message}</p>
            <p className="mt-1">{diagnosis.repairHint}</p>
            <div className="mt-2 grid gap-1 sm:grid-cols-2">
              <p>
                x + y ={' '}
                <span className="font-semibold">{formatKernelNumber(diagnosis.residual[0])}</span>
              </p>
              <p>
                x - z ={' '}
                <span className="font-semibold">{formatKernelNumber(diagnosis.residual[1])}</span>
              </p>
            </div>
          </div>
        </div>
      }
      feedback={
        <div className="space-y-1">
          <p>
            Условия: <span className="font-semibold">x + y = 0</span> и{' '}
            <span className="font-semibold">x - z = 0</span>.
          </p>
          <p className="text-xs text-ink/60">
            Текущий вектор: ({candidate.map(formatKernelNumber).join(', ')})
          </p>
          <p className="text-xs text-ink/60">
            Параметризация: x = {formatKernelNumber(diagnosis.parameter)}(-1, 1, -1). Диагноз:{' '}
            <span className="font-semibold">{diagnosis.kind}</span>.
          </p>
          {activeLevel.id === 'rank-nullity' && (
            <p className="text-xs font-semibold text-success">
              rank A = 2, dim ker A = 1, поэтому 3 = 2 + 1.
            </p>
          )}
          <p className="text-xs text-ink/60">
            Оранжевую ручку можно тянуть прямо в 3D-сцене по текущей плоскости z.
          </p>
        </div>
      }
    />
  )
}
