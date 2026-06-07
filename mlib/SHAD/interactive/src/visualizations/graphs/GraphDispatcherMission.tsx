import { useEffect, useMemo, useState } from 'react'
import { TracePanel } from '../../game/components/trace/TracePanel'
import { MascotOverlay } from '../../game/components/MascotOverlay'
import { MissionShell } from '../../game/components/MissionShell'
import { chooseMascotState, missionMessage } from '../../game/missionFeedback'
import { graphDispatcherMission } from '../../game/missions'
import type { MissionBadge, MissionLevel } from '../../game/missionTypes'
import { useMissionRuntime } from '../../game/useMissionRuntime'
import {
  graphTraceInvariantLabel,
  graphTraceLevelSuccess,
  graphTraceLevels,
  initialTraceState,
  nextRequiredVertex,
  stepGraphTrace,
  type GraphTraceState,
} from './graphTraceModel'

export function GraphDispatcherMission() {
  const definition = graphDispatcherMission
  const runtime = useMissionRuntime(definition)
  const activeLevel = runtime.activeLevel
  return (
    <GraphDispatcherLevel
      key={activeLevel.id}
      activeLevel={activeLevel}
      completeActiveLevel={runtime.completeActiveLevel}
      setActiveLevelId={runtime.setActiveLevelId}
    />
  )
}

function GraphDispatcherLevel({
  activeLevel,
  completeActiveLevel,
  setActiveLevelId,
}: {
  activeLevel: MissionLevel
  completeActiveLevel: () => void
  setActiveLevelId: (levelId: string) => void
}) {
  const definition = graphDispatcherMission
  const levelSpec = graphTraceLevels[activeLevel.id]
  const [state, setState] = useState<GraphTraceState>(() => initialTraceState(levelSpec))
  const required = nextRequiredVertex(state)
  const levelSuccess = useMemo(
    () => graphTraceLevelSuccess(levelSpec, state),
    [levelSpec, state],
  )

  useEffect(() => {
    if (!levelSuccess) return
    completeActiveLevel()
  }, [completeActiveLevel, levelSuccess])

  const mascotState = chooseMascotState({
    success: levelSuccess,
    warning: state.mistakes > 0,
    hint: state.frontier.length <= 2,
    thinking: state.steps.length > 0,
  })
  const mascotMessage = missionMessage(mascotState, {
    success: activeLevel.successText,
    warning:
      activeLevel.mistakeFeedback?.[0] ??
      'Инвариант очереди или стека нарушен. Сбрось уровень и возьми верхний элемент границы.',
    hint: activeLevel.hint,
    thinking: `Следующий ход: ${required ?? 'граница пуста'}.`,
    idle: 'Кликай вершину, которая стоит первой в очереди или на вершине стека.',
  })

  const badges: MissionBadge[] = [
    {
      id: 'frontier',
      label: levelSpec.mode === 'bfs' ? 'queue' : 'stack',
      value: state.frontier.join(' ') || 'empty',
      tone: levelSuccess ? 'success' : 'target',
    },
    {
      id: 'visited',
      label: 'visited',
      value: `${state.visited.length}/${levelSpec.targetVisited.length}`,
      tone: levelSuccess ? 'success' : 'neutral',
    },
    {
      id: 'cost',
      label: 'edges',
      value: state.checkedEdges,
      tone: state.mistakes > 0 ? 'danger' : 'energy',
    },
  ]

  const handleVertex = (vertexId: string) => {
    if (levelSuccess) return
    setState((current) => stepGraphTrace(levelSpec, current, vertexId))
  }

  const resetLevel = () => {
    setState(initialTraceState(levelSpec))
  }

  const visitedSet = new Set(state.visited)
  const frontierSet = new Set(state.frontier)
  const treeEdgeKeys = new Set(state.treeEdges.map(([a, b]) => `${a}-${b}`))
  const requiredVertexPosition = levelSpec.graph.vertices.find((vertex) => vertex.id === required)

  return (
    <MissionShell
      definition={definition}
      activeLevelId={activeLevel.id}
      onLevelSelect={setActiveLevelId}
      mascotState={mascotState}
      mascotMessage={mascotMessage}
      badges={badges}
      scene={
        <div className="flex h-full items-center justify-center bg-[radial-gradient(circle_at_70%_18%,rgba(77,134,168,0.13),transparent_30%),linear-gradient(180deg,#fffdf7,#faf9f5)] p-4">
          <div className="relative h-full max-h-[520px] w-full max-w-4xl">
            {requiredVertexPosition && (
              <MascotOverlay
                role="frontier"
                state={mascotState}
                label={requiredVertexPosition.label}
                xPercent={requiredVertexPosition.x}
                yPercent={requiredVertexPosition.y}
              />
            )}
          <svg
            viewBox="0 0 100 100"
            className="h-full w-full rounded-md border border-ink/10 bg-paper shadow-[0_18px_44px_rgba(20,20,19,0.08)]"
            role="img"
            aria-label="Граф для обхода"
            data-testid="graph-dispatcher-plane"
          >
            {levelSpec.graph.edges.map(([a, b]) => {
              const from = levelSpec.graph.vertices.find((vertex) => vertex.id === a)
              const to = levelSpec.graph.vertices.find((vertex) => vertex.id === b)
              if (!from || !to) return null
              const tree = treeEdgeKeys.has(`${a}-${b}`) || treeEdgeKeys.has(`${b}-${a}`)
              return (
                <line
                  key={`${a}-${b}`}
                  x1={from.x}
                  y1={from.y}
                  x2={to.x}
                  y2={to.y}
                  className={tree ? 'stroke-success' : 'stroke-grid'}
                  strokeWidth={tree ? 1.8 : 1.1}
                />
              )
            })}
            {levelSpec.graph.vertices.map((vertex) => {
              const visited = visitedSet.has(vertex.id)
              const frontier = frontierSet.has(vertex.id)
              const current = state.current === vertex.id
              const requiredVertex = required === vertex.id
              return (
                <g
                  key={vertex.id}
                  role="button"
                  tabIndex={0}
                  aria-label={`Вершина ${vertex.id}`}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter' || event.key === ' ') handleVertex(vertex.id)
                  }}
                    onClick={() => handleVertex(vertex.id)}
                    className="cursor-pointer"
                    data-testid={`graph-vertex-${vertex.id}`}
                  >
                    <circle
                      cx={vertex.x}
                      cy={vertex.y}
                      r={requiredVertex ? 6.8 : 5.8}
                      className={
                        current
                          ? 'fill-orange stroke-ink'
                          : visited
                            ? 'fill-success stroke-ink/70'
                            : frontier
                              ? 'fill-target stroke-ink/70'
                              : 'fill-bg stroke-ink/35'
                      }
                      strokeWidth={requiredVertex ? 1.4 : 1}
                    />
                    <text
                      x={vertex.x}
                      y={vertex.y + 1.4}
                      textAnchor="middle"
                      className="pointer-events-none fill-ink text-[5px] font-bold"
                    >
                      {vertex.label}
                    </text>
                </g>
              )
            })}
          </svg>
          </div>
        </div>
      }
      controls={
        <div className="space-y-3">
          <TracePanel
            mode={levelSpec.mode === 'bfs' ? 'queue' : 'stack'}
            frontier={state.frontier}
            visited={state.visited}
            current={state.current}
            cost={state.checkedEdges}
            invariantOk={state.mistakes === 0}
            invariantLabel={graphTraceInvariantLabel(state)}
            steps={state.steps}
          />
          <button
            type="button"
            onClick={resetLevel}
            className="rounded border border-ink/10 bg-paper px-2 py-1 text-xs font-semibold text-ink/75 hover:border-orange/40 hover:text-ink"
            data-testid="graph-reset"
          >
            Сбросить уровень
          </button>
        </div>
      }
      feedback={
        <p>
          Следующий допустимый ход: <span className="font-semibold">{required ?? 'нет'}</span>.
          Проверяем не картинку графа, а состояние обхода.
        </p>
      }
    />
  )
}
