# SHAD — интерактивные визуализации

Браузерное приложение к лекциям ШАД: игровые миссии, 3D/2D-сцены,
формулы KaTeX, навигация по разделам и проводник Меби.

Игровой план развития: [gameplay_roadmap.md](gameplay_roadmap.md).
План закрытого игрового среза: [next_stage_plan.md](next_stage_plan.md).
План следующего содержательного этапа: [next_content_stage_plan.md](next_content_stage_plan.md).
План этапа карты и trace-механики: [next_course_map_trace_plan.md](next_course_map_trace_plan.md).
Текущий следующий этап: [next_consolidation_plan.md](next_consolidation_plan.md).
Этап системы производства миссий: [next_mission_authoring_system_plan.md](next_mission_authoring_system_plan.md).
Guide для новых миссий: [mission_authoring_guide.md](mission_authoring_guide.md).
Checklist качества миссии: [mission_quality_checklist.md](mission_quality_checklist.md).

## Стек

- Node.js 22 LTS (`.nvmrc`, `.node-version`; Docker использует `node:22-alpine`)
- Vite + React + TypeScript
- React Three Fiber + drei + three
- Zustand, React Router (HashRouter)
- Tailwind CSS v4, KaTeX
- Vitest, Python Playwright smoke

## Команды

```bash
cd SHAD/interactive
nvm use        # если используешь nvm
npm install
npm run dev      # http://localhost:5173/#/map
npm run build    # артефакт в dist/
npm run preview  # проверка статической сборки
```

Из корня репозитория:

```bash
make lint
make test-js
make interactive-test
make interactive-build
make interactive-smoke   # Playwright screenshots + full happy paths
make interactive-quality # lint + tests + build + smoke
make interactive-dev
make compose-dev   # Docker dev с hot reload
make compose-prod  # production nginx на http://localhost:8080
make compose-down
```

## Статическая публикация

Сборка с `base: './'` — относительные пути к ассетам. После `npm run build` каталог `dist/` можно:

- открыть локально через `npm run preview`;
- положить на GitLab Pages / любой static host;
- закоммитить `dist/` в репозиторий, если viewer отдаёт файлы как есть (иначе собирать перед деплоем в CI).

Ссылка из лекции (пример):

```markdown
[Игровая миссия](../../interactive/#/algebra/linear-maps/kernel)
```

Маршрут по умолчанию: `#/map`.
Карта курса: `#/map`.
Прототип цеха перестановок: `#/algebra/substitutions/workshop`.
Прототип определителя: `#/algebra/determinants/forge`.
Прототип матричной машины: `#/algebra/matrices/machine`.
Прототип графового trace: `#/combinatorics/graphs/dispatcher`.
Бернулли-лаборатория (вероятность): `#/probability/bernoulli/lab`.
Градиентный склон (анализ): `#/calculus/gradient/slope`.
Куча-кузница (структуры данных): `#/algorithms/heaps/forge`.
Орбита корней (комплексные числа): `#/algebra/complex-numbers/roots`.
Фурье-синтезатор (анализ): `#/calculus/fourier/synth`.
Монте-Карло (геом. вероятность): `#/probability/monte-carlo/area`.
Гаусс-станция (линейные уравнения): `#/algebra/linear-equations/gauss`.
Лес связности (DSU): `#/algorithms/dsu/forest`.
DP-станция (редакционное расстояние): `#/algorithms/dynamic-programming/edit-distance`.
Собственные векторы (eigen): `#/algebra/eigenvalues/chase`.
Эйлеров путь (графы): `#/combinatorics/euler/trail`.
Дерево поиска (BST): `#/algorithms/bst/quest`.

В исходных лекциях используем dev-friendly ссылки `../../interactive/#/...`.
Для опубликованной статической сборки их можно заменить на
`../../interactive/dist/index.html#/...`.

## Добавление миссии

1. Описать `MissionDefinition` и уровни в `src/game/missions.ts`.
2. Добавить тему в `src/game/curriculumGraph.ts`.
3. Вынести предметную логику в чистый model module рядом со сценой.
4. Добавить `*.test.ts` для model-функций и curriculum validation.
5. Сделать компонент сцены в `src/visualizations/<topic>/`.
6. Обернуть сцену в `MissionShell` и использовать `useMissionRuntime`.
7. Подключить запись в `src/visualizations/missionRegistry.ts`.
8. Подключить lazy import в `src/visualizations/routeLoaders.ts`.
9. Добавить пункт навигации в `src/visualizations/navigation.ts`.
10. Добавить устойчивые `data-testid` для Playwright.
11. Пройти [mission_quality_checklist.md](mission_quality_checklist.md).
12. Выполнить проверки.
13. Обновить ссылку в `lesson.md` только после успешной сборки.

## Архитектура

- `src/game/` - общий shell, runtime, feedback policy, takeaways, summaries,
  типы миссий и UI-компоненты.
- `src/game/courseMap.ts` - маршрут миссий, recommended next step и progress
  helpers для первого экрана.
- `src/game/curriculumGraph.ts` - учебный граф тем, prerequisites, лекции и
  связь с playable missions.
- `src/game/components/trace/` - очередь/стек, visited set, trace steps и
  инвариантные проверки для алгоритмических миссий.
- `src/visualizations/*/*Model.ts` - чистая математика без React/DOM.
- `src/visualizations/missionRegistry.ts` - playable/prototype mission metadata.
- `src/visualizations/navigation.ts` - дерево sidebar/drawer.
- `src/visualizations/routeLoaders.ts` - lazy imports.
- `src/store/progressStore.ts` - persistent progress с migration/reset для тестов.
- `TraceStep` в `src/game/missionTypes.ts` - минимальный контракт для будущих
  algorithm/programming/data-analysis миссий без преждевременного code editor.
- [accessibility_baseline.md](accessibility_baseline.md) - minimum viable
  accessibility для новых миссий.
- [performance_budget.md](performance_budget.md) - build/assets budget.
- [deploy_link_policy.md](deploy_link_policy.md) - policy ссылок и публикации.

## Playwright screenshots

`make interactive-smoke` пишет скриншоты в:

```text
/tmp/shad-interactive-screens/
```

Сейчас проверяются desktop/mobile маршруты:

- `kernel-*`;
- `substitution-*`;
- `determinant-*`;
- `matrix-*`;
- `graph-*`;
- `map-*`.

## Палитра

Токены в `src/theme/tokens.ts` совпадают с [lecture_visual_design_system.md](../lecture_visual_generation/lecture_visual_design_system.md).

## Типографика

- Display (заголовки): **Literata** (тёплая антиква, optical sizing, кириллица).
- Body: **Golos Text** (humanist sans, родная кириллица). KaTeX — для формул.
- Оба self-hosted (woff2, cyrillic+latin) в `src/assets/fonts/`, без CDN.
- Утилита `font-display` (Tailwind-токен `--font-display`) для заголовков;
  `.draft-grid` — бумажная текстура; `:focus-visible` — кольца фокуса.
- Аудит и план дизайна: [next_ui_design_plan.md](next_ui_design_plan.md).
