# SHAD Interactive: план этапа "закрытие педагогического hardening"

Этот этап продолжает
[next_gameplay_learning_stage_plan.md](next_gameplay_learning_stage_plan.md).
Предыдущий проход уже усилил authoring contract, `Цех перестановок` и
`Матрицу как машину`: появились диагностика ошибок, repair hints, smoke на
typical mistake path и более полный mission metadata. Теперь нужно довести
оставшиеся игровые прототипы и карту курса до того же уровня.

Короткая цель этапа: **перед добавлением новых algorithms/data-analysis игр
сделать текущие пять миссий цельной учебной системой**.

## Почему это следующий этап

Если сейчас сразу добавить `Арену асимптотик` или `ML-полигон`, новые миссии
начнут наследовать неровности текущей базы:

- две алгебраические миссии еще не имеют полноценной диагностики ошибок;
- `Graph Dispatcher` силен как trace, но не проверяет intentional mistake path;
- Меби пока в основном coach, а не игровой marker/pivot/frontier;
- карта курса показывает маршрут и прогресс, но не показывает навыки,
  unlocks и review;
- performance debt по PNG Меби и тяжелому 3D chunk уже виден в build output.

Поэтому этот этап не про расширение количества сцен. Он про надежность игрового
языка: каждую существующую миссию должно быть можно использовать как образец
для следующей.

## Текущее состояние

### Уже готово

- `mission_authoring_guide.md` описывает `Learning loop`.
- `mission_quality_checklist.md` содержит блок `Diagnosis and Repair`.
- `mission_brief_template.md` можно использовать для новых миссий.
- `Цех перестановок`:
  - имеет hints ladder, mistake feedback, reflection/transfer;
  - диагностирует `in-progress`, `target-mismatch`, `near-target`,
    `wrong-parity`, `over-budget`, `success`;
  - имеет unit tests и Playwright mistake path.
- `Матрица как машина`:
  - имеет input fallback;
  - диагностирует перепутанные столбцы, неверный столбец, направление и длину;
  - имеет unit tests и Playwright mistake path.
- Dev stack работает через Docker на `http://localhost:5173/`.

### Еще не готово

- `Кузница определителя` пока не диагностирует площадь, знак и вырожденность
  как разные ошибки.
- `Охота за ядром` пока не показывает пользователю структуру ошибок
  `x + y` и `x - z` как repair surface.
- `Graph Dispatcher` не имеет отдельного smoke на intentional mistake.
- Course map не хранит и не показывает skill/unlock/review слой.
- Mascot layer не имеет явного `MascotRole`.
- Performance budget не превращен в actionable work по крупным assets/chunks.

## Статус выполнения

### Выполнено в текущем заходе

- `Кузница определителя` получила diagnosis model:
  `in-progress`, `success`, `area-too-small`, `area-too-large`,
  `wrong-orientation`, `unexpected-degenerate`, `needs-degenerate`,
  `needs-repair-after-degenerate`.
- В `Кузнице определителя` добавлены input fallback, diagnosis panel,
  reset control, richer success/warning coloring и Playwright mistake path.
- `Охота за ядром` получила residual diagnosis:
  `zero-vector`, ошибки `x + y`, ошибки `x - z`, ошибки обеих строк,
  масштаб той же прямой, basis scale и rank-nullity readiness.
- В `Охоте за ядром` добавлены residual readout, параметризация
  `x = t(-1, 1, -1)`, diagnosis panel и Playwright mistake path.
- `Graph Dispatcher` получил Playwright mistake path для неверного BFS-хода.
- Добавлены `MascotRole` и `MascotOverlay`.
- `MascotOverlay` подключен в двух миссиях:
  - `Цех перестановок`: выбранная позиция как pivot;
  - `Graph Dispatcher`: required frontier vertex.
- `CurriculumNode` расширен полями `skillIds`, `unlocks`,
  `reviewAfterMissionIds`, `readinessLabel`, `coverageStatus`.
- Course map показывает skill/readiness/unlocks/coverage и фильтры
  `Все`, `Алгебра`, `Алгоритмы`, `Data`, `Повторить`.
- `performance_budget.md` получил baseline 2026-06-07 и action items по PNG
  Меби/WebP.
- Добавлен [programming_data_primitives_plan.md](programming_data_primitives_plan.md).

### Осталось следующим куском

- Конверсия активных PNG Меби в WebP/AVIF-кандидаты и проверка качества.
- Более умная recommendation logic с review candidate после завершения миссий.
- Реализация первого programming/data primitive, вероятнее `CodeTracePanel` +
  `StrategyCompare` для `Арены асимптотик`.
- Более тонкая mobile ergonomics для `KernelHuntMission`: 3D-сцена все еще
  занимает много первого экрана.

## P0. Retrofit `Кузница определителя`

Цель: сделать определитель игрой про три разных смысла числа `det A`:
площадь, ориентацию и вырожденность.

### Model layer

Файлы:

- `src/visualizations/determinants/determinantForgeModel.ts`;
- `src/visualizations/determinants/determinantForgeModel.test.ts`.

Добавить:

- `DeterminantDiagnosisKind`:
  - `in-progress`;
  - `success`;
  - `area-too-small`;
  - `area-too-large`;
  - `wrong-orientation`;
  - `unexpected-degenerate`;
  - `needs-degenerate`;
  - `needs-repair-after-degenerate`.
- `diagnoseDeterminantState({ levelId, u, v, completedLevelIds, touched })`;
- helper для сравнения target area/sign/degeneracy;
- стартовое состояние без ложной ошибки до первого действия.

### UI

Файл:

- `src/visualizations/determinants/DeterminantForgeMission.tsx`.

Сделать:

- добавить diagnosis panel с repair hint;
- добавить numeric input fallback для `u.x`, `u.y`, `v.x`, `v.y`;
- подсвечивать параллелограмм:
  - success;
  - wrong orientation;
  - degeneracy;
  - near target area;
- разделить mascot messages:
  - площадь почти поймана;
  - знак неверный;
  - вырожденность случилась не на том уровне;
  - repair после вырожденности.

### Mission metadata

Файл:

- `src/game/missions.ts`.

Добавить для `determinantForgeMission`:

- `reflectionPrompt`;
- `transferTask`;
- `qualityTags`;
- `estimatedMinutes`;
- `hintLevels`;
- `mistakeFeedback`;
- `successConditionLabel`.

### Tests

Добавить:

- unit tests для всех основных diagnosis kinds;
- Playwright mistake path:
  - на `area-two` сделать `det = -2`;
  - проверить `wrong-orientation` или специальный message, если цель требует
    только площадь;
  - на `flip-orientation` сделать положительную площадь и проверить
    `wrong-orientation`;
  - reset/repair smoke.

Готово, когда пользователь понимает, что именно не совпало: модуль, знак или
вырожденность.

## P0. Retrofit `Охота за ядром`

Цель: превратить ядро из 3D-сцены с правильным вектором в игру про систему
ошибок `Ax = 0`.

### Model layer

Файлы:

- `src/visualizations/linear-maps/kernelHuntModel.ts`;
- `src/visualizations/linear-maps/kernelHuntModel.test.ts`.

Добавить:

- `KernelDiagnosisKind`:
  - `in-progress`;
  - `success`;
  - `zero-vector`;
  - `first-equation-error`;
  - `second-equation-error`;
  - `both-equations-error`;
  - `same-solution-scale-needed`;
  - `basis-scale-error`;
  - `rank-nullity-not-ready`.
- `diagnoseKernelState({ levelId, candidate, completedLevelIds, touched })`;
- helper для параметра `t` в `x = t(-1, 1, -1)`;
- helper для residual labels: `x + y`, `x - z`.

### UI

Файлы:

- `src/visualizations/linear-maps/KernelHuntMission.tsx`;
- возможно `KernelLineViz.tsx`, если удобно вынести readout.

Сделать:

- diagnosis panel:
  - показывает `x + y`;
  - показывает `x - z`;
  - объясняет, какая строка матрицы еще не занулена;
- success readout:
  - `x = t(-1, 1, -1)`;
  - `dim ker A = 1`;
- для уровня `rank-nullity` сделать мини-сборку/readout:
  - `rank A = 2`;
  - `dim ker A = 1`;
  - `3 = 2 + 1`;
- проверить mobile: 3D canvas не должен отрывать пользователя от controls.

### Mission metadata

Файл:

- `src/game/missions.ts`.

Добавить для `kernelHuntMission`:

- `reflectionPrompt`;
- `transferTask`;
- `qualityTags`;
- `estimatedMinutes`;
- `hintLevels`;
- `mistakeFeedback`;
- `successConditionLabel`.

### Tests

Добавить:

- unit tests для residual diagnosis;
- smoke mistake path:
  - ввести zero vector;
  - ввести вектор, где занулено только `x + y`;
  - проверить diagnosis и mascot warning;
  - затем happy path.

Готово, когда пользователь видит ядро как множество решений системы, а не
только как одну угаданную точку в 3D.

## P0. Graph Dispatcher mistake path

`Graph Dispatcher` уже ближе всего к нужной модели. Его надо закрепить как
эталон code-trace миссии.

Сделать:

- добавить smoke `run_graph_mistake_path`;
- сценарий:
  - открыть BFS;
  - кликнуть не первую вершину frontier после старта;
  - проверить warning и `mistakes > 0`;
  - reset;
  - проверить восстановление начального frontier;
- при необходимости добавить `data-testid` на invariant panel/mistake counter;
- убедиться, что keyboard path не сломан.

Готово, когда trace-миссия проверяет не только правильный обход, но и типовую
ошибку trace.

## P1. Mascot as mechanic v1

Цель: Меби должен стать частью состояния хотя бы в двух миссиях, но без
декоративного шума.

### Types

Файлы:

- `src/game/missionTypes.ts`;
- возможно новый `src/game/mascotTypes.ts`.

Добавить:

```ts
type MascotRole =
  | 'guide'
  | 'pivot'
  | 'frontier'
  | 'error-marker'
  | 'invariant-token'
  | 'data-point'
```

Варианты применения:

- mission-level default role;
- level override;
- scene overlay props.

### UI

Файлы:

- `src/game/components/MascotCoach.tsx`;
- новый `src/game/components/MascotOverlay.tsx`.

Сделать:

- `MascotCoach` остается текстовым coach;
- `MascotOverlay` используется внутри игрового поля, если роль помогает:
  - перестановки: выбранная транспозиция;
  - графы: required frontier vertex;
  - матрицы: текущий образ базиса;
  - определитель: orientation/area warning marker.
- добавить правило: если overlay мешает чтению поля на mobile, он скрывается и
  остается только coach.

### First uses

Минимум:

- `Цех перестановок`: Меби показывает выбранную первую плитку или pending
  transposition.
- `Graph Dispatcher`: Меби/малый marker указывает required frontier vertex.

Готово, когда Меби не просто говорит, а помогает увидеть текущий ход.

## P1. Course map as skill route

Цель: карта должна показывать учебные навыки и связи, а не только список миссий.

### Data model

Файлы:

- `src/game/curriculumTypes.ts`;
- `src/game/curriculumGraph.ts`;
- `src/game/curriculumGraph.test.ts`;
- `src/game/courseMap.ts`.

Добавить к `CurriculumNode`:

- `skillIds: string[]`;
- `unlocks: string[]`;
- `reviewAfterMissionIds?: string[]`;
- `readinessLabel: string`;
- `coverageStatus: 'seed' | 'playable' | 'diagnosed' | 'review-ready'`.

Добавить validation:

- unknown unlock node id;
- empty `skillIds`;
- invalid review mission id;
- `coverageStatus` соответствует mission readiness.

### UI

Файлы:

- `src/pages/CourseMapPage.tsx`;
- `src/game/components/MissionCard.tsx`;
- `src/game/components/CoursePath.tsx`.

Сделать:

- на карточке показывать:
  - основной навык;
  - unlocks;
  - coverage/readiness;
  - review prompt после завершения;
- добавить segmented filter:
  - `Все`;
  - `Алгебра`;
  - `Алгоритмы`;
  - `Data`;
  - `Повторить`;
- не перегружать mobile: details compact, CTA остается заметным.

### Recommendation logic

Обновить `recommendedMissionId`:

- сначала незавершенная миссия;
- затем review candidate, если миссия завершена давно или открывает новый
  навык;
- затем planned/prototype next step.

Готово, когда карта отвечает на вопрос: "что этот уровень открыл и что теперь
повторить?"

## P1. Performance and asset triage

Build сейчас показывает:

- несколько PNG Меби около `469-489 KB`;
- `KernelHuntMission` chunk около `923 KB`;
- main bundle около `550 KB`.

Сделать:

- проверить, какие mascot PNG реально используются;
- удалить/перенести неиспользуемые ассеты в `_rejected` или reference-history,
  если они попадают в bundle;
- рассмотреть WebP/AVIF для mascot assets;
- убедиться, что 3D миссия lazy-loaded и не тянет Three.js в initial route
  сверх необходимого;
- добавить в `performance_budget.md` текущий baseline и лимиты:
  - mascot asset target;
  - max route chunk;
  - action при превышении.

Готово, когда performance debt записан не как наблюдение, а как проверяемая
задача с baseline.

## P2. Programming/data primitives design pass

Не реализовывать все primitives в этом этапе, но подготовить технический brief,
чтобы следующая новая миссия не проектировалась с нуля.

Создать:

- `programming_data_primitives_plan.md`.

Описать:

- `CodeTracePanel`;
- `DataTableMini`;
- `MetricBoard`;
- `StrategyCompare`;
- shared types для `cost`, `metric`, `traceStep`, `datasetRow`;
- какие компоненты можно переиспользовать из `TracePanel`;
- первая целевая миссия: `Арена асимптотик` или `ML-полигон`.

Готово, когда мы можем начать новую algorithms/data mission с готовым UI/data
контрактом.

## Порядок выполнения

### Итерация 1: Determinant retrofit

1. Добавить determinant diagnosis в model.
2. Добавить unit tests.
3. Добавить input fallback и diagnosis panel в UI.
4. Расширить mission metadata.
5. Добавить smoke mistake path.
6. Проверить desktop/mobile screenshots.

### Итерация 2: Kernel retrofit

1. Добавить kernel residual diagnosis в model.
2. Добавить unit tests.
3. Добавить residual/readout UI.
4. Расширить mission metadata.
5. Добавить smoke mistake path.
6. Проверить 3D/mobile ergonomics.

### Итерация 3: Graph mistake path + MascotRole

1. Добавить graph mistake smoke.
2. Ввести `MascotRole`.
3. Добавить `MascotOverlay` v1.
4. Подключить overlay в двух миссиях.
5. Проверить mobile: overlay не мешает controls.

### Итерация 4: Course map skills/unlocks

1. Расширить curriculum types and graph.
2. Обновить validation tests.
3. Обновить mission cards.
4. Добавить фильтры.
5. Обновить recommendation logic.
6. Проверить screenshots карты.

### Итерация 5: Performance + next primitives brief

1. Зафиксировать build baseline в `performance_budget.md`.
2. Проверить mascot assets.
3. Проверить lazy-loading 3D chunks.
4. Создать `programming_data_primitives_plan.md`.
5. Обновить roadmap links.

## Проверки

После каждой итерации:

```bash
make lint-python
make lint-js
make test-js
make interactive-build
SHAD_INTERACTIVE_URL=http://127.0.0.1:5173 .venv/bin/python SHAD/interactive/scripts/smoke_playwright.py
git diff --check
```

Для UI:

- смотреть screenshots измененных миссий desktop/mobile;
- проверять intentional mistake path вручную хотя бы один раз;
- проверять, что dev stack остается живым на `http://localhost:5173/`.

## Definition of Done

Этап закрыт, когда:

- все пять текущих миссий имеют diagnosis model, hints ladder,
  mistakeFeedback, successConditionLabel, reflection/transfer;
- минимум четыре миссии имеют Playwright typical mistake path;
- Меби используется как state marker минимум в двух миссиях;
- карта курса показывает skills/unlocks/review слой;
- performance baseline записан и не ухудшен без явного решения;
- есть план primitives для programming/data-analysis;
- `make interactive-build` и полный smoke проходят на живом dev stack.
