"""Иллюстрации для лекции про производящие функции и линейные рекурренты."""

from __future__ import annotations

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


def _setup_axis(ax: plt.Axes, xlim: tuple[float, float], ylim: tuple[float, float]) -> None:
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


def _arrow(
    ax: plt.Axes,
    p: tuple[float, float],
    q: tuple[float, float],
    *,
    color: str = C_GRAY,
    lw: float = 1.7,
    rad: float = 0.0,
) -> None:
    ax.add_patch(
        FancyArrowPatch(
            p,
            q,
            arrowstyle="-|>",
            mutation_scale=14,
            lw=lw,
            color=color,
            connectionstyle=f"arc3,rad={rad}",
            shrinkA=4,
            shrinkB=4,
        )
    )


def draw_sequence_to_series(out_name: str = "sequence_to_series.png") -> None:
    """Последовательность как список коэффициентов степенного ряда."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(10.0, 4.7))
    _setup_axis(ax, (0, 10), (0, 4.8))

    ax.text(0.35, 4.45, "Производящая функция упаковывает последовательность в ряд", fontsize=14.5, weight="bold")
    coeffs = [1, 3, 4, 7, 11]
    xs = np.linspace(1.0, 4.6, len(coeffs))
    for i, (x, value) in enumerate(zip(xs, coeffs)):
        _rounded_box(ax, (x - 0.32, 2.75), 0.64, 0.62, facecolor=C_BLUE, edgecolor=C_BLUE, alpha=0.18)
        ax.text(x, 3.06, rf"$a_{i}$", ha="center", va="center", fontsize=12, weight="bold", color=C_BLUE)
        ax.text(x, 2.35, str(value), ha="center", va="center", fontsize=12, color=C_INK)

    ax.text(2.8, 1.88, "коэффициенты", ha="center", fontsize=10.5)
    _arrow(ax, (5.0, 3.0), (6.0, 3.0), color=C_ORANGE, lw=2.0)
    ax.text(5.5, 3.28, "упаковка", ha="center", fontsize=10.5, color=C_ORANGE)
    _rounded_box(ax, (6.25, 2.45), 3.1, 1.05, facecolor="#f8f3dc", edgecolor=C_ORANGE, alpha=0.70)
    ax.text(7.8, 3.08, r"$A(x)=a_0+a_1x+a_2x^2+\cdots$", ha="center", va="center", fontsize=15)
    ax.text(7.8, 2.58, r"$[x^n]A(x)=a_n$", ha="center", va="center", fontsize=13, color=C_GREEN, weight="bold")

    ax.text(0.55, 0.55, "Мы работаем не с одним числом, а сразу со всей последовательностью.", fontsize=11)
    fig.tight_layout(pad=0.6)
    _save(fig, out_name)


def gif_shift_by_x(out_name: str = "gif_shift_by_x.gif", duration: float = 0.28) -> None:
    """GIF: умножение на x сдвигает коэффициенты вправо."""
    _apply_style()
    labels = [r"$a_0$", r"$a_1$", r"$a_2$", r"$a_3$", r"$a_4$"]
    frames = []
    steps = np.linspace(0, 1, 16)

    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for idx, t in enumerate(list(steps) + [1] * 5):
            fig, ax = plt.subplots(figsize=(9.2, 4.3))
            _setup_axis(ax, (0, 9.2), (0, 4.2))
            ax.text(0.35, 3.9, r"Умножение на $x$ сдвигает коэффициенты", fontsize=14, weight="bold")
            ax.text(0.55, 2.95, r"$A(x)$", fontsize=13, weight="bold", color=C_BLUE)
            ax.text(0.55, 1.45, r"$xA(x)$", fontsize=13, weight="bold", color=C_ORANGE)

            for i, label in enumerate(labels):
                x0 = 1.6 + i * 1.05
                _rounded_box(ax, (x0 - 0.33, 2.65), 0.66, 0.55, facecolor=C_BLUE, edgecolor=C_BLUE, alpha=0.18)
                ax.text(x0, 2.93, label, ha="center", va="center", fontsize=11)
                ax.text(x0, 2.38, rf"$x^{i}$", ha="center", va="center", fontsize=9.5, color=C_GRAY)

                x1 = x0 + 1.05 * t
                _rounded_box(ax, (x1 - 0.33, 1.15), 0.66, 0.55, facecolor=C_ORANGE, edgecolor=C_ORANGE, alpha=0.18)
                ax.text(x1, 1.43, label, ha="center", va="center", fontsize=11)
                ax.text(x1, 0.88, rf"$x^{i + 1}$", ha="center", va="center", fontsize=9.5, color=C_GRAY)

            ax.text(6.55, 1.92, r"коэффициент при $x^n$ стал $a_{n-1}$", fontsize=11, color=C_GREEN)
            fp = tmp_path / f"shift_{idx:03d}.png"
            fig.savefig(fp, dpi=140, bbox_inches="tight", facecolor=C_BG)
            plt.close(fig)
            frames.append(imageio.imread(fp))

    imageio.mimsave(ASSETS / out_name, frames, duration=duration, loop=0)


def draw_convolution(out_name: str = "convolution_coefficients.png") -> None:
    """Свёртка коэффициентов при произведении производящих функций."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(10.0, 5.0))
    _setup_axis(ax, (0, 10), (0, 5.1))

    ax.text(0.35, 4.75, r"Коэффициент произведения — это свёртка", fontsize=14.5, weight="bold")
    n = 4
    pairs = [(k, n - k) for k in range(n + 1)]
    xs = np.linspace(1.1, 8.9, len(pairs))
    for x, (k, j) in zip(xs, pairs):
        _rounded_box(ax, (x - 0.52, 2.75), 1.04, 0.72, facecolor=C_BLUE, edgecolor=C_BLUE, alpha=0.16)
        _rounded_box(ax, (x - 0.52, 1.75), 1.04, 0.72, facecolor=C_ORANGE, edgecolor=C_ORANGE, alpha=0.16)
        ax.text(x, 3.11, rf"$a_{k}x^{k}$", ha="center", va="center", fontsize=11)
        ax.text(x, 2.11, rf"$b_{j}x^{j}$", ha="center", va="center", fontsize=11)
        _arrow(ax, (x, 1.65), (x, 1.25), color=C_GRAY, lw=1.2)
        ax.text(x, 0.95, rf"$a_{k}b_{j}$", ha="center", va="center", fontsize=10.5)

    ax.plot([0.75, 9.25], [0.55, 0.55], color=C_GRAY, lw=1.0)
    ax.text(5.0, 0.16, r"$[x^4]A(x)B(x)=a_0b_4+a_1b_3+a_2b_2+a_3b_1+a_4b_0$", ha="center", fontsize=13, color=C_GREEN, weight="bold")
    ax.text(0.7, 4.0, r"Берём пары степеней, сумма которых равна $4$.", fontsize=11)
    fig.tight_layout(pad=0.6)
    _save(fig, out_name)


def draw_fibonacci_recurrence(out_name: str = "fibonacci_recurrence_flow.png") -> None:
    """Числа Фибоначчи: каждый следующий член собирается из двух предыдущих."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(10.0, 4.8))
    _setup_axis(ax, (0, 10), (0, 4.8))

    fib = [0, 1, 1, 2, 3, 5, 8]
    xs = np.linspace(0.9, 9.1, len(fib))
    y = 2.35
    for i, (x, value) in enumerate(zip(xs, fib)):
        color = "#f8f3dc" if i >= 2 else C_PANEL
        _rounded_box(ax, (x - 0.36, y - 0.34), 0.72, 0.68, facecolor=color, edgecolor=C_ORANGE if i >= 2 else C_GRAY, alpha=0.8)
        ax.text(x, y + 0.06, str(value), ha="center", va="center", fontsize=13, weight="bold")
        ax.text(x, y - 0.58, rf"$F_{i}$", ha="center", va="center", fontsize=10, color=C_GRAY)

    for i in range(2, len(fib)):
        _arrow(ax, (xs[i - 2], y + 0.42), (xs[i], y + 0.42), color=C_BLUE, lw=1.2, rad=0.24)
        _arrow(ax, (xs[i - 1], y + 0.40), (xs[i], y + 0.40), color=C_GREEN, lw=1.2, rad=0.16)

    ax.text(0.35, 4.35, "Рекуррент: новый член зависит от предыдущих", fontsize=14.5, weight="bold")
    ax.text(3.7, 3.52, r"$F_n=F_{n-1}+F_{n-2}$", fontsize=16, bbox=dict(boxstyle="round,pad=0.28", facecolor="#f8f3dc", edgecolor=C_ORANGE))
    ax.text(0.65, 0.55, r"Производящая функция превращает такие сдвиги в алгебраическое уравнение для $F(x)$.", fontsize=11)
    fig.tight_layout(pad=0.6)
    _save(fig, out_name)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_sequence_to_series()
    gif_shift_by_x()
    draw_convolution()
    draw_fibonacci_recurrence()
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
