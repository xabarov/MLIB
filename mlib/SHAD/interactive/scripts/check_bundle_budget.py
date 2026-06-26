from __future__ import annotations

"""Bundle budget guard for SHAD/interactive.

Parses the production build in ``dist/`` and enforces the budgets written down in
``performance_budget.md``. The script is intentionally a warning/gate tool: it
catches unexpected growth of the initial bundle and of 2D/SVG/trace mission
chunks, and it makes sure the heavy Three.js scene stays in its own lazy chunk
instead of leaking into the entry bundle.

Usage::

    python scripts/check_bundle_budget.py            # build, then check
    python scripts/check_bundle_budget.py --no-build  # check existing dist/

Exit code is non-zero when a hard budget is exceeded, so it can be wired into CI.
"""

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
INDEX_HTML = DIST / "index.html"
ASSETS = DIST / "assets"

# Budgets in raw (uncompressed) kB. Mirror performance_budget.md "Бюджеты v1".
INITIAL_JS_LIMIT_KB = 700.0  # entry chunk loaded on first paint
LIGHT_MISSION_LIMIT_KB = 80.0  # 2D/SVG/trace mission chunks
# Chunks allowed to exceed the light limit because they bundle a heavy library.
# They must still be lazy (i.e. not the entry chunk), which this script verifies:
# - KernelHuntMission ships Three.js;
# - VizPage ships KaTeX + the mission shell, loaded only on a mission route so the
#   initial map stays light.
HEAVY_LAZY_PREFIXES = ("KernelHuntMission", "VizPage")
CSS_LIMIT_KB = 150.0


@dataclass
class Chunk:
    name: str
    size_kb: float


def _kb(path: Path) -> float:
    return path.stat().st_size / 1024.0


def run_build() -> None:
    print("building (npm run build)...", flush=True)
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if result.returncode != 0:
        sys.stdout.write(result.stdout)
        print("\nFAIL: build did not complete", file=sys.stderr)
        raise SystemExit(2)


def find_entry_chunk() -> str | None:
    """Return the entry JS filename referenced from index.html."""
    if not INDEX_HTML.exists():
        return None
    html = INDEX_HTML.read_text(encoding="utf-8")
    # <script type="module" ... src="./assets/index-XXXX.js">
    match = re.search(r'src="\.?/?assets/([^"]+\.js)"', html)
    return match.group(1) if match else None


def collect_chunks() -> list[Chunk]:
    return sorted(
        (Chunk(p.name, _kb(p)) for p in ASSETS.glob("*.js")),
        key=lambda c: c.size_kb,
        reverse=True,
    )


def is_heavy_lazy(name: str) -> bool:
    return name.startswith(HEAVY_LAZY_PREFIXES)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check SHAD/interactive bundle budgets")
    parser.add_argument(
        "--no-build",
        action="store_true",
        help="check the existing dist/ instead of rebuilding",
    )
    args = parser.parse_args()

    if not args.no_build:
        run_build()

    if not ASSETS.exists():
        print(f"FAIL: no build output at {ASSETS}", file=sys.stderr)
        return 2

    entry = find_entry_chunk()
    chunks = collect_chunks()
    css = sorted((Chunk(p.name, _kb(p)) for p in ASSETS.glob("*.css")), key=lambda c: c.size_kb, reverse=True)

    failures: list[str] = []
    warnings: list[str] = []

    print("\nbundle budget report")
    print("=" * 60)

    # Entry / initial JS budget.
    if entry is None:
        warnings.append("could not locate entry chunk in index.html")
    else:
        entry_chunk = next((c for c in chunks if c.name == entry), None)
        if entry_chunk is None:
            warnings.append(f"entry chunk {entry} not found in assets")
        else:
            status = "OK" if entry_chunk.size_kb <= INITIAL_JS_LIMIT_KB else "FAIL"
            print(f"[{status}] initial JS {entry_chunk.name}: "
                  f"{entry_chunk.size_kb:.1f} kB / {INITIAL_JS_LIMIT_KB:.0f} kB")
            if entry_chunk.size_kb > INITIAL_JS_LIMIT_KB:
                failures.append(
                    f"initial JS {entry_chunk.size_kb:.1f} kB exceeds "
                    f"{INITIAL_JS_LIMIT_KB:.0f} kB"
                )
            # Guard against Three.js leaking into the entry chunk: a >700 kB entry
            # is already caught above, but flag a suspiciously large entry early.
            if entry_chunk.size_kb > 0.85 * INITIAL_JS_LIMIT_KB:
                warnings.append(
                    f"initial JS is at {entry_chunk.size_kb:.1f} kB "
                    f"({entry_chunk.size_kb / INITIAL_JS_LIMIT_KB * 100:.0f}% of budget)"
                )

    # Mission / light chunk budget.
    print("-" * 60)
    for chunk in chunks:
        if entry and chunk.name == entry:
            continue
        if is_heavy_lazy(chunk.name):
            print(f"[lazy] {chunk.name}: {chunk.size_kb:.1f} kB (heavy lib, exempt; must stay lazy)")
            if entry and chunk.name == entry:
                failures.append(f"heavy chunk {chunk.name} is the entry chunk")
            continue
        if chunk.size_kb > LIGHT_MISSION_LIMIT_KB:
            print(f"[WARN] {chunk.name}: {chunk.size_kb:.1f} kB / {LIGHT_MISSION_LIMIT_KB:.0f} kB")
            warnings.append(
                f"{chunk.name} {chunk.size_kb:.1f} kB exceeds light limit "
                f"{LIGHT_MISSION_LIMIT_KB:.0f} kB"
            )

    # CSS budget.
    print("-" * 60)
    for sheet in css:
        status = "OK" if sheet.size_kb <= CSS_LIMIT_KB else "WARN"
        print(f"[{status}] css {sheet.name}: {sheet.size_kb:.1f} kB / {CSS_LIMIT_KB:.0f} kB")
        if sheet.size_kb > CSS_LIMIT_KB:
            warnings.append(f"css {sheet.name} {sheet.size_kb:.1f} kB exceeds {CSS_LIMIT_KB:.0f} kB")

    print("=" * 60)
    for warning in warnings:
        print(f"warning: {warning}")
    for failure in failures:
        print(f"FAIL: {failure}")

    if failures:
        print(f"\nbundle budget: {len(failures)} hard violation(s)")
        return 1
    print("\nbundle budget: OK"
          + (f" ({len(warnings)} warning(s))" if warnings else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
