from __future__ import annotations

import os
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

BASE_URL = os.environ.get("SHAD_INTERACTIVE_URL", "http://127.0.0.1:5173")
CHROMIUM = os.environ.get("PLAYWRIGHT_CHROMIUM", "/snap/bin/chromium")
OUT_DIR = Path(os.environ.get("SHAD_INTERACTIVE_SCREEN_DIR", "/tmp/shad-interactive-screens"))

ROUTES = [
    ("kernel", "#/algebra/linear-maps/kernel", "canvas"),
    ("determinant", "#/algebra/determinants/forge", 'svg[aria-label="Кузница определителя"]'),
]

VIEWPORTS = [
    ("desktop", {"width": 1440, "height": 960}),
    ("mobile", {"width": 390, "height": 844}),
]


def assert_no_horizontal_overflow(page, label: str) -> None:
    overflow = page.evaluate(
        "document.documentElement.scrollWidth > document.documentElement.clientWidth + 2"
    )
    if overflow:
        raise AssertionError(f"horizontal overflow on {label}")


def svg_point(box: dict[str, float], x: float, y: float) -> tuple[float, float]:
    return (box["x"] + ((x + 4) / 8) * box["width"], box["y"] + ((4 - y) / 8) * box["height"])


def run() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=CHROMIUM,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        for viewport_name, viewport in VIEWPORTS:
            page = browser.new_page(viewport=viewport)
            for route_name, route, selector in ROUTES:
                page.goto(f"{BASE_URL}/{route}", wait_until="domcontentloaded")
                page.wait_for_selector(selector, timeout=10_000)
                page.wait_for_timeout(1_500)
                expect(page.get_by_alt_text("Меби").first).to_be_visible(timeout=10_000)
                assert_no_horizontal_overflow(page, f"{viewport_name}:{route_name}")
                page.screenshot(
                    path=str(OUT_DIR / f"{route_name}-{viewport_name}.png"),
                    full_page=True,
                )
            page.close()

        page = browser.new_page(viewport={"width": 1440, "height": 960})
        page.goto(f"{BASE_URL}/#/algebra/linear-maps/kernel", wait_until="domcontentloaded")
        page.wait_for_selector("canvas", timeout=10_000)
        page.get_by_role("spinbutton").nth(0).fill("-1")
        page.get_by_role("spinbutton").nth(1).fill("1")
        page.get_by_role("spinbutton").nth(2).fill("-1")
        expect(page.get_by_text("Есть ненулевой вектор ядра")).to_be_visible(timeout=10_000)

        page.goto(f"{BASE_URL}/#/algebra/determinants/forge", wait_until="domcontentloaded")
        svg = page.wait_for_selector('svg[aria-label="Кузница определителя"]', timeout=10_000)
        expect(page.get_by_text("det A").first).to_be_visible(timeout=10_000)
        expect(page.get_by_text("1.00").first).to_be_visible(timeout=10_000)
        box = svg.bounding_box()
        if box is None:
            raise AssertionError("determinant SVG has no bounding box")
        start = svg_point(box, 1, 0)
        end = svg_point(box, 2, 0)
        page.mouse.move(*start)
        page.mouse.down()
        page.mouse.move(*end, steps=8)
        page.mouse.up()
        expect(page.get_by_text("Площадь поймана")).to_be_visible(timeout=10_000)
        browser.close()


if __name__ == "__main__":
    run()
