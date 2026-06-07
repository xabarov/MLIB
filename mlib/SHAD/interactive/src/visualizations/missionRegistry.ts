import {
  asymptoticArenaMission,
  determinantForgeMission,
  graphDispatcherMission,
  kernelHuntMission,
  matrixMachineMission,
  substitutionWorkshopMission,
} from '../game/missions'
import type { VizEntry } from './registryTypes'
import {
  AsymptoticArenaMission,
  DeterminantForgeMission,
  GraphDispatcherMission,
  KernelHuntMission,
  MatrixMachineMission,
  SubstitutionWorkshopMission,
} from './routeLoaders'

export const missionEntries: VizEntry[] = [
  {
    id: 'kernel',
    path: '/algebra/linear-maps/kernel',
    title: 'Охота за ядром',
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
      description: 'Ядро всегда является подпространством: здесь это прямая через начало.',
      note:
        'Плоскость на схеме — вспомогательный фрагмент, напоминающий о структуре уравнений Ax=0 (само ядро в примере — прямая, а не эта плоскость).',
    },
  },
  {
    id: 'forge',
    path: '/algebra/determinants/forge',
    title: 'Кузница определителя',
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
  {
    id: 'matrix-machine',
    path: '/algebra/matrices/machine',
    title: 'Матрица как машина',
    kind: 'mission',
    status: 'prototype',
    difficulty: 1,
    lessonPath: matrixMachineMission.lessonPath,
    mission: matrixMachineMission,
    component: MatrixMachineMission,
    meta: {
      title: 'Матрица как машина',
      formula: String.raw`A=[Ae_1\ Ae_2]`,
      description:
        'Матрица задается образами базисных векторов: эти образы становятся ее столбцами.',
    },
  },
  {
    id: 'substitution-workshop',
    path: '/algebra/substitutions/workshop',
    title: 'Цех перестановок',
    kind: 'mission',
    status: 'prototype',
    difficulty: 1,
    lessonPath: substitutionWorkshopMission.lessonPath,
    mission: substitutionWorkshopMission,
    component: SubstitutionWorkshopMission,
    meta: {
      title: 'Цех перестановок',
      formula: String.raw`\operatorname{sgn}(\sigma)=(-1)^{\mathrm{inv}(\sigma)}`,
      description:
        'Перестановка меняется транспозициями: циклы, знак и число ходов становятся игровым состоянием.',
    },
  },
  {
    id: 'graph-dispatcher',
    path: '/combinatorics/graphs/dispatcher',
    title: 'Графовый диспетчер',
    kind: 'mission',
    status: 'prototype',
    difficulty: 2,
    lessonPath: graphDispatcherMission.lessonPath,
    mission: graphDispatcherMission,
    component: GraphDispatcherMission,
    meta: {
      title: 'Графовый диспетчер',
      formula: String.raw`\mathrm{frontier}\rightarrow\mathrm{current}\rightarrow\mathrm{visited}`,
      description:
        'BFS и DFS становятся trace-состояниями: очередь, стек, посещенные вершины и стоимость шагов.',
    },
  },
  {
    id: 'asymptotic-arena',
    path: '/algorithms/asymptotics/arena',
    title: 'Арена асимптотик',
    kind: 'mission',
    status: 'prototype',
    difficulty: 2,
    lessonPath: asymptoticArenaMission.lessonPath,
    mission: asymptoticArenaMission,
    component: AsymptoticArenaMission,
    meta: {
      title: 'Арена асимптотик',
      formula: String.raw`\mathrm{total}=\mathrm{setup}+\mathrm{comparisons}`,
      description:
        'Стратегии сравниваются по модели стоимости: рост, setup, память и число запросов становятся игровыми условиями.',
    },
  },
]
