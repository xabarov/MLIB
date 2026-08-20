export type {
  NavSection,
  NavTopic,
  PlannedVizEntry,
  ReadyVizEntry,
  VizComponent,
  VizEntry,
  VizMeta,
} from './registryTypes'
export { navSections } from './navigation'
export { missionEntries } from './missionRegistry'

import { navSections } from './navigation'
import type { VizEntry } from './registryTypes'

export function findVizByPath(path: string): VizEntry | undefined {
  for (const section of navSections) {
    for (const topic of section.topics) {
      const viz = topic.visualizations.find((entry) => entry.path === path)
      if (viz) return viz
    }
  }
  return undefined
}

export function allVizPaths(): string[] {
  return navSections.flatMap((section) =>
    section.topics.flatMap((topic) => topic.visualizations.map((entry) => entry.path)),
  )
}
