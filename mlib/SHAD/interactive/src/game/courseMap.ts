import {
  determinantForgeMission,
  graphDispatcherMission,
  kernelHuntMission,
  matrixMachineMission,
  substitutionWorkshopMission,
} from './missions'
import type { MissionDefinition } from './missionTypes'

export type CourseMapNode = {
  id: string
  mission: MissionDefinition
  label: string
  shortIdea: string
  station: 'algebra' | 'combinatorics' | 'algorithms'
}

export const courseMapNodes: CourseMapNode[] = [
  {
    id: substitutionWorkshopMission.id,
    mission: substitutionWorkshopMission,
    label: 'Состояния и операции',
    shortIdea: 'Перестановка меняется транспозициями, а циклы и знак остаются видимыми.',
    station: 'combinatorics',
  },
  {
    id: matrixMachineMission.id,
    mission: matrixMachineMission,
    label: 'Матрица как действие',
    shortIdea: 'Столбцы матрицы - это образы базисных векторов.',
    station: 'algebra',
  },
  {
    id: determinantForgeMission.id,
    mission: determinantForgeMission,
    label: 'Площадь и ориентация',
    shortIdea: 'Определитель хранит масштаб площади, знак и вырожденность.',
    station: 'algebra',
  },
  {
    id: kernelHuntMission.id,
    mission: kernelHuntMission,
    label: 'Схлопнутые направления',
    shortIdea: 'Ядро - подпространство решений Ax = 0.',
    station: 'algebra',
  },
  {
    id: graphDispatcherMission.id,
    mission: graphDispatcherMission,
    label: 'Trace алгоритма',
    shortIdea: 'Очередь, стек и посещенные вершины превращают обход в проверяемое состояние.',
    station: 'algorithms',
  },
]

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
