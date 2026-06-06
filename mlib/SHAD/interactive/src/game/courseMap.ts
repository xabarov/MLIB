import { curriculumGraph } from './curriculumGraph'
import type { CurriculumNode, CurriculumSection } from './curriculumTypes'
import { missionDefinitions } from './missions'
import type { MissionDefinition } from './missionTypes'

export type CourseMapNode = {
  id: string
  curriculum: CurriculumNode
  mission: MissionDefinition
  label: string
  shortIdea: string
  station: CurriculumSection
}

const missionById = new Map(missionDefinitions.map((mission) => [mission.id, mission]))

export const courseMapNodes: CourseMapNode[] = curriculumGraph.flatMap((curriculum) =>
  curriculum.missionIds.map((missionId) => {
    const mission = missionById.get(missionId)
    if (!mission) throw new Error(`Unknown course map mission: ${missionId}`)
    return {
      id: curriculum.id,
      curriculum,
      mission,
      label: curriculum.cardLabel,
      shortIdea: curriculum.takeaway,
      station: curriculum.section,
    }
  }),
)

export function missionCompletionRatio(completed: string[] | undefined, mission: MissionDefinition) {
  const completedCount = completed?.length ?? 0
  return {
    completedCount,
    totalCount: mission.levels.length,
    complete: completedCount >= mission.levels.length,
  }
}

export function recommendedMissionId(completedLevels: Record<string, string[]>): string {
  const firstOpen = courseMapNodes.find((node) => {
    const progress = missionCompletionRatio(completedLevels[node.mission.id], node.mission)
    return !progress.complete
  })
  return firstOpen?.mission.id ?? courseMapNodes[0]?.mission.id ?? ''
}
