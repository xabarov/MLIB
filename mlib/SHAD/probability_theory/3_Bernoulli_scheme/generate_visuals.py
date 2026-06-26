"""Точные схемы для лекции про схему Бернулли и Пуассона."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from math import comb, factorial, exp

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

C_BG = "#faf9f5"
C_INK = "#141413"
C_GRAY = "#b0aea5"
C_PANEL = "#e8e6dc"
C_ORANGE = "#d97757"
C_BLUE = "#6a9bcc"
C_GREEN = "#788c5d"


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


def _save(fig, name: str) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS / name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def _binom_pmf(n: int, k_vals, p: float):
    q = 1.0 - p
    return np.array([comb(n, int(k)) * p**k * q**(n - k) for k in k_vals])


def _poisson_pmf(lam: float, k_vals):
    return np.array([lam**k * exp(-lam) / factorial(int(k)) for k in k_vals])


def draw_binomial_distribution(out_name: str = "binomial_distribution.png") -> None:
    """Гистограммы биномиального распределения при разных p, n=20."""
    _apply_style()
    n = 20
    configs = [
        (0.2, C_BLUE, r"$p = 0.2$"),
        (0.5, C_ORANGE, r"$p = 0.5$"),
        (0.8, C_GREEN, r"$p = 0.8$"),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5), sharey=False)

    for ax, (p, color, label) in zip(axes, configs):
        k_vals = np.arange(0, n + 1)
        probs = _binom_pmf(n, k_vals, p)
        k0 = int(np.floor((n + 1) * p))

        bar_colors = [C_ORANGE if k == k0 else color for k in k_vals]
        ax.bar(k_vals, probs, color=bar_colors, edgecolor=C_INK, linewidth=0.6, alpha=0.82, width=0.7)

        ax.set_title(f"{label},  $n = {n}$", fontsize=12, weight="bold", pad=6)
        ax.set_xlabel(r"$k$ (число успехов)", fontsize=10)
        ax.set_ylabel(r"$P_n(k)$", fontsize=10)
        ax.set_xlim(-0.8, n + 0.8)

        ax.annotate(
            f"$k_0 = {k0}$",
            xy=(k0, probs[k0]),
            xytext=(k0 + 2.5, probs[k0] + 0.015),
            fontsize=9,
            color=C_ORANGE,
            arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=1.2),
        )

        for spine in ax.spines.values():
            spine.set_color(C_GRAY)

    fig.suptitle(
        r"Биномиальное распределение $B(n, p)$, $n = 20$. "
        r"Оранжевый столбец — наивероятнейшее $k_0$.",
        fontsize=12,
        y=1.02,
    )
    _save(fig, out_name)


def draw_poisson_convergence(out_name: str = "poisson_convergence.png") -> None:
    """Сходимость Bin(n, λ/n) → Poisson(λ) при росте n."""
    _apply_style()
    lam = 3.0
    ns = [10, 30, 100]
    k_max = 12
    k_vals = np.arange(0, k_max + 1)

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5), sharey=True)

    pois_probs = _poisson_pmf(lam, k_vals)

    for ax, n in zip(axes, ns):
        p = lam / n
        binom_probs = _binom_pmf(n, k_vals, p)

        width = 0.38
        ax.bar(k_vals - width / 2, binom_probs, width=width,
               color=C_BLUE, edgecolor=C_INK, linewidth=0.5, alpha=0.80,
               label=rf"$B({n},\, {lam/n:.2f})$")
        ax.bar(k_vals + width / 2, pois_probs, width=width,
               color=C_ORANGE, edgecolor=C_INK, linewidth=0.5, alpha=0.80,
               label=rf"Пуассон($\lambda={lam}$)")

        ax.set_title(f"$n = {n}$,  $p = {lam/n:.3f}$", fontsize=11, weight="bold", pad=6)
        ax.set_xlabel(r"$k$", fontsize=10)
        if ax is axes[0]:
            ax.set_ylabel(r"вероятность", fontsize=10)
        ax.legend(fontsize=8, framealpha=0.6)
        ax.set_xlim(-0.8, k_max + 0.8)
        for spine in ax.spines.values():
            spine.set_color(C_GRAY)

    fig.suptitle(
        rf"Сходимость $\mathrm{{Bin}}(n,\,\lambda/n)$ к $\mathrm{{Poisson}}(\lambda={lam})$ "
        r"при $n \to \infty$",
        fontsize=12,
        y=1.02,
    )
    _save(fig, out_name)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_binomial_distribution()
    print("  binomial_distribution.png — OK")
    draw_poisson_convergence()
    print("  poisson_convergence.png — OK")
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
