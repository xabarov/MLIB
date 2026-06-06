from __future__ import annotations

import os
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

BASE_URL = os.environ.get("SHAD_INTERACTIVE_URL", "http://127.0.0.1:5173")
CHROMIUM = os.environ.get("PLAYWRIGHT_CHROMIUM", "/snap/bin/chromium")
OUT_DIR = Path(os.environ.get("SHAD_INTERACTIVE_SCREEN_DIR", "/tmp/shad-interactive-screens"))

ROUTES = [
    ("kernel", "#/algebra/linear-maps/kernel", '[data-testid="mission-kernel-hunt"]'),
    ("determinant", "#/algebra/determinants/forge", '[data-testid="mission-determinant-forge"]'),
    ("matrix", "#/algebra/matrices/machine", '[data-testid="mission-matrix-machine"]'),
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


def drag_svg_handle(page, plane_test_id: str, x_from: float, y_from: float, x_to: float, y_to: float) -> None:
    plane = page.get_by_test_id(plane_test_id)
    box = plane.bounding_box()
    if box is None:
        raise AssertionError(f"{plane_test_id} has no bounding box")
    start = svg_point(box, x_from, y_from)
    end = svg_point(box, x_to, y_to)
    page.mouse.move(*start)
    page.mouse.down()
    page.mouse.move(*end, steps=10)
    page.mouse.up()


def fill_kernel(page, x: str, y: str, z: str) -> None:
    page.get_by_test_id("kernel-input-x").fill(x)
    page.get_by_test_id("kernel-input-y").fill(y)
    page.get_by_test_id("kernel-input-z").fill(z)


def run() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=CHROMIUM,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        for viewport_name, viewport in VIEWPORTS:
            context = browser.new_context(viewport=viewport)
            context.add_init_script("window.localStorage.clear()")
            page = context.new_page()
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
            context.close()

        context = browser.new_context(viewport={"width": 1440, "height": 960})
        context.add_init_script("window.localStorage.clear()")
        page = context.new_page()
        page.goto(f"{BASE_URL}/#/algebra/linear-maps/kernel", wait_until="domcontentloaded")
        page.wait_for_selector("canvas", timeout=10_000)
        fill_kernel(page, "-1", "1", "-1")
        expect(page.get_by_text("Есть ненулевой вектор ядра")).to_be_visible(timeout=10_000)
        page.get_by_test_id("level-solution-line").click()
        fill_kernel(page, "-2", "2", "-2")
        expect(page.get_by_text("Решения тянутся вдоль одной прямой")).to_be_visible(timeout=10_000)
        page.get_by_test_id("level-kernel-basis").click()
        fill_kernel(page, "-1", "1", "-1")
        expect(page.get_by_text("Одного направления достаточно")).to_be_visible(timeout=10_000)
        page.get_by_test_id("level-rank-nullity").click()
        expect(page.get_by_text("Ранг 2 и дефект 1")).to_be_visible(timeout=10_000)

        page.goto(f"{BASE_URL}/#/algebra/determinants/forge", wait_until="domcontentloaded")
        page.wait_for_selector('[data-testid="determinant-forge-plane"]', timeout=10_000)
        expect(page.get_by_text("det A").first).to_be_visible(timeout=10_000)
        expect(page.get_by_text("1.00").first).to_be_visible(timeout=10_000)
        drag_svg_handle(page, "determinant-forge-plane", 1, 0, 2, 0)
        expect(page.get_by_text("Площадь поймана")).to_be_visible(timeout=10_000)
        page.get_by_test_id("level-flip-orientation").click()
        drag_svg_handle(page, "determinant-forge-plane", 0, 1, 0, -2)
        expect(page.get_by_text("Ориентация изменилась")).to_be_visible(timeout=10_000)
        page.get_by_test_id("level-break-invertibility").click()
        drag_svg_handle(page, "determinant-forge-plane", 0, -2, 2, 0)
        expect(page.get_by_text("Матрица вырождена")).to_be_visible(timeout=10_000)
        page.get_by_test_id("level-repair-matrix").click()
        drag_svg_handle(page, "determinant-forge-plane", 2, 0, 0, 1)
        expect(page.get_by_text("Матрица снова обратима")).to_be_visible(timeout=10_000)

        page.goto(f"{BASE_URL}/#/algebra/matrices/machine", wait_until="domcontentloaded")
        page.wait_for_selector('[data-testid="matrix-machine-plane"]', timeout=10_000)
        drag_svg_handle(page, "matrix-machine-plane", 1, 0, 2, 0)
        expect(page.get_by_text("Первый столбец растянулся")).to_be_visible(timeout=10_000)
        page.get_by_test_id("level-shear-y").click()
        drag_svg_handle(page, "matrix-machine-plane", 2, 0, 1, 0)
        drag_svg_handle(page, "matrix-machine-plane", 0, 1, 1, 1)
        expect(page.get_by_text("Сдвиг собран")).to_be_visible(timeout=10_000)
        page.get_by_test_id("level-flip-x").click()
        drag_svg_handle(page, "matrix-machine-plane", 1, 0, -1, 0)
        drag_svg_handle(page, "matrix-machine-plane", 1, 1, 0, 1)
        expect(page.get_by_text("Ось x перевернулась")).to_be_visible(timeout=10_000)
        page.get_by_test_id("level-quarter-turn").click()
        drag_svg_handle(page, "matrix-machine-plane", -1, 0, 0, 1)
        drag_svg_handle(page, "matrix-machine-plane", 0, 1, -1, 0)
        expect(page.get_by_text("Матрица поворота собрана")).to_be_visible(timeout=10_000)

        context.close()
        browser.close()


if __name__ == "__main__":
    run()
