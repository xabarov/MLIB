import { describe, expect, it } from 'vitest'
import { curriculumGraph, validateCurriculumGraph } from './curriculumGraph'
import type { CurriculumNode } from './curriculumTypes'
import { missionDefinitions } from './missions'

const knownMissionIds = new Set(missionDefinitions.map((mission) => mission.id))

describe('curriculumGraph', () => {
  it('references existing prerequisites and missions', () => {
    expect(validateCurriculumGraph(curriculumGraph, knownMissionIds)).toEqual([])
  })

  it('reports unknown prerequisite and mission ids', () => {
    const broken: CurriculumNode[] = [
      {
        id: 'broken',
        title: 'Broken',
        cardLabel: 'Broken',
        section: 'algebra',
        lessonPaths: ['lesson.md'],
        prerequisites: ['missing-node'],
        missionIds: ['missing-mission'],
        skillIds: ['broken-skill'],
        unlocks: [],
        readinessLabel: 'Broken',
        coverageStatus: 'seed',
        takeaway: 'Broken node',
        status: 'needs-review',
      },
    ]

    expect(validateCurriculumGraph(broken, knownMissionIds)).toEqual([
      'broken: unknown prerequisite missing-node',
      'broken: unknown mission missing-mission',
    ])
  })

  it('requires lesson paths for every node', () => {
    const broken: CurriculumNode[] = [
      {
        id: 'no-lesson',
        title: 'No lesson',
        cardLabel: 'No lesson',
        section: 'algebra',
        lessonPaths: [],
        prerequisites: [],
        missionIds: ['kernel-hunt'],
        skillIds: ['kernel'],
        unlocks: [],
        readinessLabel: 'No lesson',
        coverageStatus: 'seed',
        takeaway: 'No lesson path',
        status: 'needs-review',
      },
    ]

    expect(validateCurriculumGraph(broken, knownMissionIds)).toEqual([
      'no-lesson: lessonPaths must not be empty',
    ])
  })

  it('validates unlocks, review mission ids and skills', () => {
    const broken: CurriculumNode[] = [
      {
        id: 'broken-skills',
        title: 'Broken skills',
        cardLabel: 'Broken skills',
        section: 'algebra',
        lessonPaths: ['lesson.md'],
        prerequisites: [],
        missionIds: ['kernel-hunt'],
        skillIds: [],
        unlocks: ['missing-node'],
        reviewAfterMissionIds: ['missing-mission'],
        readinessLabel: 'Broken skills',
        coverageStatus: 'seed',
        takeaway: 'Broken skills',
        status: 'needs-review',
      },
    ]

    expect(validateCurriculumGraph(broken, knownMissionIds)).toEqual([
      'broken-skills: unknown unlock missing-node',
      'broken-skills: unknown review mission missing-mission',
      'broken-skills: skillIds must not be empty',
    ])
  })
})
