import type { ReactNode } from 'react'
import { useMemo } from 'react'
import { useProgressStore } from '../../store/progressStore'
import type { MascotState, MissionBadge, MissionDefinition } from '../missionTypes'
import { InvariantBadge } from './InvariantBadge'
import { LevelStepper } from './LevelStepper'
import { MascotCoach } from './MascotCoach'
import { MissionHeader } from './MissionHeader'
import { RewardMeter } from './RewardMeter'

const emptyLevels: string[] = []

type MissionShellProps = {
  definition: MissionDefinition
  activeLevelId: string
  onLevelSelect: (levelId: string) => void
  mascotState: MascotState
  mascotMessage: string
  badges: MissionBadge[]
  scene: ReactNode
  controls?: ReactNode
  feedback?: ReactNode
}

export function MissionShell({
  definition,
  activeLevelId,
  onLevelSelect,
  mascotState,
  mascotMessage,
  badges,
  scene,
  controls,
  feedback,
}: MissionShellProps) {
  const keys = useProgressStore((s) => s.keys)
  const completedLevels = useProgressStore((s) => s.completedLevels[definition.id] ?? emptyLevels)
  const isUnlocked = useProgressStore((s) => s.isLevelUnlocked)
  const firstLevelId = definition.levels[0]?.id ?? ''
  const activeLevel = useMemo(
    () => definition.levels.find((level) => level.id === activeLevelId) ?? definition.levels[0],
    [activeLevelId, definition.levels],
  )

  return (
    <div className="flex min-h-0 flex-1 flex-col bg-bg lg:flex-row">
      <section className="relative min-h-[460px] flex-1 overflow-hidden border-b border-panel lg:border-r lg:border-b-0">
        <div className="absolute inset-x-0 top-0 z-10 flex flex-wrap items-center gap-2 border-b border-ink/10 bg-bg/90 px-3 py-2 backdrop-blur">
          {badges.map((badge) => (
            <InvariantBadge
              key={badge.id}
              label={badge.label}
              value={badge.value}
              tone={badge.tone}
            />
          ))}
        </div>
        <div className="h-[560px] pt-[74px] lg:h-full">{scene}</div>
      </section>

      <aside className="flex w-full shrink-0 flex-col gap-4 overflow-y-auto border-panel bg-panel/30 p-4 lg:w-[360px] xl:w-[400px]">
        <MissionHeader definition={definition} level={activeLevel} />
        <RewardMeter
          keys={keys}
          completed={completedLevels.length}
          total={definition.levels.length}
        />
        <LevelStepper
          levels={definition.levels}
          activeLevelId={activeLevel.id}
          completedLevelIds={completedLevels}
          isUnlocked={(levelId) => isUnlocked(definition.id, levelId, firstLevelId)}
          onSelect={onLevelSelect}
        />
        {controls && <div className="rounded-md border border-ink/10 bg-bg/72 p-3">{controls}</div>}
        {feedback && (
          <div className="rounded-md border border-ink/10 bg-highlight/70 p-3 text-sm leading-relaxed text-ink/80">
            {feedback}
          </div>
        )}
        <MascotCoach state={mascotState} message={mascotMessage} />
      </aside>
    </div>
  )
}
