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
        "pca-compression",
        "#/algebra/svd/pca-compression",
        '[data-testid="mission-pca-compression-lab"]',
    ),
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
    ("bernoulli", "#/probability/bernoulli/lab", '[data-testid="mission-bernoulli-lab"]'),
    ("gradient", "#/calculus/gradient/slope", '[data-testid="mission-gradient-slope"]'),
    ("heap", "#/algorithms/heaps/forge", '[data-testid="mission-heap-forge"]'),
    ("roots", "#/algebra/complex-numbers/roots", '[data-testid="mission-roots-orbit"]'),
    ("fourier", "#/calculus/fourier/synth", '[data-testid="mission-fourier-synth"]'),
    ("monte-carlo", "#/probability/monte-carlo/area", '[data-testid="mission-monte-carlo"]'),
    ("bayes-fork", "#/probability/bayes/fork", '[data-testid="mission-bayes-fork"]'),
    ("expectation", "#/probability/expectation/lab", '[data-testid="mission-expectation-lab"]'),
    ("taylor", "#/calculus/taylor/lab", '[data-testid="mission-taylor-lab"]'),
    ("pascal", "#/combinatorics/pascal/triangle", '[data-testid="mission-pascal-triangle"]'),
    ("gauss", "#/algebra/linear-equations/gauss", '[data-testid="mission-gauss-station"]'),
    ("dsu", "#/algorithms/dsu/forest", '[data-testid="mission-dsu-forest"]'),
    ("dp", "#/algorithms/dynamic-programming/edit-distance", '[data-testid="mission-dp-station"]'),
    ("eigen", "#/algebra/eigenvalues/chase", '[data-testid="mission-eigen-chase"]'),
    ("euler", "#/combinatorics/euler/trail", '[data-testid="mission-euler-trail"]'),
    ("bst", "#/algorithms/bst/quest", '[data-testid="mission-bst-quest"]'),
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
    expect(page.get_by_test_id("field-pulse-success")).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("result-moment")).to_contain_text("area locked", timeout=10_000)
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
    expect(page.get_by_test_id("repair-marker")).to_contain_text("flip sign", timeout=10_000)
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
    page.get_by_test_id("level-parallelogram").click()
    expect(page.get_by_test_id("matrix-goal")).to_be_visible(timeout=10_000)
    fill_matrix(page, "2", "1", "1", "2")
    expect(page.get_by_text("Единичный квадрат лег на контур").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-rotate-stretch").click()
    fill_matrix(page, "1", "1", "-1", "1")
    expect(
        page.get_by_text("Квадрат повернулся на 45 градусов").first
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
    expect(page.get_by_test_id("result-moment")).to_be_visible(timeout=10_000)
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
    expect(page.get_by_test_id("repair-marker")).to_be_visible(timeout=10_000)
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
    expect(page.get_by_test_id("result-moment")).to_be_visible(timeout=10_000)
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
    expect(page.get_by_test_id("repair-marker")).to_be_visible(timeout=10_000)
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


def run_pca_compression_happy_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algebra/svd/pca-compression", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-pca-compression-lab"]', timeout=10_000)
    expect(page.get_by_test_id("pca-compression-canvas")).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("pca-original-grid")).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("pca-reconstruction-grid")).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("pca-error-grid")).to_be_visible(timeout=10_000)
    expect(page.get_by_text("Сжатие уложилось").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("result-moment")).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-component-detective").click()
    page.get_by_test_id("pca-component-toggle-1").click()
    expect(page.get_by_text("Нужная компонента найдена").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-center-before-pca").click()
    page.get_by_test_id("pca-center-toggle").check()
    expect(page.get_by_text("Данные центрированы").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-quality-gate").click()
    page.get_by_test_id("pca-fix-artifact").click()
    expect(page.get_by_text("Оба gates пройдены").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-transfer-to-features").click()
    page.get_by_test_id("pca-feature-choice-2").click()
    expect(page.get_by_text("PCA coordinates стали").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("mission-debrief")).to_be_visible(timeout=10_000)


def run_pca_compression_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algebra/svd/pca-compression", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-pca-compression-lab"]', timeout=10_000)
    page.get_by_test_id("pca-rank-choice-0").click()
    expect(page.get_by_test_id("pca-diagnosis")).to_contain_text(
        "Too much energy", timeout=10_000
    )
    expect(page.get_by_test_id("mascot-coach")).to_have_attribute("data-state", "warning")
    expect(page.get_by_test_id("pca-residual-hotspot")).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("repair-marker")).to_be_visible(timeout=10_000)
    page.get_by_test_id("pca-fit-budget").click()
    expect(page.get_by_text("Сжатие уложилось").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-component-detective").click()
    page.get_by_test_id("pca-component-toggle-1").click()
    expect(page.get_by_text("Нужная компонента найдена").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-center-before-pca").click()
    expect(page.get_by_test_id("pca-diagnosis")).to_contain_text(
        "Mean shift", timeout=10_000
    )
    page.get_by_test_id("pca-center-toggle").check()
    expect(page.get_by_text("Данные центрированы").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-quality-gate").click()
    page.get_by_test_id("pca-rank-choice-2").click()
    expect(page.get_by_test_id("pca-diagnosis")).to_contain_text(
        "artifact", timeout=10_000
    )


def run_orthogonal_happy_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algebra/euclidean/orthogonal-workshop", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-orthogonal-workshop"]', timeout=10_000)
    expect(page.get_by_test_id("orthogonal-workshop-canvas")).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("orthogonal-residual")).to_be_visible(timeout=10_000)
    page.get_by_role("button", name="project").click()
    expect(page.get_by_text("Тень найдена").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("result-moment")).to_be_visible(timeout=10_000)
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
    expect(page.get_by_test_id("repair-marker")).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("repair-marker")).to_contain_text("dot")
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
    expect(page.get_by_test_id("result-moment")).to_be_visible(timeout=10_000)
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
    expect(page.get_by_test_id("repair-marker")).to_be_visible(timeout=10_000)
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
    expect(page.get_by_test_id("result-moment")).to_be_visible(timeout=10_000)
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
    expect(page.get_by_test_id("repair-marker")).to_be_visible(timeout=10_000)
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
    expect(page.get_by_test_id("repair-marker")).to_contain_text("next A", timeout=10_000)
    expect(page.get_by_test_id("graph-ghost-next")).to_be_visible(timeout=10_000)
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
    expect(page.get_by_test_id("repair-marker")).to_be_visible(timeout=10_000)
    choose_strategy(page, "linear-scan")
    expect(page.get_by_text("Малый вход решен просто").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("result-moment")).to_be_visible(timeout=10_000)


def run_ml_playground_happy_path(page) -> None:
    page.goto(f"{BASE_URL}/#/data/ml/playground", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-ml-playground"]', timeout=10_000)
    set_ml_threshold(page, "50")
    expect(page.get_by_text("Train-порог пойман").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("result-moment")).to_be_visible(timeout=10_000)
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
    expect(page.get_by_test_id("repair-marker")).to_be_visible(timeout=10_000)
    set_ml_threshold(page, "58")
    expect(page.get_by_text("Test-контроль пройден").first).to_be_visible(timeout=10_000)


def run_feature_factory_happy_path(page) -> None:
    page.goto(f"{BASE_URL}/#/data/features/factory", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-feature-factory"]', timeout=10_000)
    expect(page.get_by_test_id("pipeline-diff")).to_be_visible(timeout=10_000)
    click_data_column_action(page, "impute-median", "temperature")
    expect(page.get_by_text("Пропуски залатаны").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("result-moment")).to_contain_text("pipeline clean", timeout=10_000)
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
    expect(page.get_by_test_id("repair-marker")).to_contain_text("dirty temp", timeout=10_000)
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
    expect(page.get_by_test_id("repair-marker")).to_have_count(0)


def run_bernoulli_happy_path(page) -> None:
    page.goto(f"{BASE_URL}/#/probability/bernoulli/lab", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-bernoulli-lab"]', timeout=10_000)
    expect(page.get_by_test_id("bernoulli-lab-canvas")).to_be_visible(timeout=10_000)
    page.get_by_test_id("bernoulli-sample-500").click()
    expect(page.get_by_text("Частота села у 0.5").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("result-moment")).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-estimate-bias").click()
    page.get_by_test_id("bernoulli-sample-500").click()
    page.get_by_test_id("bernoulli-estimate").fill("0.7")
    expect(page.get_by_text("Оценка совпала").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-law-of-large-numbers").click()
    page.get_by_test_id("bernoulli-sample-2000").click()
    expect(page.get_by_text("Хвост частоты застыл").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("mission-reflection")).to_be_visible(timeout=10_000)


def run_bernoulli_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/probability/bernoulli/lab", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-bernoulli-lab"]', timeout=10_000)
    page.get_by_test_id("bernoulli-sample-100").click()
    expect(page.get_by_test_id("bernoulli-diagnosis")).to_contain_text(
        "Слишком мало", timeout=10_000
    )
    expect(page.get_by_test_id("mascot-coach")).to_have_attribute("data-state", "warning")
    expect(page.get_by_test_id("repair-marker")).to_be_visible(timeout=10_000)
    page.get_by_test_id("bernoulli-sample-500").click()
    expect(page.get_by_text("Частота села у 0.5").first).to_be_visible(timeout=10_000)


def run_gradient_happy_path(page) -> None:
    page.goto(f"{BASE_URL}/#/calculus/gradient/slope", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-gradient-slope"]', timeout=10_000)
    expect(page.get_by_test_id("gradient-slope-canvas")).to_be_visible(timeout=10_000)
    page.get_by_test_id("gradient-lr").fill("0.5")
    expect(page.get_by_text("Точка скатилась в минимум").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("result-moment")).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-tame-the-step").click()
    page.get_by_test_id("gradient-lr").fill("0.3")
    expect(page.get_by_text("Спуск укрощён").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-narrow-valley").click()
    page.get_by_test_id("gradient-lr").fill("0.1")
    expect(page.get_by_text("Долина пройдена").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("mission-reflection")).to_be_visible(timeout=10_000)


def run_gradient_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/calculus/gradient/slope", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-gradient-slope"]', timeout=10_000)
    page.get_by_test_id("gradient-lr").fill("0.03")
    expect(page.get_by_test_id("gradient-diagnosis")).to_contain_text(
        "не доехал", timeout=10_000
    )
    expect(page.get_by_test_id("mascot-coach")).to_have_attribute("data-state", "warning")
    expect(page.get_by_test_id("repair-marker")).to_be_visible(timeout=10_000)
    page.get_by_test_id("gradient-lr").fill("0.5")
    expect(page.get_by_text("Точка скатилась в минимум").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-tame-the-step").click()
    page.get_by_test_id("gradient-lr").fill("0.7")
    expect(page.get_by_test_id("gradient-diagnosis")).to_contain_text(
        "слишком большой", timeout=10_000
    )
    expect(page.get_by_test_id("repair-marker")).to_be_visible(timeout=10_000)


def run_heap_happy_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algorithms/heaps/forge", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-heap-forge"]', timeout=10_000)
    expect(page.get_by_test_id("heap-forge-canvas")).to_be_visible(timeout=10_000)
    page.get_by_test_id("heap-node-1").click()
    page.get_by_test_id("heap-node-3").click()
    expect(page.get_by_text("Ребро починено").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("result-moment")).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-bubble-up").click()
    page.get_by_test_id("heap-node-7").click()
    page.get_by_test_id("heap-node-3").click()
    page.get_by_test_id("heap-node-3").click()
    page.get_by_test_id("heap-node-1").click()
    expect(page.get_by_text("Вставка просеяна").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-sift-down").click()
    page.get_by_test_id("heap-node-0").click()
    page.get_by_test_id("heap-node-1").click()
    expect(page.get_by_text("Корень просеян вниз").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("mission-reflection")).to_be_visible(timeout=10_000)


def run_heap_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algorithms/heaps/forge", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-heap-forge"]', timeout=10_000)
    page.get_by_test_id("heap-node-4").click()
    page.get_by_test_id("heap-node-6").click()
    expect(page.get_by_test_id("heap-diagnosis")).to_contain_text("Нарушение", timeout=10_000)
    expect(page.get_by_test_id("mascot-coach")).to_have_attribute("data-state", "warning")
    expect(page.get_by_test_id("repair-marker")).to_be_visible(timeout=10_000)
    page.get_by_test_id("heap-node-1").click()
    page.get_by_test_id("heap-node-3").click()
    expect(page.get_by_text("Ребро починено").first).to_be_visible(timeout=10_000)


def run_roots_happy_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algebra/complex-numbers/roots", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-roots-orbit"]', timeout=10_000)
    expect(page.get_by_test_id("roots-orbit-canvas")).to_be_visible(timeout=10_000)
    page.get_by_test_id("roots-snap").click()
    expect(page.get_by_text("Треугольник замкнут").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("result-moment")).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-square").click()
    page.get_by_test_id("roots-re").fill("0")
    page.get_by_test_id("roots-im").fill("1")
    expect(page.get_by_text("Квадрат собран").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-pentagon").click()
    page.get_by_test_id("roots-snap").click()
    expect(page.get_by_text("Пятиугольник закрыт").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("mission-reflection")).to_be_visible(timeout=10_000)


def run_roots_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algebra/complex-numbers/roots", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-roots-orbit"]', timeout=10_000)
    page.get_by_test_id("roots-re").fill("1.3")
    expect(page.get_by_test_id("roots-diagnosis")).to_contain_text("спирал", timeout=10_000)
    expect(page.get_by_test_id("mascot-coach")).to_have_attribute("data-state", "warning")
    expect(page.get_by_test_id("repair-marker")).to_be_visible(timeout=10_000)
    page.get_by_test_id("roots-snap").click()
    expect(page.get_by_text("Треугольник замкнут").first).to_be_visible(timeout=10_000)


_RANGE_SETTER = (
    "(node, val) => {"
    " const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;"
    " s.call(node, String(val));"
    " node.dispatchEvent(new Event('input', {bubbles: true})); }"
)


def set_range(page, test_id: str, value) -> None:
    page.get_by_test_id(test_id).evaluate(_RANGE_SETTER, value)


def run_fourier_happy_path(page) -> None:
    page.goto(f"{BASE_URL}/#/calculus/fourier/synth", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-fourier-synth"]', timeout=10_000)
    expect(page.get_by_test_id("fourier-synth-canvas")).to_be_visible(timeout=10_000)
    set_range(page, "fourier-harmonic-1", 1.0)
    set_range(page, "fourier-harmonic-2", 0.5)
    expect(page.get_by_text("Две гармоники совпали").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("result-moment")).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-square-wave").click()
    set_range(page, "fourier-harmonic-1", 1.25)
    set_range(page, "fourier-harmonic-3", 0.40)
    set_range(page, "fourier-harmonic-5", 0.25)
    expect(page.get_by_text("Прямоугольник собран").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-sawtooth").click()
    set_range(page, "fourier-harmonic-1", 0.65)
    set_range(page, "fourier-harmonic-2", -0.30)
    set_range(page, "fourier-harmonic-3", 0.20)
    set_range(page, "fourier-harmonic-4", -0.15)
    set_range(page, "fourier-harmonic-5", 0.15)
    expect(page.get_by_text("Пила собрана").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("mission-reflection")).to_be_visible(timeout=10_000)


def run_fourier_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/calculus/fourier/synth", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-fourier-synth"]', timeout=10_000)
    set_range(page, "fourier-harmonic-1", 1.0)
    expect(page.get_by_test_id("fourier-diagnosis")).to_contain_text("Гармоника", timeout=10_000)
    expect(page.get_by_test_id("mascot-coach")).to_have_attribute("data-state", "warning")
    expect(page.get_by_test_id("repair-marker")).to_be_visible(timeout=10_000)
    set_range(page, "fourier-harmonic-2", 0.5)
    expect(page.get_by_text("Две гармоники совпали").first).to_be_visible(timeout=10_000)


def run_monte_carlo_happy_path(page) -> None:
    page.goto(f"{BASE_URL}/#/probability/monte-carlo/area", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-monte-carlo"]', timeout=10_000)
    expect(page.get_by_test_id("monte-carlo-canvas")).to_be_visible(timeout=10_000)
    page.get_by_test_id("mc-sample-1000").click()
    expect(page.get_by_text("Оценка pi устаканилась").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("result-moment")).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-triangle").click()
    page.get_by_test_id("mc-sample-1000").click()
    expect(page.get_by_text("Площадь треугольника поймана").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-parabola").click()
    page.get_by_test_id("mc-sample-1000").click()
    expect(page.get_by_text("Площадь под параболой поймана").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("mission-reflection")).to_be_visible(timeout=10_000)


def run_monte_carlo_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/probability/monte-carlo/area", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-monte-carlo"]', timeout=10_000)
    page.get_by_test_id("mc-sample-200").click()
    expect(page.get_by_test_id("mc-diagnosis")).to_contain_text("Мало точек", timeout=10_000)
    expect(page.get_by_test_id("mascot-coach")).to_have_attribute("data-state", "warning")
    expect(page.get_by_test_id("repair-marker")).to_be_visible(timeout=10_000)
    page.get_by_test_id("mc-sample-1000").click()
    expect(page.get_by_text("Оценка pi устаканилась").first).to_be_visible(timeout=10_000)


def run_bayes_happy_path(page) -> None:
    page.goto(f"{BASE_URL}/#/probability/bayes/fork", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-bayes-fork"]', timeout=10_000)
    expect(page.get_by_test_id("bayes-table")).to_be_visible(timeout=10_000)
    # Level 1: condition on the disease row, read the sensitivity. Start from
    # level 1 explicitly so the path is independent of any inherited level.
    page.get_by_test_id("level-conditional-frequency").click()
    page.get_by_test_id("bayes-sample-2000").click()
    set_range(page, "bayes-estimate", 0.9)
    expect(page.get_by_text("доля плюсов среди больных").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("result-moment")).to_be_visible(timeout=10_000)
    # Level 2: rare disease, one positive -> the base-rate inversion.
    page.get_by_test_id("level-base-rate").click()
    page.get_by_test_id("bayes-sample-8000").click()
    set_range(page, "bayes-estimate", 0.24)
    expect(page.get_by_text("при редкой болезни даже точный тест").first).to_be_visible(timeout=10_000)
    # Level 3: two positives sharpen the posterior.
    page.get_by_test_id("level-two-tests").click()
    page.get_by_test_id("bayes-sample-8000").click()
    set_range(page, "bayes-estimate", 0.84)
    expect(page.get_by_text("второй независимый плюс резко поднял апостериор").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("mission-reflection")).to_be_visible(timeout=10_000)


def run_bayes_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/probability/bayes/fork", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-bayes-fork"]', timeout=10_000)
    # Clear level 1 to unlock the base-rate level where neglect can happen.
    page.get_by_test_id("bayes-sample-2000").click()
    set_range(page, "bayes-estimate", 0.9)
    expect(page.get_by_text("доля плюсов среди больных").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-base-rate").click()
    page.get_by_test_id("bayes-sample-8000").click()
    # Base-rate neglect: answering the sensitivity instead of the posterior.
    set_range(page, "bayes-estimate", 0.95)
    expect(page.get_by_test_id("bayes-diagnosis")).to_contain_text("чувствительность", timeout=10_000)
    expect(page.get_by_test_id("mascot-coach")).to_have_attribute("data-state", "warning")
    expect(page.get_by_test_id("repair-marker")).to_be_visible(timeout=10_000)
    set_range(page, "bayes-estimate", 0.24)
    expect(page.get_by_text("при редкой болезни даже точный тест").first).to_be_visible(timeout=10_000)


def run_expectation_happy_path(page) -> None:
    page.goto(f"{BASE_URL}/#/probability/expectation/lab", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-expectation-lab"]', timeout=10_000)
    expect(page.get_by_test_id("expectation-canvas")).to_be_visible(timeout=10_000)
    # Level 1: sample mean of a fair die converges to E[X] = 3.5.
    page.get_by_test_id("level-sample-mean").click()
    page.get_by_test_id("expectation-sample-1000").click()
    set_range(page, "expectation-estimate", 3.5)
    expect(page.get_by_text("Среднее село у 3.5").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("result-moment")).to_be_visible(timeout=10_000)
    # Level 2: variance is the mean squared deviation, not its root.
    page.get_by_test_id("level-sample-variance").click()
    page.get_by_test_id("expectation-sample-5000").click()
    set_range(page, "expectation-estimate", 2.9)
    expect(page.get_by_text("Дисперсия поймана").first).to_be_visible(timeout=10_000)
    # Level 3: estimate the mean of a hidden loaded die.
    page.get_by_test_id("level-estimate-mean").click()
    page.get_by_test_id("expectation-sample-1000").click()
    set_range(page, "expectation-estimate", 3.0)
    expect(page.get_by_text("восстановило скрытое ожидание").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("mission-reflection")).to_be_visible(timeout=10_000)


def run_expectation_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/probability/expectation/lab", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-expectation-lab"]', timeout=10_000)
    # Clear level 1 to unlock the variance level.
    page.get_by_test_id("level-sample-mean").click()
    page.get_by_test_id("expectation-sample-1000").click()
    set_range(page, "expectation-estimate", 3.5)
    expect(page.get_by_text("Среднее село у 3.5").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-sample-variance").click()
    page.get_by_test_id("expectation-sample-5000").click()
    # Standard deviation answered where the variance is asked.
    set_range(page, "expectation-estimate", 1.7)
    expect(page.get_by_test_id("expectation-diagnosis")).to_contain_text(
        "стандартное отклонение", timeout=10_000
    )
    expect(page.get_by_test_id("mascot-coach")).to_have_attribute("data-state", "warning")
    expect(page.get_by_test_id("repair-marker")).to_be_visible(timeout=10_000)
    set_range(page, "expectation-estimate", 2.9)
    expect(page.get_by_text("Дисперсия поймана").first).to_be_visible(timeout=10_000)


def run_taylor_happy_path(page) -> None:
    page.goto(f"{BASE_URL}/#/calculus/taylor/lab", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-taylor-lab"]', timeout=10_000)
    expect(page.get_by_test_id("taylor-canvas")).to_be_visible(timeout=10_000)
    # Level 1: tangent line of e^x is 1 + x.
    page.get_by_test_id("level-tangent").click()
    set_range(page, "taylor-coeff-0", 1.0)
    set_range(page, "taylor-coeff-1", 1.0)
    expect(page.get_by_text("Касательная найдена").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("result-moment")).to_be_visible(timeout=10_000)
    # Level 2: add the quadratic curvature term x^2/2.
    page.get_by_test_id("level-curvature").click()
    set_range(page, "taylor-coeff-0", 1.0)
    set_range(page, "taylor-coeff-1", 1.0)
    set_range(page, "taylor-coeff-2", 0.5)
    expect(page.get_by_text("Кривизна поймана").first).to_be_visible(timeout=10_000)
    # Level 3: Taylor of sin x keeps only odd terms with a sign flip.
    page.get_by_test_id("level-sine").click()
    set_range(page, "taylor-coeff-1", 1.0)
    set_range(page, "taylor-coeff-3", -0.15)
    expect(page.get_by_text("Синус собран").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("mission-reflection")).to_be_visible(timeout=10_000)


def run_taylor_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/calculus/taylor/lab", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-taylor-lab"]', timeout=10_000)
    # Only the constant term set: the linear coefficient is still missing.
    set_range(page, "taylor-coeff-0", 1.0)
    expect(page.get_by_test_id("taylor-diagnosis")).to_contain_text("Коэффициент", timeout=10_000)
    expect(page.get_by_test_id("mascot-coach")).to_have_attribute("data-state", "warning")
    expect(page.get_by_test_id("repair-marker")).to_be_visible(timeout=10_000)
    set_range(page, "taylor-coeff-1", 1.0)
    expect(page.get_by_text("Касательная найдена").first).to_be_visible(timeout=10_000)


def fill_pascal_triangle(page, rows: int) -> None:
    # Fill interior cells row by row, left to right (edges start filled).
    for i in range(2, rows):
        for j in range(1, i):
            page.get_by_test_id(f"pascal-cell-{i}-{j}").click()


def run_pascal_happy_path(page) -> None:
    page.goto(f"{BASE_URL}/#/combinatorics/pascal/triangle", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-pascal-triangle"]', timeout=10_000)
    expect(page.get_by_test_id("pascal-triangle-grid")).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-triangle-5").click()
    fill_pascal_triangle(page, 5)
    expect(page.get_by_text("внутренние клетки — суммы соседок").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("result-moment")).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-triangle-6").click()
    fill_pascal_triangle(page, 6)
    expect(page.get_by_text("Шестая строка собрана").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-triangle-7").click()
    fill_pascal_triangle(page, 7)
    expect(page.get_by_text("до седьмой строки").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("mission-reflection")).to_be_visible(timeout=10_000)


def run_pascal_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/combinatorics/pascal/triangle", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-pascal-triangle"]', timeout=10_000)
    # Cell (3,1) needs interior (2,1) first — not ready yet.
    page.get_by_test_id("pascal-cell-3-1").click()
    expect(page.get_by_test_id("pascal-diagnosis")).to_contain_text("рано считать", timeout=10_000)
    expect(page.get_by_test_id("mascot-coach")).to_have_attribute("data-state", "warning")
    expect(page.get_by_test_id("repair-marker")).to_be_visible(timeout=10_000)
    fill_pascal_triangle(page, 5)
    expect(page.get_by_text("внутренние клетки — суммы соседок").first).to_be_visible(timeout=10_000)


def run_gauss_happy_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algebra/linear-equations/gauss", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-gauss-station"]', timeout=10_000)
    expect(page.get_by_test_id("gauss-station-grid")).to_be_visible(timeout=10_000)
    page.get_by_test_id("gauss-cell-1-0").click()
    page.get_by_test_id("gauss-cell-2-0").click()
    page.get_by_test_id("gauss-cell-2-1").click()
    expect(page.get_by_text("Ступенчатый вид получен").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("gauss-solution")).to_contain_text("x = 1", timeout=10_000)
    expect(page.get_by_test_id("result-moment")).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-need-swap").click()
    page.get_by_test_id("gauss-swap-0-1").click()
    page.get_by_test_id("gauss-cell-2-0").click()
    page.get_by_test_id("gauss-cell-2-1").click()
    expect(page.get_by_text("Обмен строк спас опору").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-fractions").click()
    page.get_by_test_id("gauss-cell-1-0").click()
    page.get_by_test_id("gauss-cell-2-0").click()
    page.get_by_test_id("gauss-cell-2-1").click()
    expect(page.get_by_text("Ступенчатый вид получен и с дробными").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("mission-reflection")).to_be_visible(timeout=10_000)


def run_gauss_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algebra/linear-equations/gauss", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-gauss-station"]', timeout=10_000)
    # Clear the forward level first so the need-swap level unlocks.
    page.get_by_test_id("gauss-cell-1-0").click()
    page.get_by_test_id("gauss-cell-2-0").click()
    page.get_by_test_id("gauss-cell-2-1").click()
    expect(page.get_by_text("Ступенчатый вид получен").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-need-swap").click()
    page.get_by_test_id("gauss-swap-1-2").click()
    expect(page.get_by_test_id("gauss-diagnosis")).to_contain_text("равен нулю", timeout=10_000)
    expect(page.get_by_test_id("mascot-coach")).to_have_attribute("data-state", "warning")
    expect(page.get_by_test_id("repair-marker")).to_be_visible(timeout=10_000)
    page.get_by_test_id("gauss-reset").click()
    page.get_by_test_id("gauss-swap-0-1").click()
    page.get_by_test_id("gauss-cell-2-0").click()
    page.get_by_test_id("gauss-cell-2-1").click()
    expect(page.get_by_text("Обмен строк спас опору").first).to_be_visible(timeout=10_000)


def click_dsu_edge(page, index: int) -> None:
    # SVG <g> hit areas are transparent, so Playwright's visibility heuristic
    # needs a forced click; the element is interactable.
    page.get_by_test_id(f"dsu-edge-{index}").click(force=True)


def run_dsu_happy_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algorithms/dsu/forest", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-dsu-forest"]', timeout=10_000)
    expect(page.get_by_test_id("dsu-forest-canvas")).to_be_visible(timeout=10_000)
    for index in [0, 1, 3, 4, 5]:
        click_dsu_edge(page, index)
    expect(page.get_by_text("Все вершины связаны").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("result-moment")).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-spanning-tree").click()
    for index in [0, 1, 2, 3, 4]:
        click_dsu_edge(page, index)
    expect(page.get_by_text("Остов собран").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-two-groups").click()
    for index in [0, 1, 2, 3]:
        click_dsu_edge(page, index)
    expect(page.get_by_text("Осталось ровно две группы").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("mission-reflection")).to_be_visible(timeout=10_000)


def run_dsu_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algorithms/dsu/forest", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-dsu-forest"]', timeout=10_000)
    # Edge 2 closes a triangle: a redundant cycle before everything is connected.
    for index in [0, 1, 2]:
        click_dsu_edge(page, index)
    expect(page.get_by_test_id("mascot-coach")).to_have_attribute("data-state", "warning")
    expect(page.get_by_test_id("repair-marker")).to_contain_text("цикл", timeout=10_000)
    for index in [3, 4, 5]:
        click_dsu_edge(page, index)
    expect(page.get_by_text("Все вершины связаны").first).to_be_visible(timeout=10_000)


def fill_dp_table(page, rows: int, cols: int) -> None:
    for i in range(1, rows + 1):
        for j in range(1, cols + 1):
            page.get_by_test_id(f"dp-cell-{i}-{j}").click()


def run_dp_happy_path(page) -> None:
    page.goto(
        f"{BASE_URL}/#/algorithms/dynamic-programming/edit-distance",
        wait_until="domcontentloaded",
    )
    page.wait_for_selector('[data-testid="mission-dp-station"]', timeout=10_000)
    expect(page.get_by_test_id("dp-station-grid")).to_be_visible(timeout=10_000)
    fill_dp_table(page, 3, 3)
    expect(page.get_by_text("Таблица заполнена").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("dp-answer")).to_contain_text("= 1", timeout=10_000)
    expect(page.get_by_test_id("result-moment")).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-cat-cart").click()
    fill_dp_table(page, 3, 4)
    expect(page.get_by_text("Таблица заполнена").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-food-gold").click()
    fill_dp_table(page, 4, 4)
    expect(page.get_by_test_id("dp-answer")).to_contain_text("= 2", timeout=10_000)
    expect(page.get_by_test_id("mission-reflection")).to_be_visible(timeout=10_000)


def run_dp_mistake_path(page) -> None:
    page.goto(
        f"{BASE_URL}/#/algorithms/dynamic-programming/edit-distance",
        wait_until="domcontentloaded",
    )
    page.wait_for_selector('[data-testid="mission-dp-station"]', timeout=10_000)
    # Cell (2,2) is not ready before its neighbours are computed.
    page.get_by_test_id("dp-cell-2-2").click()
    expect(page.get_by_test_id("dp-diagnosis")).to_contain_text("рано считать", timeout=10_000)
    expect(page.get_by_test_id("mascot-coach")).to_have_attribute("data-state", "warning")
    expect(page.get_by_test_id("repair-marker")).to_be_visible(timeout=10_000)
    fill_dp_table(page, 3, 3)
    expect(page.get_by_text("Таблица заполнена").first).to_be_visible(timeout=10_000)


def run_eigen_happy_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algebra/eigenvalues/chase", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-eigen-chase"]', timeout=10_000)
    expect(page.get_by_test_id("eigen-chase-canvas")).to_be_visible(timeout=10_000)
    set_range(page, "eigen-angle", 45)
    expect(page.get_by_text("Найдено направление с λ = 3").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("result-moment")).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-small-eigen").click()
    set_range(page, "eigen-angle", 315)
    expect(page.get_by_text("Найдено второе собственное направление").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-flip-eigen").click()
    set_range(page, "eigen-angle", 315)
    expect(page.get_by_text("Найдено направление с λ = -1").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("mission-reflection")).to_be_visible(timeout=10_000)


def run_eigen_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algebra/eigenvalues/chase", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-eigen-chase"]', timeout=10_000)
    set_range(page, "eigen-angle", 0)
    expect(page.get_by_test_id("eigen-diagnosis")).to_contain_text("повёрнут", timeout=10_000)
    expect(page.get_by_test_id("mascot-coach")).to_have_attribute("data-state", "warning")
    expect(page.get_by_test_id("repair-marker")).to_be_visible(timeout=10_000)
    set_range(page, "eigen-angle", 45)
    expect(page.get_by_text("Найдено направление с λ = 3").first).to_be_visible(timeout=10_000)


def click_euler_path(page, vertices) -> None:
    for vertex in vertices:
        page.get_by_test_id(f"euler-vertex-{vertex}").click()


def run_euler_happy_path(page) -> None:
    page.goto(f"{BASE_URL}/#/combinatorics/euler/trail", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-euler-trail"]', timeout=10_000)
    expect(page.get_by_test_id("euler-trail-canvas")).to_be_visible(timeout=10_000)
    click_euler_path(page, [0, 1, 2, 3, 4, 2, 0])
    expect(page.get_by_text("Эйлеров цикл построен").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("result-moment")).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-house").click()
    click_euler_path(page, [2, 1, 0, 3, 4, 2, 3])
    expect(page.get_by_text("Эйлеров путь построен").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-envelope").click()
    click_euler_path(page, [0, 3, 2, 4, 3, 1, 2, 0, 1])
    expect(page.get_by_text("Конверт нарисован").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("mission-reflection")).to_be_visible(timeout=10_000)


def run_euler_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/combinatorics/euler/trail", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-euler-trail"]', timeout=10_000)
    page.get_by_test_id("euler-vertex-0").click()
    page.get_by_test_id("euler-vertex-3").click()  # 1 and 4 are not adjacent
    expect(page.get_by_test_id("euler-diagnosis")).to_contain_text("нет свободного ребра", timeout=10_000)
    expect(page.get_by_test_id("mascot-coach")).to_have_attribute("data-state", "warning")
    expect(page.get_by_test_id("repair-marker")).to_be_visible(timeout=10_000)
    click_euler_path(page, [1, 2, 3, 4, 2, 0])
    expect(page.get_by_text("Эйлеров цикл построен").first).to_be_visible(timeout=10_000)


def run_bst_happy_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algorithms/bst/quest", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-bst-quest"]', timeout=10_000)
    expect(page.get_by_test_id("bst-quest-canvas")).to_be_visible(timeout=10_000)
    page.get_by_test_id("bst-node-2").click()
    page.get_by_test_id("bst-node-5").click()
    expect(page.get_by_text("Число 7 найдено").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("result-moment")).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-find-deep").click()
    page.get_by_test_id("bst-node-1").click()
    page.get_by_test_id("bst-node-3").click()
    expect(page.get_by_text("Число 2 найдено").first).to_be_visible(timeout=10_000)
    page.get_by_test_id("level-not-found").click()
    page.get_by_test_id("bst-node-2").click()
    page.get_by_test_id("bst-node-5").click()
    expect(page.get_by_text("числа 6 в дереве нет").first).to_be_visible(timeout=10_000)
    expect(page.get_by_test_id("mission-reflection")).to_be_visible(timeout=10_000)


def run_bst_mistake_path(page) -> None:
    page.goto(f"{BASE_URL}/#/algorithms/bst/quest", wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="mission-bst-quest"]', timeout=10_000)
    # Target 7 is greater than root 5, so the left child (node 1) is the wrong branch.
    page.get_by_test_id("bst-node-1").click()
    expect(page.get_by_test_id("bst-diagnosis")).to_contain_text("Не та ветка", timeout=10_000)
    expect(page.get_by_test_id("mascot-coach")).to_have_attribute("data-state", "warning")
    expect(page.get_by_test_id("repair-marker")).to_be_visible(timeout=10_000)
    page.get_by_test_id("bst-node-2").click()
    page.get_by_test_id("bst-node-5").click()
    expect(page.get_by_text("Число 7 найдено").first).to_be_visible(timeout=10_000)


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
    run_pca_compression_mistake_path(page)
    run_determinant_mistake_path(page)
    run_kernel_mistake_path(page)
    run_graph_mistake_path(page)
    run_asymptotic_mistake_path(page)
    run_ml_playground_mistake_path(page)
    run_feature_factory_mistake_path(page)
    run_bernoulli_mistake_path(page)
    run_gradient_mistake_path(page)
    run_heap_mistake_path(page)
    run_roots_mistake_path(page)
    run_fourier_mistake_path(page)
    run_monte_carlo_mistake_path(page)
    run_bayes_mistake_path(page)
    run_expectation_mistake_path(page)
    run_taylor_mistake_path(page)
    run_pascal_mistake_path(page)
    run_gauss_mistake_path(page)
    run_dsu_mistake_path(page)
    run_dp_mistake_path(page)
    run_eigen_mistake_path(page)
    run_euler_mistake_path(page)
    run_bst_mistake_path(page)
    run_kernel_happy_path(page)
    run_determinant_happy_path(page)
    run_matrix_happy_path(page)
    run_quadratic_happy_path(page)
    run_orthogonal_happy_path(page)
    run_unitary_happy_path(page)
    run_svd_happy_path(page)
    run_pca_compression_happy_path(page)
    run_substitution_happy_path(page)
    run_graph_happy_path(page)
    run_asymptotic_happy_path(page)
    run_ml_playground_happy_path(page)
    run_feature_factory_happy_path(page)
    run_bernoulli_happy_path(page)
    run_gradient_happy_path(page)
    run_heap_happy_path(page)
    run_roots_happy_path(page)
    run_fourier_happy_path(page)
    run_monte_carlo_happy_path(page)
    run_bayes_happy_path(page)
    run_expectation_happy_path(page)
    run_taylor_happy_path(page)
    run_pascal_happy_path(page)
    run_gauss_happy_path(page)
    run_dsu_happy_path(page)
    run_dp_happy_path(page)
    run_eigen_happy_path(page)
    run_euler_happy_path(page)
    run_bst_happy_path(page)
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
