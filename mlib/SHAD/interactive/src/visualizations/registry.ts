import type { ComponentType } from 'react'
import { KernelLineViz } from './linear-maps/KernelLineViz'

export type VizMeta = {
  title: string
  formula?: string
  description?: string
  note?: string
  sceneTitle?: string
}

export type VizEntry = {
  id: string
  path: string
  title: string
  available: boolean
  component?: ComponentType
  meta: VizMeta
}

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

export const navSections: NavSection[] = [
  {
    id: 'algebra',
    title: 'Линейная алгебра',
    topics: [
      {
        id: 'linear-maps',
        title: 'Линейные отображения и операторы',
        visualizations: [
          {
            id: 'kernel',
            path: '/algebra/linear-maps/kernel',
            title: 'Ядро: прямая span{(-1,1,-1)}',
            available: true,
            component: KernelLineViz,
            meta: {
              title: 'Геометрия ядра линейного отображения',
              sceneTitle: 'Геометрия ядра линейного отображения',
              formula: String.raw`\ker\varphi=\mathrm{span}\{(-1,1,-1)\}`,
              description:
                'Ядро всегда является подпространством: здесь это прямая через начало.',
              note:
                'Плоскость на схеме — вспомогательный фрагмент, напоминающий о структуре уравнений Ax=0 (само ядро в примере — прямая, а не эта плоскость).',
            },
          },
          {
            id: 'projection',
            path: '/algebra/linear-maps/projection',
            title: 'Проекция на плоскость Oxy',
            available: false,
            meta: {
              title: 'Проекция на координатную плоскость',
              formula: String.raw`\varphi(x,y,z)=(x,y,0)`,
            },
          },
          {
            id: 'scheme',
            path: '/algebra/linear-maps/scheme',
            title: 'Схема отображения V → W',
            available: false,
            meta: {
              title: 'Линейное отображение',
            },
          },
          {
            id: 'two-bases',
            path: '/algebra/linear-maps/two-bases',
            title: 'Два базиса в ℝ²',
            available: false,
            meta: {
              title: 'Одна плоскость, два базиса',
            },
          },
        ],
      },
    ],
  },
]

export function findVizByPath(path: string): VizEntry | undefined {
  for (const section of navSections) {
    for (const topic of section.topics) {
      const viz = topic.visualizations.find((v) => v.path === path)
      if (viz) return viz
    }
  }
  return undefined
}

export function allVizPaths(): string[] {
  return navSections.flatMap((s) =>
    s.topics.flatMap((t) => t.visualizations.map((v) => v.path)),
  )
}
