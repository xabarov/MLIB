# SHAD Interactive: human mission review

Generated audit lives in `mission_quality_report.md` and is rewritten by
`make mission-audit`. This file is manual and should survive audit reruns.

## Review 2026-06-09 (Phase C): binary search tree

| Mission | Evidence |
| --- | --- |
| `Дерево поиска` | Раздел `algorithms`, механика `structure-builder` (третья). 3 уровня: найти 7 (лист), найти 2 (левый угол), искать 6 (нет в дереве - поиск кончается на листе). Спускаешься по дереву, кликая ребёнка в нужную сторону по сравнению (меньше - влево, больше - вправо); путь поиска зеленеет. Диагностика wrong-branch. Детерминированная модель, 6 unit-тестов, smoke happy + mistake, mobile без overflow. Audit 20/20, `available`. Лекции по структурам данных нет - программный обзор, без `lecture-linked`. |

Итог: **25 миссий, все `available`**.

## Review 2026-06-09 (Phase C): Eulerian trails (lecture-linked)

| Mission | Evidence |
| --- | --- |
| `Эйлеров путь` | Раздел `combinatorics`, механика `state-machine`, **lecture-linked** на `4. Graphs`. 3 уровня: bowtie (эйлеров цикл, все чётные), house (путь, 2 нечётные), конверт (8 рёбер не отрывая руки). Кликаешь вершины, проходя каждое ребро по разу; нечётные вершины подсвечены как старты, пройденные рёбра зеленеют. Диагностика invalid (нет ребра) / stuck (тупик). Детерминированная модель, 8 unit-тестов с проверкой маршрутов, smoke happy + mistake, mobile без overflow. Audit 20/20, `available`. |

Итог: **24 миссии, все `available`**.

## Review 2026-06-09 (Phase C): eigenvectors (lecture-linked)

| Mission | Evidence |
| --- | --- |
| `Собственные векторы` | Раздел `algebra`, механика `geometry-lab`, **lecture-linked** на `12_Eigenvectors_eigenvalues`. 3 уровня: λ=3 вдоль (1,1), λ=1 вдоль (1,-1), λ=-1 (переворот). Вращаешь v (drag + угловой input fallback), видишь A·v; собственный вектор - где A·v параллелен v. Диагностика not-aligned / wrong-eigenvalue. 8 unit-тестов, smoke happy + mistake, mobile без overflow. Audit 20/20, `available`. |

Итог: **23 миссии, все `available`**.

## Review 2026-06-08 (Phase C): dynamic programming (edit distance)

| Mission | Evidence |
| --- | --- |
| `DP-станция` | Раздел `algorithms`, механика `code-trace` (третья). 3 уровня: COT/CAT (3×3), CAT/CART (3×4, вставка), FOOD/GOLD (4×4, расстояние 2). Заполняешь таблицу Левенштейна, кликая «готовые» клетки (зависят от left/top/diagonal) — порядок вычислений как инвариант (как ready-pivot в Гауссе); клик не готовой клетки = «рано считать». Ответ в правом нижнем углу. 7 unit-тестов, smoke happy + mistake, mobile без overflow. Audit 20/20, chunk 7.5 kB, `available`. Лекции по алгоритмам нет → программный обзор, без `lecture-linked`. |

Итог: **22 миссии, все `available`**.

## Review 2026-06-08 (Phase C): disjoint-set union (structure-builder)

| Mission | Evidence |
| --- | --- |
| `Лес связности` | Раздел `algorithms`, механика `structure-builder` (вторая). 3 уровня: связать всё, остов без циклов, оставить две группы (не брать мост). Кликаешь рёбра — union объединяет компоненты, ребро внутри компоненты подсвечивается красным как цикл; раскраска вершин по компонентам. Детерминированная DSU-модель (find/union/components). 7 unit-тестов, smoke happy + mistake (force-click по SVG-рёбрам). Audit 20/20, chunk 6.7 kB, `available`. Лекции по структурам данных пока нет — `lesson.md` на программный обзор, без `lecture-linked`. |

Итог: **21 миссия, все `available`**; теперь каждое из 6 механических семейств (geometry-lab, model-arena, code-trace, sampler, state-machine, structure-builder) покрыто не менее чем двумя миссиями.

## Review 2026-06-08 (Phase C): Gaussian elimination (state-machine, lecture-linked)

| Mission | Evidence |
| --- | --- |
| `Гаусс-станция` | Раздел `algebra`, механика `state-machine` (вторая), **lecture-linked** на `3_Linear_equations`. 3 уровня: прямой ход, нулевая опора (нужен обмен строк), дробные опоры. Кликаешь подсвеченные элементы под диагональю — они зануляются опорной строкой; «ready pivot»-правило держит порядок Гаусса и исключает зацикливание. Решение читается обратным ходом. 6 unit-тестов, smoke happy + mistake, mobile без overflow. Audit 20/20, chunk 7.7 kB, `available`. |

Итог: **20 миссий, все `available`**; механика `state-machine` теперь покрыта двумя миссиями.

## Review 2026-06-08 (Phase C): geometric probability (lecture-linked)

| Mission | Evidence |
| --- | --- |
| `Монте-Карло` | Раздел `probability`, механика `sampler` (вторая), **lecture-linked** на `1_Probability_basics`. 3 уровня: оценка π через четверть круга, площадь треугольника (y<x), площадь под параболой (y<x²). Детерминированный seeded PRNG, scatter точек (внутри/снаружи), доля попаданий = оценка площади. Диагностика too-few-samples / estimate-off. 7 unit-тестов, smoke happy + mistake, mobile без overflow. Audit 20/20, chunk 6.9 kB, `available`. |

Итог: **19 миссий, все `available`**.

## Review 2026-06-08 (Phase C): Fourier synthesis (lecture-linked)

| Mission | Evidence |
| --- | --- |
| `Фурье-синтезатор` | Раздел `calculus`, механика `geometry-lab`, **lecture-linked** на `11_series_fourier`. 3 уровня: две гармоники, прямоугольник (нечётные с 1/k), пила (знакочередование). Двигаешь амплитуды 5 гармоник, синяя кривая ложится на целевую; energy = L2-расстояние спектров (точное по ортогональности). Виден феномен Гиббса на прямоугольнике. Диагностика worst-harmonic. 6 unit-тестов, smoke happy + mistake (range через native setter), mobile без overflow. Audit 20/20, chunk 6.2 kB, `available`. |

Итог: **18 миссий, все `available`**.

## Review 2026-06-08 (Phase C): roots of unity (lecture-linked)

| Mission | Evidence |
| --- | --- |
| `Орбита корней` | Раздел `algebra`, механика `geometry-lab`, **lecture-linked** на `SHAD/algebra/2_Complex numbers`. 3 уровня: треугольник (n=3), квадрат (n=4, z=i), пятиугольник (n=5). Перетаскиваешь комплексное z, его степени z⁰…zⁿ⁻¹ образуют правильный n-угольник; цель — первообразный корень e^(2πi/n), z^n=1. Диагностика modulus-off (спираль) / angle-off (не замыкается) / not-primitive (вырожденный многоугольник, напр. z=-1 для квадрата). 6 unit-тестов, smoke happy + mistake, mobile без overflow. Audit 20/20, chunk 8.6 kB, `available`. |

Итог: **17 миссий, все `available`**.

## Review 2026-06-08 (Phase C): first StructureBuilder mission

| Mission | Evidence |
| --- | --- |
| `Куча-кузница` | Раздел `algorithms`, механика `structure-builder` (первая реализация). 3 уровня: починить ребро, просеять вставку вверх, просеять корень вниз. Двоичная min-heap как дерево, красные рёбра = нарушения parent > child, обмен двух узлов. Детерминированная модель, sift-down требует именно меньшего ребёнка. 6 unit-тестов, smoke happy + mistake, mobile без overflow. Audit 20/20, chunk 5.9 kB, статус `available`. Лекции по структурам данных в SHAD пока нет — `lesson.md` указывает на программный обзор, тег `lecture-linked` не выставлен. |

Итог: **16 миссий, все `available`**; механика `structure-builder` перестала
быть пустой. Реализованы 3 из 6 механических семейств в этом проходе
(`sampler`, `geometry-lab`/анализ, `structure-builder`).

## Review 2026-06-08 (Phase C): first calculus mission

| Mission | Evidence |
| --- | --- |
| `Градиентный склон` | Новый раздел `calculus`, механика `geometry-lab`. 3 уровня: скатиться в минимум, укротить шаг (взрыв при большом lr), узкая долина (плохая обусловленность). Детерминированная модель f=ax²+by², траектория спуска по контурам уровня, режимы too-slow / oscillating / exploded. 9 unit-тестов, smoke happy + mistake, mobile без overflow, lecture link. Audit 20/20, chunk 7.3 kB, статус `available`. |

Также сквозная задача **KaTeX split**: `VizPage` сделан lazy, initial JS
642 → 377 kB (90% → 54% бюджета); KaTeX вынесен в lazy `VizPage`-chunk.

Итог: **15 миссий, все `available`**; реализованы механики `sampler` и
`geometry-lab` в новых доменах (вероятность, анализ).

## Review 2026-06-08 (Phase B): first Sampler mission

| Mission | Evidence |
| --- | --- |
| `Бернулли-лаборатория` | Новый раздел `probability`, механика `sampler`. 3 уровня: поймать 1/2, оценить смещённую монету, сузить коридор (ЗБЧ). Детерминированный seeded PRNG (mulberry32) — выборка честная и воспроизводимая. Линия сходимости частоты + tally + result/repair-маркеры. 10 unit-тестов, smoke happy + mistake, mobile без overflow, lecture link. Audit 20/20, chunk 9.4 kB. Статус сразу `available`. |

Итог: **14 миссий, все `available`**; `Sampler` перестал быть пустым
механическим семейством.

## Review 2026-06-08 (batch 3): Phase A complete

Все оставшиеся прототипы доведены до `available` — **13 из 13**.

### Promoted to `available`

| Mission | Evidence |
| --- | --- |
| `Квадратичная линза` | `ResultMoment` (главные оси) + `RepairMarker` по диагнозу (`не эллипс`, `оси одного знака`, `не та сигнатура`…). Smoke на result/repair. |
| `SVD-линза` | `ResultMoment` + `RepairMarker`; `eigenvalue-trap` теперь явный field-маркер `это λ, не σ` (закрывает wrong-space замечание). Mobile density проверена (панели стекаются, без overflow). |
| `PCA-компрессор` | `ResultMoment` + `RepairMarker` + `next`-бейдж на component rail (первая невыбранная компонента). Hotspot из batch 1. |
| `Унитарный компас` | `ResultMoment` + `RepairMarker` (ошибочный объект помечен прямо: `не эрмитова`, `не унитарна`, `i² ловушка`…). Mobile density проверена. |

### A4: recommendation + mobile

- `recommendedMissionId` теперь учитывает prerequisites: рекомендует первую
  незавершённую миссию с выполненными предусловиями, затем любую незавершённую,
  затем **завершённый** review-кандидат. Покрыто unit-тестом.
- `KernelHunt` mobile: 3D-сцена ужата (`MissionShell` floor `min-h` стал
  адаптивным `min-h-[300px] sm:min-h-[430px]`, scene `h-[300px]`), residual-board
  и sliders поднялись на ~130px (diagnosis 996→866). Прочие миссии не затронуты
  (их сцены выше floor). Full smoke без horizontal overflow.

### Status

`available` миссий — **13 из 13**. Все имеют diagnosis, field-level markers
(repair/result/hotspot), mistake-path smoke, desktop/mobile скриншоты.

## Review 2026-06-08 (batch 2)

### Promoted to `available`

| Mission | Status | Evidence |
| --- | --- | --- |
| `Матрица как машина` | `available` | Добавлены два challenge-уровня (`parallelogram`, `rotate-stretch`): оба столбца off-axis, per-column подсказки и числовая цель скрыты, цель - образ единичного квадрата. Убирает one-click. Unit tests, happy-path smoke на challenge, desktop/mobile скриншоты. |
| `Евклидова мастерская` | `available` | Field-level failure marker (`RepairMarker`) на поле: `DOT ≠ 0`, `norm ≠ 1`, `QᵀQ ≠ I`, `det = -1`, зависимость/ноль; `FieldPulse` + `ResultMoment` на успех. Smoke проверяет repair-marker и result-moment. |
| `Цех перестановок` | `available` | Уже были per-tile danger/success разметка и `MascotOverlay` (pivot); добавлены `ResultMoment` на успех и `RepairMarker` (`не та цель` / `sign ≠ target` / `over budget`). Smoke проверяет оба. |
| `Арена асимптотик` | `available` | Добавлены `ResultMoment` (стратегия-победитель) и `RepairMarker` по виду диагноза (`setup зря`, `O(n^2) взрыв`, `нужен препроцесс`…). Smoke на repair/result. |
| `ML-полигон` | `available` | Добавлены `ResultMoment` (модель обобщает) и `RepairMarker` (`train ≫ test`, `утечка в модели` danger, `порог не тот`…). Smoke на repair/result. |

### Polish applied

- `PCA-компрессор`: добавлен residual hotspot marker (`pca-residual-hotspot`) - бейдж и danger-обводка на клетке с максимальным остатком. Раскрывает metric tradeoff: высокая общая energy не спасает от яркого локального артефакта. Smoke проверяет видимость на rank 0. Миссия остаётся `prototype` (нужен ещё проход по component rail flow перед промоушном).

### Closed from previous backlog

- [x] One-click risk `Матрица как машина` (challenge variants).
- [x] Field-level failure marker pass `Евклидова мастерская`.
- [x] Residual hotspot marker `PCA-компрессор`.

### Still Prototype after this pass

`PCA-компрессор`, `Унитарный компас`, `SVD-линза`, `Квадратичная линза` —
все доведены в batch 3 (см. выше). Итог batch 2: `available` 9 из 13.

## Review 2026-06-07

### Available Candidates Promoted

| Mission | Status | Evidence |
| --- | --- | --- |
| `Кузница определителя` | `available` | Pure model tests, happy/mistake smoke, determinant field pulse, orientation/collapse repair marker and result moment. |
| `Графовый диспетчер` | `available` | Queue/stack state is playable, mistake path now shows expected ghost vertex and repair marker, smoke covers marker. |
| `Фабрика признаков` | `available` | Data cleaning has alternative bad/good actions, pipeline diff, split check, dirty-column repair markers and smoke-covered repair. |

### Still Prototype

| Mission | Reason |
| --- | --- |
| `PCA-компрессор` | New mission; needs one extra pass on residual hotspot and component rail before promotion. |
| `Унитарный компас` | Dense complex geometry; needs mobile density and field-marker review. |
| `SVD-линза` | Strong geometry, but controls and PCA transfer should be reviewed after compression stage. |
| `Евклидова мастерская` | Good model coverage; needs a field-level failure marker pass. |
| `Матрица как машина` | Clear concept, but still has worksheet-like levels. |
| `Охота за ядром` | Strong visual scene, but residual failures need clearer 2D support. |

### One-Click Risks

- `Матрица как машина`: several levels can still be solved by setting one obvious column.
- `Охота за ядром`: coordinate entry can become direct answer entry without enough visible repair.
- `PCA-компрессор`: `fit budget` and `fix artifact` are useful smoke affordances, but final user flow should still expose metric tradeoff.

### Visible-Failure Gaps

- `Унитарный компас`: fake Hermitian and non-unitary states are diagnosed well, but the failed object could be marked more directly.
- `SVD-линза`: eigenvalue trap is clear in text; field could show wrong-space selection more explicitly.
- `Kernel Hunt`: failed row equation should be marked outside the 3D canvas.

### Screenshot Notes

- `PCA-компрессор`: mobile is readable; desktop component rail is acceptable after compact layout, but local residual hotspot marker remains P1.
- `Feature Factory`: intentionally dense/operational; markers should stay compact and not become decorative.
- `Graph Dispatcher`: graph field has enough room for repair marker without covering vertices.

### Next Polish Backlog

1. Add residual hotspot marker to `PCA-компрессор`.
2. Add row-equation residual board to `Охота за ядром`.
3. Add challenge variants to `Матрица как машина`.
4. Review mobile density for `Унитарный компас`, `SVD-линза` and
   `Евклидова мастерская`.
