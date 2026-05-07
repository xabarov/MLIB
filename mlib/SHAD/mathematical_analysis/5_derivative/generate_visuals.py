"""
Точные графики для лекции про производную функции одной переменной.

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


def draw_secant_to_tangent(out_name: str = "secant_to_tangent_x2.png") -> None:
    _apply_style()
    x = np.linspace(-0.2, 3.2, 400)
    y = x**2
    x0 = 1.3
    h = 0.9
    x1 = x0 + h
    y0 = x0**2
    y1 = x1**2
    tangent = 2 * x0 * (x - x0) + y0
    secant = ((y1 - y0) / (x1 - x0)) * (x - x0) + y0

    fig, ax = plt.subplots(figsize=(8.2, 5.1))
    ax.plot(x, y, color=C_BLUE, lw=2.5, label=r"$y=x^2$")
    ax.plot(x, tangent, color=C_GREEN, lw=2.0, label="касательная")
    ax.plot(x, secant, color=C_ORANGE, lw=2.0, ls="--", label="секущая")
    ax.scatter([x0, x1], [y0, y1], s=85, color=C_PURPLE, edgecolors=C_INK, linewidths=1.0, zorder=5)
    ax.text(x0 - 0.08, y0 - 0.45, r"$x_0$", fontsize=10, color=C_INK)
    ax.text(x1 - 0.02, y1 + 0.2, r"$x_0+\Delta x$", fontsize=10, color=C_INK)
    ax.set_title("Секущая и касательная к графику: предел углового коэффициента", weight="bold", color=C_INK)
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.legend(loc="upper left", fontsize=9, framealpha=0.95)
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def draw_abs_one_sided_derivatives(out_name: str = "abs_one_sided_derivatives.png") -> None:
    _apply_style()
    x = np.linspace(-2.0, 2.0, 500)
    y = np.abs(x)

    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    ax.plot(x, y, color=C_BLUE, lw=2.6, label=r"$|x|$")
    ax.plot([-1.5, 0], [1.5, 0], color=C_ORANGE, lw=2.0, ls="--", label="левая касательная")
    ax.plot([0, 1.5], [0, 1.5], color=C_GREEN, lw=2.0, ls="--", label="правая касательная")
    ax.scatter([0], [0], s=90, color=C_PURPLE, edgecolors=C_INK, linewidths=1.0, zorder=5)
    ax.text(-1.45, 1.68, r"$f'_-(0)=-1$", color=C_ORANGE, fontsize=10)
    ax.text(0.45, 1.25, r"$f'_+(0)=1$", color=C_GREEN, fontsize=10)
    ax.set_title("У функции $|x|$ односторонние производные существуют, но не совпадают", weight="bold", color=C_INK)
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.legend(loc="upper center", fontsize=9, ncol=3, framealpha=0.95)
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def draw_linear_approximation_sqrt(out_name: str = "linear_approximation_sqrt.png") -> None:
    _apply_style()
    x = np.linspace(3.3, 4.9, 400)
    y = np.sqrt(x)
    x0 = 4.0
    y0 = np.sqrt(x0)
    tangent = y0 + (1 / (2 * np.sqrt(x0))) * (x - x0)

    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    ax.plot(x, y, color=C_BLUE, lw=2.5, label=r"$y=\sqrt{x}$")
    ax.plot(x, tangent, color=C_ORANGE, lw=2.0, ls="--", label="линейное приближение")
    ax.scatter([x0, 4.1], [np.sqrt(x0), np.sqrt(4.1)], s=75, color=C_PURPLE, edgecolors=C_INK, linewidths=1.0, zorder=5)
    ax.vlines([4.1], ymin=0, ymax=[np.sqrt(4.1)], color=C_GRAY, lw=1.0, ls=":")
    ax.text(4.12, 2.04, r"$x=4.1$", fontsize=10, color=C_INK)
    ax.text(3.46, 2.13, r"$dy \approx \Delta y$", fontsize=10, color=C_ORANGE)
    ax.set_title("Дифференциал как главная линейная часть приращения", weight="bold", color=C_INK)
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.legend(loc="lower right", fontsize=9, framealpha=0.95)
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def draw_motion_tangent_velocity(out_name: str = "motion_tangent_velocity.png") -> None:
    _apply_style()
    t = np.linspace(0, 5, 500)
    s = 0.15 * t**3 - 0.9 * t**2 + 2.4 * t + 0.2
    t0 = 2.0
    s0 = 0.15 * t0**3 - 0.9 * t0**2 + 2.4 * t0 + 0.2
    v0 = 0.45 * t0**2 - 1.8 * t0 + 2.4
    tangent = s0 + v0 * (t - t0)

    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    ax.plot(t, s, color=C_BLUE, lw=2.5, label=r"$s(t)$")
    ax.plot(t, tangent, color=C_GREEN, lw=2.0, ls="--", label="касательная в момент $t_0$")
    ax.scatter([t0], [s0], s=85, color=C_ORANGE, edgecolors=C_INK, linewidths=1.0, zorder=5)
    ax.text(t0 + 0.08, s0 + 0.15, r"наклон = $v(t_0)$", fontsize=10, color=C_GREEN)
    ax.set_title("Механический смысл: производная координаты равна мгновенной скорости", weight="bold", color=C_INK)
    ax.set_xlabel(r"$t$")
    ax.set_ylabel(r"$s(t)$")
    ax.legend(loc="upper right", fontsize=9, framealpha=0.95)
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_secant_to_tangent()
    draw_abs_one_sided_derivatives()
    draw_linear_approximation_sqrt()
    draw_motion_tangent_velocity()
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
