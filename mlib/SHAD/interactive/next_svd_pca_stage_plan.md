# SHAD Interactive: план этапа "SVD-линза и PCA"

Этот этап продолжает `Квадратичную линзу`. Если там пользователь увидел форму
`x^T A x`, главные оси и сигнатуру, то теперь нужно показать, как любая
матрица действует на геометрию и данные:

```text
единичный круг -> матрица A -> эллипс -> A^T A -> сингулярные направления -> PCA
```

Главный фокус: **SVD-линза**. Пользователь руками раскладывает действие
матрицы на поворот входных осей, растяжение по сингулярным значениям и поворот
выходных осей. Это должно ощущаться не как калькулятор SVD, а как оптический
прибор: круг проходит через линзу и превращается в эллипс, а облако данных
сжимается до главной компоненты.

## Статус 2026-06-07

P0 выполнен:

- добавлена playable миссия `SVD-линза` на route `/algebra/svd/lens`;
- реализован pure TypeScript model layer `svdLensModel.ts` with unit tests;
- миссия подключена в `MissionDefinition`, lazy route loader, mission registry,
  navigation and curriculum graph;
- добавлены SVG input/output spaces, matrix lens block, transformed circle,
  target ellipse, singular direction markers, rank-1 toggle and PCA cloud;
- добавлены smoke checks для route screenshots, happy path and mistake path;
- `mission_quality_report.md` обновлен через `make mission-audit`;
- validation пройдена: JS lint, Python lint, Vitest, build, Playwright
  happy/mistake smoke, Playwright screens-only and `git diff --check`.

Оставшийся P1: data compression lab and unitary compass remain future
extensions.

## Почему это следующий этап

После `Квадратичной линзы` в приложении уже есть:

- symmetric 2x2 model layer: eigenvalues, eigenvectors, signatures and level
  sets;
- SVG-first геометрическое поле с numeric fallback;
- уровни про главные оси, determinant и вырожденные направления;
- smoke coverage for route screenshots, happy path и mistake path.

Следующий шаг должен использовать этот фундамент, а не начинать с нуля:

- SVD строится через собственные пары `A^T A`;
- `A^T A` - положительно полуопределенная квадратичная форма;
- единичный круг под действием `A` превращается в эллипс;
- сингулярные значения - длины полуосей эллипса;
- PCA для центрированных данных выражается через SVD.

Именно здесь линейная алгебра начинает явно работать на анализ данных, поэтому
этап связывает `algebra` и `data-analysis`.

## Лекционный охват

Основной источник:

- `SHAD/algebra/13_Complex_spaces/lesson.md`
  - раздел `Сингулярное разложение (SVD)`;
  - связь SVD с `A^*A`;
  - геометрический смысл: сфера переходит в эллипсоид;
  - усеченное SVD;
  - PCA, низкоранговое приближение и устойчивые вычисления.

Связанные источники:

- `SHAD/algebra/10_Bilinear_quadratic_forms/lesson.md`
  - квадратичные формы и diagonalization.
- `SHAD/algebra/11_Euclidean_spaces/lesson.md`
  - ортогональность, ортонормированные базисы, ортогональные операторы.
- `SHAD/algebra/12_Eigenvectors_eigenvalues/lesson.md`
  - собственные направления и diagonalization.

## Цель этапа

Сделать одну новую playable миссию уровня `prototype`:

- route: `/algebra/svd/lens`;
- mission id: `svd-lens`;
- title: `SVD-линза`;
- domain: `linear-algebra`;
- mechanic: `geometry-lab`;
- difficulty: `3`;
- lessonPath: `SHAD/algebra/13_Complex_spaces/lesson.md`;
- prerequisite mission: `quadratic-lens`;
- transfer mission later: `pca-compression-lab` или data/ML mission extension.

Готовый stage должен:

1. показывать действие произвольной 2x2 матрицы на круге и data cloud;
2. иметь pure TypeScript SVD model for 2x2 real matrices;
3. давать видимые mistake paths, especially eigenvalues-vs-singular-values;
4. подключаться в `MissionDefinition`, registry, route loader, navigation и
   curriculum graph;
5. проходить lint, tests, build, mission audit and Playwright smoke.

## Игровая идея

На поле есть три слоя:

1. **Input space**: единичный круг, входные оси и правые сингулярные
   направления `v1`, `v2`.
2. **Matrix lens**: матрица `A`, которую пользователь собирает столбцами или
   выбирает из preset cases.
3. **Output space**: эллипс `A(S^1)`, полуоси `sigma1`, `sigma2`, left
   singular directions `u1`, `u2`.

Пользователь не обязан вручную считать SVD. Он должен действием увидеть:

- почему правые сингулярные направления живут во входном пространстве;
- почему левые сингулярные направления живут в выходном пространстве;
- почему `sigma` всегда неотрицательны;
- почему `A^T A` появляется как quadratic lens;
- почему усечение малой `sigma` дает лучшую rank-1 тень.

## P0. Model layer

Создать:

```text
src/visualizations/svd-lens/
  svdLensModel.ts
  svdLensModel.test.ts
```

Типы:

```ts
export type Vec2 = [number, number]

export type Matrix2x2 = {
  a: number
  b: number
  c: number
  d: number
}

export type Svd2D = {
  sigma1: number
  sigma2: number
  v1: Vec2
  v2: Vec2
  u1: Vec2
  u2: Vec2
  ata: Symmetric2x2
  condition: number
  rank: 0 | 1 | 2
}
```

Functions:

- `applyMatrix(matrix, point)`;
- `matrixFromColumns(u, v)`;
- `transposeTimesMatrix(matrix)`:
  - returns `A^T A` as `Symmetric2x2`;
  - should reuse or mirror quadratic-lens types where practical.
- `svd2x2(matrix)`:
  - uses eigenpairs of `A^T A`;
  - returns ordered singular values `sigma1 >= sigma2 >= 0`;
  - computes `u_i = A v_i / sigma_i` when `sigma_i > tolerance`;
  - handles rank-1 and zero matrix gracefully.
- `unitCircleSample(samples)`;
- `transformedCircleSample(matrix, samples)`;
- `rankKApprox(matrix, k)`;
- `projectionError(points, direction)`;
- `centerPointCloud(points)`;
- `principalComponent2D(points)`.

Unit tests:

- diagonal matrix gives obvious singular values;
- rotation matrix has `sigma1 = sigma2 = 1`;
- shear matrix has nonnegative singular values and orthonormal directions;
- rank-1 matrix returns one near-zero singular value;
- `A^T A` eigenvalues equal `sigma^2`;
- transformed unit circle reaches semi-axis lengths `sigma1`, `sigma2`;
- rank-1 approximation has lower error than arbitrary axis drop on the same
  example;
- PCA direction matches dominant singular direction of centered data matrix.

Acceptance:

- model has no React imports;
- no external numeric library in P0;
- all tolerances are explicit;
- degenerate cases do not produce `NaN`.

## P0. Mission definition

Add `svdLensMission` in `src/game/missions.ts`.

Core metadata:

```ts
export const svdLensMission: MissionDefinition = {
  id: 'svd-lens',
  route: '/algebra/svd/lens',
  title: 'SVD-линза',
  domain: 'linear-algebra',
  mechanic: 'geometry-lab',
  lessonPath: 'SHAD/algebra/13_Complex_spaces/lesson.md',
  difficulty: 3,
  mascotRole: 'invariant-token',
  qualityTags: [
    'geometry-lab',
    'input-fallback',
    'mistake-diagnostics',
    'model-tested',
    'interesting-failure',
    'data-transfer',
  ],
  estimatedMinutes: 10,
}
```

Connection:

- `quadratic-lens.nextMissionRoute` should point to `/algebra/svd/lens`;
- curriculum node `quadratic-forms` should unlock `svd-pca`;
- add curriculum node `svd-pca`;
- keep `unitary-compass` planned, not live.

## P0. Playable levels

### Level 1: `circle-to-ellipse`

Goal:

```text
Собери матрицу, которая превращает круг в заданный эллипс.
```

Action:

- user adjusts matrix columns or chooses simple transforms;
- output field shows transformed circle;
- target ellipse is ghosted.

Success:

- transformed circle semi-axis lengths match target sigmas;
- orientation matches target output axes.

Mistakes:

- determinant sign is right but singular values are wrong;
- columns look long, but action on circle has wrong ellipse;
- user creates reflection when target is pure rotation+stretch.

Takeaway:

```text
SVD видит матрицу через то, как она растягивает все направления единичного круга.
```

### Level 2: `right-directions`

Goal:

```text
Найди два входных направления, которые станут полуосями эллипса.
```

Action:

- drag two input direction markers on unit circle;
- output arrows `A v1`, `A v2` appear on ellipse;
- app checks orthogonality and semi-axis alignment.

Success:

- markers align with right singular vectors;
- output vectors align with ellipse axes;
- directions are nonzero and orthogonal.

Mistakes:

- user picks output axes in input space;
- directions are not orthogonal;
- one marker is almost correct but maps to non-axis point.

Takeaway:

```text
Правые сингулярные векторы живут на входе: это направления, которые A
растягивает без смешивания с другой осью.
```

### Level 3: `singular-vs-eigen`

Goal:

```text
Не перепутай собственные значения A и сингулярные числа A.
```

Action:

- app shows one non-symmetric matrix;
- user must choose which values are singular values;
- visualization compares eigen-directions of `A` and eigen-directions of
  `A^T A`.

Success:

- selected values are `sqrt(eigenvalues(A^T A))`;
- user rejects negative/complex eigenvalue trap.

Mistakes:

- selects eigenvalues of `A`;
- keeps sign on singular values;
- treats non-square or non-normal case like diagonalization.

Takeaway:

```text
Сингулярные числа не являются собственными значениями A; их квадраты - это
собственные значения A^T A.
```

### Level 4: `rank-one-shadow`

Goal:

```text
Оставь только сильную ось и получи лучшую rank-1 тень.
```

Action:

- user toggles `sigma1` and `sigma2`;
- output ellipse collapses to a segment;
- app shows approximation error.

Success:

- `sigma1` kept, `sigma2` removed;
- rank becomes 1;
- error equals removed energy within tolerance.

Mistakes:

- removes dominant sigma;
- removes arbitrary column instead of singular component;
- gets rank 1 but with worse projection error.

Takeaway:

```text
Усеченное SVD отбрасывает слабые сингулярные направления, а не случайные
столбцы.
```

### Level 5: `pca-cloud`

Goal:

```text
Сожми облако данных на первую главную компоненту.
```

Action:

- small centered point cloud is shown;
- user rotates a candidate component axis;
- app projects points and shows retained variance / reconstruction error.

Success:

- axis aligns with dominant PCA direction;
- retained variance exceeds threshold;
- reconstruction error beats the perpendicular candidate.

Mistakes:

- uses non-centered data;
- follows largest coordinate axis instead of covariance direction;
- maximizes visual width but not variance after projection.

Takeaway:

```text
PCA выбирает направление максимальной дисперсии центрированных данных; это SVD
матрицы данных.
```

## P0. UI design

The mission needs one strong visual memory: **a lens table with two spaces**.

Layout:

- left field: input circle with right singular directions;
- middle compact lens block: matrix `A`, `A^T A`, sigma badges;
- right field: output ellipse and left singular directions;
- optional lower strip for PCA point cloud in levels 4-5.

Use SVG first:

- curves, axes and points are 2D and inspectable;
- mobile layout can stack input -> lens -> output;
- Playwright can assert selectors without canvas pixel sampling;
- no Three.js unless later we add 3D ellipsoid.

Controls:

- matrix coefficient sliders/numeric inputs;
- preset buttons: diagonal stretch, rotation, shear, rank-1, non-normal trap;
- direction markers on input circle;
- sigma toggle for rank truncation;
- PCA axis rotation slider;
- reset and snap-to-svd buttons.

Badges:

- `sigma1`, `sigma2`;
- `rank`;
- `condition`;
- `det`;
- `retained variance` on PCA level;
- `||A - A_k||` on truncation level.

Mebi role:

- marker on input direction for levels 2-3;
- small "lens inspector" near `A^T A`;
- warning state when user picks eigenvalues of `A` instead of singular values;
- success state when circle axes and ellipse axes lock together.

Visual constraints:

- no text-heavy explanation panels;
- no nested cards inside cards;
- input/output spaces must be visually distinct but not separate dashboards;
- positive/negative determinant should not dominate SVD, because sigma are
  nonnegative;
- use shape and labels, not color alone, for axis/sign/rank states;
- mobile first viewport must show at least one full field and a hint of the
  second field.

## P0. Architecture

Reuse:

- `MissionShell`;
- `MissionDebriefCard`;
- `InvariantBadge` / existing badge pattern;
- `quadraticLensModel` eigenpair helpers if export boundaries stay clean.

Potential shared extraction:

- `src/visualizations/linear-algebra-2d/linearAlgebra2d.ts` for:
  - `Vec2`;
  - vector norm/dot/normalize;
  - 2x2 matrix apply/multiply/transpose;
  - angle helpers;
  - SVG coordinate mapping.

Do not extract if it makes the first implementation noisy. A local
`svdLensModel.ts` is acceptable, but avoid duplicating bugs from
`quadraticLensModel`.

Do not add:

- generic linear algebra library;
- symbolic formula parser;
- WebGL scene;
- second mission runtime.

## P0. Curriculum and routing

Add curriculum node:

```ts
{
  id: 'svd-pca',
  title: 'SVD и PCA',
  cardLabel: 'Круг, эллипс и данные',
  section: 'algebra',
  lessonPaths: ['SHAD/algebra/13_Complex_spaces/lesson.md'],
  prerequisites: ['quadratic-forms'],
  missionIds: ['svd-lens'],
  plannedMissionIds: ['unitary-compass', 'pca-compression-lab'],
  skillIds: ['singular-values', 'principal-components', 'low-rank'],
  unlocks: ['ml-playground'],
  reviewAfterMissionIds: ['quadratic-lens', 'feature-factory'],
  readinessLabel: 'SVD-геометрия готовится',
  coverageStatus: 'playable',
  takeaway:
    'SVD раскладывает любую матрицу на входные оси, неотрицательные растяжения и выходные оси.',
  status: 'prototype',
}
```

Validation caveat:

- current curriculum validator requires `unlocks` to point to existing node ids;
- `ml-playground` exists, so use it as real transfer;
- keep `unitary-compass` and `pca-compression-lab` in `plannedMissionIds`.

Registry:

- id: `svd-lens`;
- path: `/algebra/svd/lens`;
- status: `prototype`;
- difficulty: `3`;
- formula: `A = U Sigma V^T`;
- description: circle-to-ellipse geometry and PCA transfer.

Navigation:

- add topic under `Линейная алгебра`;
- put after `Квадратичные формы`;
- title: `SVD и PCA`.

## P0. Smoke and QA

Add to `scripts/smoke_playwright.py`:

- route screenshot desktop/mobile;
- first level happy path;
- eigen-vs-singular mistake path;
- rank-one truncation happy path;
- PCA level happy path;
- check `mission-debrief` appears after final level.

Suggested test ids:

- `svd-lens-canvas`;
- `svd-input-circle`;
- `svd-output-ellipse`;
- `svd-right-vector-1`;
- `svd-left-vector-1`;
- `svd-sigma-badge`;
- `svd-rank-toggle-sigma-2`;
- `svd-pca-cloud`;
- `svd-pca-axis`;
- `svd-diagnosis`.

Validation:

- `make lint-js`;
- `make lint-python`;
- `make interactive-test`;
- `make interactive-build`;
- `make mission-audit`;
- `.venv/bin/python SHAD/interactive/scripts/smoke_playwright.py --happy-paths-only`;
- `.venv/bin/python SHAD/interactive/scripts/smoke_playwright.py --screens-only`;
- `git diff --check`.

## P1. Data compression extension

If P0 is successful, add a second mission or level family:

```text
/data/pca/compression-lab
```

Core idea:

- tiny grayscale image or matrix heatmap;
- user keeps 1, 2, 4 singular components;
- app shows storage cost and reconstruction error.

This should not be the first SVD mission because it can become a demo of image
compression without understanding right/left singular directions. It is better
after the SVD lens teaches the geometry.

## P1. Unitary compass extension

Future route:

```text
/algebra/complex/unitary-compass
```

Core idea:

- complex vector with phase;
- Hermitian norm;
- unitary operator as norm-preserving transformation;
- `A* A` as the bridge to singular values.

This belongs after SVD P0, because then the reason for `A* A` is already
visible.

## Implementation order

1. Create `svdLensModel.ts` and focused unit tests.
2. Add mission definition with all authoring metadata.
3. Build static SVG layout with input circle, matrix lens and output ellipse.
4. Add matrix controls and target ellipse for level 1.
5. Add right/left singular direction markers for level 2.
6. Add eigen-vs-singular choice mechanic for level 3.
7. Add sigma truncation and rank/error badges for level 4.
8. Add PCA point cloud and projection axis for level 5.
9. Wire route loader, registry, navigation and curriculum graph.
10. Add Playwright smoke and screenshots.
11. Run full validation.
12. Update `mission_quality_report.md`, `gameplay_roadmap.md` and this plan
    status.

## Done criteria

The stage is done when:

- `/algebra/svd/lens` is visible in navigation and course map;
- user can complete all five levels without reading the lecture;
- circle-to-ellipse behavior is visible immediately;
- `A^T A` connection is explicit but compact;
- singular values are never allowed to become signed eigenvalue lookalikes;
- rank-1 truncation and PCA levels show actual error/variance tradeoff;
- smoke covers at least one happy path and one mistake path;
- mission audit has no new warnings.

## Risks

- **Too much linear algebra on one screen.** Keep formulas in badges, not prose.
- **SVD sign ambiguity.** Treat vector signs as equivalent in success checks.
- **Rank-deficient matrices.** Model must handle `sigma2 = 0` without `NaN`.
- **PCA overload.** Keep PCA as final transfer level, not a full ML course.
- **Mobile density.** Stack input/lens/output vertically and keep controls below.
- **Over-explaining.** Debrief should explain the bridge; main field should do
  the teaching through motion and alignment.

## Suggested first commit slice

```text
feat(interactive): add svd lens model and first mission level
```

Scope:

- `svdLensModel.ts`;
- model tests;
- `svdLensMission` metadata;
- initial `SvdLensMission.tsx` with circle-to-ellipse level;
- route/registry/curriculum wiring.

Second slice:

- singular direction markers;
- eigen-vs-singular trap;
- rank-one and PCA levels;
- smoke and audit updates.
