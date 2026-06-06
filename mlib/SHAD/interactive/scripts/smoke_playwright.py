from __future__ import annotations

import os
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

BASE_URL = os.environ.get("SHAD_INTERACTIVE_URL", "http://127.0.0.1:5173")
CHROMIUM = os.environ.get("PLAYWRIGHT_CHROMIUM", "/snap/bin/chromium")
OUT_DIR = Path(os.environ.get("SHAD_INTERACTIVE_SCREEN_DIR", "/tmp/shad-interactive-screens"))

ROUTES = [
    ("map", "#/map", '[data-testid="course-map"]'),
    ("kernel", "#/algebra/linear-maps/kernel", '[data-testid="mission-kernel-hunt"]'),
    ("determinant", "#/algebra/determinants/forge", '[data-testid="mission-determinant-forge"]'),
    ("matrix", "#/algebra/matrices/machine", '[data-testid="mission-matrix-machine"]'),
    (
        "substitution",
        "#/algebra/substitutions/workshop",
        '[data-testid="mission-substitution-workshop"]',
    ),
    ("graph", "#/combinatorics/graphs/dispatcher", '[data-testid="mission-graph-dispatcher"]'),
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


def fill_matrix(page, ux: str, uy: str, vx: str, vy: str) -> None:
    page.get_by_test_id("matrix-input-u-x").fill(ux)
    page.get_by_test_id("matrix-input-u-y").fill(uy)
    page.get_by_test_id("matrix-input-v-x").fill(vx)
    page.get_by_test_id("matrix-input-v-y").fill(vy)


def swap_tiles(page, a: int, b: int) -> None:
    page.get_by_test_id(f"substitution-tile-{a}").click()
    page.get_by_test_id(f"substitution-tile-{b}").click()


def click_graph_order(page, order: list[str]) -> None:
    for vertex in order:
        page.get_by_test_id(f"graph-vertex-{vertex}").click()


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
        expect(page.get_by_text("Матрица снова обратима: площадь вернулась.")).to_be_visible(
            timeout=10_000
        )

        page.goto(f"{BASE_URL}/#/algebra/matrices/machine", wait_until="domcontentloaded")
        page.wait_for_selector('[data-testid="matrix-machine-plane"]', timeout=10_000)
        fill_matrix(page, "2", "0", "0", "1")
        expect(page.get_by_text("Первый столбец растянулся")).to_be_visible(timeout=10_000)
        page.get_by_test_id("level-shear-y").click()
        fill_matrix(page, "1", "0", "1", "1")
        expect(page.get_by_text("Сдвиг собран")).to_be_visible(timeout=10_000)
        page.get_by_test_id("level-flip-x").click()
        fill_matrix(page, "-1", "0", "0", "1")
        expect(page.get_by_text("Ось x перевернулась")).to_be_visible(timeout=10_000)
        page.get_by_test_id("level-quarter-turn").click()
        fill_matrix(page, "0", "1", "-1", "0")
        expect(
            page.get_by_text("Матрица поворота собрана из двух образов базисных векторов.")
        ).to_be_visible(timeout=10_000)

        page.goto(f"{BASE_URL}/#/algebra/substitutions/workshop", wait_until="domcontentloaded")
        page.wait_for_selector('[data-testid="mission-substitution-workshop"]', timeout=10_000)
        swap_tiles(page, 1, 5)
        swap_tiles(page, 1, 4)
        swap_tiles(page, 1, 3)
        swap_tiles(page, 1, 2)
        expect(page.get_by_text("Цикл собран")).to_be_visible(timeout=10_000)
        page.get_by_test_id("level-flip-parity").click()
        swap_tiles(page, 1, 2)
        expect(page.get_by_text("Знак сменился")).to_be_visible(timeout=10_000)
        page.get_by_test_id("level-two-cycles").click()
        swap_tiles(page, 1, 2)
        swap_tiles(page, 3, 4)
        swap_tiles(page, 5, 6)
        expect(page.get_by_text("Три независимых обмена")).to_be_visible(timeout=10_000)
        page.get_by_test_id("level-repair").click()
        swap_tiles(page, 2, 3)
        swap_tiles(page, 3, 5)
        expect(page.get_by_text("Маршрут восстановлен")).to_be_visible(timeout=10_000)

        page.goto(f"{BASE_URL}/#/combinatorics/graphs/dispatcher", wait_until="domcontentloaded")
        page.wait_for_selector('[data-testid="mission-graph-dispatcher"]', timeout=10_000)
        click_graph_order(page, ["A", "B", "C", "D", "E", "F", "G"])
        expect(page.get_by_text("BFS прошел по слоям")).to_be_visible(timeout=10_000)
        page.get_by_test_id("level-dfs-stack").click()
        click_graph_order(page, ["A", "B", "D", "F", "E", "G", "C"])
        expect(page.get_by_text("DFS ушел в глубину")).to_be_visible(timeout=10_000)
        page.get_by_test_id("level-connected-component").click()
        click_graph_order(page, ["A", "B", "C", "D", "E", "F", "G"])
        expect(page.get_by_text("Компонента найдена")).to_be_visible(timeout=10_000)
        page.get_by_test_id("level-repair-trace").click()
        click_graph_order(page, ["B", "C", "D", "E", "F", "G"])
        expect(page.get_by_text("Trace восстановлен")).to_be_visible(timeout=10_000)

        context.close()
        browser.close()


if __name__ == "__main__":
    run()
