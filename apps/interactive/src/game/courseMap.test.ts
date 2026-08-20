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

  it('moves on to the next ready mission once a prerequisite is complete', () => {
    const first = courseMapNodes[0]
    const completed = {
      [first.mission.id]: first.mission.levels.map((level) => level.id),
    }
    const next = recommendedMissionId(completed)
    expect(next).not.toBe(first.mission.id)
    expect(next).toBe(courseMapNodes[1]?.mission.id)
  })
})
