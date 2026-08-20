"""Точные схемы для лекции про случайные величины."""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from math import factorial

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
    plt.rcParams.update({
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
    })


def _save(fig, name: str) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS / name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def draw_cdf_comparison(out_name: str = "cdf_comparison.png") -> None:
    """Ступенчатая CDF (дискретная) и гладкая CDF (непрерывная) рядом."""
    _apply_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    # --- Дискретная CDF: число орлов при двух бросках ---
    jumps = [(0, 0.25), (1, 0.75), (2, 1.0)]

    ax1.hlines(
        [0, 0.25, 0.75, 1.0],
        [-1, 0, 1, 2],
        [0, 1, 2, 3],
        colors=C_BLUE, lw=2.5,
    )
    for x, y_top in jumps:
        y_bot = y_top - [0.25, 0.5, 0.25][jumps.index((x, y_top))]
        ax1.plot(x, y_top, "o", color=C_BLUE, ms=7, zorder=5)
        ax1.plot(x, y_bot, "o", color=C_BG, ms=7, zorder=5,
                 markeredgecolor=C_BLUE, markeredgewidth=1.8)
    ax1.set_xlim(-0.8, 2.8)
    ax1.set_ylim(-0.05, 1.12)
    ax1.set_title("CDF дискретной с.в.\n(число орлов, $n=2$)", fontsize=12, weight="bold")
    ax1.set_xlabel(r"$x$")
    ax1.set_ylabel(r"$F(x)$")
    ax1.set_xticks([0, 1, 2])
    ax1.grid(True, alpha=0.3)
    for sp in ax1.spines.values():
        sp.set_color(C_GRAY)

    # --- Непрерывная CDF: равномерное U(0,1) и N(0,1) ---
    x = np.linspace(-3.2, 3.2, 400)
    cdf_norm = np.array([0.5 * (1 + float(_erf(t / np.sqrt(2)))) for t in x])
    x_unif = np.linspace(-0.5, 1.5, 400)
    cdf_unif = np.clip(x_unif, 0, 1)

    ax2.plot(x, cdf_norm, color=C_BLUE, lw=2.5, label=r"$\mathcal{N}(0,1)$")
    ax2.plot(x_unif, cdf_unif, color=C_ORANGE, lw=2.5, label=r"$\mathrm{Uniform}(0,1)$")
    ax2.set_xlim(-3.2, 3.2)
    ax2.set_ylim(-0.05, 1.12)
    ax2.set_title("CDF непрерывных распределений", fontsize=12, weight="bold")
    ax2.set_xlabel(r"$x$")
    ax2.set_ylabel(r"$F(x)$")
    ax2.legend(fontsize=10, framealpha=0.7)
    ax2.grid(True, alpha=0.3)
    for sp in ax2.spines.values():
        sp.set_color(C_GRAY)

    fig.tight_layout(pad=2.0)
    _save(fig, out_name)


def _erf(z: float) -> float:
    """Error function via series (no scipy)."""
    # Abramowitz & Stegun approximation
    t = 1.0 / (1.0 + 0.3275911 * abs(z))
    poly = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741
           + t * (-1.453152027 + t * 1.061405429))))
    result = 1.0 - poly * np.exp(-z * z)
    return float(result if z >= 0 else -result)


def draw_pdf_cdf_examples(out_name: str = "pdf_cdf_examples.png") -> None:
    """PDF и CDF нормального и равномерного распределений."""
    _apply_style()
    fig, axes = plt.subplots(2, 2, figsize=(11, 7))

    x_n = np.linspace(-3.5, 3.5, 500)
    pdf_norm = np.exp(-x_n**2 / 2) / np.sqrt(2 * np.pi)
    cdf_norm = np.array([0.5 * (1 + _erf(t / np.sqrt(2))) for t in x_n])

    x_u = np.linspace(-0.5, 1.5, 500)
    pdf_unif = np.where((x_u >= 0) & (x_u <= 1), 1.0, 0.0)
    cdf_unif = np.clip(x_u, 0, 1)

    configs = [
        (axes[0, 0], x_n, pdf_norm, C_BLUE, r"Плотность $\mathcal{N}(0,1)$",
         r"$f(x)=\frac{1}{\sqrt{2\pi}}e^{-x^2/2}$", r"$x$", r"$f(x)$"),
        (axes[0, 1], x_n, cdf_norm, C_BLUE, r"CDF $\mathcal{N}(0,1)$",
         r"$F(x) = \Phi(x)$", r"$x$", r"$F(x)$"),
        (axes[1, 0], x_u, pdf_unif, C_ORANGE, r"Плотность $\mathrm{Uniform}(0,1)$",
         r"$f(x) = 1,\; x\in[0,1]$", r"$x$", r"$f(x)$"),
        (axes[1, 1], x_u, cdf_unif, C_ORANGE, r"CDF $\mathrm{Uniform}(0,1)$",
         r"$F(x) = x,\; x\in[0,1]$", r"$x$", r"$F(x)$"),
    ]
    for ax, xv, yv, color, title, subtitle, xl, yl in configs:
        ax.plot(xv, yv, color=color, lw=2.5)
        ax.fill_between(xv, yv, alpha=0.12, color=color)
        ax.set_title(title, fontsize=11, weight="bold")
        ax.set_xlabel(xl, fontsize=10)
        ax.set_ylabel(yl, fontsize=10)
        ax.text(0.97, 0.06, subtitle, transform=ax.transAxes,
                ha="right", va="bottom", fontsize=9,
                bbox=dict(boxstyle="round,pad=0.3", facecolor=C_PANEL,
                          edgecolor=C_GRAY, alpha=0.8))
        ax.grid(True, alpha=0.3)
        for sp in ax.spines.values():
            sp.set_color(C_GRAY)

    fig.suptitle("PDF и CDF: нормальное и равномерное распределения",
                 fontsize=13, weight="bold", y=1.01)
    fig.tight_layout(pad=2.0)
    _save(fig, out_name)


def draw_order_statistics(out_name: str = "order_statistics.png") -> None:
    """Плотности порядковых статистик X_(k) для n=5, Uniform(0,1)."""
    _apply_style()
    n = 5
    x = np.linspace(0, 1, 500)

    fig, ax = plt.subplots(figsize=(9, 5))

    colors_ks = [C_GRAY, C_GREEN, C_BLUE, C_ORANGE, C_INK]
    for k, color in zip(range(1, n + 1), colors_ks):
        coeff = factorial(n) / (factorial(k - 1) * factorial(n - k))
        pdf_k = coeff * x**(k - 1) * (1 - x)**(n - k)
        lw = 2.8 if k in (1, 3, 5) else 1.8
        alpha = 1.0 if k in (1, 3, 5) else 0.7
        ax.plot(x, pdf_k, color=color, lw=lw, alpha=alpha,
                label=rf"$X_{{({k})}}$,  $E = {k}/{n+1}$")
        ax.fill_between(x, pdf_k, alpha=0.08, color=color)

    ax.set_xlabel(r"$x$", fontsize=12)
    ax.set_ylabel(r"плотность $f_{X_{(k)}}(x)$", fontsize=11)
    ax.set_title(
        rf"Порядковые статистики $X_{{(k)}}$, $n={n}$, $X_i \sim \mathrm{{Uniform}}(0,1)$",
        fontsize=12, weight="bold",
    )
    ax.legend(fontsize=10, framealpha=0.7, loc="upper center",
              ncol=3, bbox_to_anchor=(0.5, 1.0))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, None)
    ax.grid(True, alpha=0.3)
    for sp in ax.spines.values():
        sp.set_color(C_GRAY)

    # Аннотация формулы
    ax.text(0.02, 0.97,
            r"$f_{X_{(k)}}(x) = \dfrac{n!}{(k-1)!(n-k)!}\,x^{k-1}(1-x)^{n-k}$",
            transform=ax.transAxes, fontsize=10, va="top",
            bbox=dict(boxstyle="round,pad=0.4", facecolor=C_PANEL,
                      edgecolor=C_GRAY, alpha=0.85))
    _save(fig, out_name)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_cdf_comparison()
    print("  cdf_comparison.png — OK")
    draw_pdf_cdf_examples()
    print("  pdf_cdf_examples.png — OK")
    draw_order_statistics()
    print("  order_statistics.png — OK")
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
