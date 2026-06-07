import type { ReactNode } from 'react'
import { useMemo } from 'react'
import { useProgressStore } from '../../store/progressStore'
import type { MascotState, MissionBadge, MissionDefinition } from '../missionTypes'
import { InvariantBadge } from './InvariantBadge'
import { LevelStepper } from './LevelStepper'
import { MascotCoach } from './MascotCoach'
import { MissionDebriefCard } from './MissionDebriefCard'
import { MissionHeader } from './MissionHeader'
import { MissionReflection } from './MissionReflection'
import { MissionSummary } from './MissionSummary'
import { MissionTakeaway } from './MissionTakeaway'
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
  sceneViewportClassName?: string
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
  sceneViewportClassName = 'h-[540px] pt-[96px] sm:pt-[74px] lg:h-full',
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
  const levelSuccess = completedLevels.includes(activeLevel.id) || mascotState === 'success'

  return (
    <div
      className="flex min-h-0 flex-1 flex-col bg-bg lg:flex-row"
      data-testid={`mission-${definition.id}`}
    >
      <section className="relative min-h-[430px] flex-1 overflow-hidden border-b border-panel lg:border-r lg:border-b-0">
        <div className="absolute inset-x-0 top-0 z-20 border-b border-ink/10 bg-bg/92 px-3 py-2 backdrop-blur">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="min-w-[180px]">
              <p className="text-[10px] font-semibold uppercase tracking-wide text-orange">
                Цель уровня
              </p>
              <p className="text-sm font-semibold leading-snug text-ink">{activeLevel.objective}</p>
            </div>
            <div className="flex flex-wrap items-center gap-2">
          {badges.map((badge) => (
            <InvariantBadge
              key={badge.id}
              label={badge.label}
              value={badge.value}
              tone={badge.tone}
            />
          ))}
            </div>
          </div>
        </div>
        <div className={sceneViewportClassName}>{scene}</div>
      </section>

      <aside className="flex w-full shrink-0 flex-col gap-4 overflow-y-auto border-panel bg-panel/30 p-4 lg:w-[380px] xl:w-[420px]">
        <MissionHeader definition={definition} level={activeLevel} />
        <RewardMeter
          keys={keys}
          completed={completedLevels.length}
          total={definition.levels.length}
          success={levelSuccess}
        />
        <LevelStepper
          levels={definition.levels}
          activeLevelId={activeLevel.id}
          completedLevelIds={completedLevels}
          isUnlocked={(levelId) => isUnlocked(definition.id, levelId, firstLevelId)}
          onSelect={onLevelSelect}
        />
        {controls && (
          <div className="rounded-md border border-ink/10 bg-bg/72 p-3" data-testid="mission-controls">
            {controls}
          </div>
        )}
        {feedback && (
          <div
            className="rounded-md border border-ink/10 bg-highlight/70 p-3 text-sm leading-relaxed text-ink/80"
            data-testid="mission-feedback"
          >
            {feedback}
          </div>
        )}
        <MissionTakeaway level={activeLevel} success={levelSuccess} />
        <MissionSummary definition={definition} completedLevelIds={completedLevels} />
        <MissionDebriefCard definition={definition} completedLevelIds={completedLevels} />
        <MissionReflection definition={definition} completedLevelIds={completedLevels} />
        <MascotCoach state={mascotState} message={mascotMessage} />
      </aside>
    </div>
  )
}
