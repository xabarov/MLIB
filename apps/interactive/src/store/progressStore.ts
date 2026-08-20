import { create } from 'zustand'
import { persist } from 'zustand/middleware'

type ProgressState = {
  schemaVersion: 2
  completedLevels: Record<string, string[]>
  unlockedLevels: Record<string, string[]>
  keys: number
  keysByMission: Record<string, number>
  completeLevel: (missionId: string, levelId: string, nextLevelId?: string) => void
  unlockLevel: (missionId: string, levelId: string) => void
  isLevelCompleted: (missionId: string, levelId: string) => boolean
  isLevelUnlocked: (missionId: string, levelId: string, firstLevelId: string) => boolean
  resetProgress: () => void
}

function uniqueAppend(items: string[] | undefined, item: string): string[] {
  if (!items) return [item]
  return items.includes(item) ? items : [...items, item]
}

export const useProgressStore = create<ProgressState>()(
  persist(
    (set, get) => ({
      schemaVersion: 2,
      completedLevels: {},
      unlockedLevels: {},
      keys: 0,
      keysByMission: {},
      completeLevel: (missionId, levelId, nextLevelId) =>
        set((state) => {
          const alreadyDone = state.completedLevels[missionId]?.includes(levelId) ?? false
          const nextKeysByMission = alreadyDone
            ? state.keysByMission
            : {
                ...state.keysByMission,
                [missionId]: (state.keysByMission[missionId] ?? 0) + 1,
              }
          return {
            completedLevels: {
              ...state.completedLevels,
              [missionId]: uniqueAppend(state.completedLevels[missionId], levelId),
            },
            unlockedLevels: nextLevelId
              ? {
                  ...state.unlockedLevels,
                  [missionId]: uniqueAppend(state.unlockedLevels[missionId], nextLevelId),
                }
              : state.unlockedLevels,
            keys: alreadyDone ? state.keys : state.keys + 1,
            keysByMission: nextKeysByMission,
          }
        }),
      unlockLevel: (missionId, levelId) =>
        set((state) => ({
          unlockedLevels: {
            ...state.unlockedLevels,
            [missionId]: uniqueAppend(state.unlockedLevels[missionId], levelId),
          },
        })),
      isLevelCompleted: (missionId, levelId) =>
        get().completedLevels[missionId]?.includes(levelId) ?? false,
      isLevelUnlocked: (missionId, levelId, firstLevelId) =>
        levelId === firstLevelId || (get().unlockedLevels[missionId]?.includes(levelId) ?? false),
      resetProgress: () =>
        set({
          completedLevels: {},
          unlockedLevels: {},
          keys: 0,
          keysByMission: {},
        }),
    }),
    {
      name: 'shad-interactive-progress-v1',
      version: 2,
      migrate: (persisted) => {
        if (!persisted || typeof persisted !== 'object') return persisted
        const state = persisted as Partial<ProgressState>
        return {
          schemaVersion: 2,
          completedLevels: state.completedLevels ?? {},
          unlockedLevels: state.unlockedLevels ?? {},
          keys: state.keys ?? 0,
          keysByMission: state.keysByMission ?? {},
        }
      },
      partialize: (state) => ({
        schemaVersion: state.schemaVersion,
        completedLevels: state.completedLevels,
        unlockedLevels: state.unlockedLevels,
        keys: state.keys,
        keysByMission: state.keysByMission,
      }),
    },
  ),
)
