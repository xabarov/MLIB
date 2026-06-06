# SHAD — интерактивные визуализации

Браузерное приложение к лекциям ШАД: игровые миссии, 3D/2D-сцены,
формулы KaTeX, навигация по разделам и проводник Меби.

Игровой план развития: [gameplay_roadmap.md](gameplay_roadmap.md).
План текущего этапа: [next_stage_plan.md](next_stage_plan.md).

## Стек

- Vite + React + TypeScript
- React Three Fiber + drei + three
- Zustand, React Router (HashRouter)
- Tailwind CSS v4, KaTeX

## Команды

```bash
cd SHAD/interactive
npm install
npm run dev      # http://localhost:5173/#/algebra/linear-maps/kernel
npm run build    # артефакт в dist/
npm run preview  # проверка статической сборки
```

Из корня репозитория:

```bash
make lint
make interactive-build
make interactive-smoke # Playwright desktop/mobile + базовые действия
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
[Игровая миссия](../../interactive/dist/index.html#/algebra/linear-maps/kernel)
```

Маршрут по умолчанию: `#/algebra/linear-maps/kernel`.
Прототип определителя: `#/algebra/determinants/forge`.

## Добавление миссии

1. Описать `MissionDefinition` и уровни в `src/game/missions.ts`.
2. Сделать компонент сцены в `src/visualizations/`.
3. Обернуть сцену в `MissionShell` и подключить Меби/feedback.
4. Добавить запись в `src/visualizations/registry.ts` с `kind: 'mission'`.
5. Выполнить `npm run lint`, `npm run build` и Playwright-проверку.
6. Обновить ссылку в `lesson.md` только после успешной сборки.

## Палитра

Токены в `src/theme/tokens.ts` совпадают с [lecture_visual_design_system.md](../lecture_visual_generation/lecture_visual_design_system.md).
