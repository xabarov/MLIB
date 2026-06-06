# SHAD — интерактивные визуализации

Браузерное приложение к лекциям ШАД: 3D-сцены с вращением камеры, формулы KaTeX, навигация по разделам.

Игровой план развития: [gameplay_roadmap.md](gameplay_roadmap.md).

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

## Статическая публикация

Сборка с `base: './'` — относительные пути к ассетам. После `npm run build` каталог `dist/` можно:

- открыть локально через `npm run preview`;
- положить на GitLab Pages / любой static host;
- закоммитить `dist/` в репозиторий, если viewer отдаёт файлы как есть (иначе собирать перед деплоем в CI).

Ссылка из лекции (пример):

```markdown
[Интерактивная модель](../../interactive/dist/index.html#/algebra/linear-maps/kernel)
```

Маршрут по умолчанию: `#/algebra/linear-maps/kernel`.

## Добавление визуализации

1. Конфиг геометрии (по возможности синхронизировать с `generate_visuals.py` лекции).
2. Компонент сцены в `src/visualizations/`.
3. Запись в `src/visualizations/registry.ts` (`available: true`, `component`, `path`).
4. `npm run build` и обновить ссылку в `lesson.md` при необходимости.

## Палитра

Токены в `src/theme/tokens.ts` совпадают с [lecture_visual_design_system.md](../lecture_visual_generation/lecture_visual_design_system.md).
