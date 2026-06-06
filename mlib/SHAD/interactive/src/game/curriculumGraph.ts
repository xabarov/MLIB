import type { CurriculumNode } from './curriculumTypes'

export const curriculumGraph: CurriculumNode[] = [
  {
    id: 'substitutions',
    title: 'Подстановки',
    cardLabel: 'Состояния и операции',
    section: 'combinatorics',
    lessonPaths: ['SHAD/algebra/1_Substitutions/lesson.md'],
    qaPaths: ['SHAD/algebra/1_Substitutions/qa.md'],
    prerequisites: [],
    missionIds: ['substitution-workshop'],
    takeaway: 'Перестановка меняется транспозициями, а циклы и знак остаются видимыми.',
    status: 'prototype',
  },
  {
    id: 'matrices',
    title: 'Матрицы',
    cardLabel: 'Матрица как действие',
    section: 'algebra',
    lessonPaths: ['SHAD/algebra/6_Matrices/lesson.md'],
    prerequisites: ['substitutions'],
    missionIds: ['matrix-machine'],
    takeaway: 'Столбцы матрицы - это образы базисных векторов.',
    status: 'prototype',
  },
  {
    id: 'determinants',
    title: 'Определители',
    cardLabel: 'Площадь и ориентация',
    section: 'algebra',
    lessonPaths: ['SHAD/algebra/5_Det/lesson.md'],
    prerequisites: ['matrices'],
    missionIds: ['determinant-forge'],
    takeaway: 'Определитель хранит масштаб площади, знак и вырожденность.',
    status: 'prototype',
  },
  {
    id: 'linear-maps-kernel',
    title: 'Линейные отображения и ядро',
    cardLabel: 'Схлопнутые направления',
    section: 'algebra',
    lessonPaths: ['SHAD/algebra/8_Linear_maps/lesson.md'],
    prerequisites: ['matrices', 'determinants'],
    missionIds: ['kernel-hunt'],
    takeaway: 'Ядро - подпространство решений Ax = 0.',
    status: 'available',
  },
  {
    id: 'graph-trace',
    title: 'Графовые обходы',
    cardLabel: 'Trace алгоритма',
    section: 'algorithms',
    lessonPaths: ['SHAD/combinatorics/4. Graphs/lesson.md'],
    qaPaths: ['SHAD/combinatorics/4. Graphs/qa.md'],
    prerequisites: ['substitutions'],
    missionIds: ['graph-dispatcher'],
    plannedMissionIds: ['graph-bridges', 'shortest-paths'],
    takeaway:
      'Очередь, стек и посещенные вершины превращают обход в проверяемое состояние.',
    status: 'prototype',
  },
]

export function validateCurriculumGraph(
  nodes: CurriculumNode[],
  knownMissionIds: Set<string>,
): string[] {
  const errors: string[] = []
  const nodeIds = new Set(nodes.map((node) => node.id))

  for (const node of nodes) {
    for (const prerequisite of node.prerequisites) {
      if (!nodeIds.has(prerequisite)) {
        errors.push(`${node.id}: unknown prerequisite ${prerequisite}`)
      }
    }
    for (const missionId of node.missionIds) {
      if (!knownMissionIds.has(missionId)) {
        errors.push(`${node.id}: unknown mission ${missionId}`)
      }
    }
    if (node.lessonPaths.length === 0) {
      errors.push(`${node.id}: lessonPaths must not be empty`)
    }
  }

  return errors
}
