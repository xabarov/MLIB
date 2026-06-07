import type { CodeTraceLine, CostMetric, GrowthPoint, StrategyOption } from '../../game/programmingTypes'

export type InputScenarioId = 'small-random' | 'large-random' | 'nearly-sorted' | 'many-lookups'
export type AlgorithmStrategyId =
  | 'linear-scan'
  | 'binary-search-after-sort'
  | 'insertion-sort'
  | 'merge-sort'
  | 'hash-index'

export type StrategyDiagnosisKind =
  | 'good-fit'
  | 'constant-wins-small-n'
  | 'quadratic-explodes'
  | 'setup-not-worth-it'
  | 'preprocessing-pays-off'
  | 'memory-tradeoff'
  | 'wrong-cost-model'

export type InputScenario = {
  id: InputScenarioId
  title: string
  n: number
  queries: number
  disorder: number
  goal: string
}

export type StrategyCost = {
  comparisons: number
  setup: number
  memory: number
  total: number
}

export type StrategyDiagnosis = {
  kind: StrategyDiagnosisKind
  message: string
  repairHint: string
  invariantOk: boolean
}

export const asymptoticScenarios: Record<InputScenarioId, InputScenario> = {
  'small-random': {
    id: 'small-random',
    title: 'Малый вход',
    n: 12,
    queries: 1,
    disorder: 0.65,
    goal: 'Выбери стратегию для одного маленького входа.',
  },
  'large-random': {
    id: 'large-random',
    title: 'Большой вход',
    n: 1200,
    queries: 1,
    disorder: 0.9,
    goal: 'Выбери стратегию, которая не взорвется на большом n.',
  },
  'nearly-sorted': {
    id: 'nearly-sorted',
    title: 'Почти отсортировано',
    n: 80,
    queries: 1,
    disorder: 0.08,
    goal: 'Используй структуру входа, а не только худший случай.',
  },
  'many-lookups': {
    id: 'many-lookups',
    title: 'Много запросов',
    n: 500,
    queries: 80,
    disorder: 0.5,
    goal: 'Реши, когда preprocessing окупается.',
  },
}

export const asymptoticStrategies: StrategyOption[] = [
  {
    id: 'linear-scan',
    label: 'Linear scan',
    complexity: 'O(n) per query',
    memoryCost: 'O(1)',
    bestFor: 'маленький n или один простой поиск',
  },
  {
    id: 'binary-search-after-sort',
    label: 'Sort + binary search',
    complexity: 'O(n log n) + q log n',
    setupCost: 'O(n log n)',
    memoryCost: 'O(1)',
    bestFor: 'много поисковых запросов без хеш-индекса',
  },
  {
    id: 'insertion-sort',
    label: 'Insertion sort',
    complexity: 'O(n + inv)',
    memoryCost: 'O(1)',
    bestFor: 'малый или почти отсортированный вход',
  },
  {
    id: 'merge-sort',
    label: 'Merge sort',
    complexity: 'O(n log n)',
    memoryCost: 'O(n)',
    bestFor: 'большой случайный вход со стабильным ростом',
  },
  {
    id: 'hash-index',
    label: 'Hash index',
    complexity: 'O(n) + O(q)',
    setupCost: 'O(n)',
    memoryCost: 'O(n)',
    bestFor: 'много membership-запросов',
  },
]

export function log2ceil(n: number): number {
  return Math.max(1, Math.ceil(Math.log2(Math.max(2, n))))
}

export function estimateCost(strategyId: AlgorithmStrategyId, scenario: InputScenario): StrategyCost {
  const { n, queries, disorder } = scenario
  if (strategyId === 'linear-scan') {
    const comparisons = Math.ceil((n * queries) / 2)
    return { comparisons, setup: 0, memory: 1, total: comparisons }
  }
  if (strategyId === 'binary-search-after-sort') {
    const setup = Math.ceil(n * log2ceil(n))
    const comparisons = queries * log2ceil(n)
    return { comparisons, setup, memory: 1, total: setup + comparisons }
  }
  if (strategyId === 'insertion-sort') {
    const setup = Math.ceil(n + (disorder * n * n) / 2)
    return { comparisons: setup, setup: 0, memory: 1, total: setup }
  }
  if (strategyId === 'merge-sort') {
    const comparisons = Math.ceil(n * log2ceil(n))
    return { comparisons, setup: 0, memory: n, total: comparisons }
  }
  const setup = n
  const comparisons = queries
  return { comparisons, setup, memory: n, total: setup + comparisons }
}

export function bestStrategyForScenario(scenario: InputScenario): AlgorithmStrategyId {
  const allowed: AlgorithmStrategyId[] =
    scenario.id === 'many-lookups'
      ? ['linear-scan', 'binary-search-after-sort', 'hash-index']
      : scenario.id === 'nearly-sorted'
        ? ['insertion-sort', 'merge-sort', 'binary-search-after-sort']
        : scenario.id === 'large-random'
          ? ['insertion-sort', 'merge-sort', 'binary-search-after-sort']
          : ['linear-scan', 'insertion-sort', 'merge-sort', 'binary-search-after-sort']
  return allowed.reduce((best, strategy) =>
    estimateCost(strategy, scenario).total < estimateCost(best, scenario).total ? strategy : best,
  )
}

export function diagnoseStrategyChoice(
  strategyId: AlgorithmStrategyId,
  scenario: InputScenario,
): StrategyDiagnosis {
  const best = bestStrategyForScenario(scenario)
  if (strategyId === best) {
    if (scenario.id === 'small-random') {
      return {
        kind: 'constant-wins-small-n',
        message: 'Хороший выбор: на маленьком n простая стратегия выигрывает без лишнего setup.',
        repairHint: 'Запомни: O-нотация не отменяет константы и стоимость подготовки.',
        invariantOk: true,
      }
    }
    if (scenario.id === 'many-lookups') {
      return {
        kind: 'preprocessing-pays-off',
        message: 'Индекс окупился: setup один раз, а запросов много.',
        repairHint: 'Сравни setup + q с q·n у линейного поиска.',
        invariantOk: true,
      }
    }
    return {
      kind: 'good-fit',
      message: 'Стратегия совпала с cost model этого входа.',
      repairHint: 'Переходи дальше и проверь, сохранится ли выбор при другом n.',
      invariantOk: true,
    }
  }

  if (scenario.id === 'large-random' && strategyId === 'insertion-sort') {
    return {
      kind: 'quadratic-explodes',
      message: 'O(n²) взрывается на большом случайном входе.',
      repairHint: 'Выбери стратегию с ростом O(n log n).',
      invariantOk: false,
    }
  }
  if (scenario.id === 'small-random' && strategyId !== 'linear-scan') {
    return {
      kind: 'setup-not-worth-it',
      message: 'Подготовка тяжелее самой задачи: для одного маленького входа setup не окупился.',
      repairHint: 'Попробуй простую стратегию без предварительной сортировки или индекса.',
      invariantOk: false,
    }
  }
  if (scenario.id === 'many-lookups' && strategyId === 'linear-scan') {
    return {
      kind: 'preprocessing-pays-off',
      message: 'Один линейный поиск дешев, но 80 запросов превращают его в q·n.',
      repairHint: 'Построй индекс: setup окупится множеством запросов.',
      invariantOk: false,
    }
  }
  if (scenario.id === 'nearly-sorted' && strategyId === 'merge-sort') {
    return {
      kind: 'memory-tradeoff',
      message: 'Merge sort надежен, но игнорирует почти готовую структуру входа и требует память O(n).',
      repairHint: 'Для почти отсортированного массива попробуй insertion sort.',
      invariantOk: false,
    }
  }
  return {
    kind: 'wrong-cost-model',
    message: 'Выбор не совпал с cost model уровня.',
    repairHint: 'Сравни total cost, setup и число запросов.',
    invariantOk: false,
  }
}

export function growthPoints(strategyId: AlgorithmStrategyId, scenario: InputScenario): GrowthPoint[] {
  return [8, 32, 128, 512, 2048].map((n) => ({
    n,
    cost: estimateCost(strategyId, { ...scenario, n }).total,
  }))
}

export function metricsForStrategy(
  strategyId: AlgorithmStrategyId,
  scenario: InputScenario,
): CostMetric[] {
  const cost = estimateCost(strategyId, scenario)
  return [
    { id: 'comparisons', label: 'cmp', value: cost.comparisons, tone: 'energy' },
    { id: 'setup', label: 'setup', value: cost.setup, tone: cost.setup > 0 ? 'warning' : 'neutral' },
    { id: 'memory', label: 'mem', value: cost.memory, tone: cost.memory > 1 ? 'target' : 'neutral' },
  ]
}

export function codeTraceForStrategy(strategyId: AlgorithmStrategyId): CodeTraceLine[] {
  const lines: Record<AlgorithmStrategyId, string[]> = {
    'linear-scan': ['for x in array:', '  compare x with target', '  stop when found'],
    'binary-search-after-sort': ['sort(array)', 'while low <= high:', '  cut search interval in half'],
    'insertion-sort': ['for each item:', '  shift larger prefix right', '  insert item into gap'],
    'merge-sort': ['split array', 'sort halves recursively', 'merge two sorted halves'],
    'hash-index': ['build hash table', 'for each query:', '  check bucket in O(1)'],
  }
  return lines[strategyId].map((text, index) => ({
    id: `${strategyId}-${index}`,
    text,
    active: index === 0,
    executed: index < 2,
    invariantOk: true,
  }))
}
