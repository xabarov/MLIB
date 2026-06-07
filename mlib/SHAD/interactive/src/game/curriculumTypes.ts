export type CurriculumSection = 'algebra' | 'combinatorics' | 'algorithms' | 'data-analysis'

export type CurriculumStatus = 'available' | 'prototype' | 'planned' | 'needs-review'
export type CurriculumCoverageStatus = 'seed' | 'playable' | 'diagnosed' | 'review-ready'

export type CurriculumNode = {
  id: string
  title: string
  cardLabel: string
  section: CurriculumSection
  lessonPaths: string[]
  qaPaths?: string[]
  prerequisites: string[]
  missionIds: string[]
  plannedMissionIds?: string[]
  skillIds: string[]
  unlocks: string[]
  reviewAfterMissionIds?: string[]
  readinessLabel: string
  coverageStatus: CurriculumCoverageStatus
  takeaway: string
  status: CurriculumStatus
}
