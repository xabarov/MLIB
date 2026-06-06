import type { ReactNode } from 'react'

export type MissionDomain =
  | 'linear-algebra'
  | 'combinatorics'
  | 'algorithms'
  | 'data-analysis'

export type MissionMechanic =
  | 'geometry-lab'
  | 'state-machine'
  | 'structure-builder'
  | 'sampler'
  | 'model-arena'
  | 'code-trace'

export type MascotState = 'idle' | 'hint' | 'success' | 'warning' | 'thinking'

export type MissionLevel = {
  id: string
  title: string
  objective: string
  hint: string
  successText: string
}

export type MissionDefinition = {
  id: string
  route: string
  title: string
  domain: MissionDomain
  mechanic: MissionMechanic
  lessonPath?: string
  difficulty: 1 | 2 | 3
  levels: MissionLevel[]
}

export type MissionBadge = {
  id: string
  label: string
  value: ReactNode
  tone?: 'neutral' | 'success' | 'warning' | 'danger' | 'energy' | 'target'
}
