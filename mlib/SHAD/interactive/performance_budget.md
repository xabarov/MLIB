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

Последний проверенный `make interactive-build` показывал:

- `index-*.js`: около 550 kB raw / 170 kB gzip;
- `KernelHuntMission`: около 923 kB raw / 247 kB gzip;
- 2D/SVG mission chunks: примерно 5-10 kB raw;
- активные PNG Меби из `src/assets/game/mascot/`: примерно 469-489 kB каждый;
- reference/trial PNG больше 1 MB лежат вне импортируемого `mascot/index.ts` и
  не должны попадать в bundle.

Action для следующего performance pass:

- сконвертировать активные PNG Меби в WebP/AVIF-кандидаты;
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

## Проверка

Перед завершением новой миссии:

```bash
make interactive-build
```

Посмотреть:

- не вырос ли `index-*.js` неожиданно;
- создался ли отдельный chunk миссии;
- не появились ли большие raster assets без причины;
- CSS не раздулся из-за одноразовых декоративных классов.
