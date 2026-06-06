import { describe, expect, it } from 'vitest'
import {
  graphTraceLevelSuccess,
  graphTraceLevels,
  initialTraceState,
  stepGraphTrace,
} from './graphTraceModel'

function runOrder(levelId: string, order: string[]) {
  const spec = graphTraceLevels[levelId]
  return order.reduce((state, vertex) => stepGraphTrace(spec, state, vertex), initialTraceState(spec))
}

describe('graphTraceModel', () => {
  it('accepts BFS layer order', () => {
    const spec = graphTraceLevels['bfs-layers']
    const state = runOrder('bfs-layers', ['A', 'B', 'C', 'D', 'E', 'F', 'G'])
    expect(state.visited).toEqual(spec.targetVisited)
    expect(graphTraceLevelSuccess(spec, state)).toBe(true)
  })

  it('accepts deterministic DFS stack order', () => {
    const spec = graphTraceLevels['dfs-stack']
    const state = runOrder('dfs-stack', ['A', 'B', 'D', 'F', 'E', 'G', 'C'])
    expect(state.visited).toEqual(spec.targetVisited)
    expect(graphTraceLevelSuccess(spec, state)).toBe(true)
  })

  it('records a mistake when user skips the frontier head', () => {
    const spec = graphTraceLevels['bfs-layers']
    const state = stepGraphTrace(spec, initialTraceState(spec), 'C')
    expect(state.mistakes).toBe(1)
    expect(state.steps.at(-1)?.invariantOk).toBe(false)
    expect(graphTraceLevelSuccess(spec, state)).toBe(false)
  })

  it('keeps disconnected vertices outside connected component level', () => {
    const spec = graphTraceLevels['connected-component']
    const state = runOrder('connected-component', ['A', 'B', 'C', 'D', 'E', 'F', 'G'])
    expect(state.visited).not.toContain('H')
    expect(state.visited).not.toContain('I')
    expect(graphTraceLevelSuccess(spec, state)).toBe(true)
  })
})
