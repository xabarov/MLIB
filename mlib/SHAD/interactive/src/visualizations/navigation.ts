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
        id: 'complex-numbers',
        title: 'Комплексные числа',
        visualizations: [missionEntry('roots-orbit')],
      },
      {
        id: 'linear-equations',
        title: 'Линейные уравнения',
        visualizations: [missionEntry('gauss-station')],
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
        id: 'euclidean-spaces',
        title: 'Евклидовы пространства',
        visualizations: [missionEntry('orthogonal-workshop')],
      },
      {
        id: 'complex-spaces',
        title: 'Комплексные пространства',
        visualizations: [missionEntry('unitary-compass')],
      },
      {
        id: 'svd-pca',
        title: 'SVD и PCA',
        visualizations: [missionEntry('svd-lens'), missionEntry('pca-compression-lab')],
      },
      {
        id: 'eigenvalues',
        title: 'Собственные значения',
        visualizations: [missionEntry('eigen-chase')],
      },
    ],
  },
  {
    id: 'combinatorics',
    title: 'Комбинаторика и графы',
    topics: [
      {
        id: 'pascal',
        title: 'Треугольник Паскаля',
        visualizations: [missionEntry('pascal-triangle')],
      },
      {
        id: 'graphs',
        title: 'Графы и обходы',
        visualizations: [missionEntry('graph-dispatcher')],
      },
      {
        id: 'euler',
        title: 'Эйлеровы пути',
        visualizations: [missionEntry('euler-trail')],
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
      {
        id: 'heaps',
        title: 'Кучи',
        visualizations: [missionEntry('heap-forge')],
      },
      {
        id: 'dsu',
        title: 'Непересекающиеся множества',
        visualizations: [missionEntry('dsu-forest')],
      },
      {
        id: 'dynamic-programming',
        title: 'Динамическое программирование',
        visualizations: [missionEntry('dp-station')],
      },
      {
        id: 'bst',
        title: 'Деревья поиска',
        visualizations: [missionEntry('bst-quest')],
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
  {
    id: 'probability',
    title: 'Вероятность',
    topics: [
      {
        id: 'bernoulli',
        title: 'Бернулли и частоты',
        visualizations: [missionEntry('bernoulli-lab')],
      },
      {
        id: 'monte-carlo',
        title: 'Монте-Карло',
        visualizations: [missionEntry('monte-carlo')],
      },
      {
        id: 'bayes',
        title: 'Условная вероятность',
        visualizations: [missionEntry('bayes-fork')],
      },
      {
        id: 'expectation',
        title: 'Ожидание и дисперсия',
        visualizations: [missionEntry('expectation-lab')],
      },
    ],
  },
  {
    id: 'calculus',
    title: 'Анализ',
    topics: [
      {
        id: 'gradient',
        title: 'Градиент и спуск',
        visualizations: [missionEntry('gradient-slope')],
      },
      {
        id: 'taylor',
        title: 'Полином Тейлора',
        visualizations: [missionEntry('taylor-lab')],
      },
      {
        id: 'fourier',
        title: 'Ряды Фурье',
        visualizations: [missionEntry('fourier-synth')],
      },
    ],
  },
]
