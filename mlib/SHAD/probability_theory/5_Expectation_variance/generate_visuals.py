"""Точные схемы для лекции про МО, дисперсию, ковариацию, условное МО."""

from __future__ import annotations

from pathlib import Path
import math

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

C_BG    = "#faf9f5"
C_INK   = "#141413"
C_GRAY  = "#b0aea5"
C_PANEL = "#e8e6dc"
C_ORANGE = "#d97757"
C_BLUE   = "#6a9bcc"
C_GREEN  = "#788c5d"


def _apply_style() -> None:
    plt.rcParams.update({
        "figure.facecolor": C_BG,
        "axes.facecolor":   C_BG,
        "axes.edgecolor":   C_GRAY,
        "axes.labelcolor":  C_INK,
        "text.color":       C_INK,
        "xtick.color":      C_INK,
        "ytick.color":      C_INK,
        "grid.color":       C_GRAY,
        "grid.alpha":       0.3,
        "font.size":        11,
    })


def _save(fig, name: str) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS / name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def _norm_pdf(x: np.ndarray, mu: float, sigma: float) -> np.ndarray:
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2) / (sigma * math.sqrt(2 * math.pi))


def draw_variance_spread(out_name: str = "variance_spread.png") -> None:
    """Нормальные распределения N(0, σ²) для σ=0.5, 1, 2 на одном графике."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(9, 4.5))

    x = np.linspace(-5.5, 5.5, 800)
    configs = [
        (0.5, C_GREEN,  r"$\sigma = 0.5$ (узкое)"),
        (1.0, C_BLUE,   r"$\sigma = 1.0$"),
        (2.0, C_ORANGE, r"$\sigma = 2.0$ (широкое)"),
    ]
    for sigma, color, label in configs:
        y = _norm_pdf(x, 0.0, sigma)
        ax.plot(x, y, color=color, lw=2.5, label=label)
        ax.fill_between(x, y, alpha=0.10, color=color)

    # Вертикальная линия в точке E[X]=0
    ax.axvline(0, color=C_INK, lw=1.4, ls="--", alpha=0.6)
    ax.text(0.07, ax.get_ylim()[1] * 0.97, r"$\mathbb{E}[X]=0$",
            color=C_INK, fontsize=10, va="top")

    ax.set_xlabel(r"$x$", fontsize=12)
    ax.set_ylabel(r"$f(x)$", fontsize=12)
    ax.set_title(
        r"Дисперсия как мера разброса: $X \sim \mathcal{N}(0,\sigma^2)$",
        fontsize=13, weight="bold",
    )
    ax.legend(fontsize=10, framealpha=0.75, loc="upper right")
    ax.set_xlim(-5.5, 5.5)
    ax.set_ylim(0, None)
    ax.grid(True, alpha=0.3)
    for sp in ax.spines.values():
        sp.set_color(C_GRAY)

    # Аннотация формулы
    ax.text(0.02, 0.96,
            r"$\mathrm{Var}(X) = \mathbb{E}[(X-\mu)^2]$",
            transform=ax.transAxes, fontsize=10, va="top",
            bbox=dict(boxstyle="round,pad=0.4", facecolor=C_PANEL,
                      edgecolor=C_GRAY, alpha=0.85))
    _save(fig, out_name)


def _bivariate_normal(n: int, rho: float, seed: int = 42) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    z = rng.standard_normal((2, n))
    x = z[0]
    y = rho * z[0] + math.sqrt(max(0.0, 1 - rho ** 2)) * z[1]
    return x, y


def draw_correlation_scatter(out_name: str = "correlation_scatter.png") -> None:
    """Диаграммы рассеяния для ρ ∈ {0, 0.5, 0.9, -0.8}."""
    _apply_style()
    rhos = [0.0, 0.5, 0.9, -0.8]
    titles = [r"$\rho = 0$ (нет линейной связи)",
              r"$\rho = 0.5$ (слабая положительная)",
              r"$\rho = 0.9$ (сильная положительная)",
              r"$\rho = -0.8$ (сильная отрицательная)"]

    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    n = 300

    for ax, rho, title in zip(axes.flat, rhos, titles):
        x, y = _bivariate_normal(n, rho, seed=abs(7 + int(rho * 100)) + 1)
        ax.scatter(x, y, s=18, alpha=0.45, color=C_BLUE, edgecolors="none")

        # Линия регрессии E[Y|X=x] = ρ·x (при стандартизованных)
        xv = np.linspace(-3.2, 3.2, 100)
        ax.plot(xv, rho * xv, color=C_ORANGE, lw=2.2,
                label=r"$\mathbb{E}[Y|X=x] = \rho\,x$")

        ax.set_title(title, fontsize=11, weight="bold")
        ax.set_xlabel(r"$X$", fontsize=10)
        ax.set_ylabel(r"$Y$", fontsize=10)
        ax.set_xlim(-3.5, 3.5)
        ax.set_ylim(-3.5, 3.5)
        ax.axhline(0, color=C_GRAY, lw=0.8, ls="--")
        ax.axvline(0, color=C_GRAY, lw=0.8, ls="--")
        ax.legend(fontsize=8, framealpha=0.7, loc="upper left")
        ax.grid(True, alpha=0.25)
        for sp in ax.spines.values():
            sp.set_color(C_GRAY)

    fig.suptitle("Корреляция и линейная зависимость", fontsize=13, weight="bold", y=1.01)
    fig.tight_layout(pad=2.0)
    _save(fig, out_name)


def draw_conditional_expectation(out_name: str = "conditional_expectation.png") -> None:
    """Условное МО E[Y|X=x] как регрессионная кривая (линейная + нелинейная)."""
    _apply_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    rng = np.random.default_rng(0)
    n = 400

    # --- Левый: линейная регрессия (совместное нормальное) ---
    rho = 0.75
    x1, y1 = _bivariate_normal(n, rho, seed=0)
    ax1.scatter(x1, y1, s=16, alpha=0.35, color=C_BLUE, edgecolors="none")

    xv = np.linspace(-3.2, 3.2, 200)
    ax1.plot(xv, rho * xv, color=C_ORANGE, lw=2.5,
             label=rf"$\mathbb{{E}}[Y|X=x] = {rho}\,x$")

    # Вертикальные полосы — разброс Y при X≈const
    for x_cond in [-1.5, 0.0, 1.5]:
        mask = np.abs(x1 - x_cond) < 0.3
        if mask.sum() > 0:
            y_sel = y1[mask]
            ax1.scatter(x1[mask], y_sel, s=28, alpha=0.8, color=C_GREEN, edgecolors="none", zorder=4)
            ax1.vlines(x_cond, y_sel.min(), y_sel.max(),
                       color=C_GREEN, lw=1.5, alpha=0.5)
            ax1.plot(x_cond, rho * x_cond, "D", color=C_ORANGE, ms=7, zorder=5)

    ax1.set_title(r"Совместное нормальное: $\mathbb{E}[Y|X=x]$ линейно",
                  fontsize=11, weight="bold")
    ax1.set_xlabel(r"$X$", fontsize=11)
    ax1.set_ylabel(r"$Y$", fontsize=11)
    ax1.legend(fontsize=10, framealpha=0.75)
    ax1.set_xlim(-3.5, 3.5)
    ax1.set_ylim(-3.5, 3.5)
    ax1.grid(True, alpha=0.25)
    for sp in ax1.spines.values():
        sp.set_color(C_GRAY)

    # --- Правый: нелинейное условное МО (E[Y|X] = X²) ---
    x2 = rng.uniform(-2.5, 2.5, n)
    noise = rng.standard_normal(n) * 0.6
    y2 = x2 ** 2 + noise

    ax2.scatter(x2, y2, s=16, alpha=0.35, color=C_BLUE, edgecolors="none")

    xv2 = np.linspace(-2.5, 2.5, 200)
    ax2.plot(xv2, xv2 ** 2, color=C_ORANGE, lw=2.5,
             label=r"$\mathbb{E}[Y|X=x] = x^2$")

    ax2.set_title(r"Нелинейное условное МО: $Y = X^2 + \varepsilon$",
                  fontsize=11, weight="bold")
    ax2.set_xlabel(r"$X$", fontsize=11)
    ax2.set_ylabel(r"$Y$", fontsize=11)
    ax2.legend(fontsize=10, framealpha=0.75)
    ax2.set_xlim(-2.8, 2.8)
    ax2.set_ylim(-1.0, 7.5)
    ax2.grid(True, alpha=0.25)
    for sp in ax2.spines.values():
        sp.set_color(C_GRAY)

    ax2.text(0.97, 0.06,
             r"$\mathbb{E}[Y|X]$ — наилучший предсказатель $Y$ по $X$",
             transform=ax2.transAxes, ha="right", va="bottom", fontsize=9,
             bbox=dict(boxstyle="round,pad=0.3", facecolor=C_PANEL,
                       edgecolor=C_GRAY, alpha=0.85))

    fig.suptitle("Условное МО как регрессионная кривая", fontsize=13, weight="bold", y=1.01)
    fig.tight_layout(pad=2.0)
    _save(fig, out_name)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_variance_spread()
    print("  variance_spread.png — OK")
    draw_correlation_scatter()
    print("  correlation_scatter.png — OK")
    draw_conditional_expectation()
    print("  conditional_expectation.png — OK")
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
