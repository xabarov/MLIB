# SHAD Interactive: programming/data primitives plan

Этот документ готовит следующий содержательный слой после hardening текущих
миссий: algorithms, programming и data-analysis игры. Цель - не начинать каждую
новую миссию с уникального UI, а собрать общий набор проверяемых primitives.

## Целевая первая миссия

Рекомендуемый первый кандидат: **Арена асимптотик**.

Почему:

- продолжает `Graph Dispatcher` и его trace-язык;
- требует стоимости, стратегии и сравнения входов;
- не требует тяжелых raster assets;
- хорошо проверяет будущие programming primitives.

Альтернатива: **ML-полигон**, если приоритет сместится на анализ данных.

## Shared Types

Минимальные типы:

```ts
type CostMetric = {
  id: string
  label: string
  value: number | string
  tone?: 'neutral' | 'success' | 'warning' | 'danger' | 'energy' | 'target'
}

type CodeTraceLine = {
  id: string
  text: string
  active?: boolean
  executed?: boolean
  invariantOk?: boolean
}

type DatasetRow = {
  id: string
  values: Record<string, string | number | null>
  flags?: string[]
}

type ModelMetric = {
  id: string
  train: number
  test: number
  warning?: string
}
```

## CodeTracePanel

Назначение: пошаговые алгоритмы, псевдокод, инварианты и стоимость.

Переиспользовать:

- `TracePanel`;
- `TraceStepList`;
- `InvariantCheck`;
- `StateToken`.

Добавить:

- список строк псевдокода;
- active line;
- переменные;
- cost metrics;
- типовую ошибку как invariant break.

Первое применение:

- BFS/DFS/toposort;
- сортировки;
- binary search;
- DP порядок вычислений.

## DataTableMini

Назначение: маленькие датасеты 10-30 строк, которые можно чистить руками.

Нужно:

- compact table;
- row/column flags;
- выделение пропусков, выбросов, leakage;
- действие пользователя: mark/drop/impute/encode;
- проверка до/после.

Первое применение:

- Фабрика признаков;
- ML-полигон;
- train/test leakage puzzle.

## MetricBoard

Назначение: train/test, качество, переобучение, trade-offs.

Нужно:

- train/test split;
- accuracy/F1/loss;
- warning при расхождении train/test;
- short takeaway после изменения параметра.

Первое применение:

- ML-полигон;
- регуляризация;
- threshold tuning.

## StrategyCompare

Назначение: выбор алгоритма или стратегии и сравнение стоимости.

Нужно:

- 2-4 стратегии;
- входы разных размеров;
- cost curve или таблица;
- feedback: "константа выиграла здесь, асимптотика выиграла дальше".

Первое применение:

- Арена асимптотик;
- сортировки;
- структуры данных.

## Implementation Order

1. `CodeTracePanel` как расширение существующего trace layer.
2. `StrategyCompare` для `Арены асимптотик`.
3. `MetricBoard`.
4. `DataTableMini`.

## Quality Gate

Каждый primitive должен иметь:

- typed props;
- пример использования в одной миссии или dev-only route;
- unit tests для model;
- smoke selector;
- mobile screenshot без горизонтального overflow.
