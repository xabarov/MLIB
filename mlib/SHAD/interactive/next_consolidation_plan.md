# SHAD Interactive: план этапа "консолидация и готовность"

Этот этап продолжает
[next_pedagogy_hardening_plan.md](next_pedagogy_hardening_plan.md). Предыдущие
этапы построили систему производства миссий: curriculum graph, authoring schema,
QA checklist, accessibility/performance/deploy docs, audit-скрипт и Playwright
smoke. Накоплено тринадцать миссий в четырёх доменах.

Короткая цель этапа: **не добавлять новые темы, пока имеющиеся миссии не доведены
до `available`, а технический долг по перформансу и публикации не закрыт как
проверяемые задачи**.

## Почему это следующий этап

Система зрелая, но готовность отстаёт от зрелости:

- из тринадцати миссий только четыре имеют статус `available`
  (`Охота за ядром`, `Кузница определителя`, `Графовый диспетчер`,
  `Фабрика признаков`); остальные девять остаются `prototype`;
- ручное ревью ([mission_human_review.md](mission_human_review.md)) уже назвало,
  что мешает промоушену каждого прототипа, но polish backlog не закрыт;
- performance debt (PNG Меби ~469-489 KB, `KernelHunt` chunk ~923 KB) записан
  как наблюдение, но не превращён в actionable-задачу с автоматической проверкой;
- из шести механических семейств (`GeometryLab`, `StateMachine`,
  `StructureBuilder`, `Sampler`, `ModelArena`, `CodeTrace`) семейство `Sampler`
  не имеет ни одной реализации;
- deploy/link policy зафиксирована документом, но реальной CI-публикации `dist/`
  и smoke против prod нет.

Поэтому этап про надёжность и готовность, а не про количество сцен. Принцип
сохраняется: не расширять домены, пока игровой язык не доведён до `available`.

## Текущее состояние

### Статусы миссий (`src/visualizations/missionRegistry.ts`)

| Статус | Миссии |
| --- | --- |
| `available` (4) | `Охота за ядром`, `Кузница определителя`, `Графовый диспетчер`, `Фабрика признаков` |
| `prototype` (9) | `Матрица как машина`, `Квадратичная линза`, `SVD-линза`, `PCA-компрессор`, `Евклидова мастерская`, `Унитарный компас`, `Цех перестановок`, `Арена асимптотик`, `ML-полигон` |

### Уже готово

- Authoring-поля заполнены у всех миссий: audit (`make mission-audit`) даёт
  полный балл каждой миссии.
- Системный слой (curriculum graph, course map, reflection UI, MascotRole/Overlay)
  стабилен.
- Документы authoring/QA/accessibility/performance/deploy на месте.

### Ещё не готово

- Девять прототипов не прошли финальный available-pass.
- Polish backlog из ручного ревью не закрыт.
- Performance debt не автоматизирован.
- Нет ни одной `Sampler`-миссии.
- Нет реальной CI-публикации и smoke против prod.

## Приоритеты

### Фаза A (P0). Консолидация: довести прототипы до `available`

Цель: перевести минимум шесть из девяти прототипов в `available`, закрыть
технический долг. Без новых тем.

#### A1. Промоушн-конвейер для прототипов

Каждая миссия = одна итерация по шаблону из
[next_pedagogy_hardening_plan.md](next_pedagogy_hardening_plan.md):
diagnosis model → unit tests → field-level markers/result moment → input
fallback → mission metadata → Playwright mistake path → desktop/mobile
скриншоты.

Очередь и фокус (из [mission_human_review.md](mission_human_review.md)):

- `Матрица как машина` — challenge-варианты, убрать one-click уровни.
- `Евклидова мастерская` — field-level failure marker pass.
- `Цех перестановок` — финальный available-pass.
- `Орт. мастерская` / `ML-полигон` / `Арена асимптотик` — available-pass.

Готово на миссию, когда: есть diagnosis, field markers, mistake-path smoke,
скриншоты прошли ревью; `status` в `missionRegistry.ts` меняется на `available`,
`coverageStatus` узла → `review-ready`.

#### A2. Polish backlog из ручного ревью

- `PCA-компрессор`: residual hotspot marker + раскрыть metric tradeoff в
  финальном уровне.
- `Охота за ядром`: проверить, что row-equation residual board вынесен за
  пределы 3D-canvas (частично сделано в pedagogy-этапе).
- Mobile density review: `Унитарный компас`, `SVD-линза`,
  `Евклидова мастерская`.

#### A3. Performance triage

- Сконвертировать используемые PNG Меби в WebP/AVIF; неиспользуемые перенести в
  `_rejected`/reference, чтобы не попадали в bundle.
- Проверить lazy-loading 3D-chunk `KernelHunt` (Three.js не должен течь в
  initial route).
- Создать `scripts/check_bundle_budget.py`, парсящий Vite build output.
- Зафиксировать в [performance_budget.md](performance_budget.md) baseline и
  лимиты: mascot asset target, max route chunk, action при превышении.

Готово, когда рост ассетов проверяется автоматически, а не наблюдением.

#### A4. Recommendation + map ergonomics

- Доделать `recommendedMissionId`: незавершённая миссия → review-кандидат
  (давно пройдено или открывает новый навык) → planned/prototype next step.
- Mobile ergonomics `KernelHuntMission`: 3D-сцена не должна занимать почти весь
  первый экран.

### Фаза B (P1). Один новый домен: вероятность через `Sampler`

После консолидации добавить одну миссию механики, которой ещё нет, чтобы
проверить универсальность shell на не-геометрии и не-trace.

- Кандидат: **`Вероятностный стол` / `Бернулли-лаборатория`** (`Sampler`): seed,
  частоты, события, геометрическая вероятность, сходимость частоты к вероятности
  (ЗБЧ как видимый инвариант).
- Полный рецепт из README: curriculum node → mission brief → `samplerModel.ts` +
  tests → сцена → registry/navigation/courseMap → smoke → screenshots →
  QA checklist.

Почему вероятность раньше анализа и структур: домен частично есть в лекциях ШАД,
а `Sampler` — единственное механическое семейство без реализаций.

### Фаза C (P2). Расширение по roadmap

В порядке ценности "играбельной теоремы":

1. **Градиентный склон** (`GeometryLab`, мат. анализ): шаг, сходимость,
   осцилляция, взрыв.
2. **Кузница структур данных** (`StructureBuilder`): куча или DSU — первый
   builder, переиспользует trace-примитивы.
3. **Орбита корней** (алгебра P1): комплексные корни из единицы, правильный
   многоугольник.
4. **Фурье-синтезатор** / **DP-станция** — по остаточному приоритету.

### Сквозные задачи

- Smoke-архитектура: helpers по миссиям, mistake-path для всех `available`.
- Deploy на практике: CI-сборка `dist/`, smoke против preview/prod, замена
  dev-ссылок в лекциях на static-build варианты.
- Mascot as mechanic: расширить `MascotOverlay` (pivot/frontier/error-marker)
  ещё на 2-3 миссии.

## Рекомендуемый ближайший спринт

1. `npm install` → `make test-js` + `make interactive-build`, зафиксировать build
   baseline.
2. **A3** целиком (performance triage + `check_bundle_budget.py`).
3. **A1** на двух миссиях: `Матрица как машина` (challenge-варианты) и
   `Евклидова мастерская` (field markers) → промоушн в `available`.
4. **A2**: PCA residual hotspot marker.

После спринта `available`-миссий станет 6-7 из 13, техдолг по перформансу закрыт,
есть автоматический контроль bundle.

## Статус выполнения

### Заход 2026-06-08

- Зафиксирован baseline: `npm install`, тесты 97/97, build (`index` 631 kB,
  `KernelHunt` 927 kB lazy, `dist` ~3.3 MB).
- **A3 (performance)**: WebP-конверсия Меби оказалась уже сделанной; добавлен
  `scripts/check_bundle_budget.py` + `make bundle-budget`; обновлён
  `performance_budget.md` (baseline 2026-06-08, авто-проверка). 30 PNG-исходников
  (~25 MB) под git не бандлятся - вынесено как отдельное решение.
- **A1 `Матрица как машина` → `available`**: два challenge-уровня без one-click
  (скрытые столбцы, цель = образ единичного квадрата), unit tests, smoke,
  скриншоты. Audit 38/38.
- **A1 `Евклидова мастерская` → `available`**: field-level failure marker
  (`FieldPulse` + `RepairMarker` + `ResultMoment`), smoke на marker.
- **A2 PCA hotspot**: residual hotspot marker (worst-cell badge + danger-обводка),
  unit test, smoke. `PCA-компрессор` остаётся `prototype`.
- Итог первой части: `available` миссий 4 → 6 из 13.

### Заход 2026-06-08 (вторая часть)

- **A1 `Цех перестановок` → `available`**: добавлены `ResultMoment` и
  `RepairMarker` поверх уже существующей per-tile разметки и `MascotOverlay`.
- **A1 `Арена асимптотик` → `available`**: `ResultMoment` + `RepairMarker` по
  виду диагноза стратегии.
- **A1 `ML-полигон` → `available`**: `ResultMoment` + `RepairMarker`
  (train≫test, утечка danger, порог…).
- Smoke расширен marker-ассертами на все три. Итог: **9 из 13 `available`**.
- Тесты 100/100, ESLint чист, audit 0 warnings, smoke зелёный, build/bundle OK
  (initial JS 620 kB).

### Заход 2026-06-08 (третья часть) — Фаза A закрыта

- **A1** последние 4 прототипа → `available`: `Квадратичная линза`, `SVD-линза`,
  `PCA-компрессор` (+ next-бейдж на rail), `Унитарный компас`. У каждого
  `ResultMoment` + `RepairMarker` по диагнозу; smoke на result/repair.
- Mobile density `SVD-линза` и `Унитарный компас` проверена (панели стекаются,
  без horizontal overflow).
- **A4**: `recommendedMissionId` учитывает prerequisites (готовая миссия →
  любая незавершённая → завершённый review-кандидат), unit-тест добавлен;
  `KernelHunt` mobile — 3D ужата через адаптивный `min-h` в `MissionShell`,
  residual-board поднялся на ~130px.
- **Итог: 13 из 13 `available`.** Тесты 101/101, ESLint чист, audit 0 warnings,
  полный smoke (route screenshots + happy/mistake) зелёный, build/bundle OK.

### Статус Фазы A: завершена

Все 13 миссий `available` с diagnosis, field-level markers, mistake-path smoke и
проверенными desktop/mobile скриншотами.

### Фаза B (начата 2026-06-08): первая `Sampler`-миссия

- Добавлена **`Бернулли-лаборатория`** (новый раздел `probability`, механика
  `sampler`): 3 уровня — поймать 1/2, оценить смещённую монету, сузить коридор
  (ЗБЧ). Детерминированный seeded PRNG (mulberry32), линия сходимости частоты,
  result/repair-маркеры.
- Полный рецепт пройден: model + 10 unit-тестов, сцена, registry/navigation/
  curriculum/courseMap, lazy route, фильтр карты, smoke happy + mistake, lecture
  link на `SHAD/probability_theory/1_Probability_basics`.
- Новый домен/секция `probability` добавлены в типы, навигацию и фильтры карты.
- Audit 20/20, chunk 9.4 kB. **Итого 14 миссий, все `available`.**
- Тесты 111/111, ESLint чист, smoke зелёный, build/bundle OK.

### Сквозная задача: KaTeX split (2026-06-08)

- `VizPage` сделан lazy (`src/routes.tsx`): маршруты миссий грузятся отдельным
  chunk вместе с `VizPanel`/`MathBlock`/KaTeX. Карта курса больше не тянет KaTeX.
- **initial JS 642 → 370 kB raw** (90% → 53% бюджета); KaTeX (~263 kB) теперь в
  lazy `VizPage`-chunk. `check_bundle_budget.py` помечает `VizPage` и
  `KernelHuntMission` как heavy-lazy exempt. Запас под новые миссии восстановлен.
- Smoke зелёный после сплита (Suspense-граница на маршруте миссии не ломает
  навигацию).

### Фаза C (начата 2026-06-08): первая `GeometryLab`-миссия анализа

- Добавлен **`Градиентный склон`** (новый раздел `calculus`, механика
  `geometry-lab`): 3 уровня — скатиться в минимум, укротить шаг (взрыв), узкая
  долина (плохая обусловленность). Детерминированная f=ax²+by², траектория по
  контурам уровня, режимы too-slow / oscillating / exploded.
- Полный рецепт: model + 9 unit-тестов, сцена, новый домен/секция `calculus`,
  registry/navigation/curriculum/courseMap/filter, lazy route, smoke happy +
  mistake, lecture link на `7_functions_of_many_variables`.
- Audit 20/20, chunk 7.3 kB. **Итого 15 миссий, все `available`.**
- Тесты 120/120, ESLint чист, smoke зелёный, build/bundle OK (initial JS 377 kB
  благодаря KaTeX split).

### Фаза C: первая `StructureBuilder`-миссия (2026-06-08)

- Добавлена **`Куча-кузница`** (раздел `algorithms`, механика `structure-builder`,
  первая реализация семейства): 3 уровня — починить ребро, bubble-up вставки,
  sift-down корня. Двоичная min-heap как дерево, красные рёбра-нарушения, обмен
  узлов; sift-down требует меньшего ребёнка.
- model + 6 unit-тестов, сцена, registry/navigation/curriculum, lazy route,
  smoke happy + mistake. Без новой проводки домена (раздел `algorithms` уже был).
- Лекций по структурам данных в SHAD нет — `lessonPath` на программный обзор,
  без тега `lecture-linked`.
- Audit 20/20, chunk 5.9 kB. **Итого 16 миссий, все `available`.**
- Тесты 126/126, ESLint чист, smoke зелёный, build/bundle OK (initial JS 384 kB).
  Реализованы 3 из 6 механических семейств за проход: `sampler`, `geometry-lab`
  (анализ), `structure-builder`.

### Фаза C: корни из единицы, lecture-linked (2026-06-08)

- Добавлена **`Орбита корней`** (раздел `algebra`, механика `geometry-lab`,
  lecture-linked на `2_Complex numbers`): 3 уровня — треугольник, квадрат,
  пятиугольник. Перетаскиваешь z, его степени образуют правильный n-угольник;
  цель — первообразный корень e^(2πi/n). Диагностика modulus-off / angle-off /
  not-primitive (z=-1 для квадрата = вырожденный дигон).
- model + 6 unit-тестов, сцена с перетаскиванием и input fallback,
  registry/navigation/curriculum, lazy route, smoke happy + mistake.
- Audit 20/20, chunk 8.6 kB. **Итого 17 миссий, все `available`.**
- Тесты 132/132, ESLint чист, smoke зелёный, build/bundle OK (initial JS 390 kB).

### Фаза C: ряды Фурье, lecture-linked (2026-06-08)

- Добавлен **`Фурье-синтезатор`** (раздел `calculus`, механика `geometry-lab`,
  lecture-linked на `11_series_fourier`): 3 уровня — две гармоники, прямоугольник
  (нечётные гармоники 1/k), пила (знакочередование). Амплитуды 5 гармоник, energy
  ошибки = точное L2-расстояние спектров; виден феномен Гиббса.
- model + 6 unit-тестов, сцена с графиком сигнала, registry/navigation/curriculum,
  lazy route, smoke happy + mistake (range через native setter helper).
- Audit 20/20, chunk 6.2 kB. **Итого 18 миссий, все `available`.**
- Тесты 138/138, ESLint чист, smoke зелёный, build/bundle OK (initial JS 397 kB).

### Фаза C: геометрическая вероятность (2026-06-08)

- Добавлен **`Монте-Карло`** (раздел `probability`, механика `sampler` —
  вторая, lecture-linked на `1_Probability_basics`): 3 уровня — оценка π через
  четверть круга, площадь треугольника, площадь под параболой. Доля случайных
  точек = оценка площади (геом. вероятность как отношение площадей).
- model + 7 unit-тестов (детерминированный seeded PRNG), сцена со scatter,
  registry/navigation/curriculum, lazy route, smoke happy + mistake.
- Audit 20/20, chunk 6.9 kB. **Итого 19 миссий, все `available`.**
- Тесты 145/145, ESLint чист, smoke зелёный, build/bundle OK (initial JS 403 kB).

### Фаза C: метод Гаусса, state-machine (2026-06-08)

- Добавлена **`Гаусс-станция`** (раздел `algebra`, механика `state-machine`,
  lecture-linked на `3_Linear_equations`): 3 уровня — прямой ход, нулевая опора
  (обмен строк), дробные опоры. Клик по подсвеченным поддиагональным элементам
  зануляет их опорной строкой; «ready pivot»-инвариант держит порядок Гаусса;
  решение читается обратным ходом.
- model + 6 unit-тестов, сцена с матрицей-grid, registry/navigation/curriculum,
  lazy route, smoke happy + mistake.
- Audit 20/20, chunk 7.7 kB. **Итого 20 миссий, все `available`.**
- Тесты 151/151, ESLint чист, smoke зелёный, build/bundle OK (initial JS 410 kB).

### Фаза C: DSU / union-find, structure-builder (2026-06-08)

- Добавлен **`Лес связности`** (раздел `algorithms`, механика
  `structure-builder` — вторая): 3 уровня — связать всё, остов без циклов,
  оставить две группы (не брать мост). Клик по рёбрам объединяет компоненты;
  ребро внутри компоненты = цикл (красный); вершины раскрашены по компонентам.
- model + 7 unit-тестов (find/union/components), сцена с графом и кликабельными
  рёбрами, registry/navigation/curriculum, lazy route, smoke happy + mistake
  (force-click по SVG-рёбрам; collinear-рёбра убраны во избежание промахов).
- Лекций по структурам данных нет — `lessonPath` на программный обзор, без
  `lecture-linked`.
- Audit 20/20, chunk 6.7 kB. **Итого 21 миссия, все `available`.**
- Тесты 165/165, ESLint чист, smoke зелёный, build/bundle OK (initial JS 417 kB).
  Все 6 механических семейств теперь покрыты не менее чем двумя миссиями.

### Фаза C: динамическое программирование, code-trace (2026-06-08)

- Добавлена **`DP-станция`** (раздел `algorithms`, механика `code-trace`): 3
  уровня — COT/CAT, CAT/CART (вставка), FOOD/GOLD (расстояние 2). Заполняешь
  таблицу Левенштейна, кликая «готовые» клетки (зависят от left/top/diagonal);
  порядок вычислений как инвариант; ответ в правом нижнем углу.
- model + 7 unit-тестов, сцена с таблицей-grid, registry/navigation/curriculum,
  lazy route, smoke happy + mistake. Без лекции → программный обзор.
- Audit 20/20, chunk 7.5 kB. **Итого 22 миссии, все `available`.**
- Тесты 165/165 (24 файла), build/bundle OK (initial JS 423 kB / 60%).

### Фаза C: собственные векторы, lecture-linked (2026-06-09)

- Добавлены **`Собственные векторы`** (раздел `algebra`, механика `geometry-lab`,
  lecture-linked на `12_Eigenvectors_eigenvalues`): 3 уровня — λ=3, λ=1, λ=-1
  (переворот). Вращаешь v, ищешь направление, где A·v параллелен v; λ = vᵀAv.
  Диагностика not-aligned / wrong-eigenvalue.
- model + 8 unit-тестов, сцена с drag + угловым input fallback,
  registry/navigation/curriculum, lazy route, smoke happy + mistake.
- Audit 20/20, chunk 7.4 kB. **Итого 23 миссии, все `available`.**
- Тесты 173/173 (25 файлов), build/bundle OK (initial JS 430 kB / 61%).

### Фаза C: эйлеровы пути, state-machine (2026-06-09)

- Добавлен **`Эйлеров путь`** (раздел `combinatorics`, механика `state-machine`,
  lecture-linked на `4. Graphs`): 3 уровня — эйлеров цикл (bowtie), путь (house),
  конверт «не отрывая руки» (8 рёбер). Кликаешь вершины, проходя каждое ребро по
  разу; нечётные вершины - старты, пройденные рёбра зеленеют; диагностика
  invalid / stuck.
- model + 8 unit-тестов (проверка реальных маршрутов), сцена с кликабельными
  вершинами, registry/navigation/curriculum, lazy route, smoke happy + mistake.
- Audit 20/20, chunk 7.4 kB. **Итого 24 миссии, все `available`.**
- Тесты 181/181 (26 файлов), ESLint чист, smoke зелёный, build/bundle OK
  (initial JS 437 kB / 62%).

### Фаза C: дерево поиска, structure-builder (2026-06-09)

- Добавлено **`Дерево поиска`** (раздел `algorithms`, механика
  `structure-builder`): 3 уровня - найти лист (7), левый угол (2), неуспешный
  поиск (6 нет в дереве). Спускаешься по BST, кликая ребёнка по сравнению; путь
  зеленеет, диагностика wrong-branch.
- model + 6 unit-тестов, сцена с кликабельным деревом, registry/navigation/
  curriculum, lazy route, smoke happy + mistake. Без лекции -> программный обзор.
- Audit 20/20, chunk 6.7 kB. **Итого 25 миссий, все `available`.**
- Тесты 187/187 (27 файлов), build/bundle OK (initial JS 442 kB / 63%).

### Заметка о направлении

Mission breadth теперь очень широкая: 25 миссий, все 6 механик (>=3 у пяти из
них), все 6 доменов. Дальнейшая ценность - не в количестве, а в: (1) сквозной
задаче deploy на практике (CI dist, smoke против prod), (2) polish/ревью
существующих миссий, (3) точечных недостающих темах. Рекомендуется пауза в
добавлении новых миссий.

## Порядок работ

1. Установить зависимости, снять build/test baseline.
2. Performance triage и `check_bundle_budget.py` (A3).
3. Промоушн прототипов по очереди (A1), каждый с mistake-path smoke и
   скриншотами.
4. Закрыть polish backlog (A2).
5. Доделать recommendation и mobile ergonomics (A4).
6. Спроектировать и реализовать первую `Sampler`-миссию (Фаза B).
7. Обновить README, roadmap и этот документ статусом выполнения.

## Definition of Done

- Минимум шесть из девяти прототипов переведены в `available` с diagnosis,
  field markers, mistake-path smoke и проверенными скриншотами.
- Polish backlog из [mission_human_review.md](mission_human_review.md) закрыт
  или явно перенесён с обоснованием.
- Bundle budget проверяется автоматически; baseline и лимиты зафиксированы.
- Recommendation logic учитывает review-кандидатов.
- Появилась хотя бы одна `Sampler`-миссия с полным authoring-контрактом.
- `make lint-js`, `make test-js`, `make interactive-build` и полный Playwright
  smoke проходят на живом dev stack.

## Риски

- **Промоушн ради статуса.** Менять `prototype` → `available` только после
  реального diagnosis/markers/skreenshot pass, а не по таймеру.
- **Performance budget останется бумажным.** В этап обязан войти рабочий
  `check_bundle_budget.py`, а не только обновлённый документ.
- **`Sampler` уйдёт в "красивые графики".** Toy dataset, seed, видимая ошибка,
  проверяемая цель — иначе это калькулятор, а не игра.
- **Расползание на новые темы.** Фаза C не начинается, пока Фаза A не закрыта.

## Что не входит в этап

- Редактор миссий и backend.
- Аккаунты пользователей и оценивание.
- Реализация всех `StructureBuilder`/`DP` миссий сразу.
- Публичный прод-deploy, если нет отдельной задачи на публикацию.
