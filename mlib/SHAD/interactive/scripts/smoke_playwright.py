from __future__ import annotations

import argparse
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
    (
        "asymptotic",
        "#/algorithms/asymptotics/arena",
        '[data-testid="mission-asymptotic-arena"]',
    ),
    ("ml", "#/data/ml/playground", '[data-testid="mission-ml-playground"]'),
    ("feature-factory", "#/data/features/factory", '[data-testid="mission-feature-factory"]'),
]

VIEWPORTS = [
    ("desktop", {"width": 1440, "height": 960}),
    ("mobile", {"width": 390, "height": 844}),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke test SHAD interactive routes.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--screens-only", action="store_true", help="Only capture route screenshots.")
    mode.add_argument("--happy-paths-only", action="store_true", help="Only run happy paths.")
    return parser.parse_args()


def assert_no_horizontal_overflow(page, label: str) -> None:
    overflow = page.evaluate(
        "document.documentElement.scrollWidth > document.documentElement.clientWidth + 2"
    )
    if overflow:
        raise AssertionError(f"horizontal overflow on {label}")


def svg_point(box: dict[str, float], x: float, y: float) -> tuple[float, float]:
    return (box["x"] + ((x + 4) / 8) * box["width"], box["y"] + ((4 - y) / 8) * box["height"])


def drag_svg_handle(
    page,
    plane_test_id: str,
    x_from: float,
    y_from: float,
    x_to: float,
    y_to: float,
) -> None:
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


def fill_determinant(page, ux: str, uy: str, vx: str, vy: str) -> None:
    page.get_by_test_id("determinant-input-u-x").fill(ux)
    page.get_by_test_id("determinant-input-u-y").fill(uy)
    page.get_by_test_id("determinant-input-v-x").fill(vx)
    page.get_by_test_id("determinant-input-v-y").fill(vy)


def swap_tiles(page, a: int, b: int) -> None:
    page.get_by_test_id(f"substitution-tile-{a}").click()
    page.get_by_test_id(f"substitution-tile-{b}").click()


def click_graph_order(page, order: list[str]) -> None:
    for vertex in order:
        page.get_by_test_id(f"graph-vertex-{vertex}").click()


def choose_strategy(page, strategy_id: str) -> None:
    page.get_by_test_id(f"strategy-{strategy_id}").click()


def set_ml_threshold(page, threshold: str) -> None:
    page.get_by_test_id("ml-threshold-input").fill(threshold)


def choose_ml_feature(page, feature_id: str) -> None:
    page.get_by_test_id(f"ml-feature-{feature_id}").click()


def click_data_column_action(page, action_id: str, column_id: str) -> None:
    page.get_by_test_id(f"data-column-action-{action_id}-{column_id}").first.click()


def click_data_row_action(page, action_id: str, row_id: str) -> None:
    page.get_by_test_id(f"data-row-action-{action_id}-{row_id}").first.click()


def toggle_feature(page, feature_id: str) -> None:
    page.get_by_test_id(f"feature-toggle-{feature_id}").click()


def encode_feature(page, feature_id: str) -> None:
    page.get_by_test_id(f"feature-encode-{feature_id}").click()


def capture_route_screenshots(browser) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
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
            page.screenshot(path=str(OUT_DIR / f"{route_name}-{viewport_name}.png"), full_page=True)
        context.close()


def run_kernel_happy_path(page) -> None:
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


def run_kernel_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algebra/linear-maps/kernel", wait_until="domcontentloaded")
    page.wait_for_selector("canvas", timeout=10_000)
    fill_kernel(page, "0", "0", "0")
    expect(page.get_by_test_id("kernel-diagnosis")).to_contain_text(
        "Нулевой вектор зануляет Ax", timeout=10_000
    )
    expect(page.get_by_test_id("mascot-coach")).to_have_attribute("data-state", "warning")
    fill_kernel(page, "1", "-1", "0")
    expect(page.get_by_test_id("kernel-diagnosis")).to_contain_text(
        "x - z ≠ 0", timeout=10_000
    )


def run_determinant_happy_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algebra/determinants/forge", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="determinant-forge-plane"]', timeout=10_000)
    expect(page.get_by_text("det A").first).to_be_visible(timeout=10_000)
    expect(page.get_by_text("1.00").first).to_be_visible(timeout=10_000)
    fill_determinant(page, "2", "0", "0", "1")
    expect(page.get_by_text("Площадь поймана")).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-flip-orientation").click()
    fill_determinant(page, "2", "0", "0", "-1")
    expect(page.get_by_text("Ориентация изменилась")).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-break-invertibility").click()
    fill_determinant(page, "1", "0", "2", "0")
    expect(page.get_by_text("Матрица вырождена")).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-repair-matrix").click()
    fill_determinant(page, "1", "0", "0", "1")
    expect(page.get_by_text("Матрица снова обратима: площадь вернулась.")).to_be_visible(
        timeout=10_000
    )


def run_determinant_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algebra/determinants/forge", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="determinant-forge-plane"]', timeout=10_000)
    fill_determinant(page, "1", "0", "0", "2")
    expect(page.get_by_text("Площадь поймана")).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-flip-orientation").click()
    fill_determinant(page, "1", "0", "0", "2")
    expect(page.get_by_test_id("determinant-diagnosis")).to_contain_text(
        "ориентация все еще положительная", timeout=10_000
    )
    expect(page.get_by_test_id("mascot-coach")).to_have_attribute("data-state", "warning")
    page.get_by_test_id("determinant-reset").click()
    expect(page.get_by_test_id("determinant-diagnosis")).to_contain_text(
        "Параллелограмм еще не настроен", timeout=10_000
    )


def run_matrix_happy_path(page) -> None:
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


def run_matrix_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algebra/matrices/machine", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="matrix-machine-plane"]', timeout=10_000)
    fill_matrix(page, "0", "1", "2", "0")
    expect(page.get_by_test_id("matrix-diagnosis")).to_contain_text(
        "Образы e1 и e2 перепутаны местами.", timeout=10_000
    )
    expect(page.get_by_test_id("mascot-coach")).to_have_attribute("data-state", "warning")
    page.get_by_test_id("matrix-reset").click()
    expect(page.get_by_test_id("matrix-diagnosis")).to_contain_text(
        "Матрица еще не настроена", timeout=10_000
    )


def run_substitution_happy_path(page) -> None:
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


def run_substitution_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algebra/substitutions/workshop", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-substitution-workshop"]', timeout=10_000)
    swap_tiles(page, 1, 2)
    expect(page.get_by_test_id("substitution-diagnosis")).to_contain_text(
        "Целевая циклическая структура нарушена", timeout=10_000
    )
    expect(page.get_by_test_id("mascot-coach")).to_have_attribute("data-state", "warning")
    page.get_by_test_id("substitution-reset").click()
    expect(page.get_by_test_id("substitution-diagnosis")).to_contain_text(
        "Состояние еще не нарушает явный запрет", timeout=10_000
    )


def run_graph_happy_path(page) -> None:
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
    expect(page.get_by_test_id("mission-reflection")).to_be_visible(timeout=10_000)


def run_graph_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/combinatorics/graphs/dispatcher", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-graph-dispatcher"]', timeout=10_000)
    page.get_by_test_id("graph-vertex-B").click()
    expect(page.get_by_test_id("mission-feedback")).to_contain_text(
        "Следующий допустимый ход: A", timeout=10_000
    )
    expect(page.get_by_test_id("mascot-coach")).to_have_attribute("data-state", "warning")
    page.get_by_test_id("graph-reset").click()
    expect(page.get_by_test_id("mission-feedback")).to_contain_text(
        "Следующий допустимый ход: A", timeout=10_000
    )


def run_asymptotic_happy_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algorithms/asymptotics/arena", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-asymptotic-arena"]', timeout=10_000)
    choose_strategy(page, "linear-scan")
    expect(page.get_by_text("Малый вход решен просто")).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-large-input").click()
    choose_strategy(page, "merge-sort")
    expect(page.get_by_text("Большой вход пережил рост")).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-nearly-sorted").click()
    choose_strategy(page, "insertion-sort")
    expect(page.get_by_text("Структура входа использована")).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-many-lookups").click()
    choose_strategy(page, "hash-index")
    expect(page.get_by_text("Preprocessing окупился")).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("mission-reflection")).to_be_visible(timeout=10_000)


def run_asymptotic_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algorithms/asymptotics/arena", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-asymptotic-arena"]', timeout=10_000)
    expect(page.get_by_test_id("mission-feedback")).to_contain_text(
        "setup-not-worth-it", timeout=10_000
    )
    choose_strategy(page, "linear-scan")
    expect(page.get_by_text("Малый вход решен просто")).to_be_visible(timeout=10_000)


def run_ml_playground_happy_path(page) -> None:
    page.goto(f"{BASE_URL}/#/data/ml/playground", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-ml-playground"]', timeout=10_000)
    set_ml_threshold(page, "50")
    expect(page.get_by_text("Train-порог пойман").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-test-control").click()
    set_ml_threshold(page, "58")
    expect(page.get_by_text("Test-контроль пройден").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-f1-threshold").click()
    set_ml_threshold(page, "59")
    expect(page.get_by_text("F1 сбалансирован").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-leakage-trap").click()
    choose_ml_feature(page, "signal")
    set_ml_threshold(page, "58")
    expect(page.get_by_text("Утечка отключена").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("mission-reflection")).to_be_visible(timeout=10_000)


def run_ml_playground_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/data/ml/playground", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-ml-playground"]', timeout=10_000)
    set_ml_threshold(page, "50")
    expect(page.get_by_text("Train-порог пойман").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-test-control").click()
    expect(page.get_by_test_id("mission-feedback")).to_contain_text(
        "train-test-gap", timeout=10_000
    )
    set_ml_threshold(page, "58")
    expect(page.get_by_text("Test-контроль пройден").first).to_be_visible(timeout=10_000)


def run_feature_factory_happy_path(page) -> None:
    page.goto(f"{BASE_URL}/#/data/features/factory", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-feature-factory"]', timeout=10_000)
    click_data_column_action(page, "impute-median", "temperature")
    expect(page.get_by_text("Пропуски залатаны").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-outlier-repair").click()
    click_data_row_action(page, "drop-row", "ff-07")
    expect(page.get_by_text("Выброс удален").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-leakage-off").click()
    toggle_feature(page, "leakage_code")
    expect(page.get_by_text("Leakage отключен").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-encode-category").click()
    encode_feature(page, "segment")
    expect(page.get_by_text("Категория закодирована").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("mission-reflection")).to_be_visible(timeout=10_000)


def run_feature_factory_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/data/features/factory", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-feature-factory"]', timeout=10_000)
    expect(page.get_by_test_id("feature-factory-diagnosis")).to_contain_text(
        "остались NA", timeout=10_000
    )
    expect(page.get_by_test_id("mascot-coach")).to_have_attribute("data-state", "warning")
    click_data_column_action(page, "impute-median", "signal")
    expect(page.get_by_test_id("pipeline-strip")).to_contain_text("median impute signal")
    click_data_column_action(page, "impute-median", "temperature")
    expect(page.get_by_text("Пропуски залатаны").first).to_be_visible(timeout=10_000)


def run_happy_paths(browser) -> None:
    context = browser.new_context(viewport={"width": 1440, "height": 960})
    context.add_init_script("window.localStorage.clear()")
    page = context.new_page()
    run_substitution_mistake_path(page)
    run_matrix_mistake_path(page)
    run_determinant_mistake_path(page)
    run_kernel_mistake_path(page)
    run_graph_mistake_path(page)
    run_asymptotic_mistake_path(page)
    run_ml_playground_mistake_path(page)
    run_feature_factory_mistake_path(page)
    run_kernel_happy_path(page)
    run_determinant_happy_path(page)
    run_matrix_happy_path(page)
    run_substitution_happy_path(page)
    run_graph_happy_path(page)
    run_asymptotic_happy_path(page)
    run_ml_playground_happy_path(page)
    run_feature_factory_happy_path(page)
    context.close()


def run() -> None:
    args = parse_args()
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=CHROMIUM,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        if not args.happy_paths_only:
            capture_route_screenshots(browser)
        if not args.screens_only:
            run_happy_paths(browser)
        browser.close()


if __name__ == "__main__":
    run()
