import { lazy, type ComponentType, type LazyExoticComponent } from 'react'
import type { MissionDefinition } from '../game/missionTypes'
import { determinantForgeMission, kernelHuntMission } from '../game/missions'

const DeterminantForgeMission = lazy(() =>
  import('./determinants/DeterminantForgeMission').then((module) => ({
    default: module.DeterminantForgeMission,
  })),
)

const KernelHuntMission = lazy(() =>
  import('./linear-maps/KernelHuntMission').then((module) => ({
    default: module.KernelHuntMission,
  })),
)

export type VizMeta = {
  title: string
  formula?: string
  description?: string
  note?: string
  sceneTitle?: string
}

export type VizComponent = ComponentType | LazyExoticComponent<ComponentType>

export type VizEntry = {
  id: string
  path: string
  title: string
  available: boolean
  kind?: 'viewer' | 'mission' | 'prototype'
  difficulty?: 1 | 2 | 3
  lessonPath?: string
  mission?: MissionDefinition
  status?: 'available' | 'prototype' | 'planned'
  component?: VizComponent
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
            title: 'Охота за ядром',
            available: true,
            kind: 'mission',
            status: 'available',
            difficulty: 1,
            lessonPath: kernelHuntMission.lessonPath,
            mission: kernelHuntMission,
            component: KernelHuntMission,
            meta: {
              title: 'Охота за ядром',
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
      {
        id: 'determinants',
        title: 'Определители',
        visualizations: [
          {
            id: 'forge',
            path: '/algebra/determinants/forge',
            title: 'Кузница определителя',
            available: true,
            kind: 'mission',
            status: 'prototype',
            difficulty: 1,
            lessonPath: determinantForgeMission.lessonPath,
            mission: determinantForgeMission,
            component: DeterminantForgeMission,
            meta: {
              title: 'Кузница определителя',
              formula: String.raw`\det\begin{pmatrix}a&b\\c&d\end{pmatrix}=ad-bc`,
              description:
                'Два столбца матрицы задают параллелограмм: площадь, ориентация и обратимость видны через определитель.',
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
