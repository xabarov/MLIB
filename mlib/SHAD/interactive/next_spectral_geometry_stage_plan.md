# SHAD Interactive: план этапа "Спектральная геометрия и формы"

Этот этап возвращает interactive к линейной алгебре после quality/game-feel
улучшений и первых programming/data миссий. Цель - не просто добавить еще одну
визуализацию, а собрать следующую сильную игровую механику для лекций про
билинейные и квадратичные формы, евклидовы пространства, собственные векторы и
комплексные пространства.

Главный фокус этапа: **Квадратичная линза**. Пользователь руками меняет
симметрическую форму, видит эллипс, седло, вырожденное направление и главные
оси, а затем учится убирать смешанный член поворотом базиса. Это естественный
мост к спектральной теореме, SVD, PCA и устойчивой геометрии данных.

## Статус 2026-06-07

P0 выполнен:

- добавлена playable миссия `Квадратичная линза` на route
  `/algebra/quadratic-forms/lens`;
- реализован чистый model layer `quadraticLensModel.ts` with unit tests;
- миссия подключена в `MissionDefinition`, lazy route loader, mission registry,
  navigation and curriculum graph;
- добавлены SVG-поле, контуры формы, главные оси, поворот базиса, markers
  направлений, coefficient controls and numeric fallback;
- добавлены smoke checks для happy path, mistake path and screenshots;
- `mission_quality_report.md` обновлен через `make mission-audit`;
- validation пройдена: JS lint, Python lint, Vitest, build, Playwright
  happy/mistake smoke, Playwright screens-only and `git diff --check`.

Оставшийся P1: `SVD-линза`, `Евклидова мастерская` and `Унитарный компас`
остаются будущими расширениями.

Следующий подробный план для P1 вынесен в
[next_svd_pca_stage_plan.md](next_svd_pca_stage_plan.md).

## Почему это следующий этап

Сейчас в приложении уже есть базовый язык линейной алгебры:

- `Матрица как машина` показывает столбцы как действие на базисе;
- `Кузница определителя` показывает площадь, ориентацию и вырожденность;
- `Охота за ядром` показывает схлопнутые направления и rank-nullity;
- общий `MissionShell`, debrief, quality audit и smoke-проверки уже готовы.

Но между этими миссиями и будущими SVD/PCA сюжетами пока не хватает
центрального геометрического звена:

```text
матрица -> форма x^T A x -> главные оси -> собственные направления -> SVD/PCA
```

Именно это звено хорошо "трогается руками": поворот осей, знак энергии,
схлопывание одного направления, исчезновение смешанного члена и классификация
по сигнатуре дают не текстовую, а игровую обратную связь.

## Лекционный охват

Этап должен опираться на уже накопленные лекции:

- `SHAD/algebra/10_Bilinear_quadratic_forms/lesson.md`
  - билинейные формы;
  - квадратичные формы;
  - матрица формы;
  - приведение к диагональному виду;
  - сигнатура и вырожденность.
- `SHAD/algebra/11_Euclidean_spaces/lesson.md`
  - скалярное произведение;
  - положительная определенность;
  - ортогональность;
  - ортонормированные базисы;
  - квадрики.
- `SHAD/algebra/12_Eigenvectors_eigenvalues/lesson.md`
  - собственные направления;
  - собственные подпространства;
  - диагонализация.
- `SHAD/algebra/13_Complex_spaces/lesson.md`
  - эрмитовы формы;
  - унитарность;
  - SVD;
  - PCA and low-rank approximation as later transfer.

На этом этапе реализуем P0 только для вещественного 2D случая. Комплексные
пространства и SVD фиксируем как следующий слой, чтобы не перегрузить первую
вертикаль.

## Цель этапа

Сделать одну новую playable миссию уровня `prototype`, которая:

1. работает как прямое manipulation-поле, а не как калькулятор;
2. имеет чистый model layer с unit tests;
3. подключена в `MissionDefinition`, registry, route loaders, curriculum graph
   и карту курса;
4. проходит mission audit, unit tests, build and Playwright smoke;
5. дает понятный мост к SVD без реализации SVD в этом же этапе.

Рабочее имя:

- route: `/algebra/quadratic-forms/lens`;
- mission id: `quadratic-lens`;
- title: `Квадратичная линза`;
- domain: `linear-algebra`;
- mechanic: `geometry-lab`;
- difficulty: `2`;
- lessonPath: `SHAD/algebra/10_Bilinear_quadratic_forms/lesson.md`;
- next mission later: `SVD-линза`.

## Игровая идея

Пользователь видит поле с координатной сеткой и форму

```text
q(x, y) = ax^2 + 2bxy + cy^2.
```

Он меняет коэффициенты `a`, `b`, `c`, вращает базис и таскает тестовый вектор.
Поле показывает:

- уровень `q(x,y)=1` как эллипс, гиперболу, пару линий или исчезнувшую форму;
- главные оси формы;
- знак энергии выбранного направления;
- собственные значения как "растяжения" по главным осям;
- смешанный член `2bxy` как видимое смешивание координат;
- сигнатуру: `(+,+)`, `(+,-)`, `(+,0)`, `(-,-)`.

Меби здесь не просто подсказчик, а **маркер направления**: он встает на
тестовый вектор или главную ось и реагирует на знак формы. Если направление
положительное, отрицательное или нулевое, это видно в поле, а не только в
тексте.

## Почему это игра

В хорошей версии миссии нельзя пройти уровни чтением формулы. Нужно сделать
видимый объект правильным:

- закрыть эллипс, не получив седло;
- убрать смешанный член не удалением коэффициента, а поворотом осей;
- найти два направления с разными знаками;
- схлопнуть одно направление до нулевой энергии;
- объяснить итог через сигнатуру.

Ошибки должны быть интересными:

- если форма стала неопределенной, эллипс распадается в седло;
- если выбран нулевой вектор, Меби показывает "это не направление";
- если пользователь просто ставит `b=0`, уровень про поворот не засчитывается;
- если determinant почти ноль, поле должно показать fragile/collapse state;
- если ось почти совпала с eigenvector, включается snap/lock feedback.

## P0. Model layer

Создать папку:

```text
src/visualizations/quadratic-lens/
```

Добавить чистую модель:

```text
quadraticLensModel.ts
quadraticLensModel.test.ts
```

Основные типы:

```ts
export type Symmetric2x2 = {
  a: number
  b: number
  c: number
}

export type QuadraticClassification =
  | 'positive-definite'
  | 'negative-definite'
  | 'indefinite'
  | 'positive-semidefinite'
  | 'negative-semidefinite'
  | 'zero'

export type EigenPair2D = {
  lambda: number
  vector: { x: number; y: number }
}
```

Функции:

- `quadraticValue(form, point)`:
  - считает `ax^2 + 2bxy + cy^2`;
  - используется в UI, success conditions and tests.
- `determinantOfForm(form)`:
  - считает `ac - b^2`;
  - связывает миссию с `Кузницей определителя`.
- `classifyQuadraticForm(form)`:
  - возвращает тип формы по знакам собственных значений and determinant.
- `eigenPairsSymmetric2x2(form)`:
  - аналитически считает две пары;
  - нормирует векторы;
  - гарантирует ортогональность с учетом tolerance.
- `rotateForm(form, theta)`:
  - считает матрицу формы в повернутом базисе;
  - нужен для уровня "убери смешанный член".
- `principalAxisAngle(form)`:
  - возвращает угол главной оси;
  - устойчиво обрабатывает `a ~= c`.
- `levelSetSample(form, level, options)`:
  - генерирует SVG-friendly точки/ветви для ellipse/hyperbola/degenerate;
  - не должен падать на вырожденных формах.
- `signatureLabel(form)`:
  - возвращает `(+,+)`, `(+,-)`, `(+,0)`, etc.

Unit tests:

- диагональная форма `x^2 + 4y^2` классифицируется как positive definite;
- форма `x^2 - y^2` классифицируется как indefinite;
- форма `x^2` классифицируется как positive semidefinite;
- форма `-x^2 - y^2` классифицируется как negative definite;
- для симметрической формы eigenvectors ортогональны;
- `rotateForm` с углом главной оси делает cross-term near zero;
- `quadraticValue` сохраняется при согласованном повороте формы и точки;
- `levelSetSample` возвращает непустой набор для ellipse and hyperbola;
- near-degenerate cases не дают `NaN`.

Acceptance:

- `pnpm test -- quadraticLensModel` проходит;
- функции не зависят от React;
- все tolerance вынесены в константы рядом с моделью.

## P0. Mission definition

Добавить `quadraticLensMission` в `src/game/missions.ts`.

Базовые поля:

```ts
export const quadraticLensMission: MissionDefinition = {
  id: 'quadratic-lens',
  route: '/algebra/quadratic-forms/lens',
  title: 'Квадратичная линза',
  domain: 'linear-algebra',
  mechanic: 'geometry-lab',
  lessonPath: 'SHAD/algebra/10_Bilinear_quadratic_forms/lesson.md',
  difficulty: 2,
  mascotRole: 'invariant-token',
  qualityTags: [
    'geometry-lab',
    'input-fallback',
    'mistake-diagnostics',
    'model-tested',
    'interesting-failure',
  ],
  estimatedMinutes: 8,
}
```

Связать с существующими миссиями:

- `matrix-machine.nextMissionRoute` can point to determinant or keep current
  chain unchanged;
- `determinant-forge` and `kernel-hunt` remain earlier missions;
- `quadratic-lens` should appear after `determinants` and `linear-maps-kernel`
  in curriculum graph;
- later `quadratic-lens.nextMissionRoute` should point to `/algebra/svd/lens`
  when SVD mission exists.

## P0. Уровни миссии

### Level 1: `positive-energy`

Цель:

```text
Собери форму, которая измеряет положительную энергию во всех ненулевых
направлениях.
```

Игровое действие:

- sliders/inputs for `a`, `b`, `c`;
- пользователь должен получить closed ellipse;
- badge показывает `det = ac - b^2` and `signature = (+,+)`.

Success:

- classification is `positive-definite`;
- determinant is greater than tolerance;
- both eigenvalues are positive.

Mistakes:

- `det <= 0`: field turns into saddle/collapse;
- `a <= 0`: first coordinate already has non-positive energy;
- zero vector selected: not a direction.

Takeaway:

```text
Положительно определенная квадратичная форма ведет себя как квадрат длины:
q(x,x)>0 для любого ненулевого x.
```

### Level 2: `cross-term-rotation`

Цель:

```text
Убери смешанный член поворотом осей, не редактируя саму форму.
```

Игровое действие:

- форма стартует с `b != 0`;
- coefficients locked after start;
- пользователь вращает coordinate frame;
- UI показывает текущий cross-term in rotated basis.

Success:

- `abs(rotated.b) < tolerance`;
- axis angle aligns with principal axis;
- original form still has nonzero `b`, чтобы нельзя было пройти простым
  занулением coefficient.

Mistakes:

- повернут не базис, а коэффициент отредактирован вручную;
- ось почти правильная, но cross-term still visible;
- пользователь перепутал две главные оси, but classification remains correct.

Takeaway:

```text
Главные оси - это направления, в которых форма перестает смешивать координаты.
```

### Level 3: `saddle-signature`

Цель:

```text
Найди два направления: в одном q положительна, в другом отрицательна.
```

Игровое действие:

- start form is indefinite;
- user drags two direction markers;
- one marker must land in positive region, another in negative region.

Success:

- selected direction `u` has `q(u) > threshold`;
- selected direction `v` has `q(v) < -threshold`;
- markers are nonzero and sufficiently separated.

Mistakes:

- both directions have same sign;
- one marker too close to zero;
- user finds sign by tiny numerical noise near asymptote.

Takeaway:

```text
Неопределенная форма не является длиной: у нее есть положительные и
отрицательные направления.
```

### Level 4: `degenerate-direction`

Цель:

```text
Схлопни форму так, чтобы одно ненулевое направление стало нулевой энергией.
```

Игровое действие:

- user adjusts coefficients or target axis;
- contour collapses into parallel lines or a strip-like degenerate state;
- Mebi stands on null-energy direction.

Success:

- determinant near zero;
- exactly one eigenvalue near zero and the other is away from zero;
- selected marker is nonzero and has `abs(q(marker)) < tolerance`.

Mistakes:

- all coefficients near zero: form disappeared, not one direction collapsed;
- determinant not near zero;
- selected null marker is zero vector.

Takeaway:

```text
Вырожденная квадратичная форма теряет измерение хотя бы одного ненулевого
направления.
```

### Level 5: `signature-repair`

Цель:

```text
Почини форму под заданную сигнатуру.
```

Игровое действие:

- app gives target signature, for example `(+,+)` or `(+,-)`;
- user may choose either rotate axes or adjust one coefficient depending on
  scenario;
- diagnosis compares eigenvalues, determinant and current contour.

Success:

- current signature equals target signature;
- if target is positive definite, ellipse is visible and stable;
- if target is indefinite, both signs are demonstrated by markers.

Mistakes:

- target achieved only numerically near tolerance;
- contour contradicts signature because sampling failed;
- user changes determinant sign but ignores selected direction checks.

Takeaway:

```text
Сигнатура классифицирует форму по знакам главных коэффициентов после
диагонализации.
```

Acceptance for levels:

- every level has `hintLevels`, `mistakeFeedback`, `successConditionLabel`,
  `takeaway`, `lectureAnchor` and `nextPrompt`;
- every level has at least one real mistake path;
- final debrief connects forms to eigenvectors and SVD.

## P0. UI components

### `QuadraticLensMission.tsx`

Главный контейнер должен переиспользовать:

- `MissionShell`;
- `InvariantBadge`;
- `MetricBadge` if useful for energy values;
- `MascotCoach`;
- `MissionDebriefCard`.

Do not build a separate page shell.

### `QuadraticCanvas`

Лучше начать с SVG, not Three.js:

- 2D level sets are precise and cheaper;
- mobile behavior easier to control;
- Playwright can inspect DOM selectors;
- no risk of blank WebGL/canvas scene.

Responsibilities:

- draw coordinate grid;
- draw contour branches;
- draw principal axes;
- draw rotated basis ghost axes;
- draw draggable test vectors;
- show positive/negative/zero regions by restrained color accents;
- expose stable `data-testid` values for smoke tests.

Visual constraints:

- игровое поле должно быть главным элементом первого экрана;
- no nested cards inside cards;
- controls should not dominate the scene;
- use distinct colors for positive, negative, zero/collapse and target;
- no one-hue palette;
- all labels must fit on mobile.

### `QuadraticControlPanel`

Controls:

- sliders and numeric inputs for `a`, `b`, `c`;
- rotate handle/slider for basis angle;
- level value selector, default `q=1`;
- reset button;
- snap-to-axis toggle;
- reduced motion friendly mode.

Controls must be feature-complete, but compact. The user should be able to use
mouse/touch on canvas and numeric inputs as fallback.

### `SignatureBadge`

Small focused badge:

```text
signature: (+,+)
lambda: 3.2, 0.8
det: 2.56
```

Do not make it a long explanation block. The learning sentence belongs in the
debrief and level takeaway.

## P0. Curriculum and navigation

Add a curriculum node:

```ts
{
  id: 'quadratic-forms',
  title: 'Квадратичные формы',
  cardLabel: 'Энергия и главные оси',
  section: 'algebra',
  lessonPaths: ['SHAD/algebra/10_Bilinear_quadratic_forms/lesson.md'],
  prerequisites: ['matrices', 'determinants', 'linear-maps-kernel'],
  missionIds: ['quadratic-lens'],
  plannedMissionIds: ['svd-lens', 'unitary-compass'],
  skillIds: ['quadratic-form', 'signature', 'principal-axes'],
  unlocks: ['euclidean-geometry', 'eigenvectors'],
  reviewAfterMissionIds: ['determinant-forge', 'kernel-hunt'],
  readinessLabel: 'Главные оси готовятся',
  coverageStatus: 'playable',
  takeaway: 'Симметрическая форма измеряет направления через главные оси и сигнатуру.',
  status: 'prototype',
}
```

If `euclidean-geometry` and `eigenvectors` nodes do not exist yet, add either:

- only planned unlock strings after extending validation, or
- placeholder curriculum nodes with `plannedMissionIds` and no live mission.

For this repo the safer P0 path is:

- add `quadratic-forms` as live node;
- let it unlock existing `linear-maps-kernel` only if validation requires
  current node IDs;
- document future `euclidean-geometry`, `eigenvectors`, `svd-lens` in this
  plan but do not force placeholder graph nodes unless implementation needs
  them.

## P0. Routing and lazy loading

Add:

- `src/visualizations/quadratic-lens/QuadraticLensMission.tsx`;
- export lazy component in `src/visualizations/routeLoaders.ts`;
- add entry to `src/visualizations/missionRegistry.ts`;
- add mission to `missionDefinitions`;
- ensure `courseMapNodes` shows it.

Registry entry:

```ts
{
  id: 'quadratic-lens',
  path: '/algebra/quadratic-forms/lens',
  title: 'Квадратичная линза',
  kind: 'mission',
  status: 'prototype',
  difficulty: 2,
  lessonPath: quadraticLensMission.lessonPath,
  mission: quadraticLensMission,
  component: QuadraticLensMission,
  meta: {
    title: 'Квадратичная линза',
    formula: String.raw`q(x,y)=ax^2+2bxy+cy^2`,
    description:
      'Квадратичная форма превращается в эллипс, седло или вырожденное направление; главные оси убирают смешанный член.',
  },
}
```

## P0. Tests and smoke

Unit:

- `quadraticLensModel.test.ts`;
- curriculum graph validation;
- mission quality audit.

Playwright:

- route opens without console errors;
- first level positive-definite happy path;
- second level cross-term rotation happy path;
- mistake path for indefinite form on positive level;
- debrief appears after completing all levels;
- mobile screenshot at one narrow viewport;
- no overlapping text in main controls.

Suggested test ids:

- `quadratic-lens-canvas`;
- `quadratic-contour`;
- `principal-axis`;
- `basis-rotation`;
- `coefficient-a`;
- `coefficient-b`;
- `coefficient-c`;
- `signature-badge`;
- `energy-marker`;
- `quadratic-level-success`.

Acceptance:

- `pnpm lint`;
- `pnpm test`;
- `pnpm build`;
- `pnpm exec playwright test`;
- `make mission-audit`;
- `git diff --check`.

If full Playwright is too slow, at minimum run the new smoke spec and keep the
limitation explicit in the final report.

## P1. SVD-линза

Do not implement SVD in P0, but design P0 so that P1 is natural.

Future route:

```text
/algebra/svd/lens
```

Core mechanic:

- start with unit circle;
- apply arbitrary 2x2 matrix;
- user decomposes transformation into:
  - right rotation/reflection;
  - axis scaling by singular values;
  - left rotation/reflection;
- app shows `A = U Sigma V^T`.

Playable levels:

1. make circle become the target ellipse;
2. identify two singular directions;
3. compare eigenvalues of `A` and singular values of `A`;
4. truncate one singular value and see low-rank approximation;
5. connect to PCA by squeezing a small point cloud.

Why later:

- SVD needs the quadratic lens vocabulary first;
- users need to have seen `A^T A` as a positive semidefinite form;
- UI complexity is higher, because it combines transformation and form.

## P1. Евклидова мастерская

Future route:

```text
/algebra/euclidean/orthogonal-workshop
```

Core mechanic:

- user builds orthonormal basis with Gram-Schmidt;
- app shows projection shadows and residuals;
- mistakes are visible when a residual is not orthogonal.

Playable levels:

1. project a vector onto a line;
2. make two vectors orthogonal;
3. normalize without changing direction;
4. build an orthonormal basis from two vectors;
5. preserve length with an orthogonal operator.

This can be either before or after SVD. If the P0 Quadratic Lens feels too
abstract in testing, Euclidean Workshop is the best next remedial mission.

## P1. Унитарный компас

Future route:

```text
/algebra/complex/unitary-compass
```

Core mechanic:

- complex vector as point/arrow with phase;
- conjugation is visible;
- unitary transformation preserves Hermitian norm;
- self-adjoint operator has real eigenvalues.

Playable levels:

1. distinguish bilinear from sesquilinear by trying to scale by `i`;
2. make a Hermitian form;
3. preserve norm under unitary rotation;
4. catch a fake "symmetric" complex matrix that is not Hermitian;
5. connect singular values to eigenvalues of `A* A`.

This belongs after users already understand the real 2D quadratic lens.

## Design notes

The mission should feel like a precise mathematical instrument, not a
dashboard:

- first viewport: field, goal, compact badges, Mebi marker;
- controls are dense but calm;
- no decorative hero;
- no text-heavy explanation panels;
- use motion only to show state changes:
  - contour morph;
  - axis snap;
  - collapse pulse near determinant zero;
  - positive/negative direction glow.

Palette proposal within current design language:

- paper/warm neutral background;
- ink grid and axes;
- positive energy: green accent;
- negative energy: red/coral accent;
- zero/collapse: graphite or amber;
- target axis: blue accent;
- Mebi expression changes by state, but keeps the same scale.

Accessibility:

- every color-coded state also has a label or shape difference;
- sliders have numeric inputs;
- canvas interactions have keyboard/numeric fallback;
- reduced motion disables morph animation and uses immediate redraw;
- touch targets meet mobile size expectations.

## Architecture constraints

Keep the implementation boring in the right places:

- math in pure TypeScript model;
- React component only renders model state;
- no string parsing for formulas;
- no new global store unless progress/runtime needs it;
- do not add a second mission runtime;
- do not hardcode success in UI event handlers;
- use existing mission runtime and quality audit fields.

Potential extraction only if it removes real duplication:

- shared `Vector2` helpers;
- shared 2D drag hook;
- shared `NumericSliderField`;
- shared `AxisGridSvg`.

Do not extract a generic geometry engine yet. One well-tested mission is more
valuable than a premature framework.

## Implementation order

1. Create model and tests.
2. Add mission definition with full authoring metadata.
3. Build `QuadraticLensMission` with static SVG state first.
4. Add coefficient controls and direction marker.
5. Add basis rotation level and cross-term diagnostics.
6. Add degenerate and signature repair levels.
7. Connect route loader, registry, curriculum graph and course map.
8. Add Playwright smoke for happy and mistake paths.
9. Run lint, unit tests, build, smoke and mission audit.
10. Update `mission_quality_report.md`, screenshots notes if needed and this
    plan status.

## Done criteria

The stage is done when:

- `/algebra/quadratic-forms/lens` is visible from the app and course map;
- all five levels are playable without reading source code or lecture text;
- user actions visibly change contour, axes, signature and energy;
- at least two wrong paths are visually repairable;
- final debrief explains the bridge to eigenvectors and SVD;
- quality audit has no new hard failures;
- full validation is recorded in the final work report.

## Risks

- **Hyperbola rendering can become messy.** Keep sampling conservative and use
  clipped SVG branches instead of trying to draw perfect analytic curves.
- **Rotation math can be confusing.** Tests must pin down whether `theta`
  rotates the basis or the object.
- **Too many controls can kill the game feel.** Start with canvas-first layout
  and hide advanced numeric details in compact panels.
- **SVD temptation.** Avoid implementing SVD in this stage. Mention it in
  debrief and roadmap only.
- **Near-zero numerical states.** Use explicit tolerance and show "almost
  degenerate" as warning, not success.

## Suggested next commit slice

Recommended first implementation commit:

```text
feat(interactive): add quadratic lens model and mission shell
```

Scope:

- model and unit tests;
- mission definition;
- initial component with level 1 and static/interactive coefficients;
- route/registry/curriculum wiring.

Then a second commit can add rotation, degenerate levels and smoke tests.
