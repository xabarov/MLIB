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

export type MascotRole =
  | 'guide'
  | 'pivot'
  | 'frontier'
  | 'error-marker'
  | 'invariant-token'
  | 'data-point'
  | 'metric-inspector'

export type TraceStep = {
  id: string
  label: string
  state: Record<string, unknown>
  cost?: number
  invariantOk?: boolean
}

export type MissionDataContract = {
  traceSteps?: TraceStep[]
}

export type MissionLevel = {
  id: string
  title: string
  objective: string
  hint: string
  hintLevels?: string[]
  mistakeFeedback?: string[]
  successText: string
  successConditionLabel?: string
  mascotRole?: MascotRole
  takeaway: string
  lectureAnchor?: string
  nextPrompt?: string
}

export type MissionDefinition = {
  id: string
  route: string
  title: string
  domain: MissionDomain
  mechanic: MissionMechanic
  lessonPath?: string
  difficulty: 1 | 2 | 3
  summaryTitle?: string
  summaryText?: string
  reflectionPrompt?: string
  transferTask?: string
  qualityTags?: string[]
  estimatedMinutes?: number
  mascotRole?: MascotRole
  nextMissionRoute?: string
  nextMissionLabel?: string
  dataContract?: MissionDataContract
  levels: MissionLevel[]
}

export type MissionBadge = {
  id: string
  label: string
  value: ReactNode
  tone?: 'neutral' | 'success' | 'warning' | 'danger' | 'energy' | 'target'
}
