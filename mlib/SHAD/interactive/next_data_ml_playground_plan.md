# SHAD Interactive: план этапа "ML-полигон и data primitives"

Этот этап начинается после `Арены асимптотик`. Приложение уже умеет:

- вести пользователя по course map;
- запускать playable missions через `MissionShell`;
- проверять happy path и mistake path в Playwright;
- показывать алгоритмическую стоимость через `CodeTracePanel` и
  `StrategyCompare`;
- lazy-load миссии отдельными chunks.

Следующий шаг: **сделать первый data-analysis / ML vertical slice** и вынести
из него переиспользуемые primitives для будущих миссий по данным.

Основная миссия этапа: **ML-полигон**.

## Статус 2026-06-07

Выполнено в текущей итерации:

- добавлены `dataTypes.ts`, `DataTableMini`, `MetricBoard` и `DecisionPlane`;
- реализован model layer `mlPlaygroundModel.ts` с fixed toy datasets,
  threshold predictions, confusion counts, accuracy, precision, recall and F1;
- добавлена playable mission `ML-полигон` с 4 уровнями:
  `simple-threshold`, `test-control`, `f1-threshold`, `leakage-trap`;
- миссия подключена в lazy route, registry, navigation и curriculum graph;
- course map получила data-analysis node после `Арены асимптотик`;
- Playwright smoke расширен route screenshot, mistake path и happy path для
  `ML-полигона`;
- build сохраняет mission chunk маленьким: после следующего split
  `MlPlaygroundMission` около 16.45 kB raw / 5.68 kB gzip.

Следующий data/ML этап выполнен отдельным планом:

- `Feature Factory` добавлена на тех же primitives:
  [next_feature_factory_plan.md](next_feature_factory_plan.md);
- завести живые материалы в `SHAD/data analysis` и подключить `lessonPath`;
- добавить state screenshots для leakage warning и final success, если они
  понадобятся для визуального regression review.

## Почему именно ML-полигон

`ML-полигон` лучше всего проверяет новую часть системы:

- переводит приложение из "математической мастерской" в работу с данными;
- использует уже заложенные `MissionDomain = 'data-analysis'` и
  `MissionMechanic = 'model-arena'`;
- заставляет добавить `MetricBoard` и `DataTableMini`, а не рисовать очередную
  специальную сцену;
- дает понятный игровой конфликт: улучшить train-метрику легко, а сохранить
  test-метрику сложнее;
- готовит основу для feature engineering, leakage puzzles, decision trees,
  clustering и ranking metrics;
- не требует backend, real ML libraries или больших datasets.

Важно: это должна быть не "панель с метриками", а короткая игра. Пользователь
двигает порог или простую границу решения, видит ошибки на train/test и
получает диагностику: underfit, overfit, leakage, bad threshold или balanced
choice.

## Текущее основание

Уже есть:

- `MissionShell`, `MissionSummary`, `MissionReflection`, `MascotCoach`;
- `MetricBadge`, `InvariantBadge`, `RewardMeter`;
- `programmingTypes.ts` с первыми cost/trace/strategy типами;
- `courseMap.ts`, `curriculumGraph.ts`, lazy `routeLoaders.ts`;
- фильтр `Data` в course map уже существует как пользовательская категория;
- smoke script покрывает route screenshots, happy paths и typical mistakes.

Не хватает:

- data-specific shared types;
- compact dataset table;
- metric board with train/test split;
- decision boundary / threshold playground;
- model diagnosis layer;
- первой `data-analysis` mission в registry/navigation/curriculum.

## UI/UX оценка перед этапом

Текущий shell хорошо работает для геометрии и trace-миссий, но data/ML миссии
легко превращаются в сухой dashboard. Этого надо избежать.

Что оставить:

- верхняя цель уровня и badges;
- короткие уровни с unlock progression;
- Меби как реакция на инвариант/ошибку;
- route-level screenshots desktop/mobile.

Что адаптировать:

- центральная сцена должна быть не таблицей во весь экран, а **игровым полем
  данных**: точки, порог, ошибки и sample cards;
- `DataTableMini` должен быть compact support panel, а не главный интерфейс;
- `MetricBoard` должен показывать только 3-5 ключевых чисел, без "ML dashboard"
  перегруза;
- mobile layout должен складываться в порядок:
  1. цель и badges;
  2. decision playground;
  3. metric board;
  4. sample table;
  5. mission controls.

Визуальное направление: **лаборатория контрольных примеров**. Не темная
аналитическая BI-панель, а светлая мастерская: точки как физические образцы,
граница решения как подвижная линейка, ошибки как красные/оранжевые маркеры.
Меби в этой миссии играет роль `data-point` или `error-marker`.

## Product Slice

### Игровой сюжет

Игрок получает маленький двумерный dataset:

- 14-24 точки;
- две числовые features;
- binary label;
- явное разделение train/test;
- несколько точек около границы;
- один шумный/outlier пример;
- optional leakage flag на позднем уровне.

Действие игрока:

- двигать threshold или простую линейную границу;
- переключать feature;
- включать/выключать один подозрительный признак;
- смотреть, какие точки ошибочно классифицированы;
- выбирать модель, которая лучше обобщает, а не только запоминает train.

### Уровни миссии

1. **Поймай простой порог**
   - Двигать threshold по одному признаку.
   - Условие успеха: train accuracy >= заданного уровня.
   - Ошибка: threshold стоит с неправильной стороны облака.

2. **Не обмани test**
   - Появляется test split.
   - Условие успеха: test accuracy/F1 не хуже порога.
   - Ошибка: train хорош, test просел.

3. **Порог против F1**
   - Dataset несбалансирован.
   - Условие успеха: выбрать threshold с приемлемым precision/recall trade-off.
   - Ошибка: accuracy выглядит хорошо, но recall класса 1 плохой.

4. **Поймай leakage**
   - В `DataTableMini` появляется подозрительная колонка.
   - Условие успеха: отключить leakage feature и сохранить честную test-метрику.
   - Ошибка: "идеальная" train-метрика не считается победой.

5. **Стабильная граница**
   - Простая линейная граница с ручками angle/intercept.
   - Условие успеха: balanced score на train/test.
   - Итог: пользователь видит, что модель оценивают по обобщению.

Если этап нужно сделать компактнее, первую реализацию можно ограничить 4
уровнями и оставить `Стабильную границу` на следующий pass.

### Обучающий смысл

После миссии пользователь должен унести:

- train metric не равна качеству модели;
- test split нужен как контроль обобщения;
- threshold меняет precision/recall;
- accuracy может обмануть на несбалансированных данных;
- leakage дает красивую, но нечестную метрику;
- простая модель с честным split лучше магической идеальной подгонки.

## P0. Data Types

Файл-кандидат:

- `src/game/dataTypes.ts`.

Типы:

```ts
export type DatasetSplit = 'train' | 'test'

export type DatasetRow = {
  id: string
  split: DatasetSplit
  label: 0 | 1
  prediction?: 0 | 1
  values: Record<string, number | string | null>
  flags?: Array<'outlier' | 'missing' | 'leakage' | 'misclassified'>
}

export type ModelMetric = {
  id: string
  label: string
  train: number
  test: number
  format?: 'percent' | 'number'
  warning?: string
}

export type ConfusionCounts = {
  tp: number
  fp: number
  tn: number
  fn: number
}

export type ThresholdModel = {
  featureId: string
  threshold: number
  direction: 'gte' | 'lt'
}
```

Решение: не смешивать эти типы с `programmingTypes.ts`, потому что data/ML
объекты быстро начнут жить отдельной жизнью.

Готово, когда типы используются и в model layer, и в UI primitives.

## P0. DataTableMini

Файл:

- `src/game/components/data/DataTableMini.tsx`.

Назначение: compact table for 10-30 rows, not spreadsheet.

Props:

- `rows: DatasetRow[]`;
- `columns`;
- `selectedRowId?`;
- `onRowSelect?`;
- `onToggleFlag?`;
- `highlightMode: 'errors' | 'leakage' | 'split'`;
- `maxRowsCollapsed?`.

UI:

- sticky header only inside the component;
- row badges: train/test, y, prediction;
- flags as small icons/tokens;
- misclassified rows highlighted;
- on mobile: card-like rows, not squeezed table;
- no nested heavy cards.

Готово, когда можно выбрать точку в таблице и увидеть ее на playground.

## P0. MetricBoard

Файл:

- `src/game/components/data/MetricBoard.tsx`.

Назначение: train/test metrics and warning state.

Props:

- `metrics: ModelMetric[]`;
- `confusionTrain?: ConfusionCounts`;
- `confusionTest?: ConfusionCounts`;
- `primaryMetricId`;
- `diagnosis`.

UI:

- 3-5 metric cells maximum;
- train/test shown side by side;
- gap warning if train high and test low;
- mini confusion counts as 2x2 compact grid;
- strong color only for actionable warning/success.

Готово, когда user can see "train looks good, test is worse" in one glance.

## P0. Decision Playground

Файлы:

- `src/game/components/data/DecisionPlane.tsx`;
- optional `src/game/components/data/ThresholdControl.tsx`.

Назначение: главное игровое поле.

UI:

- scatter plot with train/test marker style;
- color by true label;
- outline or ring for misclassified points;
- draggable threshold line or slider fallback;
- selected row sync with `DataTableMini`;
- Mebi marker can sit near the worst error or current threshold.

Технически:

- начать с SVG, не добавлять chart library;
- deterministic coordinate scaling;
- pointer drag for desktop;
- range/input fallback for mobile;
- no canvas until dataset grows.

Готово, когда threshold movement immediately updates predictions and metrics.

## P0. Model Layer

Папка:

- `src/visualizations/ml-playground/`.

Файлы:

- `mlPlaygroundModel.ts`;
- `mlPlaygroundModel.test.ts`;
- `MlPlaygroundMission.tsx`.

Model functions:

- `predictThreshold(row, model)`;
- `applyModel(rows, model)`;
- `confusionCounts(rows)`;
- `accuracy(rows)`;
- `precisionRecallF1(rows)`;
- `trainTestMetrics(rows)`;
- `diagnoseModel(levelId, rows, model, toggles)`.

Diagnosis kinds:

- `good-fit`;
- `bad-threshold`;
- `train-test-gap`;
- `accuracy-trap`;
- `leakage-used`;
- `underfit`;
- `wrong-feature`.

Unit tests:

- metrics on known tiny dataset;
- precision/recall/F1 edge cases with zero division;
- leakage diagnosis beats raw high accuracy;
- threshold direction matters;
- recommended level solutions pass.

## P0. Mission Definition

Mission id:

- `ml-playground`.

Route:

- `/data/ml/playground`.

Definition:

- `domain: 'data-analysis'`;
- `mechanic: 'model-arena'`;
- `difficulty: 2`;
- `mascotRole: 'data-point'`;
- `lessonPath`: пока не указывать, потому что `SHAD/data analysis` пустой.
  Вместо этого добавить `plannedLessonPath` только в plan/docs. Когда появится
  живая лекция, подключить реальный `lessonPath`.

Quality tags:

- `model-tested`;
- `train-test-split`;
- `metric-diagnostics`;
- `data-table`;
- `mistake-path`.

Course map:

- добавить curriculum node `ml-playground`;
- section: `data`;
- prerequisites: `asymptotics`;
- missionIds: `['ml-playground']`;
- skillIds: `['train-test-split', 'thresholding', 'metric-tradeoff']`;
- reviewAfterMissionIds: `['asymptotic-arena']`;
- status: `prototype`;
- coverageStatus: `playable` after smoke.

Navigation:

- добавить section `data`;
- topic `ml-basics`;
- entry `ML-полигон`.

## P1. Gameplay and Copy

Тон:

- короткие команды;
- no hidden math jargon before action;
- after action, name the concept precisely.

Примеры сообщений:

- idle: "Двигай границу. Я подсвечу ошибки на train и test."
- warning train/test: "Train выглядит красиво, но test уже спорит."
- warning leakage: "Этот признак слишком знает ответ. Похоже на утечку."
- success threshold: "Порог не идеален, но честно обобщает."
- success final: "Модель выбрана по test-контролю, а не по самообману."

Уровневые takeaways должны быть достаточно короткими, чтобы они помещались в
`MissionTakeaway` без превращения sidebar в конспект.

## P1. UI/UX Polish

Проверить:

- no horizontal overflow at 390x844;
- threshold line remains draggable/tappable;
- table rows are readable on mobile;
- metric board does not dominate scene;
- success/warning colors are distinguishable without relying only on color;
- text in buttons does not truncate important concept words.

Особый риск: `MissionShell` сейчас оптимален для геометрии и trace. Для
data/ML может понадобиться prop:

- `sceneViewportClassName`;
- `sidebarPriority?: 'controls-first' | 'feedback-first'`;
- maybe `wideScene?: boolean` later.

Не делать это заранее, только если ML mission реально покажет проблему.

## P1. Smoke and Screenshots

Расширить `scripts/smoke_playwright.py`:

- route screenshot:
  - `ml-playground-desktop`;
  - `ml-playground-mobile`;
- mistake path:
  - выбрать threshold с train/test gap;
  - проверить warning diagnosis;
  - починить threshold;
- happy path:
  - пройти все уровни;
  - проверить final reflection.

Дополнительно полезны state screenshots:

- initial threshold;
- train/test warning;
- leakage warning;
- final success.

## P1. Docs and Links

Обновить:

- `gameplay_roadmap.md`;
- `programming_data_primitives_plan.md`;
- `performance_budget.md`;
- `mission_authoring_guide.md`, если появится новый обязательный data primitive
  checklist.

Не добавлять ссылки из лекций, пока нет живой data-analysis лекции. Можно
создать отдельную будущую заметку:

- `SHAD/data analysis/README.md` or plan-only entry;
- но не подменять учебный материал интерактивом.

## P2. Optional Probability Bridge

Если во время реализации станет очевидно, что ML-полигон слишком рано вводит
много ML-слов, можно добавить маленький probability bridge вместо пятого уровня:

- `Вероятностный стол`: выбирать событие в sample space и сравнивать empirical
  frequency with probability;
- reuse `DataTableMini` as outcome table;
- use `MetricBoard` as frequency/error board.

Но это fallback, а не основной путь. Главная цель этапа - data/ML primitives.

## Implementation Order

### Итерация 1: model and types

1. Создать `dataTypes.ts`.
2. Создать fixed toy dataset.
3. Реализовать model functions.
4. Покрыть metrics and diagnosis unit tests.

### Итерация 2: data primitives

1. Добавить `DataTableMini`.
2. Добавить `MetricBoard`.
3. Добавить `DecisionPlane`.
4. Сделать маленький internal example through mission scene, не отдельный route.

### Итерация 3: mission

1. Создать `MlPlaygroundMission.tsx`.
2. Подключить `MissionShell`.
3. Добавить 4 уровня.
4. Настроить feedback, mascot states, badges.

### Итерация 4: registry and curriculum

1. Добавить mission definition.
2. Подключить lazy route.
3. Добавить registry/navigation.
4. Добавить curriculum node.
5. Проверить course map desktop/mobile.

### Итерация 5: QA

1. Добавить route screenshots.
2. Добавить mistake path smoke.
3. Добавить happy path smoke.
4. Прогнать full quality gate.
5. Проверить mobile screenshots глазами.

### Итерация 6: docs and cleanup

1. Обновить roadmap/status docs.
2. Зафиксировать build chunk sizes.
3. Убедиться, что нет новых больших raster assets.
4. Сделать commit/push отдельным changeset.

## Проверки

Минимум:

```bash
make lint-python
make lint-js
make test-js
make interactive-build
SHAD_INTERACTIVE_URL=http://127.0.0.1:5173 .venv/bin/python SHAD/interactive/scripts/smoke_playwright.py
git diff --check
```

UI:

- screenshots:
  - map desktop/mobile;
  - ML playground desktop/mobile;
  - train/test warning;
  - leakage warning;
  - success/reflection;
- no horizontal overflow;
- no hidden table columns on mobile;
- no unreadable metric labels;
- mascot does not cover data points.

## Definition of Done

Этап закрыт, когда:

- `ML-полигон` playable from course map;
- есть reusable `DataTableMini`, `MetricBoard`, `DecisionPlane`;
- model tests cover metrics and typical data/ML mistakes;
- Playwright smoke covers happy path and mistake path;
- data section appears in navigation/course map;
- mobile UI is readable without horizontal scroll;
- no backend or heavy ML dependency added;
- full quality gate passes.
