import { create } from 'zustand'
import { persist } from 'zustand/middleware'

type ProgressState = {
  completedLevels: Record<string, string[]>
  unlockedLevels: Record<string, string[]>
  keys: number
  completeLevel: (missionId: string, levelId: string, nextLevelId?: string) => void
  unlockLevel: (missionId: string, levelId: string) => void
  isLevelCompleted: (missionId: string, levelId: string) => boolean
  isLevelUnlocked: (missionId: string, levelId: string, firstLevelId: string) => boolean
}

function uniqueAppend(items: string[] | undefined, item: string): string[] {
  if (!items) return [item]
  return items.includes(item) ? items : [...items, item]
}

export const useProgressStore = create<ProgressState>()(
  persist(
    (set, get) => ({
      completedLevels: {},
      unlockedLevels: {},
      keys: 0,
      completeLevel: (missionId, levelId, nextLevelId) =>
        set((state) => {
          const alreadyDone = state.completedLevels[missionId]?.includes(levelId) ?? false
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
    }),
    {
      name: 'shad-interactive-progress-v1',
      partialize: (state) => ({
        completedLevels: state.completedLevels,
        unlockedLevels: state.unlockedLevels,
        keys: state.keys,
      }),
    },
  ),
)
