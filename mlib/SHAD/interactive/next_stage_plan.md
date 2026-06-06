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

Оставшиеся улучшения после этапа: более точное 3D-drag управление в Kernel
Hunt, прохождение всех уровней в Playwright и дальнейшая оптимизация веса
Kernel route chunk при необходимости.

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
