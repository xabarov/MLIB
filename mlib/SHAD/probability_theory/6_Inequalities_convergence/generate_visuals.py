"""Точные схемы для лекции про неравенства и виды сходимости."""

from __future__ import annotations

from pathlib import Path
import math

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

C_BG     = "#faf9f5"
C_INK    = "#141413"
C_GRAY   = "#b0aea5"
C_PANEL  = "#e8e6dc"
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


def _arrow(ax, x1: float, y1: float, x2: float, y2: float,
           color: str = C_INK) -> None:
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color,
                                lw=1.8, mutation_scale=16))


def draw_convergence_diagram(out_name: str = "convergence_diagram.png") -> None:
    """Диаграмма вложений видов сходимости."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 6)
    ax.axis("off")

    # (x, y, w, h, color, label_top, label_bot)
    boxes = [
        (0.15, 0.5,  2.6, 5.0, C_GREEN,  "п.н.",
         "$P(\\omega: X_n(\\omega)\\to X(\\omega))=1$"),
        (3.10, 0.9,  2.6, 4.2, C_BLUE,   "$L^p$",
         "$\\mathbb{E}[|X_n-X|^p]\\to 0$"),
        (6.10, 1.3,  2.6, 3.4, C_ORANGE, "по вер-ти",
         "$P(|X_n-X|>\\varepsilon)\\to 0$"),
        (9.00, 1.7,  1.8, 2.6, C_GRAY,   "по расп-ю",
         "$F_{X_n}(x)\\to F_X(x)$"),
    ]

    for x, y, w, h, color, top, bot in boxes:
        rect = mpatches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.15",
            linewidth=2.2,
            edgecolor=color,
            facecolor=color + "1a",
        )
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h - 0.32, top,
                ha="center", va="top", fontsize=12, weight="bold", color=color)
        ax.text(x + w / 2, y + h / 2 - 0.15, bot,
                ha="center", va="center", fontsize=8.5, color=C_INK)

    # п.н. --> по вер-ти (верхняя стрелка, y=3.5)
    _arrow(ax, 2.75, 3.5, 6.10, 3.5)
    # L^p --> по вер-ти (нижняя стрелка, y=2.0)
    ax.annotate("", xy=(6.10, 2.0), xytext=(2.75, 2.0),
                arrowprops=dict(arrowstyle="-|>", color=C_BLUE,
                                lw=1.8, mutation_scale=16))
    # по вер-ти --> по расп-ю
    _arrow(ax, 8.70, 3.0, 9.00, 3.0)

    # Метки на стрелках
    ax.text(4.4,  3.82, "$\\Rightarrow$", ha="center", fontsize=14, color=C_INK)
    ax.text(7.85, 3.3,  "$\\Rightarrow$", ha="center", fontsize=14, color=C_INK)
    ax.text(4.3,  2.30, "$L^p\\Rightarrow$",
            ha="center", fontsize=10, color=C_BLUE)

    ax.set_title("Виды сходимости с.в.: иерархия импликаций",
                 fontsize=13, weight="bold", pad=12)

    ax.text(5.5, 0.15,
            "Исключение: сход-ть по расп-ю к константе c  =>  по вер-ти к c",
            ha="center", va="bottom", fontsize=9, color=C_GRAY,
            bbox=dict(boxstyle="round,pad=0.3", facecolor=C_PANEL,
                      edgecolor=C_GRAY, alpha=0.85))

    _save(fig, out_name)


def _erf(z: float) -> float:
    """Error function (Abramowitz & Stegun approximation)."""
    t = 1.0 / (1.0 + 0.3275911 * abs(z))
    poly = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741
           + t * (-1.453152027 + t * 1.061405429))))
    result = 1.0 - poly * math.exp(-z * z)
    return float(result if z >= 0 else -result)


def draw_chebyshev_illustration(out_name: str = "chebyshev_illustration.png") -> None:
    """Неравенство Чебышёва: реальная вероятность хвоста vs оценка."""
    _apply_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

    # --- Левый: PDF N(0,1) с затенением хвостов ---
    x = np.linspace(-4, 4, 600)
    pdf = np.exp(-x**2 / 2) / math.sqrt(2 * math.pi)

    eps = 2.0
    ax1.plot(x, pdf, color=C_BLUE, lw=2.5)
    mask = np.abs(x) >= eps
    ax1.fill_between(x, pdf, where=mask, alpha=0.45, color=C_ORANGE,
                     label=f"$|X|\\geq{eps:.0f}\\sigma$")
    ax1.fill_between(x, pdf, where=~mask, alpha=0.15, color=C_BLUE)
    ax1.axvline(eps,  color=C_ORANGE, lw=1.5, ls="--")
    ax1.axvline(-eps, color=C_ORANGE, lw=1.5, ls="--")

    real_prob = 2 * (1 - 0.5 * (1 + _erf(eps / math.sqrt(2))))
    ax1.text(0, 0.30,
             f"Реальная: {real_prob:.4f}\nЧебышёв: $\\leq$ {1/eps**2:.4f}",
             ha="center", va="center", fontsize=10,
             bbox=dict(boxstyle="round,pad=0.4", facecolor=C_PANEL,
                       edgecolor=C_GRAY, alpha=0.9))
    ax1.set_title(f"$\\mathcal{{N}}(0,1)$: хвост при $\\varepsilon = {eps:.0f}\\sigma$",
                  fontsize=12, weight="bold")
    ax1.set_xlabel("$x$")
    ax1.set_ylabel("$f(x)$")
    ax1.legend(fontsize=10, framealpha=0.75)
    ax1.grid(True, alpha=0.3)
    for sp in ax1.spines.values():
        sp.set_color(C_GRAY)

    # --- Правый: Чебышёв vs реальный хвост в лог. шкале ---
    k_vals = np.linspace(1.01, 5, 300)
    cheb_bound = 1 / k_vals**2
    real_tail = np.array([
        2 * (1 - 0.5 * (1 + _erf(k / math.sqrt(2)))) for k in k_vals
    ])

    ax2.semilogy(k_vals, cheb_bound, color=C_ORANGE, lw=2.5,
                 label="Граница Чебышёва: $1/k^2$")
    ax2.semilogy(k_vals, real_tail, color=C_BLUE, lw=2.5,
                 label="Реальный хвост $\\mathcal{N}(0,1)$")
    ax2.set_xlabel("$k$ (отклонение в $\\sigma$)", fontsize=11)
    ax2.set_ylabel("$P(|X|\\geq k\\sigma)$", fontsize=11)
    ax2.set_title("Чебышёв vs реальный хвост (лог. шкала)", fontsize=12, weight="bold")
    ax2.legend(fontsize=10, framealpha=0.75)
    ax2.grid(True, alpha=0.3, which="both")
    for sp in ax2.spines.values():
        sp.set_color(C_GRAY)

    fig.suptitle(
        "$P(|X-\\mu|\\geqq k\\sigma)\\leq 1/k^2$ (неравенство Чебышёва)",
        fontsize=13, weight="bold", y=1.02,
    )
    fig.tight_layout(pad=2.0)
    _save(fig, out_name)


def draw_lln_illustration(out_name: str = "lln_illustration.png") -> None:
    """Сходимость выборочного среднего к МО (ЗБЧ / УЗБЧ)."""
    _apply_style()
    rng = np.random.default_rng(42)
    mu = 2.0
    sigma = 1.5
    n_max = 500
    n_trials = 4

    fig, ax = plt.subplots(figsize=(10, 5))

    colors = [C_BLUE, C_GREEN, C_ORANGE, C_GRAY]
    n_arr = np.arange(1, n_max + 1)

    for i, color in enumerate(colors[:n_trials]):
        xs = rng.normal(mu, sigma, n_max)
        cum_mean = np.cumsum(xs) / n_arr
        alpha = 0.85 if i == 0 else 0.55
        lw = 2.2 if i == 0 else 1.5
        ax.plot(n_arr, cum_mean, color=color, lw=lw, alpha=alpha,
                label=f"Выборка {i+1}")

    ax.axhline(mu, color=C_INK, lw=2.0, ls="--", label=f"$\\mu = {mu}$")

    cheb_band = 2 * sigma / np.sqrt(n_arr)
    ax.fill_between(n_arr, mu - cheb_band, mu + cheb_band,
                    alpha=0.10, color=C_INK,
                    label="$\\pm 2\\sigma/\\sqrt{n}$ (Чебышёв)")

    ax.set_xlabel("$n$ (объём выборки)", fontsize=12)
    ax.set_ylabel("$\\bar{X}_n$", fontsize=12)
    ax.set_title(
        f"Закон больших чисел: выборочное среднее стремится к $\\mu={mu}$"
        f"\n($\\sigma={sigma}$, $X_i\\sim\\mathcal{{N}}(\\mu,\\sigma^2)$)",
        fontsize=12, weight="bold",
    )
    ax.legend(fontsize=10, framealpha=0.75, loc="upper right")
    ax.set_xlim(1, n_max)
    ax.grid(True, alpha=0.3)
    for sp in ax.spines.values():
        sp.set_color(C_GRAY)

    _save(fig, out_name)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_convergence_diagram()
    print("  convergence_diagram.png — OK")
    draw_chebyshev_illustration()
    print("  chebyshev_illustration.png — OK")
    draw_lln_illustration()
    print("  lln_illustration.png — OK")
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
