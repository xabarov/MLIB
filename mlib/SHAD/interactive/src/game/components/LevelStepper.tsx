import type { MissionLevel } from '../missionTypes'

type LevelStepperProps = {
  levels: MissionLevel[]
  activeLevelId: string
  completedLevelIds: string[]
  isUnlocked: (levelId: string) => boolean
  onSelect: (levelId: string) => void
}

export function LevelStepper({
  levels,
  activeLevelId,
  completedLevelIds,
  isUnlocked,
  onSelect,
}: LevelStepperProps) {
  return (
    <div className="grid grid-cols-4 gap-1.5" aria-label="Уровни миссии">
      {levels.map((level, index) => {
        const completed = completedLevelIds.includes(level.id)
        const unlocked = isUnlocked(level.id)
        const active = activeLevelId === level.id
        return (
          <button
            key={level.id}
            type="button"
            disabled={!unlocked}
            onClick={() => onSelect(level.id)}
            className={`flex aspect-square items-center justify-center rounded-md border text-xs font-semibold transition ${
              active
                ? 'border-orange bg-orange text-bg shadow-sm'
                : completed
                  ? 'border-success/50 bg-success/15 text-ink'
                  : unlocked
                    ? 'border-ink/10 bg-bg/80 text-ink hover:border-orange/50'
                    : 'cursor-not-allowed border-ink/5 bg-panel/50 text-ink/30'
            }`}
            title={level.title}
          >
            {index + 1}
          </button>
        )
      })}
    </div>
  )
}
