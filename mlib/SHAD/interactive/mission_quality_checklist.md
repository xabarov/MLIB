# SHAD Interactive: mission quality checklist

Использовать перед тем, как добавлять новую миссию в карту курса или менять
статус миссии на `available`.

## 1. Game Value

- [ ] У пользователя есть цель, ограничение и видимая обратная связь.
- [ ] Состояние меняется от действия пользователя.
- [ ] Есть автоматическая проверка успеха.
- [ ] Ошибка видна как нарушение инварианта, а не просто "неправильно".
- [ ] Миссия не дублирует статичную картинку из лекции.

## 2. Didactic Value

- [ ] У миссии есть понятный `takeaway`.
- [ ] Каждый уровень имеет свой `takeaway`.
- [ ] Есть `reflectionPrompt` или осознанная причина, почему он не нужен.
- [ ] Есть `transferTask` или ссылка на конкретное место в лекции.
- [ ] Текста внутри UI достаточно мало, чтобы игра оставалась игрой.

## 3. Authoring Contract

- [ ] Миссия описана в `MissionDefinition`.
- [ ] Тема добавлена в `curriculumGraph.ts`.
- [ ] Уровни имеют `hintLevels`.
- [ ] Типовые ошибки имеют `mistakeFeedback`.
- [ ] Уровни имеют `successConditionLabel`.
- [ ] Есть `qualityTags` и `estimatedMinutes`.

## 4. Architecture

- [ ] Предметная логика вынесена в `*Model.ts`.
- [ ] React-компонент не содержит скрытой математики, которую нельзя проверить.
- [ ] Миссия подключена к `missionRegistry.ts`.
- [ ] Lazy import добавлен в `routeLoaders.ts`.
- [ ] Навигация обновлена в `navigation.ts`.
- [ ] Карта курса показывает миссию в правильном месте.

## 5. Tests

- [ ] Есть unit tests для model.
- [ ] Curriculum graph validation проходит.
- [ ] Playwright smoke делает screenshot route.
- [ ] Playwright happy path проходит все уровни миссии.
- [ ] `git diff --check` чистый.

## 6. Accessibility

- [ ] Основное действие имеет keyboard path или input fallback.
- [ ] Интерактивные SVG/DOM элементы имеют `aria-label` там, где нужно.
- [ ] Focus state виден.
- [ ] Цвет не является единственным носителем смысла.
- [ ] Анимации уважают `prefers-reduced-motion`.
- [ ] Mobile tap targets достаточно крупные.

## 7. Performance

- [ ] Новые assets не раздувают initial route без необходимости.
- [ ] Тяжелые сцены lazy-loaded.
- [ ] Build output просмотрен после `npm run build`.
- [ ] Если добавлены PNG, проверен размер и формат.

## 8. Lecture Link

- [ ] Ссылка добавлена в `lesson.md` только после успешных проверок.
- [ ] Формат ссылки dev-friendly: `../../interactive/#/...`.
- [ ] Если нужна публикация, применена policy из `deploy_link_policy.md`.

## Required Commands

```bash
make lint-python
make lint-js
make test-js
make interactive-build
SHAD_INTERACTIVE_URL=http://127.0.0.1:5173 .venv/bin/python SHAD/interactive/scripts/smoke_playwright.py
```
