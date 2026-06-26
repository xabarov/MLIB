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
const curriculumById = new Map(curriculumGraph.map((node) => [node.id, node]))

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

export function isMissionComplete(
  missionId: string,
  completedLevels: Record<string, string[]>,
): boolean {
  const mission = missionById.get(missionId)
  if (!mission) return false
  return missionCompletionRatio(completedLevels[missionId], mission).complete
}

function isCurriculumNodeComplete(
  nodeId: string,
  completedLevels: Record<string, string[]>,
): boolean {
  const node = curriculumById.get(nodeId)
  // Unknown prerequisite ids should not block a recommendation.
  if (!node) return true
  return node.missionIds.every((missionId) => isMissionComplete(missionId, completedLevels))
}

export function recommendedMissionId(completedLevels: Record<string, string[]>): string {
  // 1. First incomplete mission whose prerequisites are all complete: it is the
  //    next thing the learner is actually ready to play.
  const ready = courseMapNodes.find((node) => {
    if (isMissionComplete(node.mission.id, completedLevels)) return false
    const prerequisites = node.curriculum.prerequisites ?? []
    return prerequisites.every((id) => isCurriculumNodeComplete(id, completedLevels))
  })
  if (ready) return ready.mission.id

  // 2. Otherwise the first incomplete mission, even if its prerequisites are not
  //    finished yet, so the map never stalls on a gap.
  const anyOpen = courseMapNodes.find(
    (node) => !isMissionComplete(node.mission.id, completedLevels),
  )
  if (anyOpen) return anyOpen.mission.id

  // 3. Everything is complete: suggest a review candidate, but only one that has
  //    actually been finished, so review points back at real progress.
  const reviewTarget = courseMapNodes
    .flatMap((node) => node.curriculum.reviewAfterMissionIds ?? [])
    .find((missionId) => isMissionComplete(missionId, completedLevels))
  return reviewTarget ?? courseMapNodes[0]?.mission.id ?? ''
}
