# SHAD Interactive: план этапа "Евклидова мастерская и унитарный компас"

Этот этап закрывает геометрический пробел между `Квадратичной линзой` и
`SVD-линзой`. Сейчас приложение уже умеет показывать форму, главные оси,
эллипс образа круга, сингулярные направления и PCA. Но пользователь еще не
получил отдельной игровой сцены, где ортогональность, проекция,
ортонормированный базис и сохранение длины становятся действиями.

Главный фокус этапа: **Евклидова мастерская**. Пользователь строит проекции,
остатки и ортонормированные базисы руками. Миссия должна объяснить не формулу
Грама-Шмидта как рецепт, а инвариант: каждый новый остаток должен быть
ортогонален уже построенному подпространству, а ортогональные операторы
сохраняют длины и углы.

P1-расширение этапа: **Унитарный компас** для комплексных пространств. На
момент P0 его нужно было спроектировать, но не реализовывать в первом срезе,
чтобы не перегрузить экран комплексной арифметикой, сопряжением и спектральной
теорией одновременно. Отдельный P1-этап теперь выполнен в
[next_unitary_compass_stage_plan.md](next_unitary_compass_stage_plan.md).

## Статус 2026-06-07

P0 выполнен:

- добавлена playable миссия `Евклидова мастерская` на route
  `/algebra/euclidean/orthogonal-workshop`;
- реализован pure TypeScript model layer `orthogonalWorkshopModel.ts` with
  unit tests;
- миссия подключена в `MissionDefinition`, lazy route loader, mission registry,
  navigation and curriculum graph;
- добавлены SVG-поле проекций, residual segment, orthogonal pair lab,
  normalization ray, Gram-Schmidt view and orthogonal operator circle;
- добавлены controls with numeric fallback and snap buttons for smoke;
- добавлены Playwright route screenshots, happy path and mistake path;
- `mission_quality_report.md` обновлен через `make mission-audit`;
- validation пройдена: JS lint, Python lint, Vitest, build, mission audit,
  Playwright happy/mistake smoke, Playwright screens-only and `git diff --check`.

P1 `Унитарный компас` выполнен отдельным этапом: добавлена playable mission
`/algebra/complex/unitary-compass`, pure model layer, route/registry/navigation,
curriculum node `complex-geometry` and Playwright smoke. Оставшийся хвост после
этой линии: `PCA compression lab`.

Подробный статус P1 `Унитарный компас` вынесен в
[next_unitary_compass_stage_plan.md](next_unitary_compass_stage_plan.md).

## Текущее состояние

В приложении уже есть двенадцать playable/prototype миссий:

- `Охота за ядром`;
- `Кузница определителя`;
- `Матрица как машина`;
- `Квадратичная линза`;
- `Евклидова мастерская`;
- `Унитарный компас`;
- `SVD-линза`;
- `Цех перестановок`;
- `Графовый диспетчер`;
- `Арена асимптотик`;
- `ML-полигон`;
- `Фабрика признаков`.

`mission_quality_report.md` показывает, что все текущие миссии проходят
authoring audit без предупреждений. Это хороший момент не добавлять очередной
демо-калькулятор, а поднять качество геометрической линии:

```text
матрица как действие
  -> площадь и ориентация
  -> ядро
  -> квадратичная форма
  -> ортогональность и проекция
  -> SVD/PCA
```

До выполнения `Унитарного компаса` в `curriculumGraph.ts` были planned links:

- `unitary-compass` у `quadratic-forms`;
- `unitary-compass` и `pca-compression-lab` у `svd-pca`.

Теперь отдельные curriculum nodes есть для `euclidean-geometry` и
`complex-geometry`; `unitary-compass` стал playable mission, а planned-хвостом
для этой линии остался `pca-compression-lab`.

## Лекционный охват

Основной источник:

- `SHAD/algebra/11_Euclidean_spaces/lesson.md`
  - скалярное произведение, длина и угол;
  - ортогональность и ортогональное дополнение;
  - ортогональная проекция на подпространство;
  - метод Грама-Шмидта;
  - ортогональные операторы и условие `Q^T Q = I`;
  - ошибки: путать независимость и ортогональность, забывать нормировку,
    вычитать не все проекции.

Связанные источники:

- `SHAD/algebra/10_Bilinear_quadratic_forms/lesson.md`
  - положительно определенные формы как скалярные произведения;
  - главные оси и ортогональная замена координат.
- `SHAD/algebra/12_Eigenvectors_eigenvalues/lesson.md`
  - ортогональность собственных направлений для симметрических операторов.
- `SHAD/algebra/13_Complex_spaces/lesson.md`
  - эрмитово произведение, унитарность, сопряжение, `A^*A` and SVD.

## Цель этапа

Сделать одну новую playable миссию уровня `prototype`:

- route: `/algebra/euclidean/orthogonal-workshop`;
- mission id: `orthogonal-workshop`;
- title: `Евклидова мастерская`;
- domain: `linear-algebra`;
- mechanic: `geometry-lab`;
- difficulty: `2`;
- lessonPath: `SHAD/algebra/11_Euclidean_spaces/lesson.md`;
- prerequisite missions: `quadratic-lens`, `kernel-hunt`;
- next mission later: `SVD-линза` or `Унитарный компас`.

Готовый stage должен:

1. показывать проекцию как тень на прямую или плоскость;
2. делать остаток видимо перпендикулярным подпространству;
3. давать игровую реализацию Грама-Шмидта;
4. показывать разницу между "независимо" и "ортогонально";
5. проверять ортогональный оператор через сохранение длины, угла и
   `Q^TQ = I`;
6. иметь pure TypeScript model layer с unit tests;
7. подключаться в `MissionDefinition`, registry, route loader, navigation and
   curriculum graph;
8. проходить lint, tests, build, mission audit and Playwright smoke.

## Игровая идея

На поле есть три зоны:

1. **Вектор и тень**: пользователь двигает вектор `x`, линия или подпространство
   ловит его проекцию `p`.
2. **Остаток**: отрезок `r = x - p` подсвечивается только тогда, когда
   `r` перпендикулярен подпространству.
3. **Мастерская базиса**: сырые векторы превращаются в ортонормированный базис
   через последовательное вычитание проекций и нормировку.

Важное ощущение: ортогонализация - это не "повернуть красиво", а "вычесть уже
объясненную часть". Если пользователь двигает второй вектор, приложение
показывает, какая его часть уже лежит в первом направлении, а какая остается
новой информацией.

Меби в этой миссии работает как **тень-остаток**:

- стоит на конце residual vector;
- краснеет, если остаток не ортогонален;
- вытягивает "перпендикулярную нитку", когда dot product становится нулем;
- показывает, что нулевой остаток означает зависимость, а не новый базис.

## Почему это игра

Миссия должна требовать действий, а не чтения:

- нельзя пройти уровень, просто выставив два независимых вектора;
- нужно сделать dot product нулевым;
- нужно нормировать без изменения направления;
- нужно вычесть обе проекции, а не только последнюю;
- нужно отличить отражение от поворота по determinant, при том что оба
  оператора ортогональны;
- нужно поймать fake-orthogonal matrix, которая сохраняет одну длину, но
  ломает угол или вторую ось.

Ошибки должны быть видимыми:

- остаток не перпендикулярен: угол не 90 degrees, badge `dot != 0`;
- вектор нормирован, но направление поменялось;
- векторы независимы, но сетка стала косой;
- `Q^TQ` почти `I`, but determinant sign explains rotation vs reflection;
- пользователь вычел только одну проекцию in 3-vector mode.

## P0. Model layer

Создать:

```text
src/visualizations/orthogonal-workshop/
  orthogonalWorkshopModel.ts
  orthogonalWorkshopModel.test.ts
```

Типы:

```ts
export type Vec2 = [number, number]
export type Vec3 = [number, number, number]

export type Matrix2x2 = {
  a: number
  b: number
  c: number
  d: number
}

export type OrthogonalDiagnosisKind =
  | 'ready'
  | 'zero-vector'
  | 'dependent'
  | 'not-orthogonal'
  | 'not-normalized'
  | 'not-orthogonal-operator'
  | 'reflection-vs-rotation'
```

Functions:

- `dot2(a, b)` and `dot3(a, b)`;
- `norm2(v)` and `norm3(v)`;
- `normalize2(v)` and `normalize3(v)`;
- `projectOntoLine2(point, direction)`;
- `projectOntoPlane3(point, basisA, basisB)`;
- `residual2(point, direction)`;
- `residual3(point, basis)`;
- `angleBetween2(a, b)`;
- `gramSchmidt2(vectors)`;
- `gramSchmidt3(vectors)`;
- `isOrthonormal2(vectors)`;
- `isOrthonormal3(vectors)`;
- `matrixColumns(matrix)`;
- `transposeTimesMatrix2(matrix)`;
- `determinant2(matrix)`;
- `isOrthogonalMatrix2(matrix)`;
- `applyMatrix2(matrix, point)`;
- `orthogonalOperatorDiagnosis(matrix)`.

Unit tests:

- projection residual is orthogonal to the line;
- projection onto a line reconstructs `x = p + r`;
- Gram-Schmidt preserves span in a simple 2D case;
- Gram-Schmidt detects dependent vectors without `NaN`;
- normalized vectors have norm `1`;
- independent but non-orthogonal vectors are rejected;
- rotation matrix is orthogonal and has determinant `1`;
- reflection matrix is orthogonal and has determinant `-1`;
- shear matrix is not orthogonal even if one vector length looks unchanged;
- near-zero vectors return explicit diagnosis.

Acceptance:

- model has no React imports;
- no external numeric library in P0;
- tolerances are explicit and shared inside this model;
- degenerate cases return diagnoses, not `NaN`.

## P0. Mission definition

Add `orthogonalWorkshopMission` in `src/game/missions.ts`.

Core metadata:

```ts
export const orthogonalWorkshopMission: MissionDefinition = {
  id: 'orthogonal-workshop',
  route: '/algebra/euclidean/orthogonal-workshop',
  title: 'Евклидова мастерская',
  domain: 'linear-algebra',
  mechanic: 'geometry-lab',
  lessonPath: 'SHAD/algebra/11_Euclidean_spaces/lesson.md',
  difficulty: 2,
  mascotRole: 'invariant-token',
  qualityTags: [
    'geometry-lab',
    'input-fallback',
    'mistake-diagnostics',
    'model-tested',
    'interesting-failure',
    'repair-loop',
  ],
  estimatedMinutes: 9,
}
```

Connection:

- `quadratic-lens.nextMissionRoute` can point to
  `/algebra/euclidean/orthogonal-workshop`;
- `orthogonal-workshop.nextMissionRoute` should point to `/algebra/svd/lens`;
- add curriculum node `euclidean-geometry`;
- `quadratic-forms.unlocks` should include `euclidean-geometry`;
- `euclidean-geometry.unlocks` should include `svd-pca`;
- `svd-pca.prerequisites` should include `euclidean-geometry` only if the
  course map can handle the extra gate without making existing SVD access feel
  broken. If that creates too much friction, use `reviewAfterMissionIds`
  instead.

## P0. Playable levels

### Level 1: `shadow-on-line`

Goal:

```text
Поставь тень x на прямую так, чтобы остаток стал перпендикулярен.
```

Action:

- user drags point `x`;
- user drags projection point `p` along a fixed line;
- residual `r = x - p` is drawn as a segment.

Success:

- `p` lies on the line;
- `dot(r, direction) ~= 0`;
- `x ~= p + r`.

Mistakes:

- `p` close to line visually but not actually on it;
- residual short but not perpendicular;
- user chooses zero direction for the line.

Takeaway:

```text
Ортогональная проекция - это такая тень, после которой ошибка перпендикулярна подпространству.
```

### Level 2: `independent-is-not-orthogonal`

Goal:

```text
Сделай два вектора ортогональными, не схлопнув базис.
```

Action:

- user drags two basis vectors;
- field shows parallelogram area, dot product and angle.

Success:

- both vectors nonzero;
- `abs(dot) < tolerance`;
- determinant area remains noticeable.

Mistakes:

- vectors independent but dot product nonzero;
- vectors perpendicular but one is nearly zero;
- vectors become collinear while trying to repair.

Takeaway:

```text
Ортогональность сильнее линейной независимости: она одновременно дает независимость и удобные координаты.
```

### Level 3: `normalize-without-turning`

Goal:

```text
Сделай вектор единичным, сохранив направление.
```

Action:

- user controls length and angle separately;
- ghost ray marks original direction.

Success:

- norm is `1`;
- direction matches the original ray up to sign policy chosen by level.

Mistakes:

- norm fixed but direction changed;
- direction fixed but length not `1`;
- vector crosses through zero.

Takeaway:

```text
Нормировка меняет масштаб, но не направление.
```

### Level 4: `gram-schmidt-two`

Goal:

```text
Из двух косых векторов собери ортонормированный базис с той же оболочкой.
```

Action:

- stage shows raw vectors `a1`, `a2`;
- user chooses projection of `a2` onto `e1`;
- app shows residual `b2 = a2 - proj`;
- user normalizes `b1`, `b2`.

Success:

- `e1`, `e2` are orthonormal;
- span is preserved;
- residual step was used, not replaced by arbitrary perpendicular vector.

Mistakes:

- arbitrary perpendicular vector with wrong span;
- normalized before subtracting projection;
- forgot to subtract projection.

Takeaway:

```text
Грам-Шмидт сохраняет уже построенную оболочку и добавляет только новый ортогональный остаток.
```

### Level 5: `orthogonal-operator`

Goal:

```text
Собери оператор, который сохраняет длины и углы.
```

Action:

- user adjusts 2x2 matrix columns;
- app shows transformed unit square/circle;
- badges show `Q^TQ`, determinant, angle and lengths.

Success:

- columns are orthonormal;
- `Q^TQ ~= I`;
- transformed circle remains circle.

Mistakes:

- matrix preserves one vector length but not all lengths;
- determinant is `-1` when level asks for rotation;
- almost orthogonal but with visible angle drift.

Takeaway:

```text
Ортогональный оператор сохраняет скалярное произведение целиком, поэтому сохраняет длины и углы сразу для всех векторов.
```

## P0. UI design

The mission should be visually calmer than `SVD-линза`: fewer formulas, more
geometry.

Layout:

- first viewport remains the playable field;
- compact top badges:
  - `dot`;
  - `norm`;
  - `angle`;
  - `det` or `Q^TQ`;
- left/main SVG field:
  - paper grid;
  - line or basis;
  - projection shadow;
  - residual segment;
  - angle marker;
- right/controls:
  - numeric fallback for vector coordinates;
  - buttons `project`, `orthogonalize`, `normalize`, `snap Q`;
  - level stepper and diagnosis.

Design details:

- projection shadow should look like an actual shadow dropped onto the line;
- residual should be a crisp contrasting segment, not a faint helper;
- right angle marker should appear only near success;
- avoid text-heavy explanation panels;
- Mebi should attach to the residual endpoint, because that is the concept the
  user is repairing.

Mobile:

- SVG field above controls;
- vector controls one column;
- no two-column matrix controls under 390px;
- badges wrap in two rows without horizontal overflow;
- Playwright screenshots must include this route.

## P0. Route, registry and navigation

Add lazy route:

```ts
export const OrthogonalWorkshopMission = lazy(() =>
  import('./orthogonal-workshop/OrthogonalWorkshopMission').then((module) => ({
    default: module.OrthogonalWorkshopMission,
  })),
)
```

Add mission entry:

```ts
{
  id: 'orthogonal-workshop',
  path: '/algebra/euclidean/orthogonal-workshop',
  title: 'Евклидова мастерская',
  kind: 'mission',
  status: 'prototype',
  difficulty: 2,
  lessonPath: orthogonalWorkshopMission.lessonPath,
  mission: orthogonalWorkshopMission,
  component: OrthogonalWorkshopMission,
  meta: {
    title: 'Евклидова мастерская',
    formula: String.raw`x=\mathrm{proj}_U x + r,\quad r\perp U`,
    description:
      'Проекция, остаток и Грам-Шмидт становятся игровыми операциями над ортогональностью.',
  },
}
```

Navigation:

- add algebra topic `Евклидовы пространства`;
- place it between `Квадратичные формы` and `SVD и PCA`;
- include `missionEntry('orthogonal-workshop')`.

## P0. Playwright smoke

Add route screenshots:

- `orthogonal-workshop-desktop.png`;
- `orthogonal-workshop-mobile.png`.

Add happy path:

1. open `#/algebra/euclidean/orthogonal-workshop`;
2. check `mission-orthogonal-workshop`;
3. level 1: click `project`, expect success;
4. level 2: click `orthogonalize`, expect success;
5. level 3: click `normalize`, expect success;
6. level 4: click `gram-schmidt`, expect success;
7. level 5: click `snap Q`, expect debrief.

Add mistake path:

1. level 2: make vectors independent but non-orthogonal;
2. expect diagnosis to mention `dot`;
3. expect mascot warning state;
4. level 5: set shear matrix;
5. expect diagnosis to mention that preserving one length is not enough.

Suggested test ids:

- `mission-orthogonal-workshop`;
- `orthogonal-workshop-canvas`;
- `orthogonal-line`;
- `orthogonal-vector-x`;
- `orthogonal-projection`;
- `orthogonal-residual`;
- `orthogonal-angle-marker`;
- `orthogonal-dot-badge`;
- `orthogonal-norm-badge`;
- `orthogonal-det-badge`;
- `orthogonal-qtq-badge`;
- `orthogonal-diagnosis`;
- `orthogonal-vector-a-x`;
- `orthogonal-vector-a-y`;
- `orthogonal-vector-b-x`;
- `orthogonal-vector-b-y`;
- `orthogonal-matrix-a`;
- `orthogonal-matrix-b`;
- `orthogonal-matrix-c`;
- `orthogonal-matrix-d`;

## P0. Refactoring guardrails

Do not create a broad math framework before the mission works. But while
implementing, watch for real duplication with:

- `quadratic-lens/quadraticLensModel.ts`;
- `svd-lens/svdLensModel.ts`;
- existing vector/matrix helpers inside mission components.

Allowed small extraction if duplication becomes meaningful:

```text
src/visualizations/shared/linearAlgebra2d.ts
```

Only extract stable primitives:

- `Vec2`;
- `Matrix2x2`;
- `dot`;
- `norm`;
- `normalize`;
- `determinant`;
- `applyMatrix`;
- `transposeTimesMatrix`.

Do not move domain-specific functions:

- quadratic classification;
- SVD sign/degenerate handling;
- Gram-Schmidt diagnostics;
- level success conditions.

Acceptance for refactor:

- no change in public route behavior;
- existing `quadraticLensModel` and `svdLensModel` tests remain green;
- imports stay shallow and readable.

## P1. Унитарный компас

Future route:

```text
/algebra/complex/unitary-compass
```

Core idea:

- complex number/vector shown as arrow with phase;
- conjugation is visible as reflection of phase;
- Hermitian inner product uses conjugation in one argument;
- unitary operator preserves Hermitian norm;
- `A^*A` bridges back to SVD.

Playable levels:

1. `i-scale-trap`: scale by `i` and catch why bilinear dot product is wrong;
2. `conjugate-slot`: choose the correct conjugated slot in Hermitian product;
3. `phase-preserve`: rotate phase without changing norm;
4. `fake-hermitian`: catch a matrix that looks symmetric but is not Hermitian;
5. `a-star-a`: build `A^*A` and connect it to singular values.

Why not P0:

- complex arithmetic needs a different visual grammar;
- current app has no complex-plane control primitives yet;
- P0 Euclidean Workshop gives the norm/orthogonality vocabulary first.

## P1. PCA compression lab

Future route:

```text
/data/pca/compression-lab
```

Core idea:

- tiny grayscale matrix or low-resolution image;
- user chooses rank `k`;
- app shows reconstruction, storage cost and Frobenius error;
- mission connects `SVD-линза` to data compression and feature reduction.

Why not immediate:

- without Euclidean/projection vocabulary it risks becoming "image slider";
- after `Евклидова мастерская`, error as orthogonal residual is easier to
  explain.

## Implementation order

1. Create `orthogonalWorkshopModel.ts` and focused unit tests.
2. Build `OrthogonalWorkshopMission.tsx` with static SVG layout and one level.
3. Add mission definition with all authoring metadata.
4. Add levels 2-5 and pure success/diagnosis helpers.
5. Wire route loader, registry, navigation and curriculum graph.
6. Add Playwright route screenshots, happy path and mistake path.
7. Run `make mission-audit` and update `mission_quality_report.md`.
8. Run full validation:
   - `make lint-js`;
   - `make lint-python`;
   - `make interactive-test`;
   - `make interactive-build`;
   - `.venv/bin/python SHAD/interactive/scripts/smoke_playwright.py --happy-paths-only`;
   - `.venv/bin/python SHAD/interactive/scripts/smoke_playwright.py --screens-only`;
   - `git diff --check`.
9. Inspect desktop/mobile screenshots manually.
10. Update `gameplay_roadmap.md` and this plan status.

## Done criteria

The stage is done when:

- `/algebra/euclidean/orthogonal-workshop` is visible in navigation and course
  map;
- user can complete all five levels without reading the lecture;
- projection residual is visible and checked geometrically;
- Gram-Schmidt level requires projection subtraction, not arbitrary
  perpendicular vector;
- orthogonal operator level catches shear and reflection-vs-rotation mistakes;
- mission audit has no warnings;
- unit tests cover degenerate vector and fake orthogonal cases;
- Playwright covers happy path, mistake path and screenshots;
- mobile screenshot has no horizontal overflow in vector or matrix controls.

## Risks

- **Too abstract.** Keep projection/residual visible as geometry, not formulas.
- **Too many badges.** Show only the invariant that matters for the active
  level.
- **Gram-Schmidt becomes one-click.** The snap button is allowed for smoke, but
  the normal interaction should expose projection and residual separately.
- **Span preservation is invisible.** Use ghost raw vectors and a shaded span
  wedge so arbitrary perpendicular replacement is visibly wrong.
- **Orthogonal operator duplicates SVD.** Keep this level about preserving
  circle as circle, not circle-to-ellipse.
- **Complex P1 overload.** Do not implement `Унитарный компас` until Euclidean
  controls feel good.

## Suggested first commit slice

```text
feat(interactive): add orthogonal workshop model
```

Scope:

- `orthogonalWorkshopModel.ts`;
- model tests;
- mission metadata skeleton;
- no route UI yet.

Second slice:

```text
feat(interactive): add orthogonal workshop mission
```

Scope:

- mission component;
- registry/navigation/curriculum;
- smoke and screenshots;
- mission audit update.
