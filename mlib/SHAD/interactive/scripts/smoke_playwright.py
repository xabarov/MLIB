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
    ("quadratic-lens", "#/algebra/quadratic-forms/lens", '[data-testid="mission-quadratic-lens"]'),
    (
        "orthogonal-workshop",
        "#/algebra/euclidean/orthogonal-workshop",
        '[data-testid="mission-orthogonal-workshop"]',
    ),
    (
        "unitary-compass",
        "#/algebra/complex/unitary-compass",
        '[data-testid="mission-unitary-compass"]',
    ),
    ("svd-lens", "#/algebra/svd/lens", '[data-testid="mission-svd-lens"]'),
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


def fill_quadratic(page, a: str, b: str, c: str) -> None:
    page.get_by_test_id("coefficient-a").fill(a)
    page.get_by_test_id("coefficient-b").fill(b)
    page.get_by_test_id("coefficient-c").fill(c)


def set_quadratic_rotation(page, theta: str) -> None:
    page.get_by_test_id("basis-rotation").fill(theta)


def set_quadratic_direction(page, target: str, x: str, y: str) -> None:
    page.get_by_test_id(f"{target}-x").fill(x)
    page.get_by_test_id(f"{target}-y").fill(y)


def fill_svd_matrix(page, a: str, b: str, c: str, d: str) -> None:
    page.get_by_test_id("svd-matrix-a").fill(a)
    page.get_by_test_id("svd-matrix-b").fill(b)
    page.get_by_test_id("svd-matrix-c").fill(c)
    page.get_by_test_id("svd-matrix-d").fill(d)


def fill_orthogonal_matrix(page, a: str, b: str, c: str, d: str) -> None:
    page.get_by_test_id("orthogonal-matrix-a").fill(a)
    page.get_by_test_id("orthogonal-matrix-b").fill(b)
    page.get_by_test_id("orthogonal-matrix-c").fill(c)
    page.get_by_test_id("orthogonal-matrix-d").fill(d)


def fill_unitary_matrix(page, a_re: str, a_im: str, b_re: str, b_im: str) -> None:
    page.get_by_test_id("unitary-u-a-re").fill(a_re)
    page.get_by_test_id("unitary-u-a-im").fill(a_im)
    page.get_by_test_id("unitary-u-b-re").fill(b_re)
    page.get_by_test_id("unitary-u-b-im").fill(b_im)


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
    expect(page.get_by_text("Есть ненулевой вектор ядра").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-solution-line").click()
    fill_kernel(page, "-2", "2", "-2")
    expect(page.get_by_text("Решения тянутся вдоль одной прямой").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-kernel-basis").click()
    fill_kernel(page, "-1", "1", "-1")
    expect(page.get_by_text("Одного направления достаточно").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-rank-nullity").click()
    expect(page.get_by_text("Ранг 2 и дефект 1").first).to_be_visible(timeout=10_000)


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
    expect(page.get_by_text("Площадь поймана").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-flip-orientation").click()
    fill_determinant(page, "2", "0", "0", "-1")
    expect(page.get_by_text("Ориентация изменилась").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-break-invertibility").click()
    fill_determinant(page, "1", "0", "2", "0")
    expect(page.get_by_text("Матрица вырождена").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-repair-matrix").click()
    fill_determinant(page, "1", "0", "0", "1")
    expect(page.get_by_text("Матрица снова обратима: площадь вернулась.").first).to_be_visible(
        timeout=10_000
    )


def run_determinant_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algebra/determinants/forge", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="determinant-forge-plane"]', timeout=10_000)
    fill_determinant(page, "1", "0", "0", "2")
    expect(page.get_by_text("Площадь поймана").first).to_be_visible(timeout=10_000)
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
    expect(page.get_by_text("Первый столбец растянулся").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-shear-y").click()
    fill_matrix(page, "1", "0", "1", "1")
    expect(page.get_by_text("Сдвиг собран").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-flip-x").click()
    fill_matrix(page, "-1", "0", "0", "1")
    expect(page.get_by_text("Ось x перевернулась").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-quarter-turn").click()
    fill_matrix(page, "0", "1", "-1", "0")
    expect(
        page.get_by_text("Матрица поворота собрана из двух образов базисных векторов.").first
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


def run_quadratic_happy_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algebra/quadratic-forms/lens", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-quadratic-lens"]', timeout=10_000)
    expect(page.get_by_test_id("quadratic-lens-canvas")).to_be_visible(timeout=10_000)
    fill_quadratic(page, "2", "0.2", "1")
    expect(page.get_by_text("Эллипс закрыт").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-cross-term-rotation").click()
    page.get_by_text("snap axes").click()
    expect(page.get_by_text("Оси совпали с главными направлениями").first).to_be_visible(
        timeout=10_000
    )
    page.get_by_test_id("level-saddle-signature").click()
    set_quadratic_direction(page, "positive", "1", "0")
    set_quadratic_direction(page, "negative", "0", "1")
    expect(page.get_by_text("Седло поймано").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-degenerate-direction").click()
    fill_quadratic(page, "1", "0", "0")
    set_quadratic_direction(page, "null", "0", "1")
    expect(page.get_by_text("Ненулевое направление стало нулевой энергией").first).to_be_visible(
        timeout=10_000
    )
    page.get_by_test_id("level-signature-repair").click()
    fill_quadratic(page, "1", "0", "-1")
    expect(page.get_by_text("Сигнатура исправлена").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("mission-debrief")).to_be_visible(timeout=10_000)


def run_quadratic_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algebra/quadratic-forms/lens", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-quadratic-lens"]', timeout=10_000)
    fill_quadratic(page, "1", "0", "-1")
    expect(page.get_by_test_id("quadratic-diagnosis")).to_contain_text(
        "не положительная энергия", timeout=10_000
    )
    expect(page.get_by_test_id("mascot-coach")).to_have_attribute("data-state", "warning")
    fill_quadratic(page, "2", "0.2", "1")
    expect(page.get_by_text("Эллипс закрыт").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-cross-term-rotation").click()
    set_quadratic_rotation(page, "0.1")
    expect(page.get_by_test_id("quadratic-diagnosis")).to_contain_text(
        "смешанный член", timeout=10_000
    )


def run_svd_happy_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algebra/svd/lens", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-svd-lens"]', timeout=10_000)
    expect(page.get_by_test_id("svd-lens-canvas")).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("svd-output-ellipse")).to_be_visible(timeout=10_000)
    page.get_by_role("button", name="lens").click()
    expect(page.get_by_text("Круг прошел через линзу").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-right-directions").click()
    page.get_by_role("button", name="snap v").click()
    expect(page.get_by_text("Правые сингулярные направления найдены").first).to_be_visible(
        timeout=10_000
    )
    page.get_by_test_id("level-singular-vs-eigen").click()
    page.get_by_test_id("svd-choice-singular-values").click()
    expect(page.get_by_text("Ловушка пройдена").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-rank-one-shadow").click()
    page.get_by_test_id("svd-rank-toggle-sigma-2").click()
    expect(page.get_by_text("Слабая ось отброшена").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-pca-cloud").click()
    page.get_by_role("button", name="PCA axis").click()
    expect(page.get_by_text("Облако сжато").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("mission-debrief")).to_be_visible(timeout=10_000)


def run_svd_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algebra/svd/lens", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-svd-lens"]', timeout=10_000)
    fill_svd_matrix(page, "1", "0", "0", "1")
    expect(page.get_by_test_id("svd-diagnosis")).to_contain_text(
        "не в тот эллипс", timeout=10_000
    )
    expect(page.get_by_test_id("mascot-coach")).to_have_attribute("data-state", "warning")
    page.get_by_role("button", name="lens").click()
    expect(page.get_by_text("Круг прошел через линзу").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-right-directions").click()
    page.get_by_role("button", name="snap v").click()
    expect(page.get_by_text("Правые сингулярные направления найдены").first).to_be_visible(
        timeout=10_000
    )
    page.get_by_test_id("level-singular-vs-eigen").click()
    expect(page.get_by_test_id("svd-diagnosis")).to_contain_text(
        "собственные значения A", timeout=10_000
    )


def run_orthogonal_happy_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algebra/euclidean/orthogonal-workshop", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-orthogonal-workshop"]', timeout=10_000)
    expect(page.get_by_test_id("orthogonal-workshop-canvas")).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("orthogonal-residual")).to_be_visible(timeout=10_000)
    page.get_by_role("button", name="project").click()
    expect(page.get_by_text("Тень найдена").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-independent-is-not-orthogonal").click()
    page.get_by_role("button", name="orthogonalize").click()
    expect(page.get_by_text("Векторы ненулевые").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-normalize-without-turning").click()
    page.get_by_role("button", name="normalize").click()
    expect(page.get_by_text("Вектор нормирован").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-gram-schmidt-two").click()
    page.get_by_role("button", name="gram-schmidt").click()
    expect(page.get_by_text("Грам-Шмидт сработал").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-orthogonal-operator").click()
    page.get_by_role("button", name="snap Q").click()
    expect(page.get_by_text("Оператор ортогонален").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("mission-debrief")).to_be_visible(timeout=10_000)


def run_orthogonal_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algebra/euclidean/orthogonal-workshop", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-orthogonal-workshop"]', timeout=10_000)
    page.get_by_role("button", name="project").click()
    expect(page.get_by_text("Тень найдена").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-independent-is-not-orthogonal").click()
    page.get_by_test_id("orthogonal-vector-b-x").fill("1.1")
    expect(page.get_by_test_id("orthogonal-diagnosis")).to_contain_text("dot", timeout=10_000)
    expect(page.get_by_test_id("mascot-coach")).to_have_attribute("data-state", "warning")
    page.get_by_role("button", name="orthogonalize").click()
    expect(page.get_by_text("Векторы ненулевые").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-normalize-without-turning").click()
    page.get_by_role("button", name="normalize").click()
    expect(page.get_by_text("Вектор нормирован").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-gram-schmidt-two").click()
    page.get_by_role("button", name="gram-schmidt").click()
    expect(page.get_by_text("Грам-Шмидт сработал").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-orthogonal-operator").click()
    fill_orthogonal_matrix(page, "1", "1", "0", "1")
    expect(page.get_by_test_id("orthogonal-diagnosis")).to_contain_text(
        "не ортогональный оператор", timeout=10_000
    )


def run_unitary_happy_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algebra/complex/unitary-compass", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-unitary-compass"]', timeout=10_000)
    expect(page.get_by_test_id("unitary-compass-canvas")).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("complex-vector-plane")).to_be_visible(timeout=10_000)
    page.get_by_test_id("unitary-hermitian-choice").click()
    expect(page.get_by_text("Ловушка поймана").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-conjugate-slot").click()
    page.get_by_test_id("unitary-conjugate-second-choice").click()
    expect(page.get_by_text("Conjugate slot выбран").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-phase-preserve").click()
    page.get_by_test_id("unitary-phase-pi-half").click()
    expect(page.get_by_text("Фаза повернулась").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-fake-hermitian").click()
    page.get_by_test_id("unitary-make-hermitian").click()
    expect(page.get_by_text("Матрица стала Hermitian").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-unitary-motion").click()
    page.get_by_test_id("unitary-snap-u").click()
    expect(page.get_by_text("U*U = I").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-a-star-a-bridge").click()
    page.get_by_test_id("unitary-choice-astar-a").click()
    expect(page.get_by_text("A* A построена").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("mission-debrief")).to_be_visible(timeout=10_000)


def run_unitary_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algebra/complex/unitary-compass", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-unitary-compass"]', timeout=10_000)
    page.get_by_test_id("unitary-bilinear-choice").click()
    expect(page.get_by_test_id("unitary-diagnosis")).to_contain_text(
        "B(ix, ix)", timeout=10_000
    )
    expect(page.get_by_test_id("mascot-coach")).to_have_attribute("data-state", "warning")
    page.get_by_test_id("unitary-hermitian-choice").click()
    expect(page.get_by_text("Ловушка поймана").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-conjugate-slot").click()
    page.get_by_test_id("unitary-bilinear-choice").click()
    expect(page.get_by_test_id("unitary-diagnosis")).to_contain_text(
        "B(ix, ix)", timeout=10_000
    )
    page.get_by_test_id("unitary-conjugate-second-choice").click()
    expect(page.get_by_text("Conjugate slot выбран").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-phase-preserve").click()
    page.get_by_test_id("unitary-phase-pi-half").click()
    expect(page.get_by_text("Фаза повернулась").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-fake-hermitian").click()
    expect(page.get_by_test_id("unitary-diagnosis")).to_contain_text(
        "A != A*", timeout=10_000
    )
    page.get_by_test_id("unitary-make-hermitian").click()
    expect(page.get_by_text("Матрица стала Hermitian").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-unitary-motion").click()
    fill_unitary_matrix(page, "1", "0", "1", "0")
    expect(page.get_by_test_id("unitary-diagnosis")).to_contain_text(
        "не unitary", timeout=10_000
    )
    page.get_by_test_id("unitary-snap-u").click()
    expect(page.get_by_text("U*U = I").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-a-star-a-bridge").click()
    page.get_by_test_id("unitary-choice-ata").click()
    expect(page.get_by_test_id("unitary-diagnosis")).to_contain_text(
        "transpose без сопряжения", timeout=10_000
    )


def run_substitution_happy_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algebra/substitutions/workshop", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-substitution-workshop"]', timeout=10_000)
    expect(page.get_by_test_id("cycle-rail")).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("swap-budget-stars")).to_be_visible(timeout=10_000)
    swap_tiles(page, 1, 5)
    swap_tiles(page, 1, 4)
    swap_tiles(page, 1, 3)
    swap_tiles(page, 1, 2)
    expect(page.get_by_text("Цикл собран").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-flip-parity").click()
    swap_tiles(page, 1, 2)
    expect(page.get_by_text("Знак сменился").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-two-cycles").click()
    swap_tiles(page, 1, 2)
    swap_tiles(page, 3, 4)
    swap_tiles(page, 5, 6)
    expect(page.get_by_text("Три независимых обмена").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-repair").click()
    swap_tiles(page, 2, 3)
    swap_tiles(page, 3, 5)
    expect(page.get_by_text("Маршрут восстановлен").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("mission-debrief")).to_be_visible(timeout=10_000)


def run_substitution_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algebra/substitutions/workshop", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-substitution-workshop"]', timeout=10_000)
    expect(page.get_by_test_id("cycle-rail")).to_be_visible(timeout=10_000)
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
    expect(page.get_by_text("BFS прошел по слоям").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-dfs-stack").click()
    click_graph_order(page, ["A", "B", "D", "F", "E", "G", "C"])
    expect(page.get_by_text("DFS ушел в глубину").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-connected-component").click()
    click_graph_order(page, ["A", "B", "C", "D", "E", "F", "G"])
    expect(page.get_by_text("Компонента найдена").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-repair-trace").click()
    click_graph_order(page, ["B", "C", "D", "E", "F", "G"])
    expect(page.get_by_text("Trace восстановлен").first).to_be_visible(timeout=10_000)
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
    expect(page.get_by_test_id("strategy-race")).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("race-result")).to_contain_text("winner")
    choose_strategy(page, "linear-scan")
    expect(page.get_by_text("Малый вход решен просто").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-large-input").click()
    choose_strategy(page, "merge-sort")
    expect(page.get_by_text("Большой вход пережил рост").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-nearly-sorted").click()
    choose_strategy(page, "insertion-sort")
    expect(page.get_by_text("Структура входа использована").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-many-lookups").click()
    choose_strategy(page, "hash-index")
    expect(page.get_by_text("Preprocessing окупился").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("mission-debrief")).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("mission-reflection")).to_be_visible(timeout=10_000)


def run_asymptotic_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algorithms/asymptotics/arena", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-asymptotic-arena"]', timeout=10_000)
    expect(page.get_by_test_id("race-row-binary-search-after-sort")).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("mission-feedback")).to_contain_text(
        "setup-not-worth-it", timeout=10_000
    )
    choose_strategy(page, "linear-scan")
    expect(page.get_by_text("Малый вход решен просто").first).to_be_visible(timeout=10_000)


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
    expect(page.get_by_test_id("pipeline-diff")).to_be_visible(timeout=10_000)
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
    page.get_by_test_id("level-split-check").click()
    page.get_by_test_id("split-seed-balanced").click()
    expect(page.get_by_text("Split сбалансирован").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("mission-debrief")).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("mission-reflection")).to_be_visible(timeout=10_000)


def run_feature_factory_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/data/features/factory", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-feature-factory"]', timeout=10_000)
    expect(page.get_by_test_id("feature-factory-diagnosis")).to_contain_text(
        "остались NA", timeout=10_000
    )
    expect(page.get_by_test_id("mascot-coach")).to_have_attribute("data-state", "warning")
    click_data_column_action(page, "fill-zero", "temperature")
    expect(page.get_by_test_id("feature-factory-diagnosis")).to_contain_text("Нули закрыли NA")
    expect(page.get_by_test_id("pipeline-strip")).to_contain_text("fill zero temperature")
    page.reload(wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-feature-factory"]', timeout=10_000)
    click_data_column_action(page, "drop-missing", "temperature")
    expect(page.get_by_test_id("feature-factory-diagnosis")).to_contain_text("NA исчезли")
    page.reload(wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-feature-factory"]', timeout=10_000)
    click_data_column_action(page, "impute-median", "temperature")
    expect(page.get_by_text("Пропуски залатаны").first).to_be_visible(timeout=10_000)


def run_happy_paths(browser) -> None:
    context = browser.new_context(viewport={"width": 1440, "height": 960})
    context.add_init_script("window.localStorage.clear()")
    page = context.new_page()
    run_substitution_mistake_path(page)
    run_matrix_mistake_path(page)
    run_quadratic_mistake_path(page)
    run_orthogonal_mistake_path(page)
    run_unitary_mistake_path(page)
    run_svd_mistake_path(page)
    run_determinant_mistake_path(page)
    run_kernel_mistake_path(page)
    run_graph_mistake_path(page)
    run_asymptotic_mistake_path(page)
    run_ml_playground_mistake_path(page)
    run_feature_factory_mistake_path(page)
    run_kernel_happy_path(page)
    run_determinant_happy_path(page)
    run_matrix_happy_path(page)
    run_quadratic_happy_path(page)
    run_orthogonal_happy_path(page)
    run_unitary_happy_path(page)
    run_svd_happy_path(page)
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
