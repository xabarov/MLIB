import type { MissionDefinition, MissionLevel } from '../missionTypes'

type MissionHeaderProps = {
  definition: MissionDefinition
  level: MissionLevel
}

export function MissionHeader({ definition, level }: MissionHeaderProps) {
  return (
    <header className="space-y-2">
      <p className="text-xs font-semibold uppercase tracking-wide text-orange">
        {definition.mechanic.replace('-', ' ')}
      </p>
      <div>
        <h1 className="text-xl font-semibold text-ink">{definition.title}</h1>
        <p className="mt-1 text-sm font-medium text-ink/70">{level.title}</p>
      </div>
      <p className="text-sm leading-relaxed text-ink/85">{level.objective}</p>
    </header>
  )
}
