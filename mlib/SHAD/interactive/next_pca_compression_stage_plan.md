# SHAD Interactive: план этапа "PCA-компрессор"

Этот этап продолжает связку `Унитарный компас -> SVD-линза` и закрывает
оставшийся planned-хвост `pca-compression-lab` в `complex-geometry` and
`svd-pca`. Сейчас пользователь уже видит, что SVD превращает круг в эллипс,
как появляются singular values, почему `A^*A` важен и как PCA выбирает
направление максимальной дисперсии. Но пока нет отдельной игровой сцены, где
усеченное SVD/PCA становится практическим решением: **что оставить, что
выбросить, сколько это стоит и как выглядит ошибка**.

Главный фокус: **PCA-компрессор**. Пользователь сжимает маленькую матрицу,
тепловую карту или мини-изображение через сингулярные компоненты. Это не должно
быть демо "вот картинка стала мутной". Игровой смысл: найти компромисс между
качеством восстановления, бюджетом памяти and честной ошибкой.

```text
matrix/image -> centered data -> singular components -> rank-k budget -> reconstruction -> error map
```

## Статус 2026-06-07

P0 выполнен.

- Добавлена playable mission `/algebra/svd/pca-compression` with id
  `pca-compression-lab` and title `PCA-компрессор`.
- Добавлен pure model layer `pcaCompressionModel.ts` with deterministic small
  matrix fixtures, Jacobi eigen decomposition for `A^T A`, low-rank
  reconstruction, centering helpers, storage/energy/error metrics and
  diagnostics.
- Добавлены focused tests for rank-k reconstruction, monotone retained energy,
  storage cost, local artifact detection, centering and no-NaN paths.
- Миссия подключена в `MissionDefinition`, route loader, registry, navigation
  and curriculum graph.
- `pca-compression-lab` removed from planned mission lists and added to
  `svd-pca.missionIds`.
- Playwright smoke covers the route, happy path, mistake path and screenshots.
- Mission audit обновлен: `PCA-компрессор: 32/32`.
- Validation пройдена: JS lint, Python lint, Vitest, build, mission audit,
  Playwright happy/mistake smoke and screens-only smoke.

## Почему это следующий этап

В приложении уже есть нужный фундамент:

- `SVD-линза` показывает circle-to-ellipse geometry, singular directions,
  rank-1 shadow and PCA cloud;
- `Унитарный компас` делает понятным `A^*A` and Hermitian geometry;
- `Фабрика признаков` and `ML-полигон` уже ввели data-подход: train/test,
  metrics, leakage and pipelines;
- `mission_quality_report.md` показывает, что текущие миссии проходят
  authoring audit без warnings.

Следующий шаг должен быть прикладным, но не превращаться в пассивную галерею.
Хорошая миссия должна заставить пользователя сделать несколько выборов:

- сколько компонентов оставить при fixed storage budget;
- какую компоненту нельзя выбрасывать, даже если визуально она кажется слабой;
- почему centering меняет PCA;
- когда rank-1 approximation хороша, а когда нужна rank-2/rank-3;
- чем отличаются Frobenius error, retained energy and visible artifact.

## Текущее состояние planned gap

До начала этапа `pca-compression-lab` упоминался как planned mission:

- `complex-geometry.plannedMissionIds`;
- `svd-pca.plannedMissionIds`.

После выполнения этапа:

- `pca-compression-lab` стал playable mission;
- `complex-geometry.plannedMissionIds` no longer includes it;
- `svd-pca.missionIds` includes both `svd-lens` and
  `pca-compression-lab`;
- `svd-pca.plannedMissionIds` removed;
- navigation under `SVD и PCA` shows both `SVD-линза` and
  `PCA-компрессор`.

## Лекционный охват

Основной источник:

- `SHAD/algebra/13_Complex_spaces/lesson.md`
  - singular value decomposition;
  - `A^*A` and nonnegative singular values;
  - truncated SVD;
  - low-rank approximation;
  - PCA and centered data;
  - numerical stability and approximation quality.

Связанные источники:

- `SHAD/algebra/11_Euclidean_spaces/lesson.md`
  - orthogonal projections and reconstruction error.
- `SHAD/algebra/10_Bilinear_quadratic_forms/lesson.md`
  - positive forms and energy.
- `SHAD/Programma_dlya_postupayushhih_v_Shkolu_analiza_dannyh_3_749884e44e.md`
  - data-analysis motivation: compression, features, variance and metrics.

## Цель этапа

Сделать одну новую playable миссию уровня `prototype`:

- route: `/algebra/svd/pca-compression`;
- mission id: `pca-compression-lab`;
- title: `PCA-компрессор`;
- domain: `data-analysis`;
- mechanic: `model-arena`;
- difficulty: `3`;
- lessonPath: `SHAD/algebra/13_Complex_spaces/lesson.md`;
- prerequisite mission: `svd-lens`;
- next mission: `ML-полигон` or `Фабрика признаков`.

Готовый stage должен:

1. показывать маленькую матрицу/изображение as data, not decoration;
2. позволять включать/выключать singular components and rank `k`;
3. показывать reconstruction and error map side by side;
4. считать storage cost, retained energy, Frobenius error and compression ratio;
5. иметь levels with budgets and visible mistake paths;
6. поддерживать numeric fallback controls for smoke and accessibility;
7. иметь pure TypeScript model layer with unit tests;
8. подключаться в `MissionDefinition`, registry, route loader, navigation and
   curriculum graph;
9. проходить lint, tests, build, mission audit and Playwright smoke.

## Почему это игра

Пользователь не должен просто двигать slider `k`.

У каждого уровня есть цель, ограничение and tradeoff:

- "уложись в 35% storage и сохрани букву читаемой";
- "выбери компоненты, которые сохраняют диагональный stroke";
- "найди, почему rank-1 хорошо по energy, но плохо по локальной ошибке";
- "сначала центрируй данные, иначе первая компонента ловит mean shift";
- "сожми train-like pattern, а потом проверь на второй матрице с похожей
  структурой".

Меби здесь работает как **инспектор ошибки**:

- стоит на самой яркой клетке error map;
- warning state, когда compression ratio хороший, но ошибка слишком локальная;
- thinking state, когда пользователь держит слишком много компонентов без
  выигрыша;
- success state, когда восстановление проходит quality threshold inside budget.

## P0. Model layer

Создать:

```text
src/visualizations/pca-compression/
  pcaCompressionModel.ts
  pcaCompressionModel.test.ts
```

Types:

```ts
export type MatrixData = number[][]

export type LowRankComponent = {
  index: number
  sigma: number
  left: number[]
  right: number[]
  energy: number
}

export type CompressionResult = {
  rank: number
  reconstruction: MatrixData
  residual: MatrixData
  frobeniusError: number
  retainedEnergy: number
  storageCost: number
  compressionRatio: number
  maxCellError: number
}

export type CompressionDiagnosisKind =
  | 'ready'
  | 'over-budget'
  | 'underfit'
  | 'local-artifact'
  | 'mean-not-centered'
  | 'component-mismatch'
```

Functions:

- matrix helpers:
  - `shape(matrix)`;
  - `centerColumns(matrix)`;
  - `uncenterColumns(matrix, means)`;
  - `frobeniusNorm(matrix)`;
  - `subtractMatrices(left, right)`;
  - `maxAbsCell(matrix)`;
  - `normalizeMatrixForHeatmap(matrix)`.
- SVD helpers:
  - `svdSmallMatrix(matrix)`;
  - `reconstructFromComponents(components, selectedIndexes)`;
  - `rankKReconstruction(matrix, k)`;
  - `componentEnergy(components)`;
  - `storageCost(rows, cols, k)` using `k * (rows + cols + 1)`;
  - `compressionRatio(rows, cols, k)`.
- PCA helpers:
  - `covarianceFromCenteredData(matrix)`;
  - `projectRowsToComponents(matrix, components, k)`;
  - `reconstructRowsFromProjection(...)`.
- diagnostics:
  - `diagnoseCompressionBudget(result, budget)`;
  - `diagnoseRetainedEnergy(result, threshold)`;
  - `diagnoseLocalArtifact(result, maxCellThreshold)`;
  - `diagnoseCentering(raw, centeredResult)`.

Implementation note:

- P0 can implement exact SVD for small rank using the existing 2D SVD ideas
  only if datasets stay 2-column. For image/heatmap compression, prefer a
  small deterministic eigen decomposition of `A^T A` for `n <= 6`; do not add a
  heavy numeric dependency unless the hand-written version becomes fragile.
- Keep fixtures tiny: 6x6 or 8x8 matrices are enough for game feel and tests.
- All tolerances must be explicit.
- Degenerate matrices should return stable zero components, not `NaN`.

Unit tests:

- rank-0 reconstruction is all zeros or column means, depending on centered
  mode;
- rank-1 reconstruction reduces Frobenius error on a structured matrix;
- retained energy is monotone as `k` increases;
- storage cost grows as `k * (rows + cols + 1)`;
- compression ratio can be worse than raw storage for too-large `k`;
- max-cell error catches a local artifact even when total energy is acceptable;
- centered PCA beats uncentered PCA on a mean-shifted data fixture;
- selected component reconstruction equals full reconstruction when all
  components are selected;
- no fixture path produces `NaN`.

## P0. Mission definition

Add `pcaCompressionMission` in `src/game/missions.ts`.

Core metadata:

```ts
export const pcaCompressionMission: MissionDefinition = {
  id: 'pca-compression-lab',
  route: '/algebra/svd/pca-compression',
  title: 'PCA-компрессор',
  domain: 'data-analysis',
  mechanic: 'model-arena',
  lessonPath: 'SHAD/algebra/13_Complex_spaces/lesson.md',
  difficulty: 3,
  mascotRole: 'metric-inspector',
  qualityTags: [
    'model-arena',
    'input-fallback',
    'mistake-diagnostics',
    'model-tested',
    'interesting-failure',
    'repair-loop',
    'data-transfer',
  ],
  estimatedMinutes: 10,
}
```

Connection:

- `svdLensMission.nextMissionRoute` should point to
  `/algebra/svd/pca-compression`;
- `pcaCompressionMission.nextMissionRoute` can point to `/data/ml/playground`;
- add mission to `missionDefinitions`;
- add mission entry after `svd-lens`;
- add lazy route loader;
- add to `navigation.ts` under topic `SVD и PCA`.

## P0. Playable levels

### Level 1: `rank-budget`

Goal:

```text
Сожми тепловую карту до заданного бюджета и сохрани узнаваемую структуру.
```

Action:

- user chooses rank `k` or toggles components;
- app shows original, reconstruction and error map;
- badges show storage cost, compression ratio and retained energy.

Success:

- storage cost is below budget;
- retained energy is above threshold;
- max-cell error stays below threshold.

Mistakes:

- uses too many components and exceeds budget;
- uses rank 1 when diagonal/local stroke disappears;
- watches only retained energy and ignores error map.

Takeaway:

```text
Сжатие - это не только "оставить побольше sigma": нужен бюджет и контроль ошибки.
```

### Level 2: `component-detective`

Goal:

```text
Выбери компоненту, которая отвечает за тонкую деталь.
```

Action:

- app shows individual singular components as ghost heatmaps;
- user toggles components non-sequentially in a diagnostic sandbox;
- final answer must keep the component that repairs a visible artifact.

Success:

- selected set repairs target cell/stripe under budget;
- user does not blindly keep the largest component only.

Mistakes:

- keeps first component and loses small but important structure;
- keeps a component that improves total energy but not the target artifact;
- confuses sign pattern with magnitude.

Takeaway:

```text
Большая sigma часто важнее, но маленькая компонента может хранить локально заметную ошибку.
```

### Level 3: `center-before-pca`

Goal:

```text
Перед PCA убери среднее, иначе первая компонента поймает сдвиг.
```

Action:

- user toggles centering;
- app shows raw cloud/matrix, centered version and first component;
- metrics compare reconstruction error after projection.

Success:

- centering is enabled;
- retained variance reflects shape, not mean shift;
- reconstruction beats uncentered baseline.

Mistakes:

- runs PCA on raw shifted data;
- chooses coordinate axis because mean dominates;
- thinks centering is just cosmetic.

Takeaway:

```text
PCA ищет направления разброса вокруг среднего, поэтому centering - часть метода.
```

### Level 4: `quality-gate`

Goal:

```text
Пройди два quality gates: total error and worst-cell artifact.
```

Action:

- user adjusts rank/components;
- app runs two checks:
  - global Frobenius error;
  - local max-cell error.

Success:

- both gates pass;
- compression ratio remains meaningful.

Mistakes:

- global error low, but one cell has a strong artifact;
- local artifact fixed by keeping too many components;
- over-compresses flat regions and under-compresses sharp edges.

Takeaway:

```text
Одна метрика может спрятать плохую ошибку; quality gate должен смотреть и глобально, и локально.
```

### Level 5: `transfer-to-features`

Goal:

```text
Используй первые PCA coordinates как компактные признаки.
```

Action:

- tiny set of points/matrices has two classes or two pattern families;
- user chooses 1D or 2D PCA features;
- app shows overlap/separation and storage cost.

Success:

- selected dimension keeps enough separation;
- app shows why too-small dimension loses class distinction.

Mistakes:

- chooses 1D because it is cheaper but classes overlap;
- chooses too many dimensions and gets no compression;
- treats PCA as supervised class separator.

Takeaway:

```text
PCA дает компактные unsupervised признаки; они полезны, но не знают метки заранее.
```

## P0. UI/UX design

The mission should feel like a compact **compression bench**, not a chart
dashboard.

First viewport:

- left: original heatmap/data tile;
- center: component rail with singular bars and toggle buttons;
- right: reconstruction and error map;
- bottom strip: budget/quality badges and one active control group.

Controls:

- segmented rank selector `0 / 1 / 2 / 3 / full`;
- component toggles with mini heatmap preview;
- centering toggle;
- budget slider or preset chips;
- snap buttons for smoke: `fit budget`, `fix artifact`, `center data`.

Badges:

- `rank`;
- `storage`;
- `compression`;
- `retained energy`;
- `Frobenius error`;
- `max-cell error`;
- `centered/raw`.

Visual language:

- keep existing warm paper/grid base;
- use heatmap palettes with clear neutral zero and diverging residual colors;
- original/reconstruction/error must have identical dimensions and aligned
  cells;
- residual map should use shape/outline as well as color for accessibility;
- no nested cards: tiles can be framed, but the page section stays unframed;
- text should be short: metrics and diagnosis, not lecture paragraphs.

Mobile:

- stack as `original -> reconstruction -> error -> controls`;
- component rail becomes horizontal scroll with fixed-size tiles;
- badges wrap into two columns without changing height on value updates;
- test on 390px width and desktop.

## P0. Architecture

Suggested structure:

```text
src/visualizations/pca-compression/
  PcaCompressionMission.tsx
  pcaCompressionModel.ts
  pcaCompressionModel.test.ts
```

Reuse:

- `MissionShell`;
- `MissionDebriefCard`;
- badge patterns from `SvdLensMission`;
- small matrix helpers from `svdLensModel` where export boundaries are clean.

Possible shared extraction:

- If `svdLensModel` and `pcaCompressionModel` start duplicating matrix algebra,
  extract a small `src/visualizations/linear-algebra/matrixModel.ts` with:
  - `Matrix2x2`;
  - `Vec2`;
  - dot/norm/normalize;
  - transpose/multiply;
  - Frobenius norm.

Do not extract in P0 if it makes the mission harder to land. A local model with
tests is acceptable.

Do not add:

- external numeric library before proving the fixtures need it;
- real image upload;
- large image assets;
- random datasets without fixed seeds;
- global state outside the mission runtime.

## P0. Route, registry and navigation

Route loader:

```ts
export const PcaCompressionMission = lazy(() =>
  import('./pca-compression/PcaCompressionMission').then((module) => ({
    default: module.PcaCompressionMission,
  })),
)
```

Mission registry entry:

```ts
{
  id: 'pca-compression-lab',
  path: '/algebra/svd/pca-compression',
  title: 'PCA-компрессор',
  kind: 'mission',
  status: 'prototype',
  difficulty: 3,
  formula: String.raw`A_k=\sum_{i=1}^k \sigma_i u_i v_i^T`,
}
```

Navigation:

- topic `SVD и PCA`;
- visualizations: `SVD-линза`, then `PCA-компрессор`.

Curriculum:

- `svd-pca.missionIds = ['svd-lens', 'pca-compression-lab']`;
- remove `pca-compression-lab` from `svd-pca.plannedMissionIds`;
- remove `pca-compression-lab` from `complex-geometry.plannedMissionIds`;
- add `pca-compression-lab` to `ml-playground.reviewAfterMissionIds`;
- keep `svd-pca.unlocks = ['ml-playground']`.

## P0. Smoke and QA

Add to `scripts/smoke_playwright.py`:

- route screenshot desktop/mobile;
- happy path through all five levels;
- mistake path:
  - over budget;
  - underfit rank;
  - uncentered PCA;
  - local artifact hidden by total error.

Suggested test ids:

- `mission-pca-compression-lab`;
- `pca-compression-canvas`;
- `pca-original-grid`;
- `pca-reconstruction-grid`;
- `pca-error-grid`;
- `pca-component-toggle-0`;
- `pca-component-toggle-1`;
- `pca-rank-choice-1`;
- `pca-rank-choice-2`;
- `pca-center-toggle`;
- `pca-fit-budget`;
- `pca-fix-artifact`;
- `pca-diagnosis`;
- `pca-storage-badge`;
- `pca-error-badge`;
- `pca-retained-energy-badge`.

Validation:

- `make lint-js`;
- `make lint-python`;
- `make interactive-test`;
- `make interactive-build`;
- `make mission-audit`;
- `.venv/bin/python SHAD/interactive/scripts/smoke_playwright.py --happy-paths-only`;
- `.venv/bin/python SHAD/interactive/scripts/smoke_playwright.py --screens-only`;
- inspect desktop/mobile screenshots for overflow and heatmap readability;
- `git diff --check`.

## Done criteria

The stage is done when:

- `/algebra/svd/pca-compression` is visible in navigation and course map;
- `pca-compression-lab` is no longer listed as planned;
- user can complete all levels without reading the lecture;
- at least one level cannot be solved by a single snap button without
  understanding the metric tradeoff;
- reconstruction and error map visibly change with component choices;
- centering is not optional flavor text: it changes the success condition;
- smoke covers one happy path and one meaningful mistake path;
- mission audit has no new warnings;
- UI passes desktop/mobile screenshot review.

## Risks

- **Passive slider demo.** Make budgets and gates mandatory; do not let `k`
  slider alone carry the mission.
- **Too much numeric machinery.** Keep matrices tiny and deterministic.
- **Metric overload.** Show only active metrics per level; keep the full set in
  compact badges.
- **False visual confidence.** Always show residual/error map, not only the
  reconstructed image.
- **PCA misconception.** Level 5 must say PCA is unsupervised and may not align
  with labels.
- **Mobile density.** Heatmaps must stay square and fixed-size; labels should
  wrap outside tiles, not inside cells.

## Implementation order

1. Create `pcaCompressionModel.ts` and focused tests for matrix fixtures,
   reconstruction, energy, storage and centering.
2. Add `pcaCompressionMission` metadata and level definitions.
3. Build static mission layout with original/reconstruction/error heatmaps.
4. Add rank/component controls and budget badges for `rank-budget`.
5. Add individual component previews and artifact repair for
   `component-detective`.
6. Add centering comparison for `center-before-pca`.
7. Add dual quality gate for `quality-gate`.
8. Add PCA feature projection transfer for `transfer-to-features`.
9. Wire route loader, registry, navigation and curriculum graph.
10. Add Playwright happy/mistake paths and screenshots.
11. Run full validation and inspect screenshots.
12. Update `mission_quality_report.md`, `gameplay_roadmap.md`,
    `next_svd_pca_stage_plan.md` and this plan status.

## Suggested commit slices

First slice:

```text
feat(interactive): add pca compression model
```

Scope:

- `pcaCompressionModel.ts`;
- model tests;
- small deterministic fixtures.

Second slice:

```text
feat(interactive): add pca compression mission
```

Scope:

- mission metadata;
- UI levels;
- route/registry/navigation/curriculum wiring.

Third slice:

```text
test(interactive): cover pca compression smoke
```

Scope:

- Playwright happy path;
- mistake path;
- screenshots;
- mission audit and roadmap status.
