# SHAD Interactive: план этапа "Feature Factory и split inspector"

Этот этап начинается после `ML-полигона`. Приложение уже умеет показывать
маленький dataset, threshold classifier, train/test metrics and typical ML
mistakes. Но пользователь пока в основном двигает границу решения, а не
работает с данными как с материалом.

Следующий шаг: **сделать первую feature engineering / data cleaning миссию** и
расширить data primitives так, чтобы таблица стала игровым объектом.

Основная миссия этапа: **Фабрика признаков**.

## Статус 2026-06-07

Этап реализован как playable/prototype mission:

- добавлены `DataActionKind`, `DataPipelineStep`, `FeatureState` and
  `SplitQuality` в `src/game/dataTypes.ts`;
- `DataTableMini` поддерживает row/column actions with target filters;
- добавлены shared UI primitives `FeatureTogglePanel`, `PipelineStrip` and
  `SplitInspector`;
- добавлена модель `featureFactoryModel.ts` with unit tests;
- добавлена миссия `FeatureFactoryMission.tsx` на route
  `#/data/features/factory`;
- миссия подключена к `missionDefinitions`, `missionRegistry`, navigation,
  curriculum graph and Playwright smoke;
- реализованы 4 P0 уровня: missing median imputation, outlier drop, leakage
  disable and category encoding.

Пятый уровень `Проверь split` оставлен как следующий P1 slice: компонент
`SplitInspector` уже есть на экране и показывает label/range gaps, но выбор
split seed пока не является отдельной победной механикой.

## Почему именно Фабрика признаков

`ML-полигон` научил смотреть на train/test and metrics. Но в реальной работе
модель часто ломается раньше: данные содержат пропуски, выбросы, утечку,
категориальные признаки и плохой split.

`Фабрика признаков` полезна как следующий слой, потому что:

- переиспользует `DataTableMini`, `MetricBoard` and `DecisionPlane`;
- делает таблицу интерактивной, а не декоративной;
- добавляет действия пользователя: mark, drop, impute, encode, disable feature;
- готовит будущие миссии `Decision Tree Split`, `Feature Leakage Puzzle`,
  `Clustering Sandbox`;
- остается frontend-only: fixed toy datasets, no backend, no pandas/sklearn.

Главная идея: пользователь чинит маленький dataset и сразу видит, как меняются
метрики и diagnosis. Победа не в максимальной train accuracy, а в честном,
объяснимом pipeline.

## Текущее основание

Уже есть:

- `dataTypes.ts`: `DatasetRow`, `DatasetColumn`, `ModelMetric`,
  `ConfusionCounts`, `ThresholdModel`;
- `DataTableMini`: compact rows, train/test badges, predictions, flags;
- `MetricBoard`: train/test metrics and confusion counts;
- `DecisionPlane`: SVG threshold classifier;
- `MlPlaygroundMission`: data-analysis route, model diagnostics, smoke.

Не хватает:

- действий над строками и колонками;
- истории pipeline steps;
- видимого split balance;
- feature toggle UI;
- dataset quality diagnostics;
- tests for data cleaning decisions.

## UI/UX оценка перед этапом

`ML-полигон` получился читаемым, но на mobile таблица становится длинной. Для
`Фабрики признаков` нельзя просто добавить больше строк и больше кнопок.

Что сохранить:

- главное поле должно оставаться сверху;
- метрики должны быть compact, не BI-dashboard;
- действия должны быть конкретными: "mark leakage", "impute median", "drop
  outlier", "encode category";
- Меби реагирует на качество pipeline, а не пересказывает теорию.

Что улучшить:

- `DataTableMini` должен поддержать row actions and column flags;
- на mobile нужны короткие row cards с action menu, а не много inline-кнопок;
- `MetricBoard` должен уметь показывать "before/after" или delta;
- нужен `PipelineStrip`: последовательность действий пользователя как игровой
  trace;
- нужен `SplitInspector`: train/test баланс по label and feature range.

Визуальная метафора: **лаборатория пробирок с контрольной лентой**. Данные не
таблица Excel, а маленькие образцы на конвейере. Ошибка видна как загрязнение:
leakage светится оранжевым, missing values выглядят как пустые ячейки, outlier
торчит за пределы нормального диапазона.

## Product Slice

### Игровой сюжет

Игрок получает dataset из 16-24 строк:

- числовой признак `signal`;
- категориальный признак `segment`;
- признак с пропусками `temperature`;
- подозрительный `leakage_code`;
- один явный outlier;
- train/test split с небольшим перекосом.

Действия:

- отметить подозрительную колонку как leakage;
- выбрать стратегию пропусков: keep/drop/impute median;
- отметить или удалить outlier;
- закодировать категориальный признак;
- проверить split balance;
- выбрать набор признаков для threshold/model score.

### Уровни миссии

1. **Найди пропуск**
   - Подсветить строки с missing values.
   - Выбрать median imputation вместо удаления половины test.
   - Условие успеха: missing flags cleared, row count не испорчен.

2. **Поймай выброс**
   - Найти точку, которая ломает threshold.
   - Выбрать action: mark outlier or drop from train only.
   - Условие успеха: test metric не ухудшилась, train не переобучился на выброс.

3. **Отключи leakage**
   - Найти колонку, которая подозрительно совпадает с label.
   - Условие успеха: leakage feature disabled, honest features remain enabled.

4. **Закодируй категорию**
   - Категориальный segment влияет на score.
   - Действие: one-hot/simple encode.
   - Условие успеха: metric improves without leakage.

5. **Проверь split**
   - `SplitInspector` показывает перекос label/range.
   - Действие: выбрать balanced split seed из 2-3 вариантов.
   - Условие успеха: train/test label ratio and feature range close enough.

Если этап нужно сделать компактнее, первые 4 уровня достаточно. `SplitInspector`
можно оставить как P1 component и включить в пятый уровень позже.

### Обучающий смысл

После миссии пользователь должен унести:

- качество модели начинается до выбора модели;
- пропуски и выбросы требуют явного решения;
- leakage нельзя лечить подбором threshold;
- категориальные признаки надо превратить в числовые признаки осмысленно;
- train/test split должен быть репрезентативным;
- pipeline должен быть воспроизводимым, а не набором случайных кликов.

## P0. Расширить data types

Файл:

- `src/game/dataTypes.ts`.

Добавить:

```ts
export type DataActionKind =
  | 'mark-missing'
  | 'impute-median'
  | 'drop-row'
  | 'mark-outlier'
  | 'disable-feature'
  | 'encode-category'
  | 'choose-split'

export type DataPipelineStep = {
  id: string
  kind: DataActionKind
  label: string
  targetId: string
  valid: boolean
}

export type FeatureState = {
  id: string
  enabled: boolean
  encoded?: boolean
  flaggedAsLeakage?: boolean
}

export type SplitQuality = {
  labelGap: number
  rangeGap: number
  ok: boolean
}
```

Не ломать существующие `ML-полигон` types. Новые поля должны быть optional or
separate types, чтобы threshold mission не получила лишнюю сложность.

## P0. Feature Factory Model

Папка:

- `src/visualizations/feature-factory/`.

Файлы:

- `featureFactoryModel.ts`;
- `featureFactoryModel.test.ts`;
- `FeatureFactoryMission.tsx`.

Model functions:

- `factoryRowsForLevel(levelId)`;
- `detectMissing(rows)`;
- `imputeMedian(rows, featureId)`;
- `dropRow(rows, rowId)`;
- `toggleFeature(features, featureId)`;
- `encodeCategory(rows, featureId)`;
- `splitQuality(rows)`;
- `scorePipeline(rows, features, steps)`;
- `diagnosePipeline(levelId, rows, features, steps)`.

Diagnosis kinds:

- `good-cleaning`;
- `missing-left`;
- `over-dropped`;
- `outlier-ignored`;
- `leakage-enabled`;
- `category-not-encoded`;
- `split-skewed`;
- `pipeline-too-random`.

Unit tests:

- median imputation deterministic;
- leakage diagnosis beats high train score;
- dropping too many rows fails;
- category encoding changes usable feature set;
- split quality detects label skew;
- happy solution passes each level.

## P0. DataTableMini Actions

Файл:

- `src/game/components/data/DataTableMini.tsx`.

Расширить props:

- `rowActions?: Array<{ id; label; icon?; onSelect(rowId) }>`;
- `columnActions?: Array<{ id; label; onSelect(columnId) }>`;
- `flagLegend?: boolean`;
- `compactActionMode?: 'inline' | 'menu'`.

UI:

- desktop: маленькие action buttons в row hover/последней колонке;
- mobile: один compact button per row, раскрытие в небольшое меню;
- не показывать все действия одновременно, если уровень требует только одно;
- actions должны иметь `data-testid`.

Готово, когда mission can mark/drop/impute without custom table code.

## P0. FeatureTogglePanel

Новый файл:

- `src/game/components/data/FeatureTogglePanel.tsx`.

Назначение:

- включать/выключать признаки;
- показывать encoded/leakage/missing badges;
- объяснять, почему признак подозрителен.

Props:

- `features: FeatureState[]`;
- `columns: DatasetColumn[]`;
- `onToggle(featureId)`;
- `onEncode?(featureId)`;
- `disabledFeatureIds?`;
- `diagnosisByFeature?`.

UI:

- toggles/checkboxes для enabled;
- small swatches for feature role;
- warning badge for leakage;
- encoded badge after action.

## P0. PipelineStrip

Новый файл:

- `src/game/components/data/PipelineStrip.tsx`.

Назначение: показать действия пользователя как trace.

Props:

- `steps: DataPipelineStep[]`;
- `activeStepId?`;
- `onUndo?(stepId)`;

UI:

- compact horizontal strip on desktop;
- stacked compact list on mobile;
- invalid step gets warning tone;
- no long text.

Готово, когда пользователь видит, что cleaning is reproducible sequence.

## P1. SplitInspector

Новый файл:

- `src/game/components/data/SplitInspector.tsx`.

Назначение:

- показать train/test label balance;
- показать feature range coverage;
- выбрать split seed among fixed variants.

Props:

- `quality: SplitQuality`;
- `variants?: SplitVariant[]`;
- `selectedVariantId`;
- `onVariantSelect`.

UI:

- two small bars: label ratio and range coverage;
- not a charting library;
- one clear warning when split skewed.

P1, потому что может быть пятым уровнем или отдельным hardening pass.

## P0. Mission Definition

Mission id:

- `feature-factory`.

Route:

- `/data/features/factory`.

Definition:

- `domain: 'data-analysis'`;
- `mechanic: 'model-arena'`;
- `difficulty: 2`;
- `mascotRole: 'error-marker'`;
- `lessonPath`: пока не указывать, потому что `SHAD/data analysis` пустой.

Quality tags:

- `data-cleaning`;
- `feature-engineering`;
- `leakage-diagnostics`;
- `pipeline-trace`;
- `model-tested`;

Course map:

- node id: `feature-factory`;
- section: `data-analysis`;
- prerequisites: `ml-playground`;
- missionIds: `['feature-factory']`;
- skillIds: `['missing-values', 'feature-selection', 'leakage-control']`;
- reviewAfterMissionIds: `['ml-playground']`;
- status: `prototype`;
- coverageStatus: `playable` after smoke.

Navigation:

- existing section `Data`;
- topic `features`;
- entry `Фабрика признаков`.

## P1. Gameplay Copy

Тон:

- "почини материал" вместо "настрой dashboard";
- короткая диагностика после действия;
- термин вводится после наблюдаемой ошибки.

Примеры сообщений:

- missing: "Пустая ячейка не исчезает сама. Выбери правило заполнения."
- outlier: "Один train-образец тянет границу сильнее остальных."
- leakage: "Этот признак знает ответ слишком хорошо. Это не обучение."
- category: "Категория пока текстовая: модель не умеет ее сравнивать как число."
- split: "Train и test должны быть похожими, но не одинаковыми."

## P1. UI/UX Проверки

Проверить:

- row actions usable at 390x844;
- no horizontal overflow;
- table not longer than mission scene without reason;
- pipeline strip does not push primary playground below fold on desktop;
- feature toggles readable and not confused with level buttons;
- Mebi does not cover table actions;
- colors not one-note: data warnings use orange/red sparingly, success uses
  green, split/test uses blue/energy.

Если mobile becomes too long:

- collapse table to 8 rows with "show all";
- keep metrics before table;
- put pipeline strip after controls, not before playground.

## P1. Smoke and Screenshots

Расширить `scripts/smoke_playwright.py`:

- route screenshot:
  - `feature-factory-desktop`;
  - `feature-factory-mobile`;
- mistake path:
  - leave leakage enabled;
  - over-drop rows;
  - choose skewed split if P1 included;
- happy path:
  - impute missing;
  - handle outlier;
  - disable leakage;
  - encode category;
  - final reflection.

State screenshots:

- missing warning;
- leakage warning;
- cleaned success;
- mobile action menu.

## P1. Docs

Обновить:

- `gameplay_roadmap.md`;
- `programming_data_primitives_plan.md`;
- `next_data_ml_playground_plan.md`;
- `performance_budget.md`;
- `mission_quality_checklist.md`, если row actions become required for data
  missions.

Отдельно стоит создать `SHAD/data analysis/README.md`, но не как замену
лекции. Это может быть короткий stub:

- какие interactive missions уже есть;
- какие лекции нужно написать позже;
- какие links пока intentionally absent.

## Implementation Order

### Итерация 1: model and types

1. Расширить `dataTypes.ts`.
2. Создать `featureFactoryModel.ts`.
3. Создать toy dataset and split variants.
4. Добавить unit tests for cleaning, leakage, split quality.

### Итерация 2: primitives

1. Расширить `DataTableMini` row/column actions.
2. Добавить `FeatureTogglePanel`.
3. Добавить `PipelineStrip`.
4. Добавить `SplitInspector` only if пятый уровень остается in scope.

### Итерация 3: mission

1. Создать `FeatureFactoryMission.tsx`.
2. Подключить `MissionShell`.
3. Реализовать 4 уровня.
4. Настроить feedback, badges, mascot states.

### Итерация 4: registry and curriculum

1. Добавить mission definition.
2. Добавить lazy route.
3. Добавить registry/navigation.
4. Добавить curriculum node after `ml-playground`.
5. Проверить course map filters and route path.

### Итерация 5: QA

1. Добавить smoke route screenshot.
2. Добавить mistake path and happy path.
3. Прогнать full quality gate.
4. Проверить desktop/mobile screenshots глазами.

### Итерация 6: docs and cleanup

1. Обновить status docs.
2. Зафиксировать build chunk sizes.
3. Проверить, что нет новых raster assets and heavy dependencies.
4. Подготовить commit отдельным changeset.

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

- map desktop/mobile;
- Feature Factory desktop/mobile;
- missing warning;
- leakage warning;
- final success/reflection;
- no horizontal overflow;
- row actions reachable on mobile.

## Definition of Done

Этап закрыт, когда:

- `Фабрика признаков` playable from course map;
- `DataTableMini` supports reusable row/column actions;
- `FeatureTogglePanel` and `PipelineStrip` reusable outside mission;
- model tests cover cleaning, leakage and split quality;
- Playwright smoke covers happy and mistake paths;
- data-analysis route/navigation/curriculum updated;
- mobile UI readable without horizontal scroll;
- no backend, pandas, sklearn or chart dependency added;
- full quality gate passes.
