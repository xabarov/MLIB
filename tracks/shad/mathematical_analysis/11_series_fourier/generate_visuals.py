"""
Точные графики для лекции про ряды и Фурье.

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

try:
    import imageio.v2 as imageio
except ImportError:
    import imageio  # type: ignore

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

C_BG = "#faf9f5"
C_INK = "#141413"
C_GRAY = "#b0aea5"
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


def draw_partial_sums_alternating(out_name: str = "partial_sums_alternating.png") -> None:
    _apply_style()
    n_max = 40
    n = np.arange(1, n_max + 1)
    s = np.cumsum((-1) ** (n + 1) / n)
    fig, ax = plt.subplots(figsize=(8.0, 5.0))
    ax.plot(n, s, "o-", color=C_BLUE, lw=1.8, ms=4, label=r"$S_n=\sum_{k=1}^n\frac{(-1)^{k+1}}{k}$")
    ax.axhline(np.log(2), color=C_ORANGE, ls="--", lw=2, label=r"$\ln 2$")
    ax.set_title("Знакочередующийся ряд: частичные суммы", weight="bold")
    ax.set_xlabel(r"$n$")
    ax.set_ylabel(r"$S_n$")
    ax.legend()
    ax.grid(True)
    _save(fig, out_name)


def draw_integral_test_p_series(out_name: str = "integral_test_p_series.png") -> None:
    _apply_style()
    x = np.linspace(1.0, 8.0, 400)
    p = 1.5
    y_curve = x ** (-p)
    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    ax.plot(x, y_curve, color=C_BLUE, lw=2.3, label=rf"$f(x)=x^{{-{p}}}$")
    ax.fill_between(x, 0, y_curve, alpha=0.2, color=C_BLUE)
    for k in range(1, 8):
        ax.bar(k, k ** (-p), width=0.85, color=C_ORANGE, alpha=0.35, align="center")
    ax.text(4.5, 0.35, r"$\sum \frac{1}{n^p}$ vs $\int_1^\infty x^{-p}\,dx$", fontsize=10, color=C_INK)
    ax.set_title(rf"Интегральный признак ($p={p}>1$)", weight="bold")
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.set_xlim(0.8, 8.2)
    ax.grid(True)
    _save(fig, out_name)


def draw_convergence_disk(out_name: str = "convergence_disk.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    R = 1.0
    disk = Circle((0, 0), R, fill=True, alpha=0.2, color=C_BLUE, lw=2, ec=C_BLUE)
    boundary = Circle((0, 0), R, fill=False, lw=2, color=C_ORANGE, ls="--")
    ax.add_patch(disk)
    ax.add_patch(boundary)
    ax.plot(0, 0, "o", color=C_INK, ms=6)
    ax.plot(R, 0, "o", color=C_ORANGE, ms=7)
    ax.text(0.08, 0.08, r"$x_0$", fontsize=11)
    ax.text(R + 0.05, 0.05, r"$|x-x_0|=R$", fontsize=10, color=C_ORANGE)
    ax.text(-0.9, 0.5, r"$|x-x_0|<R$", fontsize=10, color=C_BLUE)
    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(-1.4, 1.4)
    ax.set_aspect("equal")
    ax.set_title("Круг сходимости степенного ряда", weight="bold")
    ax.axis("off")
    _save(fig, out_name)


def draw_fourier_partial_sums(out_name: str = "fourier_partial_sums.png") -> None:
    _apply_style()
    x = np.linspace(-np.pi, np.pi, 600)
    target = x.copy()

    def partial_sum(xv: np.ndarray, n_terms: int) -> np.ndarray:
        s = np.zeros_like(xv, dtype=float)
        for k in range(1, n_terms + 1):
            s += 2 * ((-1) ** (k + 1)) / k * np.sin(k * xv)
        return s

    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    ax.plot(x, target, color=C_INK, lw=2.5, label=r"$f(x)=x$")
    for n_terms, color in zip([1, 3, 7, 15], [C_GRAY, C_GREEN, C_BLUE, C_ORANGE]):
        ax.plot(x, partial_sum(x, n_terms), lw=1.8, color=color, label=rf"$N={n_terms}$")
    ax.set_title(r"Частичные суммы ряда Фурье для $f(x)=x$", weight="bold")
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$S_N(x)$")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True)
    _save(fig, out_name)


def draw_fourier_buildup_gif(out_name: str = "fourier_buildup.gif") -> None:
    _apply_style()
    x = np.linspace(-np.pi, np.pi, 300)
    target = x
    frames: list[np.ndarray] = []
    terms_list = [1, 2, 3, 5, 9, 15]

    for n_terms in terms_list:
        fig, ax = plt.subplots(figsize=(6.4, 4.0))
        s = np.zeros_like(x)
        for k in range(1, n_terms + 1):
            s += 2 * ((-1) ** (k + 1)) / k * np.sin(k * x)
        ax.plot(x, target, color=C_GRAY, lw=1.5, ls="--")
        ax.plot(x, s, color=C_BLUE, lw=2.2)
        ax.set_title(rf"Ряд Фурье: $N={n_terms}$ гармоник", fontsize=11, weight="bold")
        ax.set_xlim(-np.pi, np.pi)
        ax.set_ylim(-4, 4)
        ax.grid(True, alpha=0.3)
        fig.canvas.draw()
        buf = np.asarray(fig.canvas.buffer_rgba())
        frames.append(buf[:, :, :3].copy())
        plt.close(fig)

    imageio.mimsave(ASSETS / out_name, frames, duration=0.9, loop=0)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_partial_sums_alternating()
    draw_integral_test_p_series()
    draw_convergence_disk()
    draw_fourier_partial_sums()
    draw_fourier_buildup_gif()
    print(f"Saved visuals to {ASSETS}")


if __name__ == "__main__":
    main()
