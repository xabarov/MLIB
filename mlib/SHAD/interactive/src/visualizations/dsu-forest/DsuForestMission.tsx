import { useEffect, useMemo, useState } from 'react'
import { RotateCcw } from 'lucide-react'
import { MissionShell } from '../../game/components/MissionShell'
import { RepairMarker } from '../../game/components/RepairMarker'
import { ResultMoment } from '../../game/components/ResultMoment'
import { chooseMascotState, missionMessage } from '../../game/missionFeedback'
import { dsuForestMission } from '../../game/missions'
import type { MissionBadge, MissionLevel } from '../../game/missionTypes'
import { useMissionRuntime } from '../../game/useMissionRuntime'
import {
  componentCount,
  diagnoseDsu,
  dsuLevels,
  dsuLevelSuccess,
  find,
  makeParent,
  sameComponent,
  union,
  type DsuLevelId,
  type EdgeStatus,
} from './dsuForestModel'

const levelIdMap: Record<string, DsuLevelId> = {
  'connect-all': 'connect-all',
  'spanning-tree': 'spanning-tree',
  'two-groups': 'two-groups',
}

const COMPONENT_COLORS = ['#5f8d63', '#6a9bcc', '#cf6d50', '#7c6ccf', '#c8a23a', '#3a9b8f']

export function DsuForestMission() {
  const definition = dsuForestMission
  const runtime = useMissionRuntime(definition)
  const activeLevel = runtime.activeLevel
  return (
    <DsuForestLevel
      key={activeLevel.id}
      activeLevel={activeLevel}
      completeActiveLevel={runtime.completeActiveLevel}
      setActiveLevelId={runtime.setActiveLevelId}
    />
  )
}

function DsuForestLevel({
  activeLevel,
  completeActiveLevel,
  setActiveLevelId,
}: {
  activeLevel: MissionLevel
  completeActiveLevel: () => void
  setActiveLevelId: (levelId: string) => void
}) {
  const definition = dsuForestMission
  const levelId = levelIdMap[activeLevel.id]
  const config = dsuLevels[levelId]
  const [parent, setParent] = useState<number[]>(makeParent(config.n))
  const [edgeStatus, setEdgeStatus] = useState<EdgeStatus[]>(config.edges.map(() => null))
  const [lastCycle, setLastCycle] = useState(false)
  const [touched, setTouched] = useState(false)

  const count = componentCount(parent)
  const diagnosis = diagnoseDsu({ levelId, parent, touched })
  const levelSuccess = dsuLevelSuccess(levelId, parent)
  const cycleCount = edgeStatus.filter((status) => status === 'cycle').length

  useEffect(() => {
    if (levelSuccess && touched) completeActiveLevel()
  }, [completeActiveLevel, levelSuccess, touched])

  const showRepairMarker =
    touched && !levelSuccess && (diagnosis.kind === 'over-merged' || lastCycle)
  const repairLabel = diagnosis.kind === 'over-merged' ? 'лишний мост' : 'цикл'

  const mascotState = chooseMascotState({
    success: levelSuccess && touched,
    warning: showRepairMarker,
    hint: touched && diagnosis.kind === 'in-progress',
    thinking: !touched,
  })
  const mascotMessage = missionMessage(mascotState, {
    success: activeLevel.successText,
    warning: activeLevel.mistakeFeedback?.[0] ?? diagnosis.message,
    hint: activeLevel.hint,
    thinking: 'Я держу инвариант компонент. Объединяй разные множества, цикл подсвечу красным.',
    idle: 'Кликай рёбра, чтобы объединять множества. Ребро внутри одной компоненты — цикл.',
  })

  const badges: MissionBadge[] = [
    {
      id: 'components',
      label: 'comp',
      value: `${count}/${config.target}`,
      tone: levelSuccess ? 'success' : count < config.target ? 'danger' : 'energy',
    },
    {
      id: 'cycles',
      label: 'cycles',
      value: cycleCount,
      tone: cycleCount > 0 ? 'warning' : 'neutral',
    },
  ]

  const clickEdge = (index: number) => {
    const [a, b] = config.edges[index]
    setTouched(true)
    if (sameComponent(parent, a, b)) {
      setLastCycle(true)
      setEdgeStatus((current) => {
        const next = current.slice()
        next[index] = 'cycle'
        return next
      })
      return
    }
    setLastCycle(false)
    setParent((current) => union(current, a, b).parent)
    setEdgeStatus((current) => {
      const next = current.slice()
      next[index] = 'tree'
      return next
    })
  }

  const resetLevel = () => {
    setParent(makeParent(config.n))
    setEdgeStatus(config.edges.map(() => null))
    setLastCycle(false)
    setTouched(false)
  }

  const nodeColor = useMemo(
    () => (node: number) => COMPONENT_COLORS[find(parent, node) % COMPONENT_COLORS.length],
    [parent],
  )

  return (
    <MissionShell
      definition={definition}
      activeLevelId={activeLevel.id}
      onLevelSelect={setActiveLevelId}
      mascotState={mascotState}
      mascotMessage={mascotMessage}
      badges={badges}
      sceneViewportClassName="h-[460px] pt-[104px] sm:pt-[78px] lg:h-full"
      scene={
        <div className="relative flex h-full items-center justify-center bg-[radial-gradient(circle_at_24%_18%,rgba(95,141,99,0.14),transparent_30%),linear-gradient(180deg,#fffdf7,#f5f3ec)] p-4">
          <ResultMoment show={levelSuccess && touched} label={config.target === 1 ? 'всё связано' : 'две группы'} />
          {showRepairMarker && (
            <RepairMarker tone="warning" label={repairLabel} xPercent={50} yPercent={3} />
          )}
          <svg
            viewBox="-6 -6 112 112"
            className="aspect-square max-h-full w-full max-w-[560px] rounded-md border border-ink/10 bg-paper shadow-[0_18px_42px_rgba(20,20,19,0.12)]"
            data-testid="dsu-forest-canvas"
            aria-label="Лес непересекающихся множеств"
          >
            {config.edges.map(([a, b], index) => {
              const pa = config.positions[a]
              const pb = config.positions[b]
              const status = edgeStatus[index]
              const stroke =
                status === 'tree' ? 'stroke-success' : status === 'cycle' ? 'stroke-danger' : 'stroke-ink/25'
              const width = status === 'tree' ? 1.2 : status === 'cycle' ? 1.0 : 0.6
              return (
                <g key={index} className="cursor-pointer" onClick={() => clickEdge(index)} data-testid={`dsu-edge-${index}`}>
                  <line x1={pa[0]} y1={pa[1]} x2={pb[0]} y2={pb[1]} stroke="transparent" strokeWidth={5} />
                  <line
                    x1={pa[0]}
                    y1={pa[1]}
                    x2={pb[0]}
                    y2={pb[1]}
                    className={stroke}
                    strokeWidth={width}
                    strokeDasharray={status === 'cycle' ? '2 1.5' : undefined}
                  />
                </g>
              )
            })}
            {config.positions.map((pos, node) => (
              <g key={node}>
                <circle cx={pos[0]} cy={pos[1]} r={5} fill={nodeColor(node)} stroke="#141413" strokeWidth={0.4} />
                <text x={pos[0]} y={pos[1]} textAnchor="middle" dominantBaseline="central" fontSize="4" className="fill-paper font-semibold">
                  {node + 1}
                </text>
              </g>
            ))}
          </svg>
        </div>
      }
      controls={
        <div className="space-y-3">
          <div
            className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5 text-xs leading-relaxed text-ink/70"
            data-testid="dsu-diagnosis"
          >
            <p className="font-semibold text-ink">{diagnosis.message}</p>
            <p className="mt-1">{diagnosis.repairHint}</p>
          </div>
          <p className="text-xs leading-relaxed text-ink/60">
            Каждая вершина начинает в своём множестве. Ребро между разными
            множествами объединяет их; ребро внутри одного - цикл (красный).
          </p>
          <button
            type="button"
            onClick={resetLevel}
            className="inline-flex items-center gap-1 rounded border border-ink/10 bg-paper px-2 py-1 text-xs font-semibold text-ink/75 hover:border-orange/40 hover:text-ink"
            data-testid="dsu-reset"
          >
            <RotateCcw size={14} /> Сбросить уровень
          </button>
        </div>
      }
      feedback={
        <p>
          Компонент: <span className="font-semibold">{count}</span> (цель {config.target}), циклов:{' '}
          <span className="font-semibold">{cycleCount}</span>. Диагноз:{' '}
          <span className="font-semibold">{diagnosis.kind}</span>.
        </p>
      }
    />
  )
}
