import type { NavSection, VizEntry } from './registryTypes'
import { missionEntries } from './missionRegistry'

const missionById = new Map(missionEntries.map((entry) => [entry.id, entry]))

function missionEntry(id: string): VizEntry {
  const entry = missionById.get(id)
  if (!entry) throw new Error(`Unknown mission entry: ${id}`)
  return entry
}

export const navSections: NavSection[] = [
  {
    id: 'algebra',
    title: 'Линейная алгебра',
    topics: [
      {
        id: 'substitutions',
        title: 'Подстановки',
        visualizations: [missionEntry('substitution-workshop')],
      },
      {
        id: 'linear-maps',
        title: 'Линейные отображения и операторы',
        visualizations: [
          missionEntry('kernel'),
          {
            id: 'projection',
            path: '/algebra/linear-maps/projection',
            title: 'Проекция на плоскость Oxy',
            kind: 'viewer',
            status: 'planned',
            meta: {
              title: 'Проекция на координатную плоскость',
              formula: String.raw`\varphi(x,y,z)=(x,y,0)`,
            },
          },
          {
            id: 'scheme',
            path: '/algebra/linear-maps/scheme',
            title: 'Схема отображения V → W',
            kind: 'viewer',
            status: 'planned',
            meta: {
              title: 'Линейное отображение',
            },
          },
          {
            id: 'two-bases',
            path: '/algebra/linear-maps/two-bases',
            title: 'Два базиса в ℝ²',
            kind: 'viewer',
            status: 'planned',
            meta: {
              title: 'Одна плоскость, два базиса',
            },
          },
        ],
      },
      {
        id: 'determinants',
        title: 'Определители',
        visualizations: [missionEntry('forge')],
      },
      {
        id: 'matrices',
        title: 'Матрицы',
        visualizations: [missionEntry('matrix-machine')],
      },
      {
        id: 'quadratic-forms',
        title: 'Квадратичные формы',
        visualizations: [missionEntry('quadratic-lens')],
      },
      {
        id: 'svd-pca',
        title: 'SVD и PCA',
        visualizations: [missionEntry('svd-lens')],
      },
    ],
  },
  {
    id: 'combinatorics',
    title: 'Комбинаторика и графы',
    topics: [
      {
        id: 'graphs',
        title: 'Графы и обходы',
        visualizations: [missionEntry('graph-dispatcher')],
      },
    ],
  },
  {
    id: 'algorithms',
    title: 'Алгоритмы',
    topics: [
      {
        id: 'asymptotics',
        title: 'Асимптотика',
        visualizations: [missionEntry('asymptotic-arena')],
      },
    ],
  },
  {
    id: 'data',
    title: 'Data',
    topics: [
      {
        id: 'ml-basics',
        title: 'ML и метрики',
        visualizations: [missionEntry('ml-playground'), missionEntry('feature-factory')],
      },
    ],
  },
]
