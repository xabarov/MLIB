# SHAD Interactive: план следующего этапа

Этот документ превращает общий `gameplay_roadmap.md` в рабочий план ближайшего
этапа. Цель этапа - перейти от одного 3D-viewer-маршрута к первому игровому
вертикальному срезу: игровой shell, Меби в UI, прогресс, одна доработанная
миссия по ядру и один новый 2D-прототип по определителю.

## Статус выполнения

Этап реализован как первый рабочий вертикальный срез:

- добавлены Python/ESLint gates, Docker dev/prod и корневой `Makefile`;
- runtime-ассеты Меби вынесены в `src/assets/game/mascot/`;
- добавлены `MissionDefinition`, `MissionShell`, progress store и UI-компоненты
  миссий;
- `/algebra/linear-maps/kernel` работает как миссия "Охота за ядром";
- `/algebra/determinants/forge` работает как 2D-прототип "Кузница
  определителя";
- лекции по линейным отображениям и определителям ссылаются на новые миссии;
- проверены `make lint-python`, `make lint-js`, `make interactive-build`,
  Docker compose config и Playwright desktop/mobile smoke.
- mission routes переведены на lazy imports: `DeterminantForgeMission` и
  `KernelHuntMission` грузятся отдельными chunks;
- добавлен `make interactive-smoke`: он поднимает Vite, делает desktop/mobile
  screenshots, проверяет Kernel Hunt через координаты `(-1,1,-1)` и
  Determinant Forge через drag до площади 2.

Следующий UX-first этап также выполнен: добавлена третья миссия, общий runtime,
model tests, mobile drawer и расширенный Playwright full happy path. Актуальные
остатки зафиксированы в разделе "Статус выполнения следующего этапа".

## UI/UX оценка текущего среза

Проверено по Playwright screenshots:

- `/tmp/shad-interactive-screens/kernel-desktop.png`;
- `/tmp/shad-interactive-screens/determinant-desktop.png`;
- `/tmp/shad-interactive-screens/kernel-mobile.png`;
- `/tmp/shad-interactive-screens/determinant-mobile.png`.

Сильные стороны:

- Меби уже работает как запоминающийся персонаж, а не как декоративная
  картинка: у него есть место в feedback-loop миссии.
- Kernel Hunt и Determinant Forge различаются по interaction style: 3D-control
  против 2D-drag, поэтому приложение не выглядит как набор одинаковых
  карточек.
- Правая панель на desktop хорошо держит цель, уровни, controls и подсказку.
- В Determinant Forge поле читается лучше всего: плоскость, векторы,
  параллелограмм и handles сразу объясняют, что можно трогать.
- Mobile screenshots не имеют горизонтального overflow, и миссии реально
  доступны с телефона.

Проблемы UX, которые стоит исправить до добавления новых тем:

- На mobile навигация занимает первый экран, поэтому пользователь сначала
  видит каталог, а не игру. Для игрового приложения первый viewport должен
  начинаться с миссии, а навигация должна быть drawer/overlay или компактной
  верхней строкой.
- Первый взгляд на desktop все еще ближе к "лабораторному viewer", чем к игре:
  цель уровня находится справа, а центральное поле не имеет своего
  action-oriented заголовка или явного next action.
- RewardMeter показывает прогресс, но награда пока не ощущается как игровая:
  нет короткого success moment, нет открытия следующего уровня как события,
  нет визуального "ключ получен".
- LevelStepper читается как табы формы. Для миссий лучше показать карту
  уровней: locked/completed/current, короткое название, состояние.
- Badges сверху сцены полезные, но выглядят как технические метрики. Нужен
  более смысловой слой: target badge, current badge, error/proximity badge.
- У Kernel Hunt 3D-сцена впечатляет, но взаимодействие через sliders справа
  делает ее менее tactile. Следующая итерация должна дать хотя бы один прямой
  drag/action в сцене.
- Меби и реплика находятся внизу правой панели, поэтому на desktop персонаж
  иногда воспринимается поздно. Важно, чтобы реакция Меби была рядом с
  результатом действия, а не только после всех controls.
- Тексты миссий короткие, но часть формулировок все еще звучит как объяснение
  из лекции. Нужен более игровой voice: "поймай", "сломай", "почини",
  "собери", при этом математика остается точной.

Дизайн-направление следующего этапа:

**Математическая мастерская с живыми приборами.** Не фэнтези и не детский
квест, а tactile lab: сетки, ручки, инвариант-ключи, аккуратные приборные
панели, теплый бумажный фон, цветовые состояния как математические сигналы.
Меби - дружелюбный напарник-куратор, который реагирует на действие, а не
рассказывает длинные инструкции.

## План следующего этапа: UX-first expansion

Цель этапа - превратить вертикальный срез в масштабируемую игровую основу для
алгебры, программирования и анализа данных. До новых больших тем нужно
укрепить shell, модель миссий, тесты и игровую подачу.

### Результат этапа

К концу этапа должно быть:

- 3-4 polished playable missions вместо 2 технических прототипов;
- mobile-first mission layout, где поле и цель видны раньше навигации;
- общий runtime для миссий без копирования success/unlock/mascot logic;
- чистые model modules с unit tests;
- обновленный визуальный язык уровней, наград и feedback;
- Playwright smoke, который проходит все уровни ключевых миссий;
- список следующих миссий по программированию и анализу данных с выбранными
  механиками.

### Этап 2.1. Архитектурная стабилизация перед расширением

Сделать до добавления третьей миссии:

1. Вынести общий runtime миссий.
   - `src/game/useMissionRuntime.ts`;
   - единый active level;
   - completed/unlocked;
   - safe completion без повторного начисления ключей;
   - helper `nextLevelId`;
   - derived progress для shell.

2. Вынести feedback policy.
   - `src/game/missionFeedback.ts`;
   - единые правила `idle/hint/thinking/warning/success`;
   - не держать выбор состояния Меби внутри каждой миссии.

3. Вынести предметную математику.
   - `linear-maps/kernelHuntModel.ts`;
   - `determinants/determinantForgeModel.ts`;
   - чистые функции без React/DOM/Three imports.

4. Разделить registry.
   - `missionRegistry.ts` для playable/prototype missions;
   - `navigation.ts` для sidebar/drawer tree;
   - `routeLoaders.ts` для lazy imports;
   - `registry.ts` оставить тонким фасадом.

5. Убрать двойной источник истины `available + status`.
   - сделать discriminated union для `available/prototype/planned`;
   - обновить `Sidebar` и `VizPage`.

Готово, когда новая миссия добавляется через definition + model + component, а
не копированием структуры из Kernel Hunt.

### Этап 2.2. UX shell polish

Desktop:

1. Пересобрать MissionShell в три ясных слоя:
   - scene field;
   - mission command panel;
   - feedback/reward strip.
2. Сделать objective strip над сценой или внутри верхнего слоя сцены:
   - текущая цель;
   - target value;
   - current state;
   - короткий next action.
3. Переработать badges:
   - `TargetBadge`;
   - `CurrentValueBadge`;
   - `ProximityBadge`;
   - `InvariantBadge` оставить для теоретического состояния.
4. LevelStepper заменить на compact mission map:
   - current;
   - completed;
   - locked;
   - reward per level.
5. Добавить success moment:
   - короткая анимация ключа;
   - Меби success;
   - кнопка/действие "следующий уровень";
   - без modal, чтобы не ломать flow.

Mobile:

1. Сайдбар перевести в drawer.
2. Верхний mobile header сделать компактным:
   - название миссии;
   - progress;
   - menu button.
3. Сцена должна начинаться в первом viewport после header.
4. Controls и Меби идут под сценой, но success feedback появляется рядом с
   текущим действием.
5. Проверить 390x844 и 430x932.

Готово, когда на mobile пользователь за 2-3 секунды понимает, что надо
потрогать, не прокручивая весь каталог.

### Этап 2.3. Доработка текущих миссий

Kernel Hunt:

1. Добавить direct manipulation:
   - минимум: drag endpoint в 3D через screen-space plane;
   - fallback: sliders остаются как точный режим.
2. Сделать второй и третий уровни реально отличающимися:
   - два разных решения;
   - direction/basis recognition;
   - финальный rank-nullity level как сборка равенства.
3. Улучшить визуальные подсказки:
   - projection ghost;
   - distance-to-kernel indicator;
   - цвет candidate vector по proximity.
4. Добавить Playwright прохождение всех 4 уровней.

Determinant Forge:

1. Сделать handles крупнее и tactile.
2. Добавить режим знака:
   - area fill меняет цвет по orientation;
   - вырожденность визуально схлопывает форму в линию.
3. Развести уровни:
   - площадь 2;
   - отрицательная ориентация;
   - det = 0;
   - repair from singular.
4. Добавить reset level и optional snap toggle.
5. Добавить Playwright прохождение всех 4 уровней.

Готово, когда обе миссии проходят не только smoke, а полный happy path.

### Этап 2.4. Третья миссия как проверка архитектуры

Добавить одну новую миссию, чтобы проверить, что shell не заточен только под
геометрию.

Кандидат A: **Матрица как машина**

- тема: `SHAD/algebra/6_Matrices/lesson.md`;
- механика: собрать матрицу из действий над базисными векторами;
- игра: пользователь двигает входные basis vectors и видит output vectors;
- цель: подобрать матрицу для заданного преобразования;
- польза: связывает матрицы, линейные отображения и операторы.

Кандидат B: **Ранг-ремонт**

- тема: `SHAD/algebra/4_Rank/lesson.md`;
- механика: row/column operations as moves;
- игра: минимальным числом ходов привести матрицу к нужному rank profile;
- цель: увидеть зависимость строк/столбцов через действие;
- польза: хорошо продолжает Kernel Hunt.

Выбор по умолчанию: сначала **Матрица как машина**, потому что она визуально
понятнее и лучше связывает уже открытые темы.

Готово, когда третья миссия использует общий runtime и model tests без новых
архитектурных исключений.

### Этап 2.5. Подготовка программирования и анализа данных

Не добавлять "текстовые тренажеры". Нужны только игровые механики, которые
интересно трогать.

Программирование:

- **Code Trace Runner**: пользователь переставляет/исполняет шаги алгоритма и
  видит состояние памяти.
- **Invariant Debugger**: нужно найти шаг, где ломается инвариант цикла.
- **Complexity Race**: две стратегии бегут по одному input, визуально растет
  стоимость.

Анализ данных:

- **Sampler Lab**: пользователь руками меняет выборку и видит bias/variance.
- **Metric Arena**: классификатор двигает порог, меняются precision/recall/F1.
- **Distribution Mixer**: собрать распределение из компонент и угадать
  статистики.

Для следующего этапа достаточно подготовить definitions и прототип
data-contract:

- `MissionMechanic: 'code-trace' | 'sampler' | 'model-arena'`;
- типы `MetricBadge`, `CostBadge`, `StateTrace`;
- не реализовывать полноценный code editor до отдельного решения.

### Этап 2.6. Тесты, качество и developer workflow

1. Добавить Vitest.
   - `npm run test`;
   - `make test-js`;
   - model tests для kernel/determinant.

2. Улучшить Playwright.
   - `data-testid` на mission root, handles, controls, mascot state,
     success feedback;
   - сброс localStorage перед тестом;
   - desktop + mobile full-level happy paths.

3. Обновить Makefile.
   - `make interactive-test`;
   - `make interactive-quality` = lint + test + build + smoke.

4. Обновить README.
   - как запускать dev/prod;
   - где лежат screenshots;
   - как добавлять новую mission.

Готово, когда перед коммитом можно запустить одну команду и получить честный
сигнал по JS/Python/build/e2e.

### Порядок выполнения следующего этапа

1. Архитектурная стабилизация: runtime, feedback, models, registry split.
2. Vitest и model tests.
3. MissionShell UX polish на desktop/mobile.
4. Полное прохождение Kernel Hunt.
5. Полное прохождение Determinant Forge.
6. Третья миссия "Матрица как машина".
7. Definitions для programming/data-analysis mechanics.
8. README и quality target.

### Definition of Done следующего этапа

- `make lint-python`, `make lint-js`, `make interactive-build` проходят.
- Есть `make test-js` или `make interactive-test` для model tests.
- `make interactive-smoke` проверяет desktop/mobile и полный happy path для
  двух основных миссий.
- На mobile первый meaningful viewport показывает миссию, а не длинный каталог.
- Третья миссия добавлена без дублирования runtime logic.
- План programming/data-analysis mechanics зафиксирован в roadmap без переноса
  лекционного текста как есть.

### Статус выполнения следующего этапа

Этап реализован:

- `useMissionRuntime` и `missionFeedback` вынесли общий runtime/feedback из
  компонентов миссий;
- Kernel Hunt, Determinant Forge и Matrix Machine используют чистые model
  modules;
- registry разделен на `registryTypes`, `missionRegistry`, `navigation` и
  `routeLoaders`;
- старое поле `available` заменено на `status`;
- добавлены Vitest model tests и `make test-js` / `make interactive-test`;
- mobile navigation переведена в drawer, первый mobile viewport начинается с
  миссии;
- `MissionShell` получил objective strip, mission map, success reward state и
  устойчивые `data-testid`;
- Playwright smoke сбрасывает `localStorage`, делает desktop/mobile screenshots
  трех миссий и проходит все уровни Kernel Hunt, Determinant Forge и Matrix
  Machine;
- добавлена миссия `/algebra/matrices/machine` и ссылка из
  `SHAD/algebra/6_Matrices/lesson.md`;
- добавлен `make interactive-quality`.

Оставшиеся улучшения после этапа:

- полировка 3D drag в Kernel Hunt до полноценного трехосевого режима:
  сейчас ручка тянется по плоскости текущего `z`, а `z` остается точным slider;
- более выразительная анимация "инвариант-ключ получен";
- убрать обрезание длинных названий уровней в mission map;
- отдельно спроектировать первую programming/data-analysis миссию.

## Архитектурное ревью после вертикального среза

Текущая структура уже достаточно хороша для первых двух миссий:

- `src/game/` отделяет игровой shell, типы миссий и UI-компоненты от конкретных
  визуализаций;
- `src/visualizations/` хранит предметные сцены;
- `src/store/` содержит независимые Zustand stores;
- mission routes грузятся через lazy imports и не утяжеляют стартовый route;
- runtime-ассеты Меби отделены от Photoshop/source истории.

Но перед добавлением следующих миссий нужно не дать вертикальному срезу
превратиться в набор похожих, но несовместимых компонентов. Ниже - refactor
backlog, который стоит сделать до P1-расширения или параллельно с первой новой
миссией.

### P0 refactor: вынести runtime-логику миссий из компонентов

Сейчас `KernelHuntMission.tsx` и `DeterminantForgeMission.tsx` одновременно
делают четыре вещи:

- хранят состояние уровня;
- считают предметную математику;
- определяют success/mascot/badges;
- собирают React UI.

Для двух миссий это терпимо. Для пяти миссий это начнет дублировать шаблон
`activeLevel`, `completeLevel`, `unlockLevel`, `levelSuccess`, `mascotState`.

Сделать:

- `src/game/useMissionRuntime.ts`:
  - active level;
  - completed/unlocked;
  - safe completion without repeated side effects;
  - helper `nextLevelId`;
  - derived `completedCount`.
- `src/game/missionFeedback.ts`:
  - общий тип `MissionRuntimeFeedback`;
  - helper для выбора `MascotState` по success/warning/hint.
- В миссиях оставить только предметную модель и scene-specific controls.

Готово, когда новая миссия не копирует вручную `useEffect(() => unlockLevel...)`
и `useEffect(() => completeLevel...)`.

### P0 refactor: разделить registry на навигацию и route loading

`src/visualizations/registry.ts` сейчас содержит:

- навигационное дерево;
- lazy imports компонентов;
- mission metadata;
- planned viewer entries.

Это удобно на старте, но при росте разделов файл станет главным merge-conflict
узлом.

Сделать:

- `src/visualizations/missionRegistry.ts` - только playable/prototype missions;
- `src/visualizations/navigation.ts` - дерево sidebar и planned entries;
- `src/visualizations/routeLoaders.ts` - lazy imports компонентов;
- оставить в `registry.ts` тонкий фасад `findVizByPath` / `allVizPaths`.

Готово, когда добавление новой миссии требует правки одного data-файла и одного
route-loader, а не большого смешанного registry.

### P0 refactor: вынести предметную математику в чистые modules

Сейчас вычисления ядра и определителя лежат внутри React components. Это мешает
точечному тестированию и будет плохо масштабироваться на алгоритмы/ML.

Сделать:

- `src/visualizations/linear-maps/kernelHuntModel.ts`:
  - `residual`;
  - `projectionToKernel`;
  - `isOnKernel`;
  - `isBasisAligned`;
  - level success predicates.
- `src/visualizations/determinants/determinantForgeModel.ts`:
  - `determinant`;
  - `snapCoord`;
  - `level success predicates`;
  - `svgPoint` или координатный mapper для тестов/drag.

Готово, когда model-функции можно импортировать в unit-тесты без React,
Three.js или DOM.

### P1 refactor: добавить unit tests для model functions

Сейчас есть Playwright smoke, но нет быстрых тестов предметной логики.
Перед алгоритмами и ML это станет важнее.

Сделать:

- добавить Vitest;
- `*.test.ts` рядом с model modules;
- проверить:
  - `(-1,1,-1)` дает `Ax=(0,0)`;
  - нулевой вектор не засчитывается как содержательное решение;
  - `det((1,0),(0,2)) = 2`;
  - вырожденность при коллинеарных векторах;
  - snap/clamp координат.

Готово, когда `npm run test` и `make test-js` входят в локальный quality gate.

### P1 refactor: типизировать статусы без `available + status`

Сейчас у entry есть и старое `available`, и новое `status`. Это переходный
слой, но со временем он будет давать неоднозначность.

Сделать discriminated union:

```ts
type VizEntry =
  | { status: 'available'; component: VizComponent; ... }
  | { status: 'prototype'; component: VizComponent; ... }
  | { status: 'planned'; component?: never; ... }
```

После этого убрать `available`.

Готово, когда `VizPage` и `Sidebar` не проверяют два источника истины.

### P1 refactor: нормализовать progress model

Сейчас `keys` глобальные. Для одного курса это ок, но позже появятся разделы,
серии миссий и, возможно, разные профили прогресса.

Сделать:

- хранить ключи по mission/domain:
  - `keysByMission`;
  - derived total keys;
- добавить schema version и migration для `localStorage`;
- добавить reset action для dev/test;
- в Playwright smoke сбрасывать progress перед проверкой.

Готово, когда повторный запуск тестов не зависит от старого localStorage.

### P2 refactor: стабилизировать visual test selectors

Smoke сейчас использует пользовательские тексты и `nth()` для spinbutton. Это
нормально для smoke, но хрупко для длинной e2e-сетки.

Сделать:

- добавить `data-testid` на:
  - mission root;
  - level buttons;
  - coordinate inputs;
  - determinant SVG handles;
  - mascot state;
  - success feedback.
- перевести Playwright на эти selectors.

Готово, когда можно менять UI-текст без переписывания e2e-тестов.

### P2 refactor: сделать отдельный UI-kit слой для игровых controls

`SliderControl` и `VectorReadout` сейчас живут внутри mission components. Их
лучше вынести после появления третьей миссии, чтобы не построить лишнюю
абстракцию заранее.

Сделать позже:

- `src/game/components/ScalarControl.tsx`;
- `src/game/components/VectorReadout.tsx`;
- `src/game/components/DraggablePlane.tsx` или `SvgPlane`.

Готово, когда второй/третий компонент реально переиспользует общий control.

## Цель этапа

К концу этапа приложение должно открываться как маленькая математическая игра,
а не как каталог визуализаций:

- есть единый игровой экран миссии;
- Меби встроен в интерфейс и реагирует на состояния `idle`, `hint`, `success`,
  `warning`, `thinking`;
- текущая сцена ядра превращена в миссию с проверяемой целью;
- добавлена первая 2D-миссия "Кузница определителя";
- прогресс по уровням сохраняется в `localStorage`;
- маршруты проверены через `npm run lint`, `npm run build` и Playwright
  screenshots desktop/mobile.

## Не цели этапа

- Не переносить в приложение текст лекций.
- Не добавлять много новых тем сразу.
- Не делать ML/алгоритмические миссии до стабилизации игрового shell.
- Не встраивать generated/raw Photoshop материалы в UI напрямую: финальные
  игровые ассеты должны лежать отдельно от source/reference папок.
- Не строить универсальный движок уровней раньше, чем появятся две разные
  playable миссии.

## Текущее состояние

- Стек: Vite, React, TypeScript, React Router HashRouter, Zustand, Tailwind,
  KaTeX, React Three Fiber.
- Сейчас есть один рабочий маршрут:
  `#/algebra/linear-maps/kernel`.
- Текущая сцена `KernelLineViz` показывает ядро как 3D-прямую и
  вспомогательную плоскость, но пока не имеет игровой цели.
- Навигация и metadata живут в `src/visualizations/registry.ts`.
- Состояние 3D-сцены живет в `src/store/sceneStore.ts`.
- Нормализованные transparent PNG Меби сейчас подготовлены в
  `src/assets/game/photoshop/gemini-2.5-flash/png-transparent/`.

## Продуктовое решение

Следующий этап называется **Playable Mission Shell**.

Главная механика этапа:

1. Пользователь выбирает миссию в навигации.
2. На первом экране он видит цель уровня, игровое поле и короткую реакцию Меби.
3. Пользователь меняет состояние поля руками.
4. Приложение считает инвариант/ошибку и само понимает успех.
5. После успеха открывается следующий уровень и начисляется инвариант-ключ.

Минимальный набор миссий:

| Маршрут | Название | Тип | Статус к концу этапа |
| --- | --- | --- | --- |
| `/algebra/linear-maps/kernel` | Охота за ядром | 3D + controls | playable, 4 уровня |
| `/algebra/determinants/forge` | Кузница определителя | 2D SVG/canvas | playable prototype, 4 уровня |

## Архитектура

### 1. Типы миссий

Добавить `src/game/missionTypes.ts`:

```ts
export type MissionDomain =
  | 'linear-algebra'
  | 'combinatorics'
  | 'algorithms'
  | 'data-analysis'

export type MissionMechanic =
  | 'geometry-lab'
  | 'state-machine'
  | 'structure-builder'
  | 'sampler'
  | 'model-arena'
  | 'code-trace'

export type MascotState =
  | 'idle'
  | 'hint'
  | 'success'
  | 'warning'
  | 'thinking'

export type MissionLevel = {
  id: string
  title: string
  objective: string
  hint: string
  successText: string
}

export type MissionDefinition = {
  id: string
  route: string
  title: string
  domain: MissionDomain
  mechanic: MissionMechanic
  lessonPath?: string
  difficulty: 1 | 2 | 3
  levels: MissionLevel[]
}
```

Пока не добавлять в `MissionDefinition` сериализуемые функции вроде
`successCondition`. Условия успеха лучше держать внутри конкретного компонента
миссии, потому что у 3D, 2D и ML-миссий будут разные состояния.

### 2. Реестр

Расширить `VizEntry` в `src/visualizations/registry.ts`:

- `kind: 'viewer' | 'mission' | 'prototype'`;
- `difficulty?: 1 | 2 | 3`;
- `lessonPath?: string`;
- `mission?: MissionDefinition`;
- `status?: 'available' | 'prototype' | 'planned'`.

Старое поле `available` можно временно оставить для совместимости, но новые UI
решения должны смотреть на `status` и `kind`.

### 3. Игровой shell

Добавить `src/game/components/`:

- `MissionShell.tsx` - общий экран миссии;
- `MissionHeader.tsx` - цель уровня, название, прогресс;
- `MascotCoach.tsx` - Меби, реплика и состояние;
- `RewardMeter.tsx` - инвариант-ключи и открытые уровни;
- `InvariantBadge.tsx` - математическое состояние;
- `CostBadge.tsx` - счетчик стоимости для будущих алгоритмов;
- `MetricBadge.tsx` - метрики для будущих data/ML сцен;
- `LevelStepper.tsx` - переход по уровням.

`MissionShell` должен принимать:

- `definition`;
- `activeLevel`;
- `mascotState`;
- `badges`;
- `scene`;
- `controls`;
- `feedback`.

### 4. Progress store

Добавить `src/store/progressStore.ts` на Zustand:

- `completedLevels: Record<string, string[]>`;
- `unlockedLevels: Record<string, string[]>`;
- `keys: number`;
- `completeLevel(missionId, levelId)`;
- `isLevelCompleted(missionId, levelId)`;
- persistence через `localStorage`.

Ключ localStorage: `shad-interactive-progress-v1`.

## Ассеты Меби

### 1. Разложить source и runtime assets

Оставить Photoshop/raw историю в:

```text
src/assets/game/photoshop/gemini-2.5-flash/
```

Скопировать финальные нормализованные PNG в runtime-папку:

```text
src/assets/game/mascot/mebi-idle.png
src/assets/game/mascot/mebi-hint.png
src/assets/game/mascot/mebi-success.png
src/assets/game/mascot/mebi-warning.png
src/assets/game/mascot/mebi-thinking.png
src/assets/game/mascot/mebi-hint-gesture.png
src/assets/game/mascot/mebi-thinking-focused.png
```

Runtime-файлы должны иметь единый прозрачный холст `608x800` и одинаковый
визуальный масштаб. Photoshop/source файлы можно держать для ручной доработки,
но компоненты приложения должны импортировать только `assets/game/mascot/*`.

### 2. Компонент

Добавить `src/game/components/MascotCoach.tsx`:

- выбирать PNG по `MascotState`;
- поддерживать короткую реплику;
- не занимать отдельную "карточку с персонажем", если можно встроить его в
  статусную область миссии;
- на мобильном экране уменьшать персонажа и не перекрывать игровое поле.

### 3. Правила визуального масштаба

- CSS-ширина персонажа в shell: `96-132px` desktop, `72-92px` mobile.
- Не масштабировать PNG через разные width/height для разных эмоций.
- Для `warning` и `thinking` не делать персонажа визуально "наказанием";
  состояние должно быть мягкой подсказкой, а не стресс-сигналом.

## Миссия 1: Охота за ядром

Связанные лекции:

- `SHAD/algebra/8_Linear_maps/lesson.md`;
- частично `SHAD/algebra/4_Rank/lesson.md`;
- частично `SHAD/algebra/3_Linear_equations/lesson.md`.

### Математическая модель

Использовать матрицу с ядром
`\mathrm{span}\{(-1,1,-1)\}`:

```text
A = [[1, 1, 0],
     [1, 0,-1]]
```

Тогда:

```text
Ax = (x + y, x - z)
ker A = span{(-1, 1, -1)}
rank A = 2
dim ker A = 1
```

### Игровое состояние

- `candidate: [x, y, z]`;
- `residual = Ax`;
- `error = sqrt(residual_0^2 + residual_1^2)`;
- `isZeroVector = ||candidate|| < epsilon`;
- `onKernel = error < epsilon && !isZeroVector`;
- `t = projection(candidate, direction)`;

### Управление

Первый playable вариант:

- 3 numeric steppers/sliders для `x`, `y`, `z`;
- 3D-сцена показывает candidate-вектор и его проекцию на линию ядра;
- кнопка "проверить" не нужна: проверка идет live.

Следующий вариант после стабилизации:

- draggable endpoint в 3D через plane/raycaster;
- snapping к линии ядра при близком успехе.

### Уровни

1. **Не ноль, но в ноль**  
   Найти любой ненулевой `x`, для которого `Ax = 0`.

2. **Прямая решений**  
   Найти два разных ненулевых решения и увидеть, что они лежат на одной
   прямой.

3. **Базис ядра**  
   Выбрать направление `(-1,1,-1)` или противоположное как базис ядра.

4. **Ранг плюс дефект**  
   Получить `rank A = 2`, `dim ker A = 1`, `3 = 2 + 1` как финальное состояние
   миссии.

### UI feedback

- `InvariantBadge`: `||Ax|| = ...`;
- `InvariantBadge`: `dim ker = 1`;
- `RewardMeter`: ключ за каждый уровень;
- Меби:
  - `idle`: пользователь меняет координаты;
  - `hint`: error уменьшается, но условие не выполнено;
  - `success`: `onKernel`;
  - `warning`: выбран нулевой вектор как формально верный, но неинтересный
    ответ.

## Миссия 2: Кузница определителя

Связанная лекция:

- `SHAD/algebra/5_Det/lesson.md`.

### Математическая модель

Две колонки матрицы как draggable-векторы на 2D-сетке:

```text
u = (a, c)
v = (b, d)
A = [[a, b],
     [c, d]]
det A = ad - bc
```

Площадь параллелограмма: `|det A|`.  
Ориентация: знак `det A`.  
Вырожденность: `det A = 0`.

### Реализация

Начать с SVG, не Three.js:

- `src/visualizations/determinants/DeterminantForge.tsx`;
- координатная сетка;
- две draggable-ручки векторов;
- параллелограмм с прозрачной заливкой;
- live badges: `det`, `area`, `orientation`, `invertible`.

SVG предпочтителен для первого варианта: меньше риска с drag/pointer events,
легче тестировать Playwright, быстрее получить tactile 2D-механику.

### Уровни

1. **Сделай площадь 2**  
   Настроить векторы так, чтобы `|det A| = 2`.

2. **Поменяй ориентацию**  
   Получить `det A < 0`, не меняя площадь ниже заданного порога.

3. **Сломай обратимость**  
   Сделать `det A = 0`, совместив направления.

4. **Почини матрицу**  
   Из вырожденного состояния вернуть `det A != 0` минимальным движением.

### UI feedback

- Цвет параллелограмма меняется по знаку det.
- При `det = 0` параллелограмм схлопывается в линию.
- Меби:
  - `success`: цель уровня выполнена;
  - `warning`: пользователь случайно ушел в вырожденность, когда нужна
    обратимость;
  - `hint`: det близок к цели.

## Дизайн-задачи этапа

### Визуальный принцип

Экран должен ощущаться как **математическая мастерская**, а не как учебный
дашборд:

- игровое поле занимает первое визуальное место;
- панели компактные и функциональные;
- текст в интерфейсе короткий;
- акценты означают математическое состояние, а не просто украшают экран;
- карточки использовать только для повторяемых/закрытых сущностей, не
  вкладывать карточки в карточки.

### Токены

Расширить `src/theme/tokens.ts` и `src/index.css`:

- `success`;
- `danger`;
- `target`;
- `energy`;
- `grid`;
- `paper`;
- `shadowInk`.

Не уходить в однотонную бежево-коричневую палитру: текущий теплый фон оставить,
но состояния должны давать разные смысловые акценты.

### Layout

Desktop:

- слева/сверху компактная навигация;
- центр: игровое поле;
- справа: цель уровня, badges, Меби, уровни.

Mobile:

- игровое поле первым;
- статус миссии одной строкой над полем;
- Меби и подсказка под полем;
- без горизонтального overflow.

## Порядок работ

### Шаг 1. Подготовить runtime assets

- Создать `src/assets/game/mascot/`.
- Скопировать нормализованные PNG из `photoshop/.../png-transparent/`.
- Переименовать файлы в runtime slugs без `v2/v3`.
- Добавить `src/assets/game/mascot/index.ts`.
- Проверить, что runtime PNG не имеют alpha на внешнем краю.

Готово, когда `MascotCoach` может импортировать все состояния из одного места.

### Шаг 2. Добавить типы и registry metadata

- Создать `missionTypes.ts`.
- Добавить `MissionDefinition` для `kernel-hunt`.
- Расширить `VizEntry`.
- Пометить текущий kernel route как `kind: 'mission'`.
- Добавить planned route для determinant forge.

Готово, когда sidebar может отличать playable, prototype и planned.

### Шаг 3. Собрать MissionShell

- Добавить компоненты shell.
- Встроить `MascotCoach`.
- Перенести текущий `VizPanel` в режим совместимости для viewer-страниц.
- Сделать `MissionShell` usable на desktop и mobile.

Готово, когда текущий kernel route визуально открывается как миссия, даже если
сама сцена еще почти статична.

### Шаг 4. Превратить KernelLineViz в KernelHunt

- Добавить candidate-вектор.
- Добавить координатные controls.
- Считать `Ax`, `||Ax||`, `onKernel`.
- Добавить 4 уровня.
- Сохранять завершение уровней в progress store.

Готово, когда пользователь может пройти все 4 уровня без чтения лекции.

### Шаг 5. Реализовать DeterminantForge

- Добавить route `/algebra/determinants/forge`.
- Сделать SVG-сетку и draggable-векторы.
- Считать det live.
- Добавить 4 уровня.
- Добавить связь с `SHAD/algebra/5_Det/lesson.md`.

Готово, когда миссия показывает площадь, ориентацию и вырожденность через
действия, а не через текстовое объяснение.

### Шаг 6. Обновить навигацию и лекционные ссылки

- Sidebar показывает доступные миссии отдельно от planned.
- В `SHAD/algebra/8_Linear_maps/lesson.md` обновить подпись ссылки: это уже
  миссия, а не просто модель.
- В `SHAD/algebra/5_Det/lesson.md` добавить ссылку на determinant forge только
  после прохождения build.

Готово, когда ссылки из лекций ведут на реально работающие маршруты.

### Шаг 7. QA и полировка

Команды:

```bash
cd SHAD/interactive
npm run lint
npm run build
npm run dev -- --host 127.0.0.1
```

Playwright использовать из repo `.venv` и системный Chromium
`/snap/bin/chromium`.

Проверить:

- desktop screenshot `1440x960`;
- mobile screenshot `390x844`;
- canvas/SVG не пустой;
- нет горизонтального overflow;
- Меби не перекрывает поле;
- все уровни достижимы;
- progress сохраняется после reload;
- `dist/` не попадает в git.

## Риски и решения

| Риск | Что делаем |
| --- | --- |
| 3D drag затянет первый срез | Начать Kernel Hunt со sliders/steppers, 3D drag оставить второй итерацией. |
| Меби будет занимать слишком много внимания | Ограничить размер, сделать реплики короткими, не анимировать постоянно. |
| Shell станет слишком общим | Поддерживать только две реальные миссии, обобщать после второго use case. |
| Determinant Forge превратится в калькулятор | Каждый уровень должен иметь цель и проверку, а не просто показывать det. |
| Навигация смешает будущие идеи с готовыми | Ввести `available/prototype/planned` и визуально разделить статусы. |

## Definition of Done этапа

- `kernel-hunt` и `determinant-forge` доступны из sidebar.
- В обеих миссиях есть 4 уровня, цель, live feedback и успех.
- Меби отображается из runtime assets и меняет состояние.
- Прогресс сохраняется в `localStorage`.
- Лекционные ссылки обновлены только для готовых маршрутов.
- `npm run lint` проходит.
- `npm run build` проходит.
- Есть Playwright desktop/mobile screenshots.
- `git status --short` не содержит `dist/`, `node_modules`, `.env`, `.venv`.
