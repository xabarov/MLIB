# SHAD Interactive: план этапа "Game feel и available readiness"

Этот этап не добавляет новую предметную тему. После `PCA-компрессора` в
interactive уже есть 13 playable/prototype missions, и главный риск сместился:
миссий много, но ощущение качества пока неровное. Некоторые сцены выглядят как
маленькие игры, а некоторые все еще похожи на правильный worksheet с кнопками.

Фокус этапа: **единая система игровых реакций и ревизия лучших миссий до
статуса `available`**.

```text
prototype mission -> visible failure -> repair action -> success pulse -> debrief -> available candidate
```

## Статус 2026-06-07

P0 выполнен.

- Добавлены shared primitives: `FieldPulse`, `RepairMarker`, `ResultMoment`
  with reduced-motion-safe CSS.
- `Графовый диспетчер` получил expected ghost vertex, repair marker and result
  moment; smoke checks marker on mistake path.
- `Кузница определителя` получила field pulse, orientation/collapse repair
  marker and result moment; smoke checks determinant result moment and marker.
- `Фабрика признаков` получила dirty-column repair markers and pipeline clean
  result moment; smoke checks marker before and after repair.
- Создан manual review file
  [mission_human_review.md](mission_human_review.md), separate from generated
  `mission_quality_report.md`.
- `Кузница определителя`, `Графовый диспетчер` and `Фабрика признаков`
  promoted to `available` with evidence notes.

Оставшийся P1/P2 backlog:

- residual hotspot marker for `PCA-компрессор`;
- row-equation residual board for `Охота за ядром`;
- challenge variants for `Матрица как машина`;
- mobile density review for dense linear algebra missions.

## Почему это следующий этап

Сейчас уже закрыты крупные содержательные линии:

- алгебраическая геометрия матриц: determinant, kernel, quadratic forms,
  Euclidean projections, unitary geometry, SVD and PCA compression;
- первые programming/data slices: asymptotic strategy, ML thresholding,
  feature pipeline;
- authoring/runtime skeleton: `MissionShell`, `LevelStepper`, `RewardMeter`,
  `MascotCoach`, `MissionDebriefCard`, `mission-audit`, Playwright smoke.

Новая большая тема сейчас даст меньше пользы, чем полировка уже накопленных
миссий. Пользователь должен чувствовать не "я нажал правильную кнопку", а:

- я сделал выбор;
- поле изменилось;
- ошибка стала видимой;
- я починил состояние;
- итоговый инвариант остался в голове.

## Текущее состояние

В приложении 13 playable/prototype missions:

- `Охота за ядром`;
- `Кузница определителя`;
- `Матрица как машина`;
- `Квадратичная линза`;
- `Евклидова мастерская`;
- `Унитарный компас`;
- `SVD-линза`;
- `PCA-компрессор`;
- `Цех перестановок`;
- `Графовый диспетчер`;
- `Арена асимптотик`;
- `ML-полигон`;
- `Фабрика признаков`.

`mission_quality_report.md` сейчас зеленый по authoring audit, но этот audit
ловит наличие metadata, а не качество игрового ощущения. Поэтому следующий
этап должен добавить **human-facing quality evidence**:

- screenshots reviewed;
- boring-level candidates listed;
- one-click levels identified;
- visible-failure gaps identified;
- available candidates promoted only after focused polish.

## Цель этапа

Сделать один поперечный quality pass:

1. Ввести общие primitives для success/warning pulses and field markers.
2. Добавить visible failure / repair state в 3-4 приоритетные миссии.
3. Усилить роль Меби как маркера состояния на поле, а не только говорящей
   головы справа.
4. Добавить richer audit/report, который фиксирует human review notes.
5. Перевести 2-3 самые зрелые миссии из `prototype` в `available`.
6. Сохранить текущий validation уровень: lint, tests, build, mission audit,
   smoke and screenshot review.

## Приоритеты ревизии

| Приоритет | Миссия | Почему именно она | Цель этапа |
| --- | --- | --- | --- |
| P0 | `Графовый диспетчер` | Уже одна из самых игровых миссий; хороший кандидат на `available`. | Добавить ghost trace / repair path and promote if screenshots pass. |
| P0 | `Кузница определителя` | Сильная механика площади и ориентации, но можно усилить physical reaction. | Field pulse for area/orientation/collapse and available review. |
| P0 | `Фабрика признаков` | Хороший data workflow; уже есть mistakes and pipeline diff. | Добавить field-level warning markers and available review. |
| P1 | `Матрица как машина` | Понятная идея, но уровни worksheet-like. | Добавить challenge variants and stronger result moment. |
| P1 | `Охота за ядром` | Сильный 3D образ, но уровни близки по действию. | Улучшить residual/constraint feedback and camera-free comprehension. |
| P1 | `PCA-компрессор` | Новый stage, нужен polish после первого прохода. | Уточнить component rail, local artifact marker and available-readiness notes. |
| P2 | `Унитарный компас`, `SVD-линза`, `Евклидова мастерская` | Сложные сцены, уже playable, но плотные. | Mobile density pass and screenshot notes. |

## P0. Shared game-feel primitives

Добавить небольшой слой общих UI primitives, не новую runtime-систему:

```text
src/game/components/
  FieldPulse.tsx
  RepairMarker.tsx
  ResultMoment.tsx
  MissionQualityPanel.tsx
```

### `FieldPulse`

Назначение:

- success/warning pulse прямо на игровом поле;
- визуальная реакция на объекте, который изменился;
- уважает `prefers-reduced-motion`.

Props:

```ts
type FieldPulseTone = 'success' | 'warning' | 'danger' | 'target'

type FieldPulseProps = {
  tone: FieldPulseTone
  active: boolean
  label: string
  children: ReactNode
}
```

Acceptance:

- не меняет размеры layout;
- can wrap SVG/HTML scene fragments;
- has `data-testid="field-pulse-{tone}"`;
- reduced motion switches to outline/color only.

### `RepairMarker`

Назначение:

- коротко показывает, что именно сломано: edge, cell, point, axis, row;
- дает не текстовую лекцию, а spatial marker.

Examples:

- graph: wrong next frontier node;
- determinant: collapsed/negative oriented cell;
- PCA: max residual cell;
- feature factory: dirty column marker.

Acceptance:

- visible without relying on color alone;
- marker label is 1-3 words;
- does not cover controls or important data.

### `ResultMoment`

Назначение:

- короткая фиксация после успеха внутри поля, до debrief;
- показывает "что стало лучше" в одном объекте.

Examples:

- `det area locked`;
- `frontier repaired`;
- `test stayed honest`;
- `residual hotspot fixed`.

Acceptance:

- appears only on success;
- text under 48 characters;
- smoke can assert `data-testid="result-moment"`.

## P0. Mission polish: Graph Dispatcher

Goal:

```text
Сделать ошибку обхода видимой как ghost trace and repair path.
```

Current strength:

- frontier/visited/cost are already meaningful;
- BFS/DFS mechanics are close to a real game.

Work:

- add ghost next node for current algorithm;
- when user chooses wrong node, show:
  - wrong edge pulse;
  - expected frontier node marker;
  - short replay strip: `expected -> chosen -> repair`;
- add `ResultMoment` when trace becomes valid;
- review mobile screenshot after markers.

Acceptance:

- mistake path can be understood from graph field before reading diagnosis;
- Playwright mistake path checks ghost/repair marker;
- mission remains under current viewport without horizontal overflow;
- candidate for `status: available`.

## P0. Mission polish: Determinant Forge

Goal:

```text
Сделать площадь, ориентацию и вырожденность физически ощутимыми.
```

Current strength:

- determinant as area/orientation is one of the clearest game ideas.

Work:

- wrap parallelogram in `FieldPulse`;
- add orientation flip marker when sign changes;
- add collapse marker when determinant is near zero;
- add compact result moment:
  - `area matched`;
  - `orientation flipped`;
  - `basis collapsed`;
- tune existing smoke to assert result moment on final level.

Acceptance:

- success/warning is visible in the left field, not only in sidebar;
- determinant sign/collapse can be distinguished without color alone;
- candidate for `status: available`.

## P0. Mission polish: Feature Factory

Goal:

```text
Превратить pipeline mistakes в видимые dirty-column markers.
```

Current strength:

- pipeline diff and alternative cleaning actions already create real choice.

Work:

- add `RepairMarker` on dirty/risky columns:
  - missing values;
  - outliers;
  - leakage;
  - raw category;
  - split imbalance;
- add success result moment when pipeline becomes clean;
- keep table dense and operational, not decorative;
- update smoke to check one marker disappears after repair.

Acceptance:

- bad cleaning action leaves a visible artifact in table/pipeline;
- repair action removes marker;
- candidate for `status: available`.

## P1. Mission polish: Matrix Machine

Goal:

```text
Снизить worksheet feeling через challenge variants.
```

Work:

- add two matrix action variants:
  - "hit target point";
  - "keep grid line parallel";
- add wrong-column marker when user edits the wrong basis image;
- add result moment when columns explain the full transform.

Acceptance:

- at least one level has two plausible actions, not one obvious snap;
- model tests cover variant success condition;
- smoke covers one mistake.

## P1. Mission polish: Kernel Hunt

Goal:

```text
Сделать rank-nullity/residual relation visible without over-reading the 3D scene.
```

Work:

- add 2D residual board next to 3D field;
- highlight which row equation is still nonzero;
- add repair marker on nonzero residual;
- add result moment for `Ax = 0 and x != 0`.

Acceptance:

- mistake path shows which equation failed;
- zero-vector trap remains visible;
- no additional heavy 3D dependency.

## P1. Mission polish: PCA Compressor

Goal:

```text
Довести новый compression bench после первого implementation pass.
```

Work:

- mark worst residual cell directly on error heatmap;
- make component rail less horizontally clipped on desktop;
- add level-specific active metrics:
  - rank budget: storage/energy;
  - component detective: target cell;
  - quality gate: Frobenius/max-cell;
  - transfer: separation/dimension;
- add one more unit test for quality-gate fixture thresholds.

Acceptance:

- user can identify the residual hotspot without reading diagnosis;
- desktop/mobile screenshots show the component rail cleanly;
- smoke still passes after visual changes.

## P1. Available status policy

Promote a mission from `prototype` to `available` only when all are true:

- model layer has focused unit tests;
- smoke has happy path and at least one meaningful mistake path;
- route screenshots pass desktop/mobile visual review;
- mission audit has no warnings;
- no obvious one-click final level remains;
- error is visible on field for at least one representative mistake;
- debrief and reflection are short and useful.

Initial candidates:

1. `graph-dispatcher`;
2. `determinant-forge`;
3. `feature-factory`.

Do not promote:

- very new `pca-compression-lab` until one polish pass is complete;
- dense linear algebra missions until mobile density is reviewed.

## P1. Human quality report

Extend `mission_quality_report.md` beyond generated audit.

Option A:

- keep generated table at top;
- append manual section `## Human Review 2026-06-07`;
- include:
  - `Available candidates`;
  - `One-click risks`;
  - `Visible-failure gaps`;
  - `Screenshot notes`;
  - `Next polish backlog`.

Option B:

- create separate `mission_human_review.md`;
- leave generated report fully machine-owned.

Recommended: Option B, because `make mission-audit` rewrites the generated
report and would erase manual notes.

Create:

```text
SHAD/interactive/mission_human_review.md
```

Acceptance:

- generated audit remains machine-owned;
- human review survives rerunning `make mission-audit`;
- each available candidate has a short evidence note.

## P2. Mobile and accessibility pass

Work:

- review all 13 mobile screenshots;
- mark missions where:
  - primary field is too low;
  - controls require horizontal scrolling;
  - text truncates important words;
  - mascot/debrief crowds the action;
  - color carries meaning without shape/label.

Fix only P0/P1 candidates in this stage. Leave broad mobile overhaul for a
separate pass if needed.

Acceptance:

- no horizontal overflow;
- tap targets remain at least current size;
- mission controls keep stable heights;
- reduced motion mode keeps success/warning understandable.

## P2. Validation and tooling

Add or update tests:

- `make mission-audit`;
- `make interactive-test`;
- `make interactive-build`;
- `make lint-js`;
- `make lint-python`;
- Playwright happy/mistake smoke;
- Playwright screenshots.

Add smoke assertions where practical:

- `result-moment`;
- `repair-marker`;
- `field-pulse-success` or `field-pulse-warning`;
- one marker disappearing after repair.

Do not make visual polish untestable if a simple selector can capture it.

## Implementation order

1. Add shared primitives: `FieldPulse`, `RepairMarker`, `ResultMoment`.
2. Add minimal CSS/reduced-motion support for pulses and markers.
3. Polish `Графовый диспетчер` and update smoke.
4. Polish `Кузница определителя` and update smoke.
5. Polish `Фабрика признаков` and update smoke.
6. Add `mission_human_review.md` with available-readiness evidence.
7. Promote 1-3 missions to `available` if evidence supports it.
8. Polish `PCA-компрессор` residual hotspot and component rail.
9. Run full validation.
10. Update `gameplay_roadmap.md` and this plan status.

## Done criteria

The stage is done when:

- at least three missions have field-level visible failure/success markers;
- at least two missions are honestly promoted to `available`, or the plan
  records why no promotion happened;
- `mission_human_review.md` exists and survives `make mission-audit`;
- Playwright smoke covers at least one new repair marker and result moment;
- desktop/mobile screenshots have been inspected for changed missions;
- all standard validation commands pass;
- working tree has no unrelated churn.

## Risks

- **Over-animating serious math.** Pulses must clarify state, not decorate.
- **Breaking dense operational screens.** Feature Factory should stay utilitarian.
- **Promoting too early.** `available` should mean "safe to recommend", not
  "implemented once".
- **CSS drift.** Shared primitives should use existing palette/tokens.
- **Smoke fragility.** Assert stable semantic markers, not pixel positions.

## Suggested commit slices

First slice:

```text
feat(interactive): add shared game-feel markers
```

Scope:

- `FieldPulse`;
- `RepairMarker`;
- `ResultMoment`;
- reduced-motion CSS;
- small component tests if practical.

Second slice:

```text
feat(interactive): polish graph and determinant missions
```

Scope:

- graph ghost trace/repair marker;
- determinant field pulses/result moment;
- smoke updates.

Third slice:

```text
feat(interactive): add mission available review
```

Scope:

- Feature Factory polish;
- `mission_human_review.md`;
- status promotions;
- roadmap/status updates.
