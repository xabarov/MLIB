# MLIB Working Notes

A local learning library organised into independent **tracks**, plus the tooling
that generates and renders them.

```
tracks/shad/            SHAD entrance-exam lectures (lesson.md + qa.md + assets/)
tracks/ml-interviews/   Q&A notes for huyenchip.com/ml-interviews-book
tracks/networks/        computer networking notes
apps/interactive/       React/Vite trainer built on the SHAD material
tools/                  generate_lecture.py, generate_images.py
shared/                 authoring guide and visual design system (all tracks)
essays/                 non-study writing (spiral essay, bootstrap template)
```

Each track has its own `README.md` describing its scope and format.
The most active area is `tracks/shad/`. All commands below run from the repo root.

## Local Environment

Use the repo-local Python environment when running helper scripts:

```bash
cd /home/roman/Documents/ML/MLIB
.venv/bin/python --version
```

The local `.venv/` is intentionally ignored by git. Python Playwright is
installed there for browser checks:

```bash
.venv/bin/python -m pip install playwright
```

On this machine, Playwright can use the system Chromium at `/snap/bin/chromium`;
there is no need to commit browser binaries.

Secrets live in `.env`, which is ignored. The lecture/image generators read
it automatically when present.

## Lecture Generation (`tracks/shad`)

Generate or inspect lecture drafts from the repo root:

```bash
.venv/bin/python tools/generate_lecture.py "Название темы" --section algebra --dry-run
.venv/bin/python tools/generate_lecture.py "Название темы" --section algebra --generate-qa
```

The main authoring rules are in
`shared/lecture_qa_authoring_guide.md`. Keep `lesson.md` and `qa.md` in the
topic directory, with reproducible visual scripts next to them when visuals are
added.

## Visual Assets

Preferred order for visual work:

1. Use `generate_visuals.py` with `matplotlib` / `imageio` for precise diagrams,
   graphs, and animations.
2. Use `tools/generate_images.py` and `shared/lecture_visual_generation/` for editorial
   hero images or visual metaphors.
3. Use Codex skills when the task calls for it:
   `canvas-design` for polished static PNG/PDF art, `algorithmic-art` for
   p5.js/generative sketches, `frontend-design` for UI, and `webapp-testing` for
   browser verification.

Example:

```bash
.venv/bin/python tools/generate_images.py \
  --dry-run \
  --jobs shared/lecture_visual_generation/lecture_images.example.json
```

## Interactive Trainer

The interactive app lives in `apps/interactive` and is self-contained.

```bash
cd apps/interactive
npm ci
npm run lint
npm run build
npm run dev -- --host 127.0.0.1
```

From the repo root, the same checks are available through `make`:

```bash
make setup-python
make lint-python
make lint-python-all
make lint-js
make interactive-build
make interactive-smoke
make interactive-dev
```

Docker workflows:

```bash
make compose-dev   # Vite dev server with source mounted into the container
make compose-prod  # production nginx container on http://localhost:8080
make compose-down
```

Open:

```text
http://127.0.0.1:5173/#/algebra/linear-maps/kernel
http://127.0.0.1:5173/#/algebra/determinants/forge
```

`node_modules/` and `dist/` are ignored. Commit source files and lockfiles, not
local build output.

For browser checks, use Playwright from the repo `.venv` together with the
system Chromium:

```bash
cd /home/roman/Documents/ML/MLIB
.venv/bin/python - <<'PY'
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        executable_path="/snap/bin/chromium",
        args=["--no-sandbox", "--disable-dev-shm-usage"],
    )
    page = browser.new_page(viewport={"width": 1440, "height": 960})
    page.goto("http://127.0.0.1:5173/#/algebra/linear-maps/kernel")
    page.wait_for_selector("canvas")
    print(page.title())
    browser.close()
PY
```

## Git Hygiene

Ignored local artifacts include:

- `.venv/`
- `.env`
- `.claude/`
- `_rsync_backups/`
- `_cleanup_backups/`
- `apps/interactive/node_modules/`
- `apps/interactive/dist/`
- `_generated/` (scratch output of `tools/generate_images.py`)

Before staging a large sync, run:

```bash
git status --short
git diff --check
git check-ignore -v .env .claude/settings.local.json apps/interactive/dist/index.html
```
