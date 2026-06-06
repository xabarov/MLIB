import { BookOpen, Sparkles } from 'lucide-react'
import type { MissionLevel } from '../missionTypes'

type MissionTakeawayProps = {
  level: MissionLevel
  success: boolean
}

export function MissionTakeaway({ level, success }: MissionTakeawayProps) {
  if (!success) return null

  return (
    <section
      className="rounded-md border border-success/30 bg-success/10 p-3 text-sm text-ink shadow-[0_8px_24px_rgba(95,141,101,0.12)]"
      data-testid="mission-takeaway"
    >
      <div className="flex items-start gap-2">
        <span className="mt-0.5 inline-flex size-7 shrink-0 items-center justify-center rounded bg-success/18 text-success">
          <Sparkles className="size-4" />
        </span>
        <div className="min-w-0 space-y-1">
          <p className="font-semibold">Что стало видно</p>
          <p className="leading-relaxed">{level.takeaway}</p>
          {level.nextPrompt && <p className="text-xs text-ink/65">{level.nextPrompt}</p>}
          {level.lectureAnchor && (
            <p className="inline-flex items-center gap-1 text-xs font-medium text-target">
              <BookOpen className="size-3.5" />
              {level.lectureAnchor}
            </p>
          )}
        </div>
      </div>
    </section>
  )
}
