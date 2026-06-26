import { describe, expect, it } from 'vitest'
import {
  bstLevels,
  bstLevelSuccess,
  bstSearch,
  childrenOf,
  correctChild,
  diagnoseBst,
} from './bstQuestModel'

const tree = bstLevels['find-leaf'].tree

describe('bstQuestModel', () => {
  it('chooses the correct branch by comparison', () => {
    // root is 5: 7 goes right (node 2), 2 goes left (node 1).
    expect(correctChild(tree, 0, 7)).toBe(2)
    expect(correctChild(tree, 0, 2)).toBe(1)
    // reaching the target returns null (terminal).
    expect(correctChild(tree, 5, 7)).toBeNull()
  })

  it('searches to the target node when present', () => {
    const found = bstSearch(tree, 7)
    expect(found.path).toEqual([0, 2, 5])
    expect(found.terminal).toBe(5)
    expect(found.found).toBe(true)
  })

  it('stops at the leaf where a missing value would be', () => {
    const missing = bstSearch(tree, 6)
    expect(missing.path).toEqual([0, 2, 5])
    expect(missing.found).toBe(false)
    expect(missing.terminal).toBe(5)
  })

  it('lists the existing children of a node', () => {
    expect(childrenOf(tree, 0)).toEqual([1, 2])
    expect(childrenOf(tree, 5)).toEqual([])
  })

  it('marks success at the terminal node of each level', () => {
    expect(bstLevelSuccess('find-leaf', 5)).toBe(true)
    expect(bstLevelSuccess('find-deep', 3)).toBe(true)
    expect(bstLevelSuccess('not-found', 5)).toBe(true)
    expect(bstLevelSuccess('find-leaf', 2)).toBe(false)
  })

  it('diagnoses idle, wrong-branch, and success', () => {
    expect(diagnoseBst({ levelId: 'find-leaf', current: 0, touched: false, lastWrong: false }).kind).toBe('idle')
    expect(diagnoseBst({ levelId: 'find-leaf', current: 0, touched: true, lastWrong: true }).kind).toBe('wrong-branch')
    expect(diagnoseBst({ levelId: 'find-leaf', current: 5, touched: true, lastWrong: false }).kind).toBe('success')
  })
})
