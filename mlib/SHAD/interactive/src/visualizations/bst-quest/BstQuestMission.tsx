import { useEffect, useMemo, useState } from 'react'
import { RotateCcw } from 'lucide-react'
import { MissionShell } from '../../game/components/MissionShell'
import { RepairMarker } from '../../game/components/RepairMarker'
import { ResultMoment } from '../../game/components/ResultMoment'
import { chooseMascotState, missionMessage } from '../../game/missionFeedback'
import { bstQuestMission } from '../../game/missions'
import type { MissionBadge, MissionLevel } from '../../game/missionTypes'
import { useMissionRuntime } from '../../game/useMissionRuntime'
import {
  bstLevels,
  bstLevelSuccess,
  bstSearch,
  childrenOf,
  correctChild,
  diagnoseBst,
  type BstLevelId,
} from './bstQuestModel'

const levelIdMap: Record<string, BstLevelId> = {
  'find-leaf': 'find-leaf',
  'find-deep': 'find-deep',
  'not-found': 'not-found',
}

export function BstQuestMission() {
  const definition = bstQuestMission
  const runtime = useMissionRuntime(definition)
  const activeLevel = runtime.activeLevel
  return (
    <BstQuestLevel
      key={activeLevel.id}
      activeLevel={activeLevel}
      completeActiveLevel={runtime.completeActiveLevel}
      setActiveLevelId={runtime.setActiveLevelId}
    />
  )
}

function BstQuestLevel({
  activeLevel,
  completeActiveLevel,
  setActiveLevelId,
}: {
  activeLevel: MissionLevel
  completeActiveLevel: () => void
  setActiveLevelId: (levelId: string) => void
}) {
  const definition = bstQuestMission
  const levelId = levelIdMap[activeLevel.id]
  const config = bstLevels[levelId]
  const { tree, positions, target } = config

  const [current, setCurrent] = useState(0)
  const [visited, setVisited] = useState<number[]>([0])
  const [lastWrong, setLastWrong] = useState(false)
  const [touched, setTouched] = useState(false)

  const outcome = useMemo(() => bstSearch(tree, target), [tree, target])
  const diagnosis = diagnoseBst({ levelId, current, touched, lastWrong })
  const levelSuccess = bstLevelSuccess(levelId, current)
  const childSet = useMemo(() => new Set(childrenOf(tree, current)), [tree, current])

  useEffect(() => {
    if (levelSuccess && touched) completeActiveLevel()
  }, [completeActiveLevel, levelSuccess, touched])

  const showRepairMarker = touched && !levelSuccess && diagnosis.kind === 'wrong-branch'

  const mascotState = chooseMascotState({
    success: levelSuccess && touched,
    warning: showRepairMarker,
    hint: !levelSuccess && touched,
    thinking: !touched,
  })
  const mascotMessage = missionMessage(mascotState, {
    success: activeLevel.successText,
    warning: activeLevel.mistakeFeedback?.[0] ?? diagnosis.message,
    hint: activeLevel.hint,
    thinking: 'Я на текущем узле. Сравни цель с числом и иди в нужную сторону.',
    idle: 'Спускайся по дереву: меньше - влево, больше - вправо.',
  })

  const badges: MissionBadge[] = [
    {
      id: 'target',
      label: 'target',
      value: target,
      tone: 'target',
    },
    {
      id: 'node',
      label: 'node',
      value: tree[current].value,
      tone: levelSuccess ? 'success' : 'energy',
    },
    {
      id: 'steps',
      label: 'steps',
      value: visited.length - 1,
      tone: 'neutral',
    },
  ]

  const clickNode = (v: number) => {
    if (!childSet.has(v)) return
    setTouched(true)
    if (correctChild(tree, current, target) === v) {
      setLastWrong(false)
      setCurrent(v)
      setVisited((list) => [...list, v])
      return
    }
    setLastWrong(true)
  }

  const resetLevel = () => {
    setCurrent(0)
    setVisited([0])
    setLastWrong(false)
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
        <div className="relative flex h-full items-center justify-center bg-[radial-gradient(circle_at_24%_18%,rgba(77,134,168,0.14),transparent_30%),linear-gradient(180deg,#fffdf7,#f5f3ec)] p-4">
          <ResultMoment
            show={levelSuccess && touched}
            label={outcome.found ? `${target} найден` : `${target} нет в дереве`}
          />
          {showRepairMarker && (
            <RepairMarker tone="warning" label="не та ветка" xPercent={50} yPercent={3} />
          )}
          <svg
            viewBox="0 0 100 92"
            className="w-full max-w-[600px] rounded-md border border-ink/10 bg-paper shadow-[0_18px_42px_rgba(20,20,19,0.12)]"
            data-testid="bst-quest-canvas"
            aria-label="Двоичное дерево поиска"
          >
            {tree.map((node, index) =>
              [node.left, node.right].map((child) => {
                if (child === null) return null
                const pa = positions[index]
                const pb = positions[child]
                const onPath = visited.includes(index) && visited.includes(child)
                return (
                  <line
                    key={`edge-${index}-${child}`}
                    x1={pa[0]}
                    y1={pa[1]}
                    x2={pb[0]}
                    y2={pb[1]}
                    className={onPath ? 'stroke-success' : 'stroke-ink/25'}
                    strokeWidth={onPath ? 1.1 : 0.6}
                  />
                )
              }),
            )}
            {positions.map((pos, index) => {
              const isCurrent = current === index
              const isVisited = visited.includes(index) && !isCurrent
              const isOption = childSet.has(index)
              const fill = isCurrent ? '#cf6d50' : isVisited ? '#dceadd' : isOption ? '#eef4ee' : '#fffdf7'
              const stroke = isCurrent ? '#141413' : isOption ? '#5f8d63' : '#9b988f'
              return (
                <g
                  key={`node-${index}`}
                  className={isOption ? 'cursor-pointer' : ''}
                  onClick={() => clickNode(index)}
                  data-testid={`bst-node-${index}`}
                >
                  <circle cx={pos[0]} cy={pos[1]} r={6} fill={fill} stroke={stroke} strokeWidth={isCurrent || isOption ? 0.8 : 0.5} />
                  <text x={pos[0]} y={pos[1]} textAnchor="middle" dominantBaseline="central" fontSize="4.4" className={isCurrent ? 'fill-paper font-semibold' : 'fill-ink font-semibold'}>
                    {tree[index].value}
                  </text>
                </g>
              )
            })}
          </svg>
        </div>
      }
      controls={
        <div className="space-y-3">
          <div className="rounded border border-target/20 bg-target/10 px-2 py-1.5 text-xs font-semibold text-ink" data-testid="bst-target">
            Ищем число {target}. Текущий узел: {tree[current].value}.
          </div>
          <div
            className="rounded border border-ink/10 bg-paper/80 px-2 py-1.5 text-xs leading-relaxed text-ink/70"
            data-testid="bst-diagnosis"
          >
            <p className="font-semibold text-ink">{diagnosis.message}</p>
            <p className="mt-1">{diagnosis.repairHint}</p>
          </div>
          <p className="text-xs leading-relaxed text-ink/60">
            В дереве поиска левое поддерево меньше узла, правое - больше. Поиск
            идёт по сравнениям, за высоту дерева.
          </p>
          <button
            type="button"
            onClick={resetLevel}
            className="inline-flex items-center gap-1 rounded border border-ink/10 bg-paper px-2 py-1 text-xs font-semibold text-ink/75 hover:border-orange/40 hover:text-ink"
            data-testid="bst-reset"
          >
            <RotateCcw size={14} /> Сбросить уровень
          </button>
        </div>
      }
      feedback={
        <p>
          Цель {target}, текущий узел {tree[current].value}, шагов {visited.length - 1}. Диагноз:{' '}
          <span className="font-semibold">{diagnosis.kind}</span>.
        </p>
      }
    />
  )
}
