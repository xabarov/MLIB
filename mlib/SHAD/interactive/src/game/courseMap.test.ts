import { describe, expect, it } from 'vitest'
import { courseMapNodes, recommendedMissionId } from './courseMap'

function completedAllLevels() {
  return Object.fromEntries(
    courseMapNodes.map((node) => [
      node.mission.id,
      node.mission.levels.map((level) => level.id),
    ]),
  )
}

describe('courseMap', () => {
  it('recommends the first incomplete mission before review loops', () => {
    expect(recommendedMissionId({})).toBe(courseMapNodes[0]?.mission.id)
  })

  it('recommends a configured review mission after the first pass is complete', () => {
    expect(recommendedMissionId(completedAllLevels())).toBe('matrix-machine')
  })
})
