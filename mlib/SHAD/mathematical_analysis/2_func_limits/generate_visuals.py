"""
Графики и анимации для лекции SHAD/mathematical_analysis/2_func_limits (пределы функций).

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
E_CONST = math.e


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


def draw_epsilon_delta_window(out_name: str = "epsilon_delta_window.png"):
    """Иллюстрация к определению Коши: $f(x)=\\frac{\\sin 2x}{2x}\\to 1$ при $x\\to 0$."""
    _apply_style()
    L, eps, delta = 1.0, 0.18, 0.42
    x = np.linspace(-0.75, 0.75, 600)
    x = x[np.abs(x) > 1e-9]
    y = np.sin(2 * x) / (2 * x)
    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    ax.set_facecolor(C_BG)
    fig.patch.set_facecolor(C_BG)
    ax.axhspan(L - eps, L + eps, xmin=0.08, xmax=0.92, facecolor=C_BLUE, alpha=0.18, zorder=0)
    ax.axhline(L + eps, color=C_BLUE, lw=1.4, ls="--", alpha=0.85)
    ax.axhline(L - eps, color=C_BLUE, lw=1.4, ls="--", alpha=0.85)
    ax.axvline(-delta, color=C_ORANGE, lw=1.4, ls=":", alpha=0.9)
    ax.axvline(delta, color=C_ORANGE, lw=1.4, ls=":", alpha=0.9)
    ax.fill_betweenx([L - eps, L + eps], -delta, delta, color=C_PANEL, alpha=0.45, zorder=1)
    ax.plot(x, y, color=C_INK, lw=2.4, zorder=3)
    ax.scatter([0], [L], s=120, facecolors=C_GREEN, edgecolors=C_INK, linewidths=1.4, zorder=5)
    ax.set_xlim(-0.78, 0.78)
    ax.set_ylim(0.55, 1.22)
    ax.set_xlabel(r"$x$", fontsize=12, color=C_INK)
    ax.set_ylabel(r"$f(x)$", fontsize=12, color=C_INK)
    ax.set_title(
        r"Идея $\varepsilon$–$\delta$: полоса $L\pm\varepsilon$ и окрестность $0\pm\delta$ "
        r"($f(x)=\frac{\sin 2x}{2x}$, дополнение в $0$)",
        fontsize=11,
        weight="bold",
        color=C_INK,
    )
    ax.text(delta + 0.03, 0.62, r"$\delta$", fontsize=11, color=C_ORANGE)
    ax.text(-0.12, L + eps + 0.03, r"$\varepsilon$", fontsize=11, color=C_BLUE)
    ax.grid(True, alpha=0.35)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def draw_sandwich_xsin(out_name: str = "sandwich_xsin_1overx.png"):
    """$-|x|\\le x\\sin(1/x)\\le |x|$ при $x\\ne 0$."""
    _apply_style()
    x = np.linspace(-0.45, 0.45, 800)
    x = x[np.abs(x) > 1e-6]
    lo = -np.abs(x)
    hi = np.abs(x)
    mid = x * np.sin(1 / x)
    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    ax.set_facecolor(C_BG)
    fig.patch.set_facecolor(C_BG)
    ax.plot(x, hi, color=C_BLUE, lw=1.6, label=r"$|x|$")
    ax.plot(x, lo, color=C_BLUE, lw=1.6, ls="--", label=r"$-|x|$")
    ax.plot(x, mid, color=C_ORANGE, lw=1.3, label=r"$x\sin\frac{1}{x}$")
    ax.axhline(0, color=C_GRAY, lw=0.9)
    ax.axvline(0, color=C_GRAY, lw=0.9, alpha=0.5)
    ax.set_xlabel(r"$x$", fontsize=12, color=C_INK)
    ax.set_ylabel(r"$y$", fontsize=11, color=C_INK)
    ax.set_title(
        r"Зажатость $x\sin\frac{1}{x}$ между $-|x|$ и $|x|$",
        fontsize=12,
        weight="bold",
        color=C_INK,
    )
    ax.legend(loc="upper right", fontsize=9, framealpha=0.95)
    ax.grid(True, alpha=0.35)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def draw_first_limit(out_name: str = "first_limit_sin_over_x.png"):
    """$\\frac{\\sin x}{x}$ при малых $x$ и уровень $y=1$."""
    _apply_style()
    x = np.linspace(-6, 6, 500)
    x = x[np.abs(x) > 1e-6]
    y = np.sin(x) / x
    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    ax.set_facecolor(C_BG)
    fig.patch.set_facecolor(C_BG)
    ax.plot(x, y, color=C_INK, lw=2.2, label=r"$\frac{\sin x}{x}$")
    ax.axhline(1, color=C_GREEN, lw=1.8, ls="--", label=r"$y=1$")
    ax.axhline(0, color=C_GRAY, lw=0.8)
    ax.axvline(0, color=C_GRAY, lw=0.8, alpha=0.5)
    ax.scatter([0], [1], s=100, c=C_ORANGE, edgecolors=C_INK, zorder=5, label=r"дополнение $(0,1)$")
    ax.set_xlim(-6.2, 6.2)
    ax.set_ylim(-0.45, 1.15)
    ax.set_xlabel(r"$x$", fontsize=12, color=C_INK)
    ax.set_ylabel(r"$y$", fontsize=12, color=C_INK)
    ax.set_title(r"Первый замечательный предел: $\frac{\sin x}{x}\to 1$ при $x\to 0$", fontsize=12, weight="bold", color=C_INK)
    ax.legend(loc="lower center", fontsize=9, ncol=3, framealpha=0.95)
    ax.grid(True, alpha=0.35)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def draw_limit_rational_at_infinity(out_name: str = "limit_rational_at_infinity.png"):
    """Пример из лекции: $(2x+1)/x \\to 2$ при $x\\to+\\infty$."""
    _apply_style()
    x = np.linspace(0.4, 12, 300)
    y = (2 * x + 1) / x
    fig, ax = plt.subplots(figsize=(8.2, 4.2))
    ax.set_facecolor(C_BG)
    fig.patch.set_facecolor(C_BG)
    ax.plot(x, y, color=C_ORANGE, lw=2.4, label=r"$\frac{2x+1}{x}$")
    ax.axhline(2, color=C_BLUE, lw=1.8, ls="--", label=r"$y=2$")
    ax.set_xlabel(r"$x$", fontsize=12, color=C_INK)
    ax.set_ylabel(r"$f(x)$", fontsize=12, color=C_INK)
    ax.set_title(r"Предел на бесконечности: $\frac{2x+1}{x}\to 2$", fontsize=12, weight="bold", color=C_INK)
    ax.legend(loc="upper right", fontsize=10)
    ax.grid(True, alpha=0.35)
    ax.set_xlim(0, 12.5)
    ax.set_ylim(1.85, 2.65)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def gif_second_limit_sequence(out_name: str = "gif_second_limit_sequence.gif", duration: float = 0.2):
    """Дискретная аппроксимация: $a_n=(1+1/n)^n \\to e$."""
    _apply_style()
    n_max = 42
    frames = []
    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for k in range(3, n_max + 1):
            n = np.arange(1, k + 1)
            vals = (1 + 1.0 / n) ** n
            fig, ax = plt.subplots(figsize=(7.6, 4.4))
            ax.set_facecolor(C_BG)
            fig.patch.set_facecolor(C_BG)
            ax.plot(n, vals, "o-", color=C_INK, ms=5, lw=1.4)
            ax.axhline(E_CONST, color=C_GREEN, lw=2.0, ls="--", label=r"$e$")
            ax.set_xlim(0.5, n_max + 0.5)
            lo, hi = 2.0, min(float(vals.max()) * 1.02, E_CONST * 1.02)
            ax.set_ylim(lo, hi)
            ax.set_xlabel(r"$n$", fontsize=11, color=C_INK)
            ax.set_ylabel(r"$\left(1+\frac{1}{n}\right)^n$", fontsize=11, color=C_INK)
            ax.set_title(
                fr"Второй замечательный предел (дискретная модель), первые {k} членов",
                fontsize=11,
                weight="bold",
                color=C_INK,
            )
            ax.legend(loc="lower right", fontsize=9)
            ax.grid(True, alpha=0.35)
            fig.subplots_adjust(left=0.12, right=0.96, top=0.88, bottom=0.14)
            fp = tmp_path / f"sl_{k:03d}.png"
            fig.savefig(fp, dpi=130, facecolor=C_BG)
            plt.close(fig)
            frames.append(imageio.imread(fp))
        for _ in range(8):
            frames.append(frames[-1])
    imageio.mimsave(ASSETS / out_name, frames, duration=duration, loop=0)


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_epsilon_delta_window()
    draw_sandwich_xsin()
    draw_first_limit()
    draw_limit_rational_at_infinity()
    gif_second_limit_sequence()
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
