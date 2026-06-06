# SHAD Interactive: план этапа "система производства миссий"

Этот этап нужен, чтобы `SHAD/interactive` мог расти быстрее, но не превращался
в набор ручных прототипов. Сейчас уже есть карта курса, пять игровых миссий,
общий `MissionShell`, trace-примитивы, Playwright smoke и Docker dev/prod. Это
достаточно, чтобы перейти от "добавляем сцены" к "строим систему производства
учебных игровых миссий".

Короткая цель этапа: **сделать добавление следующей миссии воспроизводимым
процессом**. После этапа новая миссия должна начинаться не с копирования
компонента, а с curriculum entry, authoring spec, QA checklist и понятного
контракта проверки.

## Почему это следующий слой

Если сейчас просто добавлять новые игры, проект начнет расползаться:

- карта курса станет ручной раскладкой карточек;
- `missions.ts` превратится в большой файл со всем контентом;
- hints, takeaways и success criteria будут написаны в разном стиле;
- Playwright smoke будет знать слишком много о каждой сцене;
- accessibility, performance и deploy останутся "когда-нибудь потом";
- связь с лекциями будет зависеть от внимательности автора.

Поэтому следующий этап должен зафиксировать не очередную механику, а правила
создания механик.

## Цель продукта

Сделать так, чтобы для любой новой темы ШАД можно было быстро ответить:

1. стоит ли ей быть интерактивом;
2. где она стоит в учебном маршруте;
3. какой игровой инвариант пользователь трогает;
4. какие уровни нужны;
5. как проверяется успех;
6. какие подсказки и ошибки показываются;
7. как миссия связана с лекцией и QA;
8. как она проходит accessibility/mobile/smoke checks.

## Что считаем недостающими элементами системы

### 1. Curriculum graph

Сейчас `courseMap.ts` задает маршрут миссий, но не хранит полноценную учебную
структуру. Нужен граф курса:

- id темы;
- раздел программы;
- prerequisites;
- связанные лекции и QA;
- playable mission ids;
- planned mission ids;
- "какую идею должен унести пользователь";
- следующий рекомендуемый шаг;
- статус: `available`, `prototype`, `planned`, `needs-review`.

Это позволит карте курса перестать быть только UI-списком и стать учебной
моделью.

### 2. Authoring schema

Сейчас `MissionDefinition` хранит миссию в TypeScript, но нет отдельного
контракта "как автор пишет миссию". Нужен schema/doc layer:

- mission brief;
- level list;
- invariants;
- success conditions;
- hints ladder;
- mistakes/feedback;
- takeaways;
- lecture anchors;
- test plan;
- asset needs.

На первом этапе это может быть TypeScript schema + markdown guide, без YAML/JSON
парсера. Важно не prematurely build CMS.

### 3. Mission QA checklist

Нужен обязательный checklist перед включением миссии в карту:

- есть ли действие, а не просто картинка;
- есть ли игровой инвариант;
- понятна ли ошибка;
- есть ли перенос обратно в лекцию;
- не слишком ли много текста;
- есть ли unit tests для model;
- есть ли Playwright happy path;
- есть ли desktop/mobile screenshots;
- есть ли keyboard path или input fallback;
- не ломает ли миссия bundle/performance budget.

### 4. Hints ladder и проверка понимания

Сейчас есть один hint и takeaway. Следующий слой:

- `hintLevels`: мягкая подсказка, структурная подсказка, почти следующий ход;
- `mistakeFeedback`: объяснение типовой ошибки;
- `reflectionPrompt`: короткий вопрос после миссии;
- `transferTask`: "узнай эту идею в формуле/задаче".

Это не должен быть тест ради теста. Цель - соединить телесное понимание с
решением задач.

### 5. Accessibility baseline

Нужно зафиксировать системные правила:

- все игровые действия имеют keyboard path или числовой/input fallback;
- SVG/canvas имеют текстовые управляющие альтернативы;
- focus states заметны;
- есть `aria-label` у интерактивных элементов;
- motion уважает `prefers-reduced-motion`;
- цвет не является единственным носителем смысла;
- mobile controls имеют нормальную tap area.

### 6. Performance and assets budget

Меби и будущие visual assets могут быстро раздуть приложение. Нужен бюджет:

- лимит размера initial JS;
- лимит размеров PNG/WebP;
- lazy loading тяжелых сцен;
- правила для mascot assets;
- проверка bundle size в build output;
- решение по WebP/AVIF для персонажа.

### 7. Deploy and link policy

Локально уже понятно, но для публикации нужно закрепить:

- dev links в лекциях;
- replacement для static build;
- CI artifact path;
- pages/nginx behavior для HashRouter;
- smoke against preview/prod;
- что делать с `dist/`: коммитить или собирать в CI.

## Продуктовая цель этапа

После этапа новая миссия должна добавляться по одному рецепту:

1. записать curriculum node;
2. заполнить mission authoring brief;
3. написать чистую model-логику;
4. добавить React scene;
5. подключить registry/navigation/course map;
6. добавить links из лекций;
7. пройти QA checklist;
8. получить unit tests, smoke и screenshots.

## Приоритеты

### P0. Curriculum graph v1

Сделать отдельный слой данных вместо текущей ручной логики карты.

Рекомендуемые файлы:

- `src/game/curriculumTypes.ts`;
- `src/game/curriculumGraph.ts`;
- `src/game/curriculumGraph.test.ts`;
- обновить `src/game/courseMap.ts`, чтобы он строился из curriculum graph.

Минимальные типы:

```ts
type CurriculumNode = {
  id: string
  title: string
  section: 'algebra' | 'combinatorics' | 'algorithms' | 'data-analysis'
  lessonPaths: string[]
  qaPaths?: string[]
  prerequisites: string[]
  missionIds: string[]
  plannedMissionIds?: string[]
  takeaway: string
  status: 'available' | 'prototype' | 'planned' | 'needs-review'
}
```

Готово, когда карта курса использует не ручной массив карточек, а curriculum
graph + mission registry.

### P0. Mission authoring schema

Расширить `MissionDefinition` аккуратно, без большого переписывания:

- `reflectionPrompt?: string`;
- `transferTask?: string`;
- `qualityTags?: string[]`;
- `estimatedMinutes?: number`;
- `level.hintLevels?: string[]`;
- `level.mistakeFeedback?: string[]`;
- `level.successConditionLabel?: string`.

Добавить документ:

- `SHAD/interactive/mission_authoring_guide.md`.

В guide описать:

- когда миссия нужна;
- как выбирать механику;
- как формулировать уровни;
- как писать hints/takeaways;
- как связывать с лекцией;
- какие tests обязательны.

Готово, когда по guide можно спроектировать новую миссию без чтения всех
существующих компонентов.

### P0. Mission QA checklist

Добавить:

- `SHAD/interactive/mission_quality_checklist.md`;
- checklist section в `README.md`;
- ссылку из `mission_authoring_guide.md`.

Checklist должен быть коротким, но обязательным:

- game value;
- didactic value;
- model tests;
- Playwright smoke;
- desktop/mobile screenshots;
- accessibility;
- performance;
- lecture link.

Готово, когда PR/commit с новой миссией можно проверять по одному списку.

### P0. Example migration of existing mission

Взять одну существующую миссию и привести ее к новой authoring schema.

Лучший кандидат: **Графовый диспетчер**, потому что:

- уже есть trace model;
- есть уровни с явным состоянием;
- хорошо демонстрирует hints ladder и mistake feedback;
- полезен для будущих algorithms/data missions.

Сделать:

- добавить `hintLevels`, `mistakeFeedback`, `reflectionPrompt`, `transferTask`;
- использовать хотя бы один `mistakeFeedback` в UI;
- добавить unit tests для curriculum graph validation.

Готово, когда новая schema доказана на реальной миссии.

### P1. Reflection/transfer UI

Добавить компактный блок после mission summary:

- 1 reflection question;
- 1 transfer task;
- ссылка на лекцию.

Не делать:

- полноценный quiz engine;
- оценивание пользователя;
- длинные формы.

Рекомендуемые файлы:

- `src/game/components/MissionReflection.tsx`;
- обновить `MissionShell.tsx`;
- Playwright check, что блок появляется после полной миссии.

Готово, когда после прохождения миссии пользователь получает не только ключ, но
и короткий мост обратно к задачам.

### P1. Accessibility baseline

Добавить документ и минимальную реализацию:

- `SHAD/interactive/accessibility_baseline.md`;
- `prefers-reduced-motion` для reward animation;
- проверить `aria-label`/keyboard path для graph SVG;
- описать fallback policy для drag-heavy scenes.

Готово, когда новые миссии обязаны иметь keyboard/input path или явную задачу
на добавление fallback.

### P1. Performance/assets budget

Добавить документ:

- `SHAD/interactive/performance_budget.md`.

Зафиксировать:

- initial route target;
- lazy scene chunks;
- mascot asset policy;
- recommended WebP/PNG rules;
- when to split scenes;
- what to watch in Vite build output.

Опционально добавить script:

- `scripts/check_bundle_budget.py` или npm script, который парсит build output.

Готово, когда рост ассетов не остается слепой зоной.

### P1. Deploy/link policy

Добавить документ:

- `SHAD/interactive/deploy_link_policy.md`.

Закрыть:

- dev links in lessons;
- static replacement;
- HashRouter behavior;
- CI build target;
- smoke target for preview/prod;
- whether `dist/` is committed.

Готово, когда публикация не требует вспоминать договоренности из чата.

### P2. Smoke architecture cleanup

Текущий `smoke_playwright.py` уже полезен, но будет расти. Нужно выделить:

- route screenshot pass;
- mission happy path pass;
- helpers by mission;
- map/progress helpers;
- optional `--screens-only`, `--happy-paths-only`.

Готово, когда добавление новой миссии не превращает smoke file в длинный
сценарий без структуры.

## UX-направление этапа

Этот этап не должен делать новый большой визуальный слой. Он должен укрепить
то, что уже есть:

- карта курса остается рабочей, плотной и без hero-страницы;
- новые docs должны помогать автору быстро принять решение;
- reflection UI должен быть компактным, не похожим на экзамен;
- checklist должен быть применимым за 5 минут;
- accessibility и performance должны быть встроены в authoring flow, а не
  лежать отдельно как "когда-нибудь".

## Порядок работ

1. Создать `curriculumTypes.ts` и `curriculumGraph.ts`.
2. Перевести `courseMap.ts` на curriculum graph.
3. Добавить validation tests для curriculum graph.
4. Расширить `MissionDefinition` и `MissionLevel` authoring-полями.
5. Обновить `GraphDispatcherMission` как пример новой schema.
6. Добавить `MissionReflection` в `MissionShell`.
7. Написать `mission_authoring_guide.md`.
8. Написать `mission_quality_checklist.md`.
9. Написать `accessibility_baseline.md`.
10. Написать `performance_budget.md`.
11. Написать `deploy_link_policy.md`.
12. Рефакторить `smoke_playwright.py` на секции/helpers, не меняя поведение.
13. Обновить README и roadmap ссылками на новые документы.
14. Прогнать `make lint-python`, `make lint-js`, `make test-js`,
    `make interactive-build`, Playwright smoke against живой dev stack.
15. Проверить screenshots карты и графовой миссии глазами.

## Definition of Done

- Карта курса строится из curriculum graph, а не из ручного массива без
  prerequisites.
- Есть authoring guide для новых миссий.
- Есть quality checklist для ревью миссии.
- Есть baseline docs для accessibility, performance/assets и deploy/link policy.
- Хотя бы одна существующая миссия использует новую schema полностью.
- После полной миссии появляется reflection/transfer блок.
- Curriculum graph покрыт unit tests.
- Smoke script не стал менее понятным и продолжает проверять текущие маршруты.
- `make lint-python`, `make lint-js`, `make test-js`, `make interactive-build`
  и Playwright smoke проходят.

## Статус выполнения

Этап реализован как системный слой поверх существующих миссий:

- добавлены `curriculumTypes.ts`, `curriculumGraph.ts` и validation tests;
- `courseMap.ts` теперь строит карту из curriculum graph и mission definitions;
- `MissionDefinition` и `MissionLevel` расширены authoring-полями:
  `reflectionPrompt`, `transferTask`, `qualityTags`, `estimatedMinutes`,
  `hintLevels`, `mistakeFeedback`, `successConditionLabel`;
- "Графовый диспетчер" мигрирован как пример новой schema;
- добавлен `MissionReflection` в общий `MissionShell`;
- `GraphDispatcherMission` использует `mistakeFeedback`;
- добавлены:
  - `mission_authoring_guide.md`;
  - `mission_quality_checklist.md`;
  - `accessibility_baseline.md`;
  - `performance_budget.md`;
  - `deploy_link_policy.md`;
- reward animation получила `prefers-reduced-motion` fallback;
- `smoke_playwright.py` разделен на route screenshots и happy paths, добавлены
  режимы `--screens-only` и `--happy-paths-only`;
- README и roadmap обновлены ссылками на системные документы.

Осталось на следующий слой:

- применить новую authoring schema ко всем старым миссиям, не только к графовой;
- добавить второй не-графовый trace/data пример, чтобы проверить универсальность
  schema;
- автоматизировать bundle budget, если build output начнет расти быстрее.

## Риски

- **Слишком много документации, мало пользы.** Поэтому каждый документ должен
  быть коротким и использоваться в Definition of Done.
- **Преждевременный CMS.** Не делать YAML/JSON loader, пока TypeScript schema
  достаточно.
- **Authoring schema станет слишком общей.** Проверять ее на `Графовом
  диспетчере`, а не на воображаемой идеальной миссии.
- **Accessibility уйдет в декларации.** Минимум один реальный UI-fix должен
  войти в этап: reduced motion или keyboard/fallback.
- **Performance budget останется бумажным.** Минимум зафиксировать текущий
  build output как baseline.

## Что не входит в этап

- новая большая предметная миссия;
- редактор миссий;
- backend;
- аккаунты пользователей;
- полноценная система quiz/evaluation;
- публичный deploy, если нет отдельной задачи на публикацию.
