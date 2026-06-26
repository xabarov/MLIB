# SHAD Interactive: deploy and link policy

Этот документ фиксирует, как связывать лекции с interactive в локальной работе
и при статической публикации.

## Source links in lessons

В исходных `lesson.md` используем dev-friendly hash route:

```markdown
[Игровая миссия](../../interactive/#/section/topic/mission)
```

Пример:

```markdown
[Графовый диспетчер](../../interactive/#/combinatorics/graphs/dispatcher)
```

Почему так:

- ссылка читается в репозитории;
- route совпадает с Vite dev server;
- не нужно коммитить `dist/`, чтобы ссылка была понятна.

## Static build links

Для публикации статической сборки можно заменить ссылки на:

```markdown
../../interactive/dist/index.html#/section/topic/mission
```

Эта replacement policy должна быть автоматизирована отдельным publish step,
если публикация станет регулярной. Вручную массово менять исходные лекции не
нужно.

## HashRouter

Приложение использует `HashRouter`, поэтому static hosting не требует server
rewrite rules для внутренних route. Достаточно отдавать `index.html` и assets.

## Docker

- Dev: `make compose-dev`, Vite hot reload на `http://localhost:5173/#/map`.
- Prod: `make compose-prod`, nginx на `http://localhost:8080`.
- Проверка конфигурации:

```bash
docker compose -f SHAD/interactive/docker-compose.dev.yml config --quiet
docker compose -f SHAD/interactive/docker-compose.yml config --quiet
```

## CI/publish target

Минимальный CI для interactive:

```bash
make lint-python
make lint-js
make test-js
make interactive-build
```

Для preview/prod smoke:

```bash
SHAD_INTERACTIVE_URL=http://127.0.0.1:5173 .venv/bin/python SHAD/interactive/scripts/smoke_playwright.py
```

URL меняется на preview/prod host.

## Что делать с dist

По умолчанию `dist/` - build artifact, не источник правды. Коммитить `dist/`
стоит только если viewer/hosting действительно отдает файлы прямо из репо и
нет CI build step.

Если `dist/` коммитится, перед этим обязательно:

```bash
make interactive-build
SHAD_INTERACTIVE_URL=<preview-url> .venv/bin/python SHAD/interactive/scripts/smoke_playwright.py
```
