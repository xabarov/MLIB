import { useEffect, useMemo, useState } from 'react'
import { RotateCcw } from 'lucide-react'
import { MissionShell } from '../../game/components/MissionShell'
import { RepairMarker } from '../../game/components/RepairMarker'
import { ResultMoment } from '../../game/components/ResultMoment'
import { chooseMascotState, missionMessage } from '../../game/missionFeedback'
import { eulerTrailMission } from '../../game/missions'
import type { MissionBadge, MissionLevel } from '../../game/missionTypes'
import { useMissionRuntime } from '../../game/useMissionRuntime'
import {
  availableFrom,
  diagnoseEuler,
  edgeBetween,
  eulerLevels,
  eulerLevelSuccess,
  oddVertices,
  startVertices,
  type EulerLevelId,
} from './eulerTrailModel'

const levelIdMap: Record<string, EulerLevelId> = {
  bowtie: 'bowtie',
  house: 'house',
  envelope: 'envelope',
}

export function EulerTrailMission() {
  const definition = eulerTrailMission
  const runtime = useMissionRuntime(definition)
  const activeLevel = runtime.activeLevel
  return (
    <EulerTrailLevel
      key={activeLevel.id}
      activeLevel={activeLevel}
      completeActiveLevel={runtime.completeActiveLevel}
      setActiveLevelId={runtime.setActiveLevelId}
    />
  )
}

function EulerTrailLevel({
  activeLevel,
  completeActiveLevel,
  setActiveLevelId,
}: {
  activeLevel: MissionLevel
  completeActiveLevel: () => void
  setActiveLevelId: (levelId: string) => void
}) {
  const definition = eulerTrailMission
  const levelId = levelIdMap[activeLevel.id]
  const config = eulerLevels[levelId]
  const [used, setUsed] = useState<number[]>([])
  const [current, setCurrent] = useState<number | null>(null)
  const [lastInvalid, setLastInvalid] = useState(false)
  const [touched, setTouched] = useState(false)

  const odd = useMemo(() => oddVertices(config.n, config.edges), [config])
  const starts = useMemo(() => startVertices(config), [config])
  const diagnosis = diagnoseEuler({ config, used, current, touched, lastInvalid })
  const levelSuccess = eulerLevelSuccess(config.edges, used)

  const nextVertices = useMemo(() => {
    if (current === null) return new Set<number>()
    const set = new Set<number>()
    for (const index of availableFrom(config.edges, used, current)) {
      const [a, b] = config.edges[index]
      set.add(a === current ? b : a)
    }
    return set
  }, [config, used, current])

  useEffect(() => {
    if (levelSuccess && touched) completeActiveLevel()
  }, [completeActiveLevel, levelSuccess, touched])

  const showRepairMarker = touched && !levelSuccess && (diagnosis.kind === 'invalid' || diagnosis.kind === 'stuck')
  const repairLabel = diagnosis.kind === 'stuck' ? 'тупик' : 'нет ребра'

  const mascotState = chooseMascotState({
    success: levelSuccess && touched,
    warning: showRepairMarker,
    hint: current !== null && !levelSuccess,
    thinking: !touched,
  })
  const mascotMessage = missionMessage(mascotState, {
    success: activeLevel.successText,
    warning: activeLevel.mistakeFeedback?.[0] ?? diagnosis.message,
    hint: activeLevel.hint,
    thinking: 'Я стою на текущей вершине. Иди в соседнюю по непройденному ребру.',
    idle: 'Кликни вершину для старта, затем соседние, проходя все рёбра по разу.',
  })

  const badges: MissionBadge[] = [
    {
      id: 'edges',
      label: 'edges',
      value: `${used.length}/${config.edges.length}`,
      tone: levelSuccess ? 'success' : 'energy',
    },
    {
      id: 'odd',
      label: 'odd',
      value: odd.length,
      tone: config.kind === 'circuit' ? 'success' : 'target',
    },
  ]

  const clickVertex = (v: number) => {
    setTouched(true)
    if (current === null) {
      setCurrent(v)
      setLastInvalid(false)
      return
    }
    const index = edgeBetween(config.edges, used, current, v)
    if (index < 0) {
      setLastInvalid(true)
      return
    }
    setUsed((list) => [...list, index])
    setCurrent(v)
    setLastInvalid(false)
  }

  const resetLevel = () => {
    setUsed([])
    setCurrent(null)
    setLastInvalid(false)
    setTouched(false)
  }

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
          <ResultMoment show={levelSuccess && touched} label="нарисовано не отрывая руки" />
          {showRepairMarker && (
            <RepairMarker tone="warning" label={repairLabel} xPercent={50} yPercent={3} />
          )}
          <svg
            viewBox="0 0 100 100"
            className="aspect-square max-h-full w-full max-w-[540px] rounded-md border border-ink/10 bg-paper shadow-[0_18px_42px_rgba(20,20,19,0.12)]"
            data-testid="euler-trail-canvas"
            aria-label="Эйлеров путь по графу"
          >
            {config.edges.map(([a, b], index) => {
              const pa = config.positions[a]
              const pb = config.positions[b]
              const isUsed = used.includes(index)
              return (
                <line
                  key={`edge-${index}`}
                  x1={pa[0]}
                  y1={pa[1]}
                  x2={pb[0]}
                  y2={pb[1]}
                  className={isUsed ? 'stroke-success' : 'stroke-ink/25'}
                  strokeWidth={isUsed ? 1.4 : 0.7}
                  strokeLinecap="round"
                />
              )
            })}
            {config.positions.map((pos, v) => {
              const isCurrent = current === v
              const isStart = current === null && starts.includes(v)
              const isNext = nextVertices.has(v)
              const fill = isCurrent
                ? '#cf6d50'
                : isStart
                  ? '#f3efe2'
                  : isNext
                    ? '#eef4ee'
                    : '#fffdf7'
              const stroke = isCurrent ? '#141413' : isStart ? '#cf6d50' : isNext ? '#5f8d63' : '#9b988f'
              return (
                <g
                  key={`v-${v}`}
                  className="cursor-pointer"
                  onClick={() => clickVertex(v)}
                  data-testid={`euler-vertex-${v}`}
                >
                  <circle cx={pos[0]} cy={pos[1]} r={5.2} fill={fill} stroke={stroke} strokeWidth={isCurrent || isStart ? 0.8 : 0.5} />
                  <text x={pos[0]} y={pos[1]} textAnchor="middle" dominantBaseline="central" fontSize="3.8" className={isCurrent ? 'fill-paper font-semibold' : 'fill-ink font-semibold'}>
                    {v + 1}
                  </text>
                </g>
              )
            })}
          </svg>
        </div>
      }
      controls={
        <div className="space-y-3">
          <div
            className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5 text-xs leading-relaxed text-ink/70"
            data-testid="euler-diagnosis"
          >
            <p className="font-semibold text-ink">{diagnosis.message}</p>
            <p className="mt-1">{diagnosis.repairHint}</p>
          </div>
          <p className="text-xs leading-relaxed text-ink/60">
            Эйлеров путь проходит каждое ребро ровно один раз. Он существует, если
            вершин нечётной степени ноль (цикл) или ровно две (путь между ними).
          </p>
          <button
            type="button"
            onClick={resetLevel}
            className="inline-flex items-center gap-1 rounded border border-ink/10 bg-paper px-2 py-1 text-xs font-semibold text-ink/75 hover:border-orange/40 hover:text-ink"
            data-testid="euler-reset"
          >
            <RotateCcw size={14} /> Сбросить уровень
          </button>
        </div>
      }
      feedback={
        <p>
          Пройдено рёбер: <span className="font-semibold">{used.length}/{config.edges.length}</span>,
          нечётных вершин: <span className="font-semibold">{odd.length}</span>. Диагноз:{' '}
          <span className="font-semibold">{diagnosis.kind}</span>.
        </p>
      }
    />
  )
}
