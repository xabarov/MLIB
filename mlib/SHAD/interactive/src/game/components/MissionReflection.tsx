import { BookOpen, MessageSquareText } from 'lucide-react'
import type { MissionDefinition } from '../missionTypes'

type MissionReflectionProps = {
  definition: MissionDefinition
  completedLevelIds: string[]
}

export function MissionReflection({ definition, completedLevelIds }: MissionReflectionProps) {
  const allDone = definition.levels.every((level) => completedLevelIds.includes(level.id))
  if (!allDone || (!definition.reflectionPrompt && !definition.transferTask)) return null

  return (
    <section
      className="rounded-md border border-orange/25 bg-highlight/75 p-3 text-sm text-ink"
      data-testid="mission-reflection"
    >
      <div className="mb-2 flex items-center gap-2">
        <span className="inline-flex size-7 items-center justify-center rounded bg-orange/15 text-orange">
          <MessageSquareText className="size-4" />
        </span>
        <div>
          <p className="font-semibold">Перенеси идею в задачу</p>
          <p className="text-xs text-ink/60">Короткая проверка понимания без оценки.</p>
        </div>
      </div>
      <div className="space-y-2 text-xs leading-relaxed text-ink/76">
        {definition.reflectionPrompt && (
          <p>
            <span className="font-semibold text-ink">Вопрос: </span>
            {definition.reflectionPrompt}
          </p>
        )}
        {definition.transferTask && (
          <p>
            <span className="font-semibold text-ink">Перенос: </span>
            {definition.transferTask}
          </p>
        )}
        {definition.lessonPath && (
          <p className="inline-flex items-center gap-1 font-medium text-target">
            <BookOpen className="size-3.5" />
            {definition.lessonPath}
          </p>
        )}
      </div>
    </section>
  )
}
