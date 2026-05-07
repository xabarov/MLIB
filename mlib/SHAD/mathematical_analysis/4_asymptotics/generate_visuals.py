"""
Точные графики для лекции про O-символику и асимптотические оценки.

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


def draw_big_o_band(out_name: str = "big_o_band.png") -> None:
    _apply_style()
    x = np.linspace(0.2, 6.0, 500)
    f = np.sin(x)
    g = x
    c = 1.0

    fig, ax = plt.subplots(figsize=(8.3, 4.8))
    ax.fill_between(x, -c * g, c * g, color=C_PANEL, alpha=0.75, label=r"$|f(x)| \leq C|g(x)|$")
    ax.plot(x, c * g, color=C_ORANGE, lw=1.8, ls="--")
    ax.plot(x, -c * g, color=C_ORANGE, lw=1.8, ls="--")
    ax.plot(x, f, color=C_BLUE, lw=2.4, label=r"$f(x)=\sin x$")
    ax.plot(x, g, color=C_GREEN, lw=1.8, alpha=0.85, label=r"$g(x)=x$")
    ax.set_title(r"Смысл $f(x)=O(g(x))$: график $f$ остается внутри полосы $\pm Cg$", weight="bold", color=C_INK)
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.set_xlim(0.2, 6.0)
    ax.legend(loc="upper left", fontsize=9, framealpha=0.95)
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def draw_local_equivalents_zero(out_name: str = "local_equivalents_zero.png") -> None:
    _apply_style()
    x = np.linspace(-0.8, 0.8, 500)
    x = x[np.abs(x) > 1e-6]
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.5))

    axes[0].plot(x, np.sin(x), color=C_BLUE, lw=2.4, label=r"$\sin x$")
    axes[0].plot(x, x, color=C_ORANGE, lw=2.0, ls="--", label=r"$x$")
    axes[0].set_title(r"$\sin x \sim x$ при $x \to 0$", weight="bold", color=C_INK)
    axes[0].set_xlabel(r"$x$")
    axes[0].set_ylabel(r"$y$")
    axes[0].legend(loc="upper left", fontsize=9, framealpha=0.95)
    axes[0].grid(True)

    x2 = np.linspace(-0.75, 0.75, 500)
    x2 = x2[x2 > -0.95]
    axes[1].plot(x2, np.log1p(x2), color=C_PURPLE, lw=2.4, label=r"$\ln(1+x)$")
    axes[1].plot(x2, x2, color=C_GREEN, lw=2.0, ls="--", label=r"$x$")
    axes[1].set_title(r"$\ln(1+x) \sim x$ при $x \to 0$", weight="bold", color=C_INK)
    axes[1].set_xlabel(r"$x$")
    axes[1].set_ylabel(r"$y$")
    axes[1].legend(loc="upper left", fontsize=9, framealpha=0.95)
    axes[1].grid(True)

    fig.suptitle("Стандартные локальные эквиваленты около нуля", fontsize=13, weight="bold", color=C_INK)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def draw_growth_scale(out_name: str = "growth_scale_log_power_exp.png") -> None:
    _apply_style()
    x = np.linspace(1.2, 10.0, 500)
    log_x = np.log(x)
    sqrt_x = np.sqrt(x)
    x_lin = x
    exp_x = np.exp(x / 3.0)

    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    ax.plot(x, log_x, color=C_GREEN, lw=2.2, label=r"$\ln x$")
    ax.plot(x, sqrt_x, color=C_ORANGE, lw=2.2, label=r"$x^{1/2}$")
    ax.plot(x, x_lin, color=C_BLUE, lw=2.2, label=r"$x$")
    ax.plot(x, exp_x, color=C_PURPLE, lw=2.2, label=r"$e^{x/3}$")
    ax.set_yscale("log")
    ax.set_title("Типичная шкала роста (логарифмическая шкала по y): логарифм, степень, линейная функция, экспонента", weight="bold", color=C_INK)
    ax.set_xlabel(r"$x$")
    ax.set_ylabel("значение функции")
    ax.legend(loc="upper left", fontsize=9, framealpha=0.95)
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def draw_rationalization_example(out_name: str = "rationalization_root_difference.png") -> None:
    _apply_style()
    x = np.linspace(1.0, 30.0, 500)
    y = np.sqrt(x**2 + x) - x
    fig, ax = plt.subplots(figsize=(8.1, 4.8))
    ax.plot(x, y, color=C_BLUE, lw=2.4, label=r"$\sqrt{x^2+x}-x$")
    ax.axhline(0.5, color=C_ORANGE, lw=2.0, ls="--", label=r"$y=\frac{1}{2}$")
    ax.set_title("Разность близких величин: после рационализации виден предел", weight="bold", color=C_INK)
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.set_xlim(1.0, 30.0)
    ax.legend(loc="lower right", fontsize=9, framealpha=0.95)
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_big_o_band()
    draw_local_equivalents_zero()
    draw_growth_scale()
    draw_rationalization_example()
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
