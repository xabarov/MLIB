"""Точные схемы для лекции про базовые понятия теории вероятностей."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
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


def _save(fig: plt.Figure, out_name: str) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def draw_sample_space_events(out_name: str = "sample_space_events.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(8.0, 5.0))
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-3.0, 3.0)
    ax.set_ylim(-2.0, 2.0)

    omega = Circle((0, 0), 1.75, facecolor="#f2efe6", edgecolor=C_INK, lw=2.0)
    event_a = Circle((-0.45, 0), 1.05, facecolor=C_BLUE, edgecolor=C_BLUE, alpha=0.35, lw=2.0)
    event_b = Circle((0.45, 0), 1.05, facecolor=C_ORANGE, edgecolor=C_ORANGE, alpha=0.35, lw=2.0)
    ax.add_patch(omega)
    ax.add_patch(event_a)
    ax.add_patch(event_b)

    points = [(-1.25, 0.85), (-0.85, -0.55), (-0.25, 0.25), (0.25, -0.18), (0.85, 0.48), (1.2, -0.72)]
    labels = ["1", "2", "3", "4", "5", "6"]
    for (x, y), label in zip(points, labels):
        ax.scatter([x], [y], s=55, color=C_INK, zorder=5)
        ax.text(x + 0.08, y + 0.08, label, fontsize=10, color=C_INK)

    ax.text(0, 1.88, r"$\Omega$", fontsize=16, weight="bold", ha="center")
    ax.text(-1.25, -1.55, r"$A$", fontsize=15, color=C_BLUE, weight="bold")
    ax.text(1.25, -1.55, r"$B$", fontsize=15, color=C_ORANGE, weight="bold")
    ax.text(0, -1.88, "События — это подмножества пространства исходов", ha="center", fontsize=12)
    ax.set_title("Пространство исходов и события", fontsize=13, weight="bold")
    _save(fig, out_name)


def draw_ordered_unordered_samples(out_name: str = "ordered_unordered_samples.png") -> None:
    _apply_style()
    fig, axes = plt.subplots(2, 2, figsize=(10.5, 7.0))
    titles = [
        "порядок важен\nбез повторений",
        "порядок не важен\nбез повторений",
        "порядок важен\nс повторениями",
        "порядок не важен\nс повторениями",
    ]
    formulas = [
        r"$A_n^k=\frac{n!}{(n-k)!}$",
        r"$C_n^k=\binom{n}{k}$",
        r"$n^k$",
        r"$\binom{n+k-1}{k}$",
    ]
    examples = [
        ["A", "C", "B"],
        ["A", "B", "C"],
        ["A", "A", "C"],
        ["A", "A", "C"],
    ]
    colors = [C_BLUE, C_GREEN, C_ORANGE]

    for ax, title, formula, example in zip(axes.flat, titles, formulas, examples):
        ax.axis("off")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.add_patch(Rectangle((0.04, 0.12), 0.92, 0.74, facecolor="#f2efe6", edgecolor=C_GRAY, lw=1.5))
        ax.text(0.5, 0.91, title, ha="center", va="top", fontsize=12, weight="bold")
        order_matters = title.startswith("порядок важен")
        for i, token in enumerate(example):
            x = 0.24 + i * 0.26
            ax.add_patch(Circle((x, 0.53), 0.095, facecolor=colors[i], edgecolor=C_INK, lw=1.2, alpha=0.8))
            ax.text(x, 0.53, token, ha="center", va="center", fontsize=12, weight="bold", color="white")
            if i < 2 and order_matters:
                ax.annotate("", xy=(x + 0.18, 0.53), xytext=(x + 0.09, 0.53), arrowprops=dict(arrowstyle="->", lw=1.5, color=C_INK))
        ax.text(0.5, 0.24, formula, ha="center", va="center", fontsize=15, color=C_PURPLE)

    fig.suptitle("Четыре режима выбора", fontsize=14, weight="bold")
    _save(fig, out_name)


def draw_geometric_probability_area(out_name: str = "geometric_probability_area.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(6.4, 6.0))
    ax.set_aspect("equal")
    ax.set_xlim(-0.08, 1.08)
    ax.set_ylim(-0.08, 1.08)
    ax.grid(True)

    ax.add_patch(Rectangle((0, 0), 1, 1, facecolor="#f2efe6", edgecolor=C_INK, lw=2.0))
    triangle = plt.Polygon([[0, 0], [1, 0], [0, 1]], closed=True, facecolor=C_BLUE, alpha=0.33, edgecolor=C_BLUE, lw=2.0)
    ax.add_patch(triangle)
    ax.plot([0, 1], [1, 0], color=C_ORANGE, lw=2.4)
    ax.text(0.52, 0.56, r"$x+y=1$", color=C_ORANGE, fontsize=12, rotation=-38)
    ax.text(0.24, 0.22, r"$A$", color=C_BLUE, fontsize=18, weight="bold")
    ax.text(0.66, 0.78, r"$\Omega=[0,1]^2$", color=C_INK, fontsize=11)
    ax.text(0.07, 0.06, r"$P(A)=area(A)/area(\Omega)=1/2$", fontsize=12, color=C_PURPLE)
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.set_title("Геометрическая вероятность в единичном квадрате", fontsize=13, weight="bold")
    _save(fig, out_name)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_sample_space_events()
    draw_ordered_unordered_samples()
    draw_geometric_probability_area()
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
