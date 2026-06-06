export type CurriculumSection = 'algebra' | 'combinatorics' | 'algorithms' | 'data-analysis'

export type CurriculumStatus = 'available' | 'prototype' | 'planned' | 'needs-review'

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
  takeaway: string
  status: CurriculumStatus
}
