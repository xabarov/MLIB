import { CheckCircle2, Map } from 'lucide-react'
import type { MissionDefinition } from '../missionTypes'

type MissionSummaryProps = {
  definition: MissionDefinition
  completedLevelIds: string[]
}

export function MissionSummary({ definition, completedLevelIds }: MissionSummaryProps) {
  const allDone = definition.levels.every((level) => completedLevelIds.includes(level.id))
  if (!allDone) return null

  return (
    <section
      className="rounded-md border border-target/30 bg-target/10 p-3 text-sm text-ink"
      data-testid="mission-summary"
    >
      <div className="mb-2 flex items-center gap-2">
        <span className="inline-flex size-7 items-center justify-center rounded bg-target/15 text-target">
          <CheckCircle2 className="size-4" />
        </span>
        <div>
          <p className="font-semibold">{definition.summaryTitle ?? 'Миссия собрана'}</p>
          <p className="text-xs text-ink/60">
            {completedLevelIds.length}/{definition.levels.length} уровней закрыты
          </p>
        </div>
      </div>
      {definition.summaryText && <p className="mb-2 leading-relaxed">{definition.summaryText}</p>}
      <ul className="space-y-1 text-xs leading-relaxed text-ink/72">
        {definition.levels.map((level) => (
          <li key={level.id} className="flex gap-2">
            <span className="mt-1 size-1.5 shrink-0 rounded-full bg-target" />
            <span>{level.takeaway}</span>
          </li>
        ))}
      </ul>
      {definition.nextMissionLabel && (
        <p className="mt-3 inline-flex items-center gap-1 text-xs font-semibold text-target">
          <Map className="size-3.5" />
          Дальше: {definition.nextMissionLabel}
        </p>
      )}
    </section>
  )
}
