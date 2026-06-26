# SHAD Interactive: performance and assets budget

Этот документ фиксирует, что нужно контролировать при добавлении новых миссий,
персонажей и визуальных assets.

## Что контролируем

- initial JS chunk;
- lazy chunks миссий;
- CSS bundle;
- mascot/images size;
- количество новых PNG/WebP;
- build output после `npm run build`.

## Текущий baseline

После каждого существенного визуального этапа смотреть вывод:

```bash
make interactive-build
```

Сейчас приложение lazy-loads тяжелые сцены через `routeLoaders.ts`. Это нужно
сохранять: новая предметная миссия должна попадать в отдельный chunk, а не в
initial bundle без причины.

### Baseline 2026-06-07

Последний проверенный `make interactive-build` после этапа quality/game-feel
показывал:

- `index-*.js`: 584.49 kB raw / 177.45 kB gzip;
- `KernelHuntMission`: 926.97 kB raw / 248.32 kB gzip;
- `AsymptoticArenaMission`: 16.90 kB raw / 5.38 kB gzip;
- `FeatureFactoryMission`: 22.84 kB raw / 6.76 kB gzip;
- `SubstitutionWorkshopMission`: 11.82 kB raw / 4.42 kB gzip;
- `MlPlaygroundMission`: 16.45 kB raw / 5.68 kB gzip;
- 2D/SVG mission chunks: примерно 8.5-23 kB raw;
- активные WebP Меби из `src/assets/game/mascot/`: примерно 38-41 kB каждый;
- исходные PNG Меби из `src/assets/game/mascot/`: примерно 458-477 kB каждый;
- reference/trial PNG больше 1 MB лежат вне импортируемого `mascot/index.ts` и
  не должны попадать в bundle.

### Baseline 2026-06-08

`npm run build` после установки зависимостей (Node 25, npm 11) показал:

- `index-*.js` (initial): 631.28 kB raw / 188.31 kB gzip (на диске 616.5 kB);
- `KernelHuntMission`: 926.97 kB raw / 248.32 kB gzip — lazy chunk с Three.js;
- остальные mission chunks: 9-23 kB raw, все ниже light-лимита 80 kB;
- `index-*.css`: 92.20 kB raw / 18.53 kB gzip;
- активные WebP Меби: 38-41 kB каждый;
- `dist/` целиком: ~3.3 MB.

Наблюдения:

- initial JS вырос с 584 kB (2026-06-07) до 631 kB — это 88% от лимита 700 kB;
  следующий рост требует решения (вынести KaTeX/часть UI в lazy chunk).
- 30 исходных PNG Меби (~25 MB) остаются под git в `src/assets/game/`, но
  **не** импортируются runtime-кодом и в bundle не попадают. Это вес репозитория,
  не bundle; решение об их выносе/удалении принимается отдельно.

### KaTeX split 2026-06-08

`VizPage` теперь lazy (`src/routes.tsx`): маршруты миссий грузятся отдельным
chunk вместе с `VizPanel`, `MathBlock` и KaTeX. Карта курса (initial route) больше
не тянет KaTeX.

- `index-*.js` (initial): 642 kB -> **370 kB raw / 112 kB gzip** (90% -> 53%
  бюджета);
- новый `VizPage-*.js`: ~263 kB raw (KaTeX + mission shell), lazy, грузится при
  первом заходе в миссию;
- `KernelHuntMission`: без изменений, ~927 kB lazy (Three.js).

`scripts/check_bundle_budget.py` помечает `VizPage` и `KernelHuntMission` как
heavy-lazy exempt: они обязаны оставаться lazy, но не входят в light-лимит 80 kB.
Это вернуло запас для новых миссий без роста initial route.

### Typography 2026-06-09

Подключены self-hosted веб-шрифты (замена системного `Trebuchet MS`):

- Literata (display) и Golos Text (body), вариативные, cyrillic+latin;
- 4 файла woff2 (~22-86 kB, суммарно ~194 kB), `font-display: swap`,
  `unicode-range` по сабсетам;
- шрифты — отдельные ассеты, в initial JS не попадают; CSS вырос на ~7 kB
  за счёт `@font-face`.

Правило: новые веса/начертания добавлять только при явной типографической
необходимости; держать суммарный вес шрифтов под контролем.

### Mascot WebP pass 2026-06-07

Активные runtime imports переключены с PNG на WebP:

- `mebi-hint-gesture`: 460 KiB -> 40 KiB;
- `mebi-hint`: 477 KiB -> 38 KiB;
- `mebi-idle`: 475 KiB -> 37 KiB;
- `mebi-success`: 476 KiB -> 38 KiB;
- `mebi-thinking-focused`: 466 KiB -> 39 KiB;
- `mebi-thinking`: 475 KiB -> 37 KiB;
- `mebi-warning`: 458 KiB -> 38 KiB.

PNG остаются исходниками рядом с WebP, но `src/assets/game/mascot/index.ts`
импортирует WebP.

Action для следующего performance pass:

- проверить визуальное качество на светлом фоне и панелях;
- оставить PNG fallback только если WebP дает заметные артефакты;
- не импортировать reference/trial assets в runtime code.

## Бюджеты v1

- Initial JS: удерживать ниже 700 kB raw до появления реального backend/data
  слоя.
- Lazy mission chunk: целиться ниже 80 kB raw для 2D/SVG/trace миссий.
- Three.js mission chunk может быть больше, но должен оставаться lazy-loaded.
- PNG персонажа: новые варианты добавлять только при явной роли в UI.
- Для больших raster assets рассматривать WebP/AVIF рядом с PNG.
- Не добавлять декоративные изображения, если они не помогают действию.

## Mascot assets

Меби уже является важным элементом системы. Новые состояния добавлять только
если они покрывают новый тип feedback:

- success;
- hint;
- warning;
- thinking;
- idle.

Если появится анимация персонажа, сначала проверить:

- размер;
- reduced motion;
- lazy loading;
- fallback static frame.

## Когда split обязателен

Split/lazy loading обязателен, если:

- сцена использует Three.js;
- сцена содержит большой dataset;
- сцена содержит raster assets больше нескольких сотен kB;
- миссия не нужна на первом экране карты.

## Автоматическая проверка

`scripts/check_bundle_budget.py` парсит `dist/` после сборки и проверяет бюджеты
из раздела "Бюджеты v1":

```bash
make interactive-build   # сначала собрать
make bundle-budget       # затем проверить dist/
```

или одной командой со сборкой:

```bash
python scripts/check_bundle_budget.py
```

Скрипт:

- находит entry-chunk из `dist/index.html` и проверяет его против 700 kB;
- предупреждает, если initial JS перевалил за 85% лимита;
- проверяет, что лёгкие mission chunks ниже 80 kB;
- помечает Three.js-миссию (`KernelHuntMission`) как exempt, но требует, чтобы
  она оставалась lazy chunk, а не entry;
- проверяет CSS против 150 kB;
- возвращает ненулевой код при жёстком нарушении (готово для CI).

## Проверка

Перед завершением новой миссии:

```bash
make interactive-build
make bundle-budget
```

Посмотреть:

- не вырос ли `index-*.js` неожиданно;
- создался ли отдельный chunk миссии;
- не появились ли большие raster assets без причины;
- CSS не раздулся из-за одноразовых декоративных классов.
