import { describe, expect, it } from 'vitest'
import {
  componentCount,
  diagnoseDsu,
  dsuLevels,
  dsuLevelSuccess,
  find,
  makeParent,
  sameComponent,
  union,
} from './dsuForestModel'

function applyEdges(n: number, edges: Array<[number, number]>): number[] {
  let parent = makeParent(n)
  for (const [a, b] of edges) {
    parent = union(parent, a, b).parent
  }
  return parent
}

describe('dsuForestModel', () => {
  it('starts with each element in its own set', () => {
    const parent = makeParent(6)
    expect(componentCount(parent)).toBe(6)
    expect(sameComponent(parent, 0, 1)).toBe(false)
  })

  it('merges two sets and reports the union', () => {
    const parent = makeParent(4)
    const result = union(parent, 0, 1)
    expect(result.merged).toBe(true)
    expect(sameComponent(result.parent, 0, 1)).toBe(true)
    expect(componentCount(result.parent)).toBe(3)
  })

  it('treats a union inside one set as a redundant cycle', () => {
    let parent = makeParent(3)
    parent = union(parent, 0, 1).parent
    parent = union(parent, 1, 2).parent
    const redundant = union(parent, 0, 2)
    expect(redundant.merged).toBe(false)
    expect(redundant.parent).toBe(parent) // unchanged reference
  })

  it('connects everything into one component for connect-all', () => {
    const parent = applyEdges(6, dsuLevels['connect-all'].edges)
    expect(componentCount(parent)).toBe(1)
    expect(dsuLevelSuccess('connect-all', parent)).toBe(true)
  })

  it('leaves two groups until the bridge is taken', () => {
    const config = dsuLevels['two-groups']
    const withoutBridge = config.edges.filter(([a, b]) => !(a === 2 && b === 3))
    const twoGroups = applyEdges(6, withoutBridge)
    expect(componentCount(twoGroups)).toBe(2)
    expect(dsuLevelSuccess('two-groups', twoGroups)).toBe(true)
    // Taking the bridge over-merges into one component.
    const merged = union(twoGroups, 2, 3).parent
    expect(componentCount(merged)).toBe(1)
    expect(diagnoseDsu({ levelId: 'two-groups', parent: merged, touched: true }).kind).toBe('over-merged')
  })

  it('diagnoses idle, in-progress, and success', () => {
    const start = makeParent(6)
    expect(diagnoseDsu({ levelId: 'connect-all', parent: start, touched: false }).kind).toBe('idle')
    const partial = union(start, 0, 1).parent
    expect(diagnoseDsu({ levelId: 'connect-all', parent: partial, touched: true }).kind).toBe('in-progress')
    const full = applyEdges(6, dsuLevels['connect-all'].edges)
    expect(diagnoseDsu({ levelId: 'connect-all', parent: full, touched: true }).kind).toBe('success')
  })

  it('keeps find stable on a chain', () => {
    const parent = applyEdges(4, [
      [0, 1],
      [1, 2],
      [2, 3],
    ])
    expect(find(parent, 3)).toBe(find(parent, 0))
  })
})
