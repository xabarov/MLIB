"""Иллюстрации для лекции про размещения, перестановки и сочетания."""

from __future__ import annotations

import itertools
from math import comb
from pathlib import Path
from tempfile import TemporaryDirectory

import imageio.v2 as imageio
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

C_BG = "#faf9f5"
C_INK = "#141413"
C_GRAY = "#b0aea5"
C_PANEL = "#e8e6dc"
C_ORANGE = "#d97757"
C_BLUE = "#6a9bcc"
C_GREEN = "#788c5d"
C_PURPLE = "#7c6ccf"


def _apply_style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": C_BG,
            "axes.facecolor": C_BG,
            "axes.edgecolor": C_GRAY,
            "axes.labelcolor": C_INK,
            "text.color": C_INK,
            "xtick.color": C_INK,
            "ytick.color": C_INK,
            "font.size": 11,
        }
    )


def _save(fig: plt.Figure, out_name: str) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def _setup_panel(ax: plt.Axes, xlim: tuple[float, float], ylim: tuple[float, float]) -> None:
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")


def _rounded_box(
    ax: plt.Axes,
    xy: tuple[float, float],
    width: float,
    height: float,
    *,
    facecolor: str,
    edgecolor: str = C_GRAY,
    alpha: float = 1.0,
) -> FancyBboxPatch:
    patch = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.04,rounding_size=0.08",
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=1.4,
        alpha=alpha,
    )
    ax.add_patch(patch)
    return patch


def draw_choice_filter(out_name: str = "choice_filter.png") -> None:
    """Два вопроса, которые выбирают нужную комбинаторную формулу."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(9.0, 5.4))
    _setup_panel(ax, (0, 10), (0, 6))

    ax.text(0.4, 5.55, "Как выбрать формулу: порядок и повторения", fontsize=15, weight="bold")
    ax.text(2.55, 4.75, "Повторения запрещены", ha="center", fontsize=12, color=C_INK)
    ax.text(7.25, 4.75, "Повторения разрешены", ha="center", fontsize=12, color=C_INK)
    ax.text(0.55, 3.55, "Порядок\nважен", ha="center", va="center", fontsize=12, color=C_INK)
    ax.text(0.55, 1.55, "Порядок\nне важен", ha="center", va="center", fontsize=12, color=C_INK)

    cells = [
        ((1.25, 2.75), C_BLUE, r"$A_n^k=\dfrac{n!}{(n-k)!}$", "размещения"),
        ((5.95, 2.75), C_ORANGE, r"$n^k$", "размещения с повторениями"),
        ((1.25, 0.75), C_GREEN, r"$C_n^k=\binom{n}{k}$", "сочетания"),
        ((5.95, 0.75), C_PURPLE, r"$\binom{n+k-1}{k}$", "сочетания с повторениями"),
    ]
    for (x, y), color, formula, title in cells:
        _rounded_box(ax, (x, y), 3.8, 1.45, facecolor=color, edgecolor=color, alpha=0.18)
        ax.text(x + 1.9, y + 0.94, title, ha="center", va="center", fontsize=12, weight="bold", color=color)
        ax.text(x + 1.9, y + 0.42, formula, ha="center", va="center", fontsize=15, color=C_INK)

    ax.plot([5.45, 5.45], [0.55, 4.45], color=C_GRAY, lw=1.2)
    ax.plot([1.0, 9.85], [2.5, 2.5], color=C_GRAY, lw=1.2)
    ax.text(0.4, 0.22, "Перестановки $n!$ — это частный случай: упорядочиваем все $n$ элементов.", fontsize=10.5)
    fig.tight_layout(pad=0.6)
    _save(fig, out_name)


def draw_order_vs_combination(out_name: str = "order_vs_combination.png") -> None:
    """Один неупорядоченный набор соответствует k! упорядоченным наборам."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(9.0, 5.2))
    _setup_panel(ax, (0, 10), (0, 5.4))

    ax.text(0.35, 5.05, r"Связь $A_n^k=C_n^k\cdot k!$: выбор плюс порядок", fontsize=15, weight="bold")
    selected = ["A", "B", "C"]
    colors = [C_BLUE, C_ORANGE, C_GREEN]
    for i, (label, color) in enumerate(zip(selected, colors)):
        x = 1.0 + i * 0.72
        ax.add_patch(Circle((x, 3.5), 0.25, facecolor=color, edgecolor=C_INK, lw=1.2, alpha=0.85))
        ax.text(x, 3.5, label, ha="center", va="center", fontsize=12, weight="bold")
    _rounded_box(ax, (0.55, 2.75), 2.35, 1.35, facecolor=C_PANEL, edgecolor=C_GRAY, alpha=0.55)
    ax.text(1.72, 2.95, "один набор\nбез порядка", ha="center", va="center", fontsize=11)

    ax.add_patch(FancyArrowPatch((3.05, 3.35), (4.35, 3.35), arrowstyle="-|>", mutation_scale=14, lw=1.7, color=C_GRAY))
    ax.text(3.7, 3.62, r"добавляем $3!$ порядков", ha="center", fontsize=10.5, color=C_INK)

    perms = list(itertools.permutations(selected))
    for idx, perm in enumerate(perms):
        row = idx // 3
        col = idx % 3
        x0 = 4.55 + col * 1.75
        y0 = 3.85 - row * 1.15
        _rounded_box(ax, (x0, y0), 1.35, 0.68, facecolor="#ffffff", edgecolor=C_GRAY, alpha=0.75)
        for j, letter in enumerate(perm):
            color = colors[selected.index(letter)]
            ax.add_patch(Circle((x0 + 0.28 + j * 0.38, y0 + 0.34), 0.16, facecolor=color, edgecolor=C_INK, lw=0.9, alpha=0.86))
            ax.text(x0 + 0.28 + j * 0.38, y0 + 0.34, letter, ha="center", va="center", fontsize=8.5, weight="bold")

    ax.text(5.95, 1.25, r"Итого $6=3!$ размещений для одного сочетания", ha="center", fontsize=12)
    ax.text(0.55, 0.35, "Если порядок не важен, эти шесть строк считаются одним способом.", fontsize=10.5)
    fig.tight_layout(pad=0.6)
    _save(fig, out_name)


def draw_pascal_triangle(out_name: str = "pascal_triangle_coefficients.png", rows: int = 6) -> None:
    """Треугольник Паскаля с подсветкой правила сложения."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(8.8, 6.0))
    _setup_panel(ax, (-4.8, 4.8), (-0.8, rows + 1.0))

    ax.text(-4.55, rows + 0.55, "Треугольник Паскаля: каждое число — сумма двух верхних", fontsize=14, weight="bold")
    positions: dict[tuple[int, int], tuple[float, float]] = {}
    for n in range(rows + 1):
        y = rows - n
        for k in range(n + 1):
            x = k - n / 2
            positions[(n, k)] = (x, y)
            value = comb(n, k)
            color = C_PANEL
            edge = C_GRAY
            if (n, k) in {(4, 1), (4, 2), (5, 2)}:
                color = "#f8f3dc"
                edge = C_ORANGE if (n, k) == (5, 2) else C_BLUE
            ax.add_patch(Circle((x, y), 0.28, facecolor=color, edgecolor=edge, lw=1.4))
            ax.text(x, y, str(value), ha="center", va="center", fontsize=10.5, weight="bold")

    for start, end in [((4, 1), (5, 2)), ((4, 2), (5, 2))]:
        ax.add_patch(
            FancyArrowPatch(
                positions[start],
                positions[end],
                arrowstyle="-|>",
                mutation_scale=12,
                lw=1.5,
                color=C_ORANGE,
                alpha=0.85,
                shrinkA=12,
                shrinkB=12,
            )
        )
    ax.text(1.65, 0.75, r"$4+6=10$", fontsize=14, color=C_ORANGE, weight="bold")
    ax.text(-4.55, -0.45, r"Строка $n$ даёт коэффициенты разложения $(a+b)^n$.", fontsize=11)
    fig.tight_layout(pad=0.6)
    _save(fig, out_name)


def draw_stars_and_bars(out_name: str = "stars_and_bars.png") -> None:
    """Сочетания с повторениями через звёзды и перегородки."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(9.0, 4.8))
    _setup_panel(ax, (0, 10), (0, 4.8))

    ax.text(0.35, 4.45, "Звёзды и перегородки: распределяем 5 объектов по 3 типам", fontsize=14, weight="bold")
    sequence = ["*", "*", "|", "*", "*", "*", "|"]
    xs = np.linspace(1.55, 8.45, len(sequence))
    y = 2.6
    for x, symbol in zip(xs, sequence):
        if symbol == "*":
            ax.add_patch(Circle((x, y), 0.22, facecolor=C_ORANGE, edgecolor=C_INK, lw=1.0))
        else:
            ax.add_patch(Rectangle((x - 0.035, y - 0.55), 0.07, 1.1, facecolor=C_BLUE, edgecolor=C_BLUE))

    groups = [(xs[0], xs[1], r"$x_1=2$"), (xs[3], xs[5], r"$x_2=3$"), (xs[6] + 0.25, xs[6] + 0.85, r"$x_3=0$")]
    for left, right, label in groups:
        ax.plot([left - 0.33, right + 0.33], [1.82, 1.82], color=C_GREEN, lw=2.0)
        ax.text((left + right) / 2, 1.42, label, ha="center", fontsize=12, color=C_GREEN, weight="bold")

    ax.text(0.6, 3.42, "позиции:", fontsize=11)
    ax.text(4.95, 3.42, r"$k+n-1=5+3-1=7$", ha="center", fontsize=13, bbox=dict(boxstyle="round,pad=0.25", facecolor="#f8f3dc", edgecolor=C_ORANGE))
    ax.text(0.6, 0.55, r"Выбираем места для $5$ звёзд или для $2$ перегородок: $\binom{7}{5}=\binom{7}{2}$.", fontsize=12)
    fig.tight_layout(pad=0.6)
    _save(fig, out_name)


def gif_order_vs_combination(out_name: str = "gif_order_vs_combination.gif", duration: float = 0.34) -> None:
    """GIF: один неупорядоченный выбор раскрывается в k! порядков."""
    _apply_style()
    selected = ["A", "B", "C"]
    colors = {letter: color for letter, color in zip(selected, [C_BLUE, C_ORANGE, C_GREEN])}
    perms = list(itertools.permutations(selected))
    frames = []

    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for step in range(len(perms) + 5):
            visible = min(step + 1, len(perms))
            fig, ax = plt.subplots(figsize=(8.8, 4.8))
            _setup_panel(ax, (0, 10), (0, 4.8))
            ax.text(0.35, 4.45, r"Сочетание превращается в $k!$ размещений, когда появляется порядок", fontsize=13, weight="bold")

            _rounded_box(ax, (0.65, 2.15), 2.2, 1.25, facecolor=C_PANEL, edgecolor=C_GRAY, alpha=0.55)
            for i, letter in enumerate(selected):
                x = 1.15 + i * 0.58
                ax.add_patch(Circle((x, 2.8), 0.2, facecolor=colors[letter], edgecolor=C_INK, lw=1.0, alpha=0.88))
                ax.text(x, 2.8, letter, ha="center", va="center", fontsize=9, weight="bold")
            ax.text(1.75, 2.32, "без порядка", ha="center", fontsize=10.5)
            ax.add_patch(FancyArrowPatch((3.0, 2.75), (4.1, 2.75), arrowstyle="-|>", mutation_scale=14, lw=1.7, color=C_GRAY))

            for idx, perm in enumerate(perms[:visible]):
                x0 = 4.35 + (idx % 3) * 1.65
                y0 = 3.35 - (idx // 3) * 1.0
                edge = C_ORANGE if idx == visible - 1 and step < len(perms) else C_GRAY
                _rounded_box(ax, (x0, y0), 1.28, 0.58, facecolor="#ffffff", edgecolor=edge, alpha=0.78)
                for j, letter in enumerate(perm):
                    x = x0 + 0.25 + j * 0.36
                    ax.add_patch(Circle((x, y0 + 0.29), 0.14, facecolor=colors[letter], edgecolor=C_INK, lw=0.8, alpha=0.88))
                    ax.text(x, y0 + 0.29, letter, ha="center", va="center", fontsize=7.8, weight="bold")

            ax.text(5.98, 0.72, rf"Показано {visible} из $3!=6$ порядков", ha="center", fontsize=12)
            fp = tmp_path / f"order_{step:03d}.png"
            fig.savefig(fp, dpi=140, bbox_inches="tight", facecolor=C_BG)
            plt.close(fig)
            frames.append(imageio.imread(fp))

        for _ in range(4):
            frames.append(frames[-1])

    imageio.mimsave(ASSETS / out_name, frames, duration=duration, loop=0)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_choice_filter()
    draw_pascal_triangle()
    draw_stars_and_bars()
    gif_order_vs_combination()
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
