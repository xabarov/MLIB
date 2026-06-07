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
    skillIds: ['state-machine', 'cycles', 'parity'],
    unlocks: ['matrices', 'graph-trace'],
    reviewAfterMissionIds: ['matrix-machine'],
    readinessLabel: 'Диагностика транспозиций готова',
    coverageStatus: 'diagnosed',
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
    skillIds: ['basis-images', 'linear-map-as-columns'],
    unlocks: ['determinants', 'linear-maps-kernel', 'quadratic-forms'],
    reviewAfterMissionIds: ['determinant-forge'],
    readinessLabel: 'Диагностика столбцов готова',
    coverageStatus: 'diagnosed',
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
    skillIds: ['area-scale', 'orientation', 'degeneracy'],
    unlocks: ['linear-maps-kernel', 'quadratic-forms'],
    reviewAfterMissionIds: ['kernel-hunt', 'quadratic-lens'],
    readinessLabel: 'Диагностика det готовится',
    coverageStatus: 'diagnosed',
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
    skillIds: ['homogeneous-system', 'kernel-basis', 'rank-nullity'],
    unlocks: ['quadratic-forms', 'graph-trace'],
    reviewAfterMissionIds: ['quadratic-lens', 'graph-dispatcher'],
    readinessLabel: 'Residual-диагностика готовится',
    coverageStatus: 'diagnosed',
    takeaway: 'Ядро - подпространство решений Ax = 0.',
    status: 'available',
  },
  {
    id: 'quadratic-forms',
    title: 'Квадратичные формы',
    cardLabel: 'Энергия и главные оси',
    section: 'algebra',
    lessonPaths: ['SHAD/algebra/10_Bilinear_quadratic_forms/lesson.md'],
    qaPaths: ['SHAD/algebra/10_Bilinear_quadratic_forms/qa.md'],
    prerequisites: ['matrices', 'determinants', 'linear-maps-kernel'],
    missionIds: ['quadratic-lens'],
    plannedMissionIds: ['unitary-compass'],
    skillIds: ['quadratic-form', 'signature', 'principal-axes'],
    unlocks: ['svd-pca', 'graph-trace'],
    reviewAfterMissionIds: ['determinant-forge', 'kernel-hunt'],
    readinessLabel: 'Главные оси готовятся',
    coverageStatus: 'playable',
    takeaway:
      'Симметрическая форма измеряет направления через главные оси, determinant и сигнатуру.',
    status: 'prototype',
  },
  {
    id: 'svd-pca',
    title: 'SVD и PCA',
    cardLabel: 'Круг, эллипс и данные',
    section: 'algebra',
    lessonPaths: ['SHAD/algebra/13_Complex_spaces/lesson.md'],
    prerequisites: ['quadratic-forms'],
    missionIds: ['svd-lens'],
    plannedMissionIds: ['unitary-compass', 'pca-compression-lab'],
    skillIds: ['singular-values', 'principal-components', 'low-rank'],
    unlocks: ['ml-playground'],
    reviewAfterMissionIds: ['quadratic-lens', 'feature-factory'],
    readinessLabel: 'SVD-геометрия готовится',
    coverageStatus: 'playable',
    takeaway:
      'SVD раскладывает любую матрицу на входные оси, неотрицательные растяжения и выходные оси.',
    status: 'prototype',
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
    skillIds: ['frontier', 'visited', 'trace-invariant'],
    unlocks: ['asymptotics'],
    reviewAfterMissionIds: ['substitution-workshop'],
    readinessLabel: 'Trace-эталон',
    coverageStatus: 'review-ready',
    takeaway:
      'Очередь, стек и посещенные вершины превращают обход в проверяемое состояние.',
    status: 'prototype',
  },
  {
    id: 'asymptotics',
    title: 'Асимптотика',
    cardLabel: 'Стратегия и стоимость',
    section: 'algorithms',
    lessonPaths: ['SHAD/mathematical_analysis/4_asymptotics/lesson.md'],
    prerequisites: ['graph-trace'],
    missionIds: ['asymptotic-arena'],
    plannedMissionIds: ['dp-station', 'ml-playground'],
    skillIds: ['growth-model', 'cost-comparison', 'strategy-choice'],
    unlocks: ['ml-playground'],
    reviewAfterMissionIds: ['graph-dispatcher'],
    readinessLabel: 'Strategy arena готовится',
    coverageStatus: 'playable',
    takeaway: 'Стратегию выбирают по setup, comparisons, памяти и росту на n.',
    status: 'prototype',
  },
  {
    id: 'ml-playground',
    title: 'ML-полигон',
    cardLabel: 'Train/test и метрики',
    section: 'data-analysis',
    lessonPaths: ['SHAD/Programma_dlya_postupayushhih_v_Shkolu_analiza_dannyh_3_749884e44e.md'],
    prerequisites: ['asymptotics'],
    missionIds: ['ml-playground'],
    plannedMissionIds: ['feature-factory', 'decision-tree-split'],
    skillIds: ['train-test-split', 'thresholding', 'metric-tradeoff'],
    unlocks: ['feature-factory'],
    reviewAfterMissionIds: ['asymptotic-arena'],
    readinessLabel: 'Metric-диагностика готовится',
    coverageStatus: 'playable',
    takeaway: 'Модель выбирают по честному test-контролю, а не по красивой train-метрике.',
    status: 'prototype',
  },
  {
    id: 'feature-factory',
    title: 'Фабрика признаков',
    cardLabel: 'Pipeline данных',
    section: 'data-analysis',
    lessonPaths: ['SHAD/Programma_dlya_postupayushhih_v_Shkolu_analiza_dannyh_3_749884e44e.md'],
    prerequisites: ['ml-playground'],
    missionIds: ['feature-factory'],
    plannedMissionIds: ['decision-tree-split'],
    skillIds: ['missing-values', 'feature-selection', 'leakage-control'],
    unlocks: [],
    reviewAfterMissionIds: ['ml-playground'],
    readinessLabel: 'Feature-pipeline готовится',
    coverageStatus: 'playable',
    takeaway:
      'Хороший признак появляется из явного pipeline: impute, outlier repair, leakage check и encoding.',
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
    for (const unlock of node.unlocks) {
      if (!nodeIds.has(unlock)) {
        errors.push(`${node.id}: unknown unlock ${unlock}`)
      }
    }
    for (const reviewMissionId of node.reviewAfterMissionIds ?? []) {
      if (!knownMissionIds.has(reviewMissionId)) {
        errors.push(`${node.id}: unknown review mission ${reviewMissionId}`)
      }
    }
    if (node.lessonPaths.length === 0) {
      errors.push(`${node.id}: lessonPaths must not be empty`)
    }
    if (node.skillIds.length === 0) {
      errors.push(`${node.id}: skillIds must not be empty`)
    }
  }

  return errors
}
