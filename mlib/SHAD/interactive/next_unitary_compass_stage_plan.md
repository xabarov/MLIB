# SHAD Interactive: план этапа "Унитарный компас"

Этот этап продолжает `Евклидову мастерскую` и закрывает planned-хвост
`unitary-compass`, который сейчас упоминается в `quadratic-forms`,
`euclidean-geometry` and `svd-pca`. После проекций, ортогональных остатков,
Грама-Шмидта и ортогональных операторов нужно показать, что в комплексных
пространствах похожая геометрия работает только после одного важного хода:
**комплексного сопряжения**.

Главный фокус: **Унитарный компас**. Пользователь управляет комплексными
векторами как стрелками с фазой, проверяет Hermitian inner product, ловит
ошибку "обычного билинейного dot product", собирает унитарное преобразование
и видит мост к `A^*A` из SVD.

Эта миссия не должна быть калькулятором комплексных матриц. Она должна быть
игрой про сохранение нормы и фазы:

```text
complex vector -> conjugate slot -> Hermitian norm -> unitary motion -> A^*A -> SVD
```

## Статус 2026-06-07

P0 выполнен.

- Добавлена playable mission `/algebra/complex/unitary-compass` с шестью
  уровнями: bilinear trap, conjugate slot, phase preservation, fake Hermitian,
  unitary motion and `A^*A` bridge.
- Добавлен pure model layer `unitaryCompassModel.ts` with focused Vitest tests
  for complex arithmetic, Hermitian symmetry, unitary checks, adjoint matrices
  and `A^*A`.
- Миссия подключена в `MissionDefinition`, lazy route loader, registry,
  navigation and curriculum graph через новый узел `complex-geometry`.
- `Евклидова мастерская` теперь ведет в `Унитарный компас`, а `Унитарный
  компас` ведет в `SVD-линзу`.
- Playwright smoke покрывает happy path, mistake path and desktop/mobile
  screenshots for the new route.
- Mission audit обновлен: `Унитарный компас: 38/38`.
- Прогнаны проверки: JS lint, Python lint, Vitest, build, mission audit,
  Playwright happy/mistake smoke and screens-only smoke.

Оставшийся P1-хвост после этого этапа: `pca-compression-lab`, который должен
использовать уже подготовленный мост `A^*A -> SVD -> PCA`.

## Текущее состояние

До начала этапа в рабочем дереве уже был P0 `Евклидова мастерская`:

- `orthogonal-workshop` на route `/algebra/euclidean/orthogonal-workshop`;
- pure model layer for real projections, Gram-Schmidt and orthogonal operators;
- route, registry, navigation, curriculum graph and Playwright smoke;
- `mission_quality_report.md` with `Евклидова мастерская: 32/32`.

До начала этапа planned gap был таким:

- `quadratic-forms.plannedMissionIds` includes `unitary-compass`;
- `euclidean-geometry.plannedMissionIds` includes `unitary-compass`;
- `svd-pca.plannedMissionIds` includes `unitary-compass` and
  `pca-compression-lab`.

После выполнения P0 `unitary-compass` стал playable mission, `complex-geometry`
стал отдельным curriculum node, а в качестве содержательного хвоста остался
`pca-compression-lab`.

`PCA compression lab` тоже важен, но его лучше делать после `Унитарного
компаса`: иначе SVD-линия уйдет в data-demo, не закрыв комплексное
сопряжение, Hermitian norm and `A^*A`.

## Лекционный охват

Основной источник:

- `SHAD/algebra/13_Complex_spaces/lesson.md`
  - complex vector spaces;
  - sesquilinear forms;
  - standard Hermitian inner product;
  - why `x_1y_1 + ... + x_ny_n` is not a good length over `C`;
  - Hermitian forms;
  - Hermitian spaces, norm and orthogonality;
  - adjoint operator `A^*`;
  - unitary operator and condition `U^*U=I`;
  - normal/self-adjoint operators;
  - bridge to SVD through `A^*A`.

Связанные источники:

- `SHAD/algebra/11_Euclidean_spaces/lesson.md`
  - orthogonal operators as real analogue of unitary operators.
- `SHAD/algebra/10_Bilinear_quadratic_forms/lesson.md`
  - positive forms as length-like objects.
- `SHAD/algebra/12_Eigenvectors_eigenvalues/lesson.md`
  - spectral theorem context and eigenvectors.

## Цель этапа

Сделать одну новую playable миссию уровня `prototype`:

- route: `/algebra/complex/unitary-compass`;
- mission id: `unitary-compass`;
- title: `Унитарный компас`;
- domain: `linear-algebra`;
- mechanic: `geometry-lab`;
- difficulty: `3`;
- lessonPath: `SHAD/algebra/13_Complex_spaces/lesson.md`;
- prerequisite mission: `orthogonal-workshop`;
- next mission: `SVD-линза` or later `PCA compression lab`.

Готовый stage должен:

1. показать комплексный вектор как стрелку с модулем и фазой;
2. сделать видимой ловушку `B(ix, ix) = -B(x, x)` for bilinear product;
3. научить выбирать conjugate slot for Hermitian inner product;
4. проверять Hermitian norm as always nonnegative real number;
5. показывать unitary transform as phase-preserving/norm-preserving motion;
6. ловить fake symmetric complex matrix that is not Hermitian;
7. дать компактный bridge from `U^*U=I` to `A^*A` in SVD;
8. иметь pure TypeScript model layer with unit tests;
9. подключаться в `MissionDefinition`, registry, route loader, navigation and
   curriculum graph;
10. проходить lint, tests, build, mission audit and Playwright smoke.

## Почему это игра

Пользователь должен не читать про сопряжение, а увидеть, что без него ломается
понятие длины:

- multiply vector by `i`: длина должна сохраниться, но bilinear square changes
  sign;
- choose which argument is conjugated: only Hermitian convention gives stable
  norm and conjugate symmetry;
- rotate phase: point moves on circle, norm stays fixed;
- inspect complex matrix: visually symmetric is not enough, off-diagonal
  entries must be conjugates;
- build `A^*A`: result becomes Hermitian positive semidefinite, exactly the
  object that feeds SVD.

Ошибки должны быть видимыми:

- norm badge turns non-real or negative under fake bilinear square;
- conjugate symmetry badge fails: `<x,y> != overline(<y,x>)`;
- unit circle becomes ellipse under non-unitary matrix;
- fake Hermitian matrix has matching positions but wrong conjugate signs;
- `A^*A` without conjugate transpose is not Hermitian.

## P0. Model layer

Создать:

```text
src/visualizations/unitary-compass/
  unitaryCompassModel.ts
  unitaryCompassModel.test.ts
```

Types:

```ts
export type Complex = {
  re: number
  im: number
}

export type ComplexVec2 = [Complex, Complex]

export type ComplexMatrix2x2 = {
  a: Complex
  b: Complex
  c: Complex
  d: Complex
}

export type UnitaryDiagnosisKind =
  | 'ready'
  | 'zero-vector'
  | 'bilinear-trap'
  | 'wrong-conjugate-slot'
  | 'not-hermitian'
  | 'not-unitary'
  | 'not-positive-semidefinite'
```

Functions:

- complex arithmetic:
  - `complex(re, im)`;
  - `addComplex`;
  - `subtractComplex`;
  - `multiplyComplex`;
  - `conjugate`;
  - `absSquared`;
  - `formatComplex`.
- vector helpers:
  - `addVec2`;
  - `scaleVec2`;
  - `complexDotBilinear(x, y)`;
  - `hermitianInner(x, y)` using current lecture convention: linear in first
    argument, conjugate-linear in second;
  - `hermitianNormSquared(x)`;
  - `normalizeComplexVec2`;
  - `phaseRotateVector(x, theta)`.
- matrix helpers:
  - `applyComplexMatrix(matrix, vector)`;
  - `adjointMatrix(matrix)`;
  - `multiplyComplexMatrices(left, right)`;
  - `identityComplexMatrix`;
  - `isHermitianMatrix(matrix)`;
  - `isUnitaryMatrix(matrix)`;
  - `matrixStarMatrix(matrix)`;
  - `hermitianMatrixEigenvalues2(matrix)` for 2x2 Hermitian matrices with real
    eigenvalues.
- diagnostics:
  - `diagnoseHermitianSlot(...)`;
  - `diagnoseUnitaryMatrix(...)`;
  - `diagnoseHermitianMatrix(...)`;
  - `diagnoseAStarABridge(...)`.

Unit tests:

- `bilinearDot(ix, ix)` flips sign for a real vector, demonstrating the trap;
- `hermitianInner(ix, ix)` stays positive and equals `hermitianInner(x, x)`;
- `hermitianInner(x, y) = conjugate(hermitianInner(y, x))`;
- standard phase rotation matrix is unitary;
- fake rotation without conjugate handling is rejected;
- matrix with `b = i`, `c = i` is not Hermitian, while `c = -i` is Hermitian;
- `A^*A` is Hermitian positive semidefinite for a non-unitary complex matrix;
- unitary matrix satisfies `U^*U = I` and preserves vector norm;
- degenerate zero vector returns explicit diagnosis, not `NaN`.

Acceptance:

- model has no React imports;
- no external numeric library in P0;
- all tolerances are explicit;
- no `NaN` in normal degenerate paths;
- model keeps the lecture convention explicit in names/comments.

## P0. Mission definition

Add `unitaryCompassMission` in `src/game/missions.ts`.

Core metadata:

```ts
export const unitaryCompassMission: MissionDefinition = {
  id: 'unitary-compass',
  route: '/algebra/complex/unitary-compass',
  title: 'Унитарный компас',
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
    'repair-loop',
    'data-transfer',
  ],
  estimatedMinutes: 10,
}
```

Connection:

- `orthogonal-workshop.nextMissionRoute` should point to
  `/algebra/complex/unitary-compass`;
- `unitary-compass.nextMissionRoute` should point to `/algebra/svd/lens`;
- add curriculum node `complex-geometry`;
- `euclidean-geometry.unlocks` should include `complex-geometry`;
- `complex-geometry.unlocks` should include `svd-pca`;
- `svd-pca.prerequisites` can become `['complex-geometry']`.

If that makes the already-playable `SVD-линза` feel too far away in the course
map, use a softer connection:

- keep `svd-pca.prerequisites = ['euclidean-geometry']`;
- add `unitary-compass` to `svd-pca.reviewAfterMissionIds`;
- keep `unitary-compass` visible in navigation before `SVD и PCA`.

## P0. Playable levels

### Level 1: `i-scale-trap`

Goal:

```text
Умножь вектор на i и поймай, почему обычный bilinear square не является длиной.
```

Action:

- user toggles between `x` and `ix`;
- app compares:
  - fake bilinear square `x1*x1 + x2*x2`;
  - Hermitian norm `<x,x>`.

Success:

- user selects Hermitian norm as the stable length;
- fake bilinear badge shows sign/complex failure.

Mistakes:

- treating bilinear square as length;
- ignoring imaginary part in a fake "real norm";
- assuming multiplication by `i` should change length.

Takeaway:

```text
В комплексном пространстве длина требует сопряжения: иначе умножение на i ломает знак.
```

### Level 2: `conjugate-slot`

Goal:

```text
Выбери правильный conjugate slot для Hermitian inner product.
```

Action:

- user chooses one of three modes:
  - no conjugate;
  - conjugate first;
  - conjugate second.
- app checks lecture convention: linear in first argument, conjugate-linear in
  second.

Success:

- selected convention satisfies conjugate symmetry and stable norm.

Mistakes:

- no conjugate: norm trap returns;
- wrong slot relative to lecture convention: math may be valid in another
  convention but does not match this course;
- using absolute values componentwise without preserving linearity.

Takeaway:

```text
Важно не только поставить сопряжение, но и быть последовательным в выбранном соглашении.
```

### Level 3: `phase-preserve`

Goal:

```text
Поверни фазу комплексного вектора, не меняя его Hermitian norm.
```

Action:

- user rotates phase with a circular control;
- field shows complex plane arrow for each coordinate;
- badge shows norm before/after.

Success:

- phase changes by target angle;
- Hermitian norm stays fixed.

Mistakes:

- scaling amplitude instead of phase;
- changing only one coordinate when level asks global phase;
- norm drift under non-unitary transform.

Takeaway:

```text
Унитарное движение может менять фазу, но не меняет Hermitian length.
```

### Level 4: `fake-hermitian`

Goal:

```text
Почини комплексную матрицу, которая выглядит симметричной, но не Hermitian.
```

Action:

- user edits imaginary signs of off-diagonal entries;
- app compares `A` and `A^*`;
- visual mirror shows conjugate reflection.

Success:

- `A = A^*`;
- diagonal entries are real;
- off-diagonal entries are conjugates.

Mistakes:

- `a12 = a21` instead of `a12 = conjugate(a21)`;
- imaginary diagonal entry remains;
- real symmetric intuition applied without conjugation.

Takeaway:

```text
В комплексном случае самосопряженность означает conjugate transpose, а не обычную симметрию.
```

### Level 5: `unitary-motion`

Goal:

```text
Собери матрицу U, которая сохраняет Hermitian inner product.
```

Action:

- user chooses phase and optional coordinate swap;
- app shows unit circle in complex-state projection;
- badges: `U^*U`, norm preservation, determinant phase.

Success:

- `U^*U = I`;
- norm of test vector preserved;
- angle/inner-product relation preserved.

Mistakes:

- preserving one vector norm but failing `U^*U`;
- using transpose instead of adjoint;
- scaling phase magnitude away from 1.

Takeaway:

```text
Унитарная матрица - комплексный аналог ортогональной: она сохраняет Hermitian geometry целиком.
```

### Level 6: `a-star-a-bridge`

Goal:

```text
Построй A^*A и увидь, почему SVD приходит из Hermitian geometry.
```

Action:

- user starts with a non-unitary complex matrix `A`;
- app lets them choose `A^T A`, `A A^*`, or `A^* A`;
- field shows whether result is Hermitian positive semidefinite.

Success:

- selected `A^*A`;
- matrix is Hermitian;
- eigenvalue/sigma badge shows nonnegative values.

Mistakes:

- using transpose instead of adjoint;
- building `AA^*` while asking for right singular directions;
- calling eigenvalues of `A` singular values.

Takeaway:

```text
SVD starts with A^*A because this matrix is Hermitian positive semidefinite and has orthonormal eigenvectors.
```

## P0. UI design

The mission should feel like a precise compass/instrument, not a dense algebra
sheet.

Layout:

- first viewport:
  - left SVG/canvas field with complex-plane dials;
  - middle compact "conjugation mirror";
  - right `MissionShell` controls;
- badges:
  - `norm`;
  - `phase`;
  - `<x,y>`;
  - `U*U`;
  - `Hermitian?`.

Visual language:

- use the existing warm paper/grid style;
- phase is a circular arc, not a slider-only number;
- conjugation should look like reflection across the real axis;
- unitary motion should keep points on a circle;
- fake modes should visibly distort the circle or produce non-real norm;
- avoid long explanatory text inside the field.

Controls:

- circular phase knob or segmented phase presets: `0`, `pi/2`, `pi`,
  `3pi/2`;
- matrix entry for small complex numbers:
  - real input;
  - imaginary input;
  - quick sign buttons for `i` and `-i`;
- mode buttons:
  - `bilinear`;
  - `conjugate first`;
  - `conjugate second`;
  - `A^T A`;
  - `A^*A`.

Mobile:

- no side-by-side complex matrix under 390px;
- complex entries stack as `real` / `imag`;
- phase dials remain at fixed square aspect ratio;
- badges wrap without horizontal overflow;
- screenshots must cover desktop and mobile.

## P0. Route, registry and navigation

Add lazy route:

```ts
export const UnitaryCompassMission = lazy(() =>
  import('./unitary-compass/UnitaryCompassMission').then((module) => ({
    default: module.UnitaryCompassMission,
  })),
)
```

Add mission entry:

```ts
{
  id: 'unitary-compass',
  path: '/algebra/complex/unitary-compass',
  title: 'Унитарный компас',
  kind: 'mission',
  status: 'prototype',
  difficulty: 3,
  lessonPath: unitaryCompassMission.lessonPath,
  mission: unitaryCompassMission,
  component: UnitaryCompassMission,
  meta: {
    title: 'Унитарный компас',
    formula: String.raw`\langle x,y\rangle=\sum x_k\overline{y_k},\quad U^*U=I`,
    description:
      'Комплексная фаза, сопряжение и унитарность становятся проверяемой геометрией.',
  },
}
```

Navigation:

- add algebra topic `Комплексные пространства`;
- place it between `Евклидовы пространства` and `SVD и PCA`;
- include `missionEntry('unitary-compass')`.

## P0. Playwright smoke

Add route screenshots:

- `unitary-compass-desktop.png`;
- `unitary-compass-mobile.png`.

Add happy path:

1. open `#/algebra/complex/unitary-compass`;
2. check `mission-unitary-compass`;
3. level 1: choose Hermitian norm, expect success;
4. level 2: choose `conjugate second`, expect success;
5. level 3: click `phase pi/2`, expect norm-preserved success;
6. level 4: click `make Hermitian`, expect success;
7. level 5: click `snap U`, expect unitary success;
8. level 6: choose `A* A`, expect SVD bridge and debrief.

Add mistake path:

1. level 1: choose bilinear square, expect `bilinear-trap`;
2. level 2: choose no conjugate, expect conjugate symmetry warning;
3. level 4: set `a12 = i`, `a21 = i`, expect not Hermitian;
4. level 5: set non-unit phase scale, expect `not-unitary`;
5. level 6: choose `A^T A`, expect warning about transpose vs adjoint.

Suggested test ids:

- `mission-unitary-compass`;
- `unitary-compass-canvas`;
- `complex-vector-plane`;
- `complex-vector-x`;
- `complex-vector-ix`;
- `unitary-bilinear-choice`;
- `unitary-hermitian-choice`;
- `unitary-conjugate-second-choice`;
- `unitary-phase-knob`;
- `unitary-phase-pi-half`;
- `unitary-hermitian-matrix`;
- `unitary-make-hermitian`;
- `unitary-matrix-a-re`;
- `unitary-matrix-a-im`;
- `unitary-matrix-b-re`;
- `unitary-matrix-b-im`;
- `unitary-snap-u`;
- `unitary-choice-ata`;
- `unitary-choice-astar-a`;
- `unitary-diagnosis`;
- `unitary-norm-badge`;
- `unitary-ustaru-badge`;

## P0. Refactoring guardrails

Do not generalize all math helpers yet. Complex arithmetic is enough of a new
domain that premature shared abstractions could make real 2D code harder to
read.

Allowed extraction only if implementation starts duplicating small stable
helpers:

```text
src/visualizations/shared/complex2d.ts
```

Allowed shared primitives:

- `Complex`;
- `addComplex`;
- `multiplyComplex`;
- `conjugate`;
- `absSquared`;
- `formatComplex`.

Keep mission-specific:

- Hermitian convention diagnostics;
- unitary success conditions;
- fake-trap messages;
- `A^*A` bridge logic;
- level presets.

## P1. PCA compression lab

Future route:

```text
/data/pca/compression-lab
```

Core idea:

- tiny matrix/image heatmap;
- user chooses rank `k`;
- app shows reconstruction, storage cost and Frobenius error;
- mission connects SVD to feature reduction and compression.

Why after `Унитарный компас`:

- `A^*A` and unitary factors will no longer be mysterious;
- low-rank approximation can focus on error/cost rather than explaining
  conjugate transpose;
- data section gets a stronger transfer from algebra.

## Implementation order

1. Create `unitaryCompassModel.ts` and focused unit tests.
2. Add mission definition with all authoring metadata.
3. Build static SVG layout for complex vector, phase arc and norm badges.
4. Add level 1 `i-scale-trap`.
5. Add level 2 `conjugate-slot`.
6. Add level 3 `phase-preserve`.
7. Add level 4 `fake-hermitian`.
8. Add level 5 `unitary-motion`.
9. Add level 6 `a-star-a-bridge`.
10. Wire route loader, registry, navigation and curriculum graph.
11. Add Playwright route screenshots, happy path and mistake path.
12. Run `make mission-audit` and update `mission_quality_report.md`.
13. Run full validation:
    - `make lint-js`;
    - `make lint-python`;
    - `make interactive-test`;
    - `make interactive-build`;
    - `.venv/bin/python SHAD/interactive/scripts/smoke_playwright.py --happy-paths-only`;
    - `.venv/bin/python SHAD/interactive/scripts/smoke_playwright.py --screens-only`;
    - `git diff --check`.
14. Inspect desktop/mobile screenshots manually.
15. Update `gameplay_roadmap.md`, `next_euclidean_unitary_stage_plan.md` and
    this plan status.

## Done criteria

The stage is done when:

- `/algebra/complex/unitary-compass` is visible in navigation and course map;
- user can complete all six levels without reading the lecture;
- bilinear-vs-Hermitian trap is visible as broken length;
- conjugation slot is explicit and matches the lecture convention;
- unitary level checks `U^*U`, not just one vector norm;
- fake Hermitian matrix mistake is caught;
- `A^*A` bridge explains why SVD uses adjoint;
- mission audit has no warnings;
- unit tests cover complex arithmetic, Hermitian symmetry, unitary preservation
  and fake traps;
- Playwright covers happy path, mistake path and screenshots;
- mobile screenshot has no horizontal overflow in complex matrix controls.

## Risks

- **Complex arithmetic overload.** Use small presets and phase controls; do not
  turn the mission into free-form matrix algebra.
- **Convention confusion.** The lecture uses linear-first/conjugate-second.
  Make that visible in labels and tests.
- **Too many formulas.** Main field should show phase, reflection and circle
  preservation; formulas stay in badges/debrief.
- **Unitary vs orthogonal duplication.** Reuse the idea of preserving geometry,
  but make conjugation the new mechanic.
- **A* A bridge too late.** Keep final level compact: one matrix, three choices,
  one visible Hermitian/PSD result.
- **Mobile density.** Complex entries are wider than real entries; stack them
  early.

## Suggested first commit slice

```text
feat(interactive): add unitary compass model
```

Scope:

- `unitaryCompassModel.ts`;
- model tests;
- mission metadata skeleton.

Second slice:

```text
feat(interactive): add unitary compass mission
```

Scope:

- mission component;
- registry/navigation/curriculum;
- smoke and screenshots;
- mission audit update.
