import { CheckCircle2 } from 'lucide-react'
import type { MissionDefinition } from '../missionTypes'

type MissionDebriefCardProps = {
  definition: MissionDefinition
  completedLevelIds: string[]
}

function lastCompletedLevel(definition: MissionDefinition, completedLevelIds: string[]) {
  return [...definition.levels]
    .reverse()
    .find((level) => completedLevelIds.includes(level.id))
}

export function MissionDebriefCard({ definition, completedLevelIds }: MissionDebriefCardProps) {
  const allDone = definition.levels.every((level) => completedLevelIds.includes(level.id))
  const level = lastCompletedLevel(definition, completedLevelIds)
  if (!allDone || !level) return null

  return (
    <section
      className="rounded-md border border-target/25 bg-target/10 p-3 text-sm text-ink"
      data-testid="mission-debrief"
    >
      <div className="mb-2 flex items-center gap-2">
        <span className="inline-flex size-7 items-center justify-center rounded bg-target/15 text-target">
          <CheckCircle2 className="size-4" />
        </span>
        <div>
          <p className="font-semibold">Что осталось в руках</p>
          <p className="text-xs text-ink/60">Короткая фиксация идеи перед лекцией.</p>
        </div>
      </div>
      <div className="space-y-1.5 text-xs leading-relaxed text-ink/76">
        <p>
          <span className="font-semibold text-ink">Изменилось: </span>
          {level.successText}
        </p>
        <p>
          <span className="font-semibold text-ink">Инвариант: </span>
          {level.takeaway}
        </p>
        {level.lectureAnchor && (
          <p>
            <span className="font-semibold text-ink">В лекции: </span>
            {level.lectureAnchor}
          </p>
        )}
        {definition.reflectionPrompt && (
          <p>
            <span className="font-semibold text-ink">Вопрос: </span>
            {definition.reflectionPrompt}
          </p>
        )}
      </div>
    </section>
  )
}
