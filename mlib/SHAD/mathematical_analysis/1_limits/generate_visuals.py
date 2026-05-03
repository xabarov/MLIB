"""
Графики и анимации для лекции SHAD/mathematical_analysis/1_limits (пределы последовательностей).

Палитра: SHAD/lecture_visual_generation/lecture_visual_design_system.md
"""

from __future__ import annotations

import math
from pathlib import Path
from tempfile import TemporaryDirectory

import imageio.v2 as imageio
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


def _apply_style():
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
            "grid.alpha": 0.35,
            "font.size": 11,
        }
    )


def draw_epsilon_neighborhood(out_name: str = "epsilon_neighborhood_sequence.png", eps: float = 0.14):
    """Геометрия §2–3: $a=0$, полоса $(-\\varepsilon,\\varepsilon)$ и точки $1/n$ на прямой."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(9.2, 3.8))
    ax.set_facecolor(C_BG)
    fig.patch.set_facecolor(C_BG)
    ax.axhline(0, color=C_INK, lw=1.8, zorder=1)
    x0, x1 = -eps, eps
    ax.fill_between([x0, x1], [-0.06, -0.06], [0.06, 0.06], color=C_BLUE, alpha=0.35, zorder=0)
    ax.plot([x0, x1], [0, 0], color=C_BLUE, lw=5, solid_capstyle="butt", alpha=0.5, zorder=0)
    ns = np.arange(1, 14)
    vals = 1.0 / ns
    ax.scatter(vals, np.zeros_like(vals), s=95, c=C_ORANGE, edgecolors=C_INK, linewidths=1.0, zorder=4)
    for n, v in zip(ns[:5], vals[:5]):
        ax.text(v, 0.11, rf"$\frac{{1}}{{{n}}}$", ha="center", fontsize=9, color=C_INK)
    ax.scatter([0], [0], s=140, c=C_GREEN, edgecolors=C_INK, linewidths=1.2, zorder=5)
    ax.text(0, -0.16, r"$0$", ha="center", fontsize=12, color=C_INK, weight="bold")
    ax.text(eps + 0.02, 0.11, rf"$\varepsilon$", fontsize=11, color=C_BLUE)
    ax.text(-eps - 0.02, 0.11, rf"$-\varepsilon$", fontsize=11, color=C_BLUE, ha="right")
    ax.set_xlim(-0.35, 1.08)
    ax.set_ylim(-0.28, 0.28)
    ax.set_title(
        r"$\varepsilon$-окрестность нуля и члены $a_n=\frac{1}{n}$ на действительной прямой",
        fontsize=12,
        weight="bold",
        color=C_INK,
        pad=10,
    )
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def draw_sequences_overview(out_name: str = "sequences_overview.png"):
    """Сходимость $1/n$, $(n+1)/n$ и расходящийся пример $(-1)^n$."""
    _apply_style()
    n_max = 22
    n = np.arange(1, n_max + 1)
    fig, axes = plt.subplots(3, 1, figsize=(8.4, 7.6), sharex=True)
    fig.patch.set_facecolor(C_BG)
    for ax in axes:
        ax.set_facecolor(C_BG)
    axes[0].stem(n, 1.0 / n, linefmt=C_ORANGE, markerfmt="o", basefmt=" ")
    axes[0].axhline(0, color=C_GRAY, lw=1.0, ls="--")
    axes[0].set_ylabel(r"$a_n$", fontsize=11, color=C_INK)
    axes[0].set_title(r"$a_n=\frac{1}{n}\to 0$", fontsize=12, weight="bold", loc="left", color=C_INK)
    axes[0].grid(True, axis="y", alpha=0.4)
    axes[1].stem(n, (n + 1.0) / n, linefmt=C_BLUE, markerfmt="o", basefmt=" ")
    axes[1].axhline(1, color=C_GRAY, lw=1.0, ls="--")
    axes[1].set_ylabel(r"$a_n$", fontsize=11, color=C_INK)
    axes[1].set_title(r"$a_n=\frac{n+1}{n}\to 1$", fontsize=12, weight="bold", loc="left", color=C_INK)
    axes[1].grid(True, axis="y", alpha=0.4)
    alt = (-1.0) ** n
    axes[2].stem(n, alt, linefmt=C_GREEN, markerfmt="o", basefmt=" ")
    axes[2].axhline(0, color=C_GRAY, lw=0.8, ls="-", alpha=0.5)
    axes[2].set_ylabel(r"$a_n$", fontsize=11, color=C_INK)
    axes[2].set_xlabel(r"$n$", fontsize=12, color=C_INK)
    axes[2].set_title(r"$a_n=(-1)^n$ (предела нет)", fontsize=12, weight="bold", loc="left", color=C_INK)
    axes[2].set_yticks([-1, 0, 1])
    axes[2].grid(True, axis="y", alpha=0.4)
    fig.suptitle("Три типовых последовательности", fontsize=13, weight="bold", y=1.01, color=C_INK)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def draw_sandwich_sin(out_name: str = "sandwich_sin_over_n.png", n_max: int = 36):
    """Теорема о зажатой: $-1/n \\le \\sin n/n \\le 1/n$."""
    _apply_style()
    n = np.arange(1, n_max + 1)
    low = -1.0 / n
    high = 1.0 / n
    mid = np.sin(n) / n
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    ax.set_facecolor(C_BG)
    fig.patch.set_facecolor(C_BG)
    ax.fill_between(n, low, high, color=C_PANEL, alpha=0.85, label=r"полоса между $\pm 1/n$")
    ax.plot(n, high, color=C_BLUE, lw=1.8, label=r"$1/n$")
    ax.plot(n, low, color=C_BLUE, lw=1.8, ls="--", label=r"$-1/n$")
    ax.plot(n, mid, "o-", color=C_ORANGE, ms=4, lw=1.1, label=r"$\sin n/n$")
    ax.set_xlabel(r"$n$", fontsize=12, color=C_INK)
    ax.set_ylabel(r"значение", fontsize=11, color=C_INK)
    ax.set_title(
        r"Зажатость $\frac{\sin n}{n}$ между $-\frac{1}{n}$ и $\frac{1}{n}$",
        fontsize=12,
        weight="bold",
        color=C_INK,
    )
    ax.legend(loc="upper right", framealpha=0.95, fontsize=9)
    ax.grid(True, alpha=0.35)
    ax.set_xlim(0.5, n_max + 0.5)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def gif_stem_one_over_n(out_name: str = "gif_stem_one_over_n.gif", duration: float = 0.22):
    """Появление всё большего числа точек $a_n=1/n$ при росте $n$ (к $0$)."""
    _apply_style()
    n_max = 24
    frames = []
    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for k in range(2, n_max + 1):
            fig, ax = plt.subplots(figsize=(7.4, 4.2))
            ax.set_facecolor(C_BG)
            fig.patch.set_facecolor(C_BG)
            n = np.arange(1, k + 1)
            ax.stem(n, 1.0 / n, linefmt=C_ORANGE, markerfmt="o", basefmt=" ")
            ax.axhline(0, color=C_GRAY, lw=1.0, ls="--")
            ax.set_xlim(0.5, n_max + 0.5)
            ax.set_ylim(-0.05, 1.08)
            ax.set_xlabel(r"$n$", fontsize=11, color=C_INK)
            ax.set_ylabel(r"$a_n$", fontsize=11, color=C_INK)
            ax.set_title(
                fr"$a_n=\frac{{1}}{{n}}$, первые {k} членов",
                fontsize=12,
                weight="bold",
                color=C_INK,
            )
            ax.grid(True, axis="y", alpha=0.4)
            fig.tight_layout()
            fp = tmp_path / f"f_{k:03d}.png"
            fig.savefig(fp, dpi=130, bbox_inches="tight", facecolor=C_BG)
            plt.close(fig)
            frames.append(imageio.imread(fp))
        for _ in range(6):
            frames.append(frames[-1])
    imageio.mimsave(ASSETS / out_name, frames, duration=duration, loop=0)


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_epsilon_neighborhood()
    draw_sequences_overview()
    draw_sandwich_sin()
    gif_stem_one_over_n()
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
