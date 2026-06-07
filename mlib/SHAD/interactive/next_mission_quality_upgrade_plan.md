# SHAD Interactive: план этапа "Качество заданий и game feel"

Этот этап не добавляет новую большую тему. Его цель - поднять качество уже
существующих заданий: сделать их интереснее как игру, точнее как обучение и
менее похожими на чеклист "нажми правильную кнопку".

## Короткий ответ: интересные ли задания сейчас?

Да, база получилась хорошая: почти все миссии уже имеют действие, инвариант,
типовую ошибку, диагностику и перенос обратно в лекцию. Особенно сильны
`Графовый диспетчер`, `ML-полигон`, `Кузница определителя` и
`Фабрика признаков`: там пользователь видит состояние, делает выбор и получает
понятную реакцию.

Но качество пока неровное:

- часть уровней решается как одиночная правильная операция;
- не хватает "interesting failure": ошибки иногда просто сообщаются текстом,
  а не превращаются в видимое состояние, которое хочется починить;
- Меби реагирует полезно, но редко становится частью игрового поля;
- progression внутри миссии иногда линейный: уровень 2 похож на уровень 1 с
  другими числами;
- мало вариативности: после прохождения почти нет причины попробовать другой
  путь или увидеть альтернативную стратегию;
- связь с лекциями уже есть в metadata, но в самом приложении не всегда ясно,
  какую именно идею пользователь только что унес.

Следующий этап должен превратить задания из "корректных интерактивных задач" в
"маленькие игровые ситуации".

## Статус 2026-06-07

Этап выполнен для основного P0/P1-среза:

- `Фабрика признаков` получила альтернативные cleaning actions: `fill zero`,
  `drop NA`, `keep raw`, disable useful feature, а также `PipelineDiff`;
- добавлен пятый уровень `Проверь split` с тремя seed-кандидатами и проверкой
  label/range gap;
- `Арена асимптотик` получила `StrategyRace`, где ошибочная стратегия видимо
  проигрывает по total cost;
- `Цех перестановок` получил `CycleRail`, ghost-route цели, подсветку текущих
  стрелок and swap budget stars;
- добавлен общий `MissionDebriefCard` после полного прохождения миссии;
- добавлен `make mission-audit`, который генерирует
  [mission_quality_report.md](mission_quality_report.md);
- Playwright smoke расширен на `pipeline-diff`, `strategy-race`,
  `cycle-rail`, `mission-debrief` and split happy path.

Оставшийся P2 после этого этапа: более тонкие success/warning pulses на
игровом поле и содержательная ревизия всех уровней на статус `available`.
Подробный план этого продолжения вынесен в
[next_game_feel_available_stage_plan.md](next_game_feel_available_stage_plan.md).

## Рубрика качества

Каждую миссию оцениваем по семи осям:

1. **Agency** - пользователь делает осмысленный выбор, а не угадывает кнопку.
2. **Visible State** - действие меняет поле, а не только текст diagnosis.
3. **Interesting Failure** - ошибка оставляет понятный след и ее можно чинить.
4. **Progression** - уровни добавляют новое ограничение, а не повторяют ход.
5. **Transfer** - после победы понятно, как это связано с лекцией или задачей.
6. **Pacing** - первый успех быстрый, но финал требует осмысления.
7. **Game Feel** - есть микронаграда, реакция Меби, движение, ощущение
   "собрал/починил/нашел".

Минимальная планка для `available`: 5/7 осей закрыты явно, а `Interesting
Failure` и `Transfer` обязательны.

## Оценка текущих миссий

| Миссия | Что уже хорошо | Что мешает интересу | Приоритет улучшения |
| --- | --- | --- | --- |
| `Охота за ядром` | Сильный 3D-образ, есть residuals and nonzero constraint. | 3D может ощущаться как подбор координат; второй и третий уровни близки по действию. | P1 |
| `Кузница определителя` | Отличная "сломай/почини" механика площади, знака и вырожденности. | Хочется больше физической реакции: площадь, ориентация и collapse могут быть выразительнее. | P2 |
| `Матрица как машина` | Очень ясная идея столбцов как образов базиса. | Уровни похожи на worksheet с ручками; мало сюрприза и вариативности. | P1 |
| `Цех перестановок` | Хорошая state-machine база: циклы, знак, бюджет swaps. | Визуально поле сухое; циклы видны текстом, а не как маршрут. | P0 |
| `Графовый диспетчер` | Одна из лучших миссий: frontier/visited/cost реально играют. | Ошибка порядка могла бы показывать ghost trace and repair path. | P1 |
| `Арена асимптотик` | Есть настоящий выбор стратегии и разные сценарии входа. | Много текста и карточек; не хватает "гонки" стратегий на входах. | P0 |
| `ML-полигон` | Хорошее живое действие: порог, ошибки, train/test, leakage. | Ошибочные точки можно сделать более говорящими; нужен before/after moment. | P1 |
| `Фабрика признаков` | Хорошая pipeline-метафора и shared primitives. | Первые уровни рискуют стать one-click tasks; нужен выбор между плохим и хорошим cleaning. | P0 |

## Главная гипотеза этапа

Самый быстрый прирост качества даст не новая математика, а три поперечных
механики:

1. **Mistake Replay** - после ошибки поле показывает, что именно сломалось, и
   предлагает repair action.
2. **Choice Pressure** - у уровня есть 2-4 правдоподобных действия, из которых
   одно хорошее в текущем контексте.
3. **Result Moment** - после успеха появляется короткая визуальная фиксация:
   маршрут замкнулся, стоимость сравнилась, pipeline стал зеленым, test
   удержался.

## P0. Сделать задания менее one-click

### `Фабрика признаков`

Проблема: уровни `missing-values`, `leakage-off`, `encode-category` сейчас
могут проходиться одной очевидной кнопкой.

Сделать:

- добавить альтернативные действия:
  - `drop missing rows`;
  - `fill with zero`;
  - `keep raw category`;
  - `disable useful feature`;
- показывать последствия:
  - coverage падает после drop;
  - stability падает после fill zero;
  - raw category не дает model-ready score;
  - полезный feature off ухудшает test stability;
- добавить `PipelineDiff`: before/after по `rows`, `missing`, `leakage`,
  `test stability`;
- сделать уровень `Проверь split` настоящим пятым уровнем:
  - 3 seed-кандидата;
  - label gap and range gap;
  - успех: balanced split без leakage.

Acceptance:

- [x] happy path все еще проходит за 4-6 кликов;
- [x] mistake path проверяет минимум два плохих cleaning action;
- [x] `PipelineStrip` показывает плохие шаги красным и repair после них.

### `Арена асимптотик`

Проблема: карточки стратегий полезны, но экран ощущается как decision table.

Сделать:

- добавить `StrategyRace`:
  - 2-4 горизонтальные дорожки стратегий;
  - по выбранному сценарию видно setup, comparisons, query cost;
  - победитель доезжает первым;
- добавить переключатель входов внутри уровня:
  - `n=12`, `n=512`, `n=2048`;
  - strategy может быть хорошей на одном n и плохой на другом;
- сделать mistake replay:
  - выбранная стратегия не просто "wrong", а проигрывает видимой гонкой.

Acceptance:

- [x] на первом уровне пользователь видит, почему setup не окупился;
- [x] на втором уровне пользователь видит, где quadratic growth проигрывает;
- [x] smoke проверяет не только текст success, но и наличие race result.

### `Цех перестановок`

Проблема: текущая запись `1 -> 1` корректна, но игровой объект слабоват.

Сделать:

- добавить `CycleRail`:
  - позиции как станции;
  - стрелки текущей перестановки;
  - целевой цикл как ghost-route;
- после swap подсвечивать:
  - какие стрелки починились;
  - какие сломались;
  - как изменилась четность;
- добавить "swap budget stars": 3/4/5 ходов визуально, без лишнего текста.

Acceptance:

- [x] пользователь видит цикл без чтения циклической записи;
- [x] ошибка "разорван маршрут" видна на поле;
- [x] parity change получает отдельный visual pulse through state/budget feedback.

## P1. Усилить learning transfer

Сейчас `reflectionPrompt` and `transferTask` есть в definitions, но часто
живут после миссии как формальная карточка. Нужно сделать финал миссии
короче, но полезнее.

Сделать общий компонент `MissionDebriefCard`:

- `What changed` - одно наблюдение из состояния;
- `Invariant` - формальная фраза;
- `Try in lecture` - короткая ссылка на lecture anchor;
- `One question` - reflection prompt.

Примеры:

- kernel: "Ты занулил обе строки Ax, но не взял нулевой вектор";
- determinant: "Площадь исчезла, потому что столбцы стали зависимыми";
- graph: "Порядок visited совпал не с картинкой, а с очередью";
- ML: "Train вырос, но test показал leakage".

Acceptance:

- [x] debrief появляется после последнего уровня;
- [x] текст не длиннее 4 коротких строк;
- [x] smoke проверяет `mission-reflection` and `mission-debrief`.

## P1. Добавить quality scoring для миссий

Сейчас `mission_quality_checklist.md` полезен, но ручной. Нужен легкий
машинный audit, который ловит самые частые проблемы.

Сделать script:

- `scripts/audit_mission_quality.ts` или `scripts/audit_mission_quality.py`;
- проверяет `missionDefinitions` на:
  - все уровни имеют `hintLevels`, `mistakeFeedback`, `takeaway`;
  - `takeaway` не равен `objective`;
  - `successConditionLabel` есть;
  - `qualityTags` включают хотя бы один mechanic tag and one validation tag;
  - `nextPrompt` есть у всех уровней кроме финальных исключений;
- выводит score по миссиям.

Acceptance:

- [x] `make mission-audit` добавлен в Makefile;
- [x] audit не блокирует build сначала, но печатает warnings;
- [x] результаты записаны в `mission_quality_report.md`.

## P2. Game feel polish

Сделать единый pass по ощущениям:

- success pulse на игровом поле, не только в правой панели;
- warning pulse на сломанном объекте;
- короткая анимация Меби при success/warning с учетом reduced motion;
- стабильные размеры controls, чтобы смена текста не прыгала;
- compact mobile order:
  1. goal;
  2. game field;
  3. action controls;
  4. diagnosis;
  5. mascot/debrief.

Acceptance:

- Playwright screenshots desktop/mobile по P0-миссиям визуально проверены;
- `prefers-reduced-motion` не ломает feedback;
- нет horizontal overflow.

## P2. Содержательная ревизия уровней

После P0/P1 пройтись по всем 8 миссиям и для каждой ответить:

- какой уровень самый скучный;
- где есть only-one-obvious-action;
- где ошибка объясняется текстом вместо состояния;
- какой финальный takeaway должен остаться в голове;
- есть ли смысл добавить random seed or challenge variant.

Результат зафиксировать в `mission_quality_report.md`:

- score до/после;
- список оставшихся P1/P2 задач;
- candidates for `available` status.

## Рекомендуемый порядок работ

1. `Фабрика признаков`: alternative cleaning actions + PipelineDiff.
2. `Арена асимптотик`: StrategyRace and visible cost replay.
3. `Цех перестановок`: CycleRail and swap feedback.
4. `MissionDebriefCard`: общий финал для всех миссий.
5. `mission quality audit`: script + report.
6. Screenshot review and smoke updates.
7. Обновить `mission_quality_checklist.md`, `gameplay_roadmap.md` and
   `performance_budget.md`.

## Quality Gate

Для этапа нужны:

```bash
make lint-python
make lint-js
make test-js
make interactive-build
SHAD_INTERACTIVE_URL=http://127.0.0.1:5173 .venv/bin/python SHAD/interactive/scripts/smoke_playwright.py
git diff --check
```

Дополнительно:

- desktop/mobile screenshots для `feature-factory`, `asymptotic`,
  `substitution`;
- ручная проверка, что каждый P0 уровень имеет не только success, но и
  интересную ошибку;
- обновленный `mission_quality_report.md`.
