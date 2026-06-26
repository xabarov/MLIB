import type { ComponentType, LazyExoticComponent } from 'react'
import type { MissionDefinition } from '../game/missionTypes'

export type VizMeta = {
  title: string
  formula?: string
  description?: string
  note?: string
  sceneTitle?: string
}

export type VizComponent = ComponentType | LazyExoticComponent<ComponentType>

type VizBase = {
  id: string
  path: string
  title: string
  kind: 'viewer' | 'mission' | 'prototype'
  difficulty?: 1 | 2 | 3
  lessonPath?: string
  mission?: MissionDefinition
  meta: VizMeta
}

export type ReadyVizEntry = VizBase & {
  status: 'available' | 'prototype'
  component: VizComponent
}

export type PlannedVizEntry = VizBase & {
  status: 'planned'
  component?: never
}

export type VizEntry = ReadyVizEntry | PlannedVizEntry

export type NavTopic = {
  id: string
  title: string
  visualizations: VizEntry[]
}

export type NavSection = {
  id: string
  title: string
  topics: NavTopic[]
}
