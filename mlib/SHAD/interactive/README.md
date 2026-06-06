# SHAD — интерактивные визуализации

Браузерное приложение к лекциям ШАД: игровые миссии, 3D/2D-сцены,
формулы KaTeX, навигация по разделам и проводник Меби.

Игровой план развития: [gameplay_roadmap.md](gameplay_roadmap.md).
План закрытого игрового среза: [next_stage_plan.md](next_stage_plan.md).
План следующего содержательного этапа: [next_content_stage_plan.md](next_content_stage_plan.md).

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
npm run dev      # http://localhost:5173/#/algebra/linear-maps/kernel
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

Маршрут по умолчанию: `#/algebra/linear-maps/kernel`.
Прототип цеха перестановок: `#/algebra/substitutions/workshop`.
Прототип определителя: `#/algebra/determinants/forge`.
Прототип матричной машины: `#/algebra/matrices/machine`.

В исходных лекциях используем dev-friendly ссылки `../../interactive/#/...`.
Для опубликованной статической сборки их можно заменить на
`../../interactive/dist/index.html#/...`.

## Добавление миссии

1. Описать `MissionDefinition` и уровни в `src/game/missions.ts`.
2. Вынести предметную логику в чистый model module рядом со сценой.
3. Добавить `*.test.ts` для model-функций.
4. Сделать компонент сцены в `src/visualizations/<topic>/`.
5. Обернуть сцену в `MissionShell` и использовать `useMissionRuntime`.
6. Подключить запись в `src/visualizations/missionRegistry.ts`.
7. Подключить lazy import в `src/visualizations/routeLoaders.ts`.
8. Добавить пункт навигации в `src/visualizations/navigation.ts`.
9. Добавить устойчивые `data-testid` для Playwright.
10. Выполнить `make interactive-quality`.
11. Обновить ссылку в `lesson.md` только после успешной сборки.

## Архитектура

- `src/game/` - общий shell, runtime, feedback policy, takeaways, summaries,
  типы миссий и UI-компоненты.
- `src/visualizations/*/*Model.ts` - чистая математика без React/DOM.
- `src/visualizations/missionRegistry.ts` - playable/prototype mission metadata.
- `src/visualizations/navigation.ts` - дерево sidebar/drawer.
- `src/visualizations/routeLoaders.ts` - lazy imports.
- `src/store/progressStore.ts` - persistent progress с migration/reset для тестов.
- `TraceStep` в `src/game/missionTypes.ts` - минимальный контракт для будущих
  algorithm/programming/data-analysis миссий без преждевременного code editor.

## Playwright screenshots

`make interactive-smoke` пишет скриншоты в:

```text
/tmp/shad-interactive-screens/
```

Сейчас проверяются desktop/mobile маршруты:

- `kernel-*`;
- `substitution-*`;
- `determinant-*`;
- `matrix-*`.

## Палитра

Токены в `src/theme/tokens.ts` совпадают с [lecture_visual_design_system.md](../lecture_visual_generation/lecture_visual_design_system.md).
