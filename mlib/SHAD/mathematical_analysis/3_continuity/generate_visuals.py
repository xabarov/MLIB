"""
Точные графики для лекции про непрерывность.

Запуск:
    python3 generate_visuals.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

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
            "grid.color": C_GRAY,
            "grid.alpha": 0.3,
            "font.size": 11,
        }
    )


def draw_discontinuity_types(out_name: str = "discontinuity_types.png") -> None:
    _apply_style()
    fig, axes = plt.subplots(1, 3, figsize=(12.8, 4.2))

    # Removable discontinuity
    ax = axes[0]
    x1 = np.linspace(-1.5, 0.95, 260)
    x2 = np.linspace(1.05, 1.7, 120)
    ax.plot(x1, x1 + 1, color=C_BLUE, lw=2.4)
    ax.plot(x2, x2 + 1, color=C_BLUE, lw=2.4)
    ax.scatter([1], [2], s=80, facecolors=C_BG, edgecolors=C_BLUE, linewidths=2, zorder=5)
    ax.scatter([1], [1.25], s=70, color=C_ORANGE, edgecolors=C_INK, linewidths=1.0, zorder=6)
    ax.set_title("Устранимый разрыв", weight="bold", color=C_INK)
    ax.set_xlim(-1.5, 1.7)
    ax.set_ylim(-0.2, 3.0)
    ax.grid(True)

    # Jump discontinuity
    ax = axes[1]
    x_left = np.linspace(-1.7, 0, 240, endpoint=False)
    x_right = np.linspace(0, 1.7, 240)
    ax.plot(x_left, x_left + 1, color=C_PURPLE, lw=2.4)
    ax.plot(x_right, x_right**2 + 0.1, color=C_ORANGE, lw=2.4)
    ax.scatter([0], [1], s=80, facecolors=C_BG, edgecolors=C_PURPLE, linewidths=2, zorder=5)
    ax.scatter([0], [0.1], s=80, color=C_ORANGE, edgecolors=C_INK, linewidths=1.0, zorder=6)
    ax.set_title("Скачок", weight="bold", color=C_INK)
    ax.set_xlim(-1.7, 1.7)
    ax.set_ylim(-0.5, 2.6)
    ax.grid(True)

    # Second kind discontinuity
    ax = axes[2]
    x = np.linspace(-0.35, 0.35, 1000)
    x = x[np.abs(x) > 1e-3]
    y = np.sin(1 / x)
    ax.plot(x, y, color=C_GREEN, lw=1.2)
    ax.axvline(0, color=C_GRAY, lw=1.0, ls="--")
    ax.set_title("Разрыв второго рода", weight="bold", color=C_INK)
    ax.set_xlim(-0.35, 0.35)
    ax.set_ylim(-1.15, 1.15)
    ax.grid(True)

    for ax in axes:
        ax.axhline(0, color=C_GRAY, lw=0.8)
        ax.axvline(0, color=C_GRAY, lw=0.8)
        ax.set_xlabel(r"$x$")
        ax.set_ylabel(r"$y$")

    fig.suptitle("Три характерных типа разрыва функции", fontsize=13, weight="bold", color=C_INK)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def draw_extrema_on_segment(out_name: str = "extrema_on_segment.png") -> None:
    _apply_style()
    x = np.linspace(-1, 2, 500)
    y = x**2
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    ax.plot(x, y, color=C_BLUE, lw=2.5)
    ax.scatter([0, 2], [0, 4], s=95, color=C_ORANGE, edgecolors=C_INK, linewidths=1.0, zorder=5)
    ax.axvspan(-1, 2, color=C_PANEL, alpha=0.22, zorder=0)
    ax.axvline(-1, color=C_GRAY, lw=1.0, ls=":")
    ax.axvline(2, color=C_GRAY, lw=1.0, ls=":")
    ax.text(0.08, 0.22, "минимум", color=C_INK, fontsize=10)
    ax.text(1.75, 4.18, "максимум\nна отрезке", color=C_INK, fontsize=10, ha="center")
    ax.set_title("Непрерывная функция на отрезке достигает минимум и максимум", weight="bold", color=C_INK)
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$f(x)$")
    ax.set_xlim(-1.15, 2.15)
    ax.set_ylim(-0.25, 4.6)
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def draw_intermediate_value(out_name: str = "intermediate_value_horizontal_line.png") -> None:
    _apply_style()
    x = np.linspace(0, 2.6, 500)
    y = 0.55 * (x - 0.35) * (x - 1.4) * (x - 2.2) + 0.85
    c = 0.85

    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    ax.plot(x, y, color=C_BLUE, lw=2.5)
    ax.axhline(c, color=C_ORANGE, lw=2.0, ls="--")

    crossings = []
    for i in range(len(x) - 1):
        if (y[i] - c) == 0 or (y[i] - c) * (y[i + 1] - c) < 0:
            crossings.append(i)
    pts_x = [x[i] for i in crossings[:3]]
    pts_y = [c] * len(pts_x)
    if pts_x:
        ax.scatter(pts_x, pts_y, s=80, color=C_GREEN, edgecolors=C_INK, linewidths=1.0, zorder=5)

    ax.text(2.02, c + 0.08, r"$y=C$", color=C_ORANGE, fontsize=11)
    ax.set_title("Теорема о промежуточном значении: горизонталь пересекает график", weight="bold", color=C_INK)
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$f(x)$")
    ax.set_xlim(0, 2.6)
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_discontinuity_types()
    draw_extrema_on_segment()
    draw_intermediate_value()
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
