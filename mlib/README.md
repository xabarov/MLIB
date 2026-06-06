# MLIB / SHAD Working Notes

This repository is a local learning library. The most active area is `SHAD/`:
lecture notes, exam-style Q&A, generated visual assets, and the
`SHAD/interactive` React viewer.

## Local Environment

Use the repo-local Python environment when running helper scripts:

```bash
cd /home/roman/Documents/ML/MLIB/mlib
.venv/bin/python --version
```

The local `.venv/` is intentionally ignored by git. Python Playwright is
installed there for browser checks:

```bash
.venv/bin/python -m pip install playwright
```

On this machine, Playwright can use the system Chromium at `/snap/bin/chromium`;
there is no need to commit browser binaries.

Secrets live in `mlib/.env`, which is ignored. The lecture/image generators read
it automatically when present.

## SHAD Lecture Generation

Generate or inspect lecture drafts from the repo root:

```bash
.venv/bin/python generate_lecture.py "Название темы" --section algebra --dry-run
.venv/bin/python generate_lecture.py "Название темы" --section algebra --generate-qa
```

The main authoring rules are in
`SHAD/lecture_qa_authoring_guide.md`. Keep `lesson.md` and `qa.md` in the
topic directory, with reproducible visual scripts next to them when visuals are
added.

## SHAD Visual Assets

Preferred order for visual work:

1. Use `generate_visuals.py` with `matplotlib` / `imageio` for precise diagrams,
   graphs, and animations.
2. Use `generate_images.py` and `SHAD/lecture_visual_generation/` for editorial
   hero images or visual metaphors.
3. Use Codex skills when the task calls for it:
   `canvas-design` for polished static PNG/PDF art, `algorithmic-art` for
   p5.js/generative sketches, `frontend-design` for UI, and `webapp-testing` for
   browser verification.

Example:

```bash
.venv/bin/python generate_images.py \
  --dry-run \
  --jobs SHAD/lecture_visual_generation/lecture_images.example.json
```

## SHAD Interactive

The interactive app lives in `SHAD/interactive`.

```bash
cd SHAD/interactive
npm ci
npm run lint
npm run build
npm run dev -- --host 127.0.0.1
```

Open:

```text
http://127.0.0.1:5173/#/algebra/linear-maps/kernel
```

`node_modules/` and `dist/` are ignored. Commit source files and lockfiles, not
local build output.

For browser checks, use Playwright from the repo `.venv` together with the
system Chromium:

```bash
cd /home/roman/Documents/ML/MLIB/mlib
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
- `SHAD/interactive/node_modules/`
- `SHAD/interactive/dist/`

Before staging a large sync, run:

```bash
git status --short
git diff --check
git check-ignore -v .env .claude/settings.local.json SHAD/interactive/dist/index.html
```

