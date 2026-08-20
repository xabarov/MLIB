import type { MissionDefinition, MissionLevel } from '../missionTypes'

type MissionHeaderProps = {
  definition: MissionDefinition
  level: MissionLevel
}

export function MissionHeader({ definition, level }: MissionHeaderProps) {
  return (
    <header className="space-y-2">
      <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-orange">
        {definition.mechanic.replace('-', ' ')}
      </p>
      <div>
        <h1 className="font-display text-2xl font-semibold tracking-tight text-ink">{definition.title}</h1>
        <p className="mt-1 text-sm font-medium text-ink/70">{level.title}</p>
      </div>
      <p className="text-sm leading-relaxed text-ink/85">{level.objective}</p>
    </header>
  )
}
