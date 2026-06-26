# SHAD Interactive: план этапа "Арена асимптотик и programming primitives"

Этот этап начинается после педагогического hardening текущих пяти миссий.
Теперь приложение умеет не только показывать игровые поля, но и диагностировать
типовые ошибки, вести по карте навыков и проверять intentional mistake paths.

Следующий правильный шаг: **сделать первую настоящую programming/algorithms
миссию и вынести из нее переиспользуемые primitives для будущих игр по
алгоритмам, программированию и анализу данных**.

Основная миссия этапа: **Арена асимптотик**.

## Статус 2026-06-07

Выполнено в текущей итерации:

- добавлены `CodeTracePanel`, `StrategyCompare` и общие programming types;
- реализована playable mission `Арена асимптотик`;
- добавлена model-диагностика для small n, large n, nearly sorted input и many
  lookups;
- миссия подключена в lazy route, registry, navigation и curriculum graph;
- Playwright smoke расширен route screenshot, mistake path и happy path для
  новой арены;
- активные Mebi assets переведены в WebP runtime imports;
- `KernelHuntMission` получила более компактный mobile scene viewport;
- course map после полного прохождения предлагает review mission.

Осталось на следующий algorithms/data этап:

- выделить `DataTableMini` и `MetricBoard`;
- добавить первую data-analysis/ML миссию;
- завести предметные algorithm lecture paths, когда появятся живые материалы в
  `SHAD/programming algorithms and data structures`.

## Почему именно Арена асимптотик

`Арена асимптотик` лучше всего продолжает текущую систему:

- наследует trace-язык `Graph Dispatcher`;
- использует уже понятный игровой цикл "выбор -> стоимость -> ошибка ->
  repair";
- вводит программирование без редактора кода и без тяжелого backend;
- готовит primitives для сортировок, бинарного поиска, DP и структур данных;
- не требует новых больших raster assets;
- дает хороший мост от математического материала к программированию и анализу
  данных.

Идея миссии: пользователь выбирает стратегию для входов разного размера и видит,
как меняются comparisons, memory и growth. Победа не в "выбрать всегда самый
быстрый алгоритм", а в понимании, когда константы важны, а когда асимптотика
переламывает игру.

## Текущее основание

Уже есть:

- `MissionShell`, `MissionSummary`, `MissionReflection`, `MascotCoach`;
- `TracePanel`, `TraceStepList`, `InvariantCheck`, `StateToken`;
- `MissionBadge`, `CostBadge`, `MetricBadge`;
- curriculum graph с `skillIds`, `unlocks`, `reviewAfterMissionIds`;
- Playwright smoke с happy paths и mistake paths;
- `programming_data_primitives_plan.md`;
- route lazy-loading для миссий.

Нужно добавить:

- shared programming/data types;
- `CodeTracePanel`;
- `StrategyCompare`;
- model layer для асимптотик;
- новую миссию в registry/course map/navigation;
- unit tests и smoke;
- ссылки/упоминания в лекциях только после успешного QA.

## Product Slice

### Пользовательский опыт

Игрок видит несколько входов:

- почти отсортированный массив;
- случайный массив;
- маленький массив;
- большой массив;
- поток запросов поиска.

На каждом уровне нужно выбрать стратегию:

- linear scan;
- binary search after sort;
- insertion sort;
- merge sort;
- quicksort-like average strategy;
- hash lookup setup, если уровень про много запросов.

UI показывает:

- cost counters: comparisons, memory, setup, queries;
- псевдокод активной стратегии;
- рост стоимости на нескольких размерах `n`;
- короткую диагностику:
  - "константа выиграла на маленьком n";
  - "setup не окупился для одного запроса";
  - "O(n log n) обогнал O(n²) на большом n";
  - "память сэкономлена ценой сравнений".

### Обучающий смысл

После миссии пользователь должен унести:

- O-нотация говорит про рост, а не про точное время на одном входе;
- маленький `n` может обмануть;
- preprocessing окупается только при достаточном числе запросов;
- разные входы меняют практический выбор стратегии;
- cost model надо явно назвать перед сравнением алгоритмов.

## P0. Shared Programming Types

Файл:

- `src/game/programmingTypes.ts`.

Добавить:

```ts
export type CostMetric = {
  id: string
  label: string
  value: number | string
  tone?: MissionBadge['tone']
}

export type CodeTraceLine = {
  id: string
  text: string
  active?: boolean
  executed?: boolean
  invariantOk?: boolean
}

export type StrategyOption = {
  id: string
  label: string
  complexity: string
  setupCost?: string
  memoryCost?: string
  bestFor: string
}

export type GrowthPoint = {
  n: number
  cost: number
}
```

Готово, когда эти типы используются не только новой миссией, но и primitives.

## P0. CodeTracePanel

Файл:

- `src/game/components/programming/CodeTracePanel.tsx`.

Назначение: компактно показать псевдокод, активную строку, переменные и cost.

Props:

- `lines: CodeTraceLine[]`;
- `variables: Record<string, string | number>`;
- `metrics: CostMetric[]`;
- `invariantOk: boolean`;
- `invariantLabel: string`.

UI:

- не делать "редактор кода";
- использовать моноширинный блок только для псевдокода;
- активная строка подсвечена;
- variables и metrics показываются как tokens;
- invariant похож на текущий `InvariantCheck`.

Готово, когда `CodeTracePanel` можно использовать в `Арена асимптотик` и позже
в DP/binary search.

## P0. StrategyCompare

Файл:

- `src/game/components/programming/StrategyCompare.tsx`.

Назначение: дать выбрать стратегию и увидеть рост стоимости.

Props:

- `strategies: StrategyOption[]`;
- `selectedStrategyId`;
- `onSelect`;
- `growthPointsByStrategy`;
- `recommendedStrategyId?`;
- `diagnosis`.

UI:

- segmented/cards для стратегий;
- compact growth table или mini bars;
- cost badges;
- no huge chart dependency;
- mobile-friendly: стратегии идут сеткой, growth table ниже.

Готово, когда пользователь может сравнить 2-4 стратегии без чтения длинного
текста.

## P0. Asymptotic Arena Model

Папка:

- `src/visualizations/asymptotics/`.

Файлы:

- `asymptoticArenaModel.ts`;
- `asymptoticArenaModel.test.ts`;
- `AsymptoticArenaMission.tsx`.

Model должен содержать:

- `InputScenario`:
  - `small-random`;
  - `large-random`;
  - `nearly-sorted`;
  - `many-lookups`;
- `AlgorithmStrategy`:
  - `linear-scan`;
  - `binary-search-after-sort`;
  - `insertion-sort`;
  - `merge-sort`;
  - `hash-index`;
- deterministic cost formulas;
- `estimateCost(strategy, scenario)`;
- `bestStrategyForScenario(scenario)`;
- `diagnoseStrategyChoice(strategy, scenario)`;
- `growthPoints(strategy, scenario)`.

Важно: не делать симулятор реальной сортировки на первом проходе. Для учебной
игры достаточно честной cost model с понятными формулами.

Диагнозы:

- `good-fit`;
- `constant-wins-small-n`;
- `quadratic-explodes`;
- `setup-not-worth-it`;
- `preprocessing-pays-off`;
- `memory-tradeoff`;
- `wrong-cost-model`.

Готово, когда model tests покрывают минимум 6 сравнений и 4 diagnosis kinds.

## P0. Mission Definition

Добавить в `src/game/missions.ts`:

- `asymptoticArenaMission`.

Поля:

- `id: 'asymptotic-arena'`;
- `route: '/algorithms/asymptotics/arena'`;
- `title: 'Арена асимптотик'`;
- `domain: 'algorithms'`;
- `mechanic: 'code-trace'` или новый `strategy-arena`, если решим расширить
  `MissionMechanic`;
- `lessonPath` на алгоритмическую лекцию, если есть подходящий файл;
- `reflectionPrompt`;
- `transferTask`;
- `qualityTags`;
- `estimatedMinutes`.

Уровни:

1. **Малый вход**
   - цель: выбрать стратегию для маленького `n`;
   - смысл: константы могут победить;
   - типовая ошибка: overengineering.
2. **Большой вход**
   - цель: выбрать стратегию, которая не взрывается;
   - смысл: O(n²) проигрывает ростом;
   - типовая ошибка: смотреть на один маленький пример.
3. **Почти отсортировано**
   - цель: выбрать insertion sort или объяснить tradeoff;
   - смысл: структура входа важна;
   - типовая ошибка: слепо брать "самую известную" стратегию.
4. **Много запросов**
   - цель: понять, когда preprocessing окупается;
   - смысл: setup cost против query cost;
   - типовая ошибка: строить индекс ради одного запроса.

Готово, когда миссия проходит полный authoring checklist.

## P0. Registry, Routes, Curriculum

Обновить:

- `src/visualizations/routeLoaders.ts`;
- `src/visualizations/missionRegistry.ts`;
- `src/visualizations/navigation.ts`;
- `src/game/curriculumGraph.ts`;
- `src/game/curriculumGraph.test.ts`;
- возможно `src/game/courseMap.ts`, если recommendation logic требует нового
  поведения.

Curriculum node:

- id: `asymptotics`;
- section: `algorithms`;
- skillIds:
  - `growth-model`;
  - `cost-comparison`;
  - `strategy-choice`;
- prerequisites:
  - `graph-trace`;
- unlocks:
  - `dp-station`;
  - `ml-playground`;
- coverageStatus: `playable` или `diagnosed` после smoke mistake path.

Готово, когда карта показывает `Арена асимптотик` после `Graph Dispatcher`.

## P1. Playwright And Tests

Unit tests:

- cost formulas;
- best strategy;
- diagnosis;
- growth points monotonicity.

Smoke:

- route screenshot desktop/mobile;
- happy path all levels;
- mistake path:
  - выбрать quadratic strategy на large input;
  - проверить warning;
  - выбрать правильную стратегию;
  - summary/reflection visible.

Обновить:

- `scripts/smoke_playwright.py`;
- screenshot route list;
- quality checklist references if needed.

Готово, когда `make test-js` и полный smoke проходят.

## P1. UI/UX Polish For Programming Mode

Цель: programming миссия должна отличаться от geometry lab, но не выглядеть как
обычный dashboard.

Design direction:

- тот же "paper workshop", но с более плотным trace/table ритмом;
- меньше декоративных карточек, больше состояния;
- code panel и strategy panel не должны конкурировать с целью уровня;
- Меби может быть `pivot`/`frontier`/`invariant-token`, но не должен закрывать
  псевдокод.

Проверить:

- desktop: поле не распадается на набор независимых карточек;
- mobile: сначала цель и выбор стратегии, потом детали стоимости;
- text fit: длинные `O(n log n)` и strategy labels не ломают кнопки;
- no horizontal overflow.

## P1. Performance Pass: Mebi Assets

До или после миссии, но в этом этапе:

- сконвертировать активные PNG из `src/assets/game/mascot/` в WebP-кандидаты;
- измерить размеры;
- визуально проверить:
  - map;
  - substitution;
  - graph overlay;
  - warning/success states;
- если качество нормальное:
  - переключить runtime imports на WebP;
  - оставить PNG source/history в photoshop/reference folders;
  - обновить `performance_budget.md`.

Готово, когда mascot runtime assets становятся заметно легче или появляется
явное решение оставить PNG из-за качества.

## P1. Kernel Mobile Ergonomics

Текущая `KernelHuntMission` на mobile полезна, но 3D-сцена занимает много
первого экрана.

Сделать:

- уменьшить высоту 3D-сцены на mobile или сделать controls быстрее доступными;
- проверить, что objective и residual diagnosis видны без слишком длинного
  скролла;
- сохранить desktop 3D framing;
- обновить screenshot review.

Готово, когда mobile-путь "увидел цель -> изменил координаты -> увидел
diagnosis" ощущается быстрее.

## P2. Smarter Review Recommendation

Текущая карта показывает review metadata, но recommendation logic пока простая.

Сделать:

- после завершения миссии показывать review candidate из
  `reviewAfterMissionIds`;
- не мешать первому прохождению: сначала незавершенные миссии;
- добавить visual marker для review;
- покрыть unit test в `courseMap` или отдельной helper-функции.

Готово, когда карта начинает вести по повторению, а не только по первому
маршруту.

## Порядок выполнения

### Итерация 1: primitives skeleton

1. Добавить `programmingTypes.ts`.
2. Добавить `CodeTracePanel`.
3. Добавить `StrategyCompare`.
4. Добавить легкие component-level smoke selectors.
5. Проверить mobile layout на dev route или сразу в миссии.

### Итерация 2: model first

1. Создать `asymptoticArenaModel.ts`.
2. Описать scenarios and strategies.
3. Реализовать cost formulas.
4. Добавить diagnosis.
5. Написать unit tests.

### Итерация 3: mission UI

1. Создать `AsymptoticArenaMission.tsx`.
2. Подключить `MissionShell`.
3. Добавить `CodeTracePanel` and `StrategyCompare`.
4. Добавить badges: `comparisons`, `memory`, `setup`, `growth`.
5. Добавить level progression and reflection.

### Итерация 4: registry and curriculum

1. Добавить mission definition.
2. Подключить lazy route.
3. Добавить registry/navigation.
4. Добавить curriculum node.
5. Обновить course map screenshots.

### Итерация 5: tests and QA

1. Добавить route screenshots.
2. Добавить happy path smoke.
3. Добавить mistake path smoke.
4. Прогнать lint/test/build/smoke.
5. Проверить desktop/mobile screenshots.

### Итерация 6: performance and polish

1. Mebi WebP/AVIF pass.
2. Kernel mobile ergonomics.
3. Review recommendation logic.
4. Обновить планы/status docs.

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

Для UI:

- screenshots:
  - map desktop/mobile;
  - asymptotic arena desktop/mobile;
  - mistake state;
  - success/reflection state;
- visual check for no text overflow;
- inspect build output for chunk sizes.

## Definition of Done

Этап закрыт, когда:

- `Арена асимптотик` playable в course map;
- есть reusable `CodeTracePanel` and `StrategyCompare`;
- model tests покрывают cost/diagnosis;
- Playwright smoke покрывает happy path and mistake path;
- карта курса показывает новый algorithms node после graph trace;
- active mascot assets либо оптимизированы, либо имеют записанное решение;
- mobile `KernelHuntMission` стала быстрее в основном loop;
- полный quality gate проходит.
