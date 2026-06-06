import type { TraceStep } from '../../game/missionTypes'

export type GraphMode = 'bfs' | 'dfs'

export type GraphVertex = {
  id: string
  label: string
  x: number
  y: number
}

export type GraphEdge = [string, string]

export type GraphDefinition = {
  vertices: GraphVertex[]
  edges: GraphEdge[]
}

export type GraphTraceState = {
  mode: GraphMode
  frontier: string[]
  visited: string[]
  current?: string
  treeEdges: GraphEdge[]
  checkedEdges: number
  mistakes: number
  steps: TraceStep[]
}

export type GraphTraceLevelSpec = {
  mode: GraphMode
  start: string
  targetVisited: string[]
  graph: GraphDefinition
  initialState?: Partial<GraphTraceState>
}

export const graphDispatcherGraph: GraphDefinition = {
  vertices: [
    { id: 'A', label: 'A', x: 18, y: 48 },
    { id: 'B', label: 'B', x: 36, y: 24 },
    { id: 'C', label: 'C', x: 36, y: 72 },
    { id: 'D', label: 'D', x: 58, y: 20 },
    { id: 'E', label: 'E', x: 62, y: 58 },
    { id: 'F', label: 'F', x: 82, y: 38 },
    { id: 'G', label: 'G', x: 82, y: 76 },
  ],
  edges: [
    ['A', 'B'],
    ['A', 'C'],
    ['B', 'D'],
    ['B', 'E'],
    ['C', 'E'],
    ['D', 'F'],
    ['E', 'F'],
    ['E', 'G'],
  ],
}

const componentGraph: GraphDefinition = {
  vertices: [
    ...graphDispatcherGraph.vertices,
    { id: 'H', label: 'H', x: 14, y: 82 },
    { id: 'I', label: 'I', x: 8, y: 66 },
  ],
  edges: [...graphDispatcherGraph.edges, ['H', 'I']],
}

export const graphTraceLevels: Record<string, GraphTraceLevelSpec> = {
  'bfs-layers': {
    mode: 'bfs',
    start: 'A',
    targetVisited: ['A', 'B', 'C', 'D', 'E', 'F', 'G'],
    graph: graphDispatcherGraph,
  },
  'dfs-stack': {
    mode: 'dfs',
    start: 'A',
    targetVisited: ['A', 'B', 'D', 'F', 'E', 'G', 'C'],
    graph: graphDispatcherGraph,
  },
  'connected-component': {
    mode: 'bfs',
    start: 'A',
    targetVisited: ['A', 'B', 'C', 'D', 'E', 'F', 'G'],
    graph: componentGraph,
  },
  'repair-trace': {
    mode: 'bfs',
    start: 'A',
    targetVisited: ['A', 'B', 'C', 'D', 'E', 'F', 'G'],
    graph: graphDispatcherGraph,
    initialState: {
      frontier: ['B', 'C'],
      visited: ['A'],
      current: 'A',
      treeEdges: [['A', 'B'], ['A', 'C']],
      checkedEdges: 2,
      steps: [
        {
          id: 'seed-A',
          label: 'A уже раскрыта: граница B, C',
          state: { current: 'A', frontier: ['B', 'C'], visited: ['A'] },
          cost: 2,
          invariantOk: true,
        },
      ],
    },
  },
}

export function neighbors(graph: GraphDefinition, vertexId: string): string[] {
  return graph.edges
    .filter(([a, b]) => a === vertexId || b === vertexId)
    .map(([a, b]) => (a === vertexId ? b : a))
    .sort()
}

export function initialTraceState(spec: GraphTraceLevelSpec): GraphTraceState {
  return {
    mode: spec.mode,
    frontier: spec.initialState?.frontier ?? [spec.start],
    visited: spec.initialState?.visited ?? [],
    current: spec.initialState?.current,
    treeEdges: spec.initialState?.treeEdges ?? [],
    checkedEdges: spec.initialState?.checkedEdges ?? 0,
    mistakes: spec.initialState?.mistakes ?? 0,
    steps: spec.initialState?.steps ?? [],
  }
}

export function nextRequiredVertex(state: GraphTraceState): string | undefined {
  return state.frontier[0]
}

export function stepGraphTrace(
  spec: GraphTraceLevelSpec,
  state: GraphTraceState,
  vertexId: string,
): GraphTraceState {
  const required = nextRequiredVertex(state)
  if (vertexId !== required) {
    return {
      ...state,
      mistakes: state.mistakes + 1,
      steps: [
        ...state.steps,
        {
          id: `mistake-${state.steps.length}`,
          label: `Нельзя брать ${vertexId}: следующий ${required ?? 'пусто'}`,
          state: { frontier: state.frontier, visited: state.visited },
          cost: state.checkedEdges,
          invariantOk: false,
        },
      ],
    }
  }

  const visitedSet = new Set([...state.visited, vertexId])
  const frontierSet = new Set(state.frontier.slice(1))
  const freshNeighbors = neighbors(spec.graph, vertexId).filter(
    (neighbor) => !visitedSet.has(neighbor) && !frontierSet.has(neighbor),
  )
  const nextFrontier =
    state.mode === 'bfs'
      ? [...state.frontier.slice(1), ...freshNeighbors]
      : [...freshNeighbors, ...state.frontier.slice(1)]
  const treeEdges: GraphEdge[] = [
    ...state.treeEdges,
    ...freshNeighbors.map((neighbor): GraphEdge => [vertexId, neighbor]),
  ]
  const nextVisited = [...state.visited, vertexId]
  const checkedEdges = state.checkedEdges + neighbors(spec.graph, vertexId).length

  return {
    ...state,
    frontier: nextFrontier,
    visited: nextVisited,
    current: vertexId,
    treeEdges,
    checkedEdges,
    steps: [
      ...state.steps,
      {
        id: `step-${state.steps.length}`,
        label: `${vertexId}: добавили ${freshNeighbors.length ? freshNeighbors.join(', ') : 'никого'}`,
        state: { current: vertexId, frontier: nextFrontier, visited: nextVisited },
        cost: checkedEdges,
        invariantOk: true,
      },
    ],
  }
}

export function graphTraceLevelSuccess(spec: GraphTraceLevelSpec, state: GraphTraceState): boolean {
  return (
    state.mistakes === 0 &&
    spec.targetVisited.length === state.visited.length &&
    spec.targetVisited.every((vertex, index) => state.visited[index] === vertex)
  )
}

export function graphTraceInvariantLabel(state: GraphTraceState): string {
  if (state.mistakes > 0) return 'инвариант нарушен'
  return state.mode === 'bfs' ? 'очередь идет по слоям' : 'стек держит глубину'
}
