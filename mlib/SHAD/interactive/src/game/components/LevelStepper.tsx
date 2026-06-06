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
    <div className="grid grid-cols-2 gap-2" aria-label="Уровни миссии" data-testid="level-map">
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
            className={`flex min-h-14 items-center gap-2 rounded-md border px-2 py-2 text-left text-xs font-semibold transition ${
              active
                ? 'border-orange bg-orange text-bg shadow-sm'
                : completed
                  ? 'border-success/50 bg-success/15 text-ink'
                  : unlocked
                    ? 'border-ink/10 bg-bg/80 text-ink hover:border-orange/50'
                    : 'cursor-not-allowed border-ink/5 bg-panel/50 text-ink/30'
            }`}
            title={level.title}
            data-testid={`level-${level.id}`}
          >
            <span className="inline-flex size-7 shrink-0 items-center justify-center rounded bg-bg/80 text-ink tabular-nums">
              {index + 1}
            </span>
            <span className="min-w-0">
              <span className="block truncate">{level.title}</span>
              <span className="block text-[10px] font-medium opacity-70">
                {completed ? 'готово' : active ? 'сейчас' : unlocked ? 'открыто' : 'закрыто'}
              </span>
            </span>
          </button>
        )
      })}
    </div>
  )
}
