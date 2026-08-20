"""
Точные схемы для лекции про метрические и нормированные пространства.

Запуск:
    python3 generate_visuals.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle

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
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def draw_epsilon_ball_R2(out_name: str = "epsilon_ball_R2.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(7.0, 6.2))
    x0, y0 = 1.2, 0.8
    eps = 1.0
    open_ball = Circle((x0, y0), eps, fill=False, lw=2.4, color=C_BLUE, ls="-")
    closed_ball = Circle((x0, y0), eps, fill=False, lw=1.6, color=C_ORANGE, ls="--")
    ax.add_patch(open_ball)
    ax.add_patch(closed_ball)
    ax.plot(x0, y0, "o", color=C_INK, ms=8)
    ax.annotate(
        r"$B_\varepsilon(x_0)$",
        xy=(x0 + eps * 0.55, y0 + eps * 0.55),
        fontsize=11,
        color=C_BLUE,
    )
    ax.annotate(
        r"$\overline{B}_\varepsilon(x_0)$",
        xy=(x0 - eps * 0.95, y0 - eps * 0.35),
        fontsize=10,
        color=C_ORANGE,
    )
    ax.annotate(r"$x_0$", xy=(x0 + 0.08, y0 + 0.08), fontsize=11)
    ax.set_xlim(-0.5, 3.5)
    ax.set_ylim(-0.8, 2.8)
    ax.set_aspect("equal")
    ax.set_title("Открытый и замкнутый шары в $\mathbb{R}^2$", weight="bold")
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.grid(True)
    _save(fig, out_name)


def draw_continuity_metric_balls(out_name: str = "continuity_metric_balls.png") -> None:
    _apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.2))

    for ax, title in zip(axes, [r"Пространство $X$", r"Пространство $Y$"]):
        ax.set_xlim(0, 4)
        ax.set_ylim(0, 3)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(title, fontsize=11, weight="bold")

    x0, y0 = 2.0, 1.5
    delta = 0.55
    axes[0].add_patch(Circle((x0, y0), delta, fill=True, alpha=0.2, color=C_BLUE, lw=2, ec=C_BLUE))
    axes[0].plot(x0, y0, "o", color=C_INK, ms=7)
    axes[0].text(0.3, 2.6, r"$B_\delta(x_0)\subset X$", fontsize=10, color=C_INK)
    axes[0].text(x0 + 0.05, y0 + 0.05, r"$x_0$", fontsize=10)

    y0p, y0q = 2.0, 1.4
    eps = 0.7
    axes[1].add_patch(Circle((y0p, y0q), eps, fill=True, alpha=0.18, color=C_ORANGE, lw=2, ec=C_ORANGE))
    axes[1].plot(y0p, y0q, "o", color=C_INK, ms=7)
    axes[1].text(0.25, 2.6, r"$B_\varepsilon(f(x_0))\subset Y$", fontsize=10, color=C_INK)
    axes[1].text(y0p + 0.05, y0q + 0.05, r"$f(x_0)$", fontsize=10)

    fig.suptitle(r"Непрерывность: $f(B_\delta(x_0))\subset B_\varepsilon(f(x_0))$", fontsize=12, weight="bold", y=1.02)
    _save(fig, out_name)


def draw_sup_norm_functions(out_name: str = "sup_norm_functions.png") -> None:
    _apply_style()
    x = np.linspace(0, 2 * np.pi, 400)
    f = np.sin(x)
    g = np.clip(0.55 * x - 0.2, -1.2, 1.2)
    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    ax.plot(x, f, color=C_BLUE, lw=2.3, label=r"$f$")
    ax.plot(x, g, color=C_GREEN, lw=2.3, label=r"$g$")
    upper = np.maximum(f, g)
    lower = np.minimum(f, g)
    ax.fill_between(x, lower, upper, color=C_ORANGE, alpha=0.25)
    ax.text(2.0, 0.95, r"$\|f-g\|_\infty=\max|f-g|$", fontsize=11, color=C_PURPLE)
    ax.set_title(r"Равномерная метрика на $C[a,b]$", weight="bold")
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.legend(loc="upper right")
    ax.grid(True)
    _save(fig, out_name)


def draw_bounded_vs_unbounded(out_name: str = "bounded_vs_unbounded.png") -> None:
    _apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.5))

    circ = Circle((0, 0), 1.2, fill=True, alpha=0.2, color=C_BLUE, lw=2, ec=C_BLUE)
    axes[0].add_patch(circ)
    axes[0].plot(0.3, 0.4, "o", color=C_ORANGE, ms=6)
    axes[0].plot(-0.5, -0.2, "o", color=C_ORANGE, ms=6)
    axes[0].set_xlim(-2, 2)
    axes[0].set_ylim(-2, 2)
    axes[0].set_aspect("equal")
    axes[0].set_title("Ограниченное множество", weight="bold")
    axes[0].text(-1.7, 1.6, r"$A\subset B_R(0)$", fontsize=10)

    t = np.linspace(0.0, 2.5, 200)
    axes[1].plot(t, np.power(t, 1.15), color=C_ORANGE, lw=2.3)
    axes[1].set_xlim(-0.5, 2.8)
    axes[1].set_ylim(-0.5, 3.5)
    axes[1].set_title("Неограниченное множество", weight="bold")
    axes[1].text(0.3, 2.8, r"$y\to\infty$", fontsize=10, color=C_INK)
    axes[1].grid(True)

    _save(fig, out_name)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_epsilon_ball_R2()
    draw_continuity_metric_balls()
    draw_sup_norm_functions()
    draw_bounded_vs_unbounded()
    print(f"Saved visuals to {ASSETS}")


if __name__ == "__main__":
    main()
