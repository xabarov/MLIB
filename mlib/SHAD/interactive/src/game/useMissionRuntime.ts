import { useCallback, useEffect, useMemo, useState } from 'react'
import { useProgressStore } from '../store/progressStore'
import type { MissionDefinition, MissionLevel } from './missionTypes'

const emptyLevels: string[] = []

export type MissionRuntime = {
  activeLevel: MissionLevel
  activeLevelIndex: number
  activeLevelId: string
  completedLevelIds: string[]
  completedCount: number
  firstLevelId: string
  nextLevelId?: string
  setActiveLevelId: (levelId: string) => void
  completeActiveLevel: () => void
  isLevelUnlocked: (levelId: string) => boolean
}

export function useMissionRuntime(definition: MissionDefinition): MissionRuntime {
  const firstLevelId = definition.levels[0]?.id ?? ''
  const [activeLevelId, setActiveLevelId] = useState(firstLevelId)

  const completeLevel = useProgressStore((s) => s.completeLevel)
  const unlockLevel = useProgressStore((s) => s.unlockLevel)
  const isUnlocked = useProgressStore((s) => s.isLevelUnlocked)
  const completedLevelIds = useProgressStore(
    (s) => s.completedLevels[definition.id] ?? emptyLevels,
  )

  useEffect(() => {
    if (firstLevelId) unlockLevel(definition.id, firstLevelId)
  }, [definition.id, firstLevelId, unlockLevel])

  const activeLevelIndex = Math.max(
    definition.levels.findIndex((level) => level.id === activeLevelId),
    0,
  )
  const activeLevel = definition.levels[activeLevelIndex] ?? definition.levels[0]
  const nextLevelId = definition.levels[activeLevelIndex + 1]?.id
  const completeActiveLevel = useCallback(() => {
    completeLevel(definition.id, activeLevel.id, nextLevelId)
  }, [activeLevel.id, completeLevel, definition.id, nextLevelId])
  const isLevelUnlocked = useCallback(
    (levelId: string) => isUnlocked(definition.id, levelId, firstLevelId),
    [definition.id, firstLevelId, isUnlocked],
  )

  const runtime = useMemo<MissionRuntime>(
    () => ({
      activeLevel,
      activeLevelIndex,
      activeLevelId: activeLevel.id,
      completedLevelIds,
      completedCount: completedLevelIds.length,
      firstLevelId,
      nextLevelId,
      setActiveLevelId,
      completeActiveLevel,
      isLevelUnlocked,
    }),
    [
      activeLevel,
      activeLevelIndex,
      completeActiveLevel,
      completedLevelIds,
      firstLevelId,
      isLevelUnlocked,
      nextLevelId,
    ],
  )

  return runtime
}
