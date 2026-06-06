import { useEffect, useMemo, useState } from 'react'
import { MissionShell } from '../../game/components/MissionShell'
import { kernelHuntMission } from '../../game/missions'
import type { MascotState, MissionBadge } from '../../game/missionTypes'
import { useProgressStore } from '../../store/progressStore'
import { KernelLineViz } from './KernelLineViz'

type Vec3 = [number, number, number]

const direction: Vec3 = [-1, 1, -1]
const directionNormSq = 3
const epsilon = 0.08
const emptyLevels: string[] = []

function residual(candidate: Vec3): [number, number] {
  const [x, y, z] = candidate
  return [x + y, x - z]
}

function norm2(values: readonly number[]): number {
  return Math.sqrt(values.reduce((sum, value) => sum + value * value, 0))
}

function projectionToKernel(candidate: Vec3): Vec3 {
  const dot =
    candidate[0] * direction[0] + candidate[1] * direction[1] + candidate[2] * direction[2]
  const t = dot / directionNormSq
  return [direction[0] * t, direction[1] * t, direction[2] * t]
}

function formatNumber(value: number): string {
  return Math.abs(value) < 0.005 ? '0.00' : value.toFixed(2)
}

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
      />
      <input
        type="number"
        min={-3}
        max={3}
        step={0.25}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
        className="w-full rounded border border-ink/10 bg-paper px-2 py-1 text-right tabular-nums"
      />
    </label>
  )
}

export function KernelHuntMission() {
  const definition = kernelHuntMission
  const [activeLevelId, setActiveLevelId] = useState(definition.levels[0].id)
  const [candidate, setCandidate] = useState<Vec3>([1, 0, 0])

  const completeLevel = useProgressStore((s) => s.completeLevel)
  const unlockLevel = useProgressStore((s) => s.unlockLevel)
  const completedLevels = useProgressStore((s) => s.completedLevels[definition.id] ?? emptyLevels)

  useEffect(() => {
    unlockLevel(definition.id, definition.levels[0].id)
  }, [definition.id, definition.levels, unlockLevel])

  const activeLevelIndex = definition.levels.findIndex((level) => level.id === activeLevelId)
  const activeLevel = definition.levels[Math.max(activeLevelIndex, 0)]
  const ax = residual(candidate)
  const error = norm2(ax)
  const candidateNorm = norm2(candidate)
  const onKernel = error < epsilon && candidateNorm > epsilon
  const projection = projectionToKernel(candidate)
  const t = projection[0] / direction[0]
  const basisAligned =
    onKernel &&
    Math.abs(Math.abs(candidate[0]) - 1) < 0.12 &&
    Math.abs(Math.abs(candidate[1]) - 1) < 0.12 &&
    Math.abs(Math.abs(candidate[2]) - 1) < 0.12
  const rankNullityReady =
    completedLevels.includes('nonzero-zero') &&
    completedLevels.includes('solution-line') &&
    completedLevels.includes('kernel-basis') &&
    onKernel

  const levelSuccess = useMemo(() => {
    if (activeLevel.id === 'nonzero-zero') return onKernel
    if (activeLevel.id === 'solution-line') {
      return onKernel && Math.abs(t) > 1.4
    }
    if (activeLevel.id === 'kernel-basis') return basisAligned
    if (activeLevel.id === 'rank-nullity') return rankNullityReady
    return false
  }, [activeLevel.id, basisAligned, onKernel, rankNullityReady, t])

  useEffect(() => {
    if (!levelSuccess) return
    const nextLevel = definition.levels[activeLevelIndex + 1]
    completeLevel(definition.id, activeLevel.id, nextLevel?.id)
  }, [activeLevel.id, activeLevelIndex, completeLevel, definition.id, definition.levels, levelSuccess])

  const mascotState: MascotState = levelSuccess
    ? 'success'
    : candidateNorm <= epsilon
      ? 'warning'
      : error < 0.7
        ? 'hint'
        : 'idle'

  const mascotMessage =
    mascotState === 'success'
      ? activeLevel.successText
      : mascotState === 'warning'
        ? 'Нулевой вектор тоже уходит в ноль, но нам нужен ненулевой носитель направления.'
        : mascotState === 'hint'
          ? activeLevel.hint
          : 'Двигай координаты. Я буду следить, насколько близко Ax к нулю.'

  const badges: MissionBadge[] = [
    {
      id: 'residual',
      label: '||Ax||',
      value: formatNumber(error),
      tone: levelSuccess ? 'success' : error < 0.7 ? 'warning' : 'energy',
    },
    {
      id: 'ax',
      label: 'Ax',
      value: `(${formatNumber(ax[0])}, ${formatNumber(ax[1])})`,
      tone: 'neutral',
    },
    {
      id: 'rank',
      label: 'rank + dim ker',
      value: '2 + 1 = 3',
      tone: rankNullityReady ? 'success' : 'target',
    },
  ]

  const setCoord = (index: number, value: number) => {
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
      scene={<KernelLineViz candidate={candidate} projection={projection} />}
      controls={
        <div className="space-y-3">
          <SliderControl label="x" value={candidate[0]} onChange={(value) => setCoord(0, value)} />
          <SliderControl label="y" value={candidate[1]} onChange={(value) => setCoord(1, value)} />
          <SliderControl label="z" value={candidate[2]} onChange={(value) => setCoord(2, value)} />
        </div>
      }
      feedback={
        <div className="space-y-1">
          <p>
            Условия: <span className="font-semibold">x + y = 0</span> и{' '}
            <span className="font-semibold">x - z = 0</span>.
          </p>
          <p className="text-xs text-ink/60">
            Текущий вектор: ({candidate.map(formatNumber).join(', ')})
          </p>
        </div>
      }
    />
  )
}
