"""Точные схемы для лекции про стандартные распределения."""

from __future__ import annotations

from pathlib import Path
import math

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
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
C_PURPLE = "#8b6db0"


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
        "font.size":        10,
    })


def _save(fig, name: str) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS / name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def _binom_pmf(k: int, n: int, p: float) -> float:
    return math.comb(n, k) * p**k * (1 - p)**(n - k)


def _poisson_pmf(k: int, lam: float) -> float:
    return math.exp(-lam) * lam**k / math.factorial(k)


def _geom_pmf(k: int, p: float) -> float:
    return (1 - p)**(k - 1) * p


def _hypergeom_pmf(k: int, N: int, K: int, n: int) -> float:
    lo = max(0, n + K - N)
    hi = min(n, K)
    if k < lo or k > hi:
        return 0.0
    return math.comb(K, k) * math.comb(N - K, n - k) / math.comb(N, n)


def draw_discrete_pmfs(out_name: str = "discrete_pmfs.png") -> None:
    """PMF для четырёх дискретных распределений."""
    _apply_style()
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    # --- Биномиальное ---
    ax = axes[0, 0]
    n, p = 20, 0.35
    ks = np.arange(0, n + 1)
    pmf = np.array([_binom_pmf(int(k), n, p) for k in ks])
    k0 = int((n + 1) * p)
    colors_bin = [C_ORANGE if k == k0 else C_BLUE for k in ks]
    ax.bar(ks, pmf, color=colors_bin, alpha=0.8, edgecolor=C_BG, linewidth=0.4)
    ax.set_title(f"Биномиальное $n={n}$, $p={p}$\n$k_0={k0}$",
                 fontsize=10, weight="bold")
    ax.set_xlabel("$k$")
    ax.set_ylabel("PMF")
    ax.grid(True, alpha=0.25, axis="y")
    for sp in ax.spines.values():
        sp.set_color(C_GRAY)

    # --- Пуассон ---
    ax = axes[0, 1]
    lam = 5.0
    ks_p = np.arange(0, 18)
    pmf_p = np.array([_poisson_pmf(int(k), lam) for k in ks_p])
    ax.bar(ks_p, pmf_p, color=C_GREEN, alpha=0.8, edgecolor=C_BG, linewidth=0.4)
    ax.set_title(f"Пуассон $\\lambda={lam:.0f}$", fontsize=10, weight="bold")
    ax.set_xlabel("$k$")
    ax.set_ylabel("PMF")
    ax.grid(True, alpha=0.25, axis="y")
    for sp in ax.spines.values():
        sp.set_color(C_GRAY)

    # --- Геометрическое ---
    ax = axes[1, 0]
    p_g = 0.3
    ks_g = np.arange(1, 16)
    pmf_g = np.array([_geom_pmf(int(k), p_g) for k in ks_g])
    ax.bar(ks_g, pmf_g, color=C_ORANGE, alpha=0.8, edgecolor=C_BG, linewidth=0.4)
    ax.set_title(f"Геометрическое $p={p_g}$\n$E[X]=1/p={1/p_g:.1f}$",
                 fontsize=10, weight="bold")
    ax.set_xlabel("$k$")
    ax.set_ylabel("PMF")
    ax.grid(True, alpha=0.25, axis="y")
    for sp in ax.spines.values():
        sp.set_color(C_GRAY)

    # --- Гипергеометрическое ---
    ax = axes[1, 1]
    N_h, K_h, n_h = 50, 15, 10
    ks_h = np.arange(0, min(n_h, K_h) + 1)
    pmf_h = np.array([_hypergeom_pmf(int(k), N_h, K_h, n_h) for k in ks_h])
    ax.bar(ks_h, pmf_h, color=C_PURPLE, alpha=0.8, edgecolor=C_BG, linewidth=0.4)
    ax.set_title(f"Гипергеометрическое $N={N_h}$, $K={K_h}$, $n={n_h}$\n"
                 f"$E[X]={n_h*K_h/N_h:.1f}$",
                 fontsize=10, weight="bold")
    ax.set_xlabel("$k$")
    ax.set_ylabel("PMF")
    ax.grid(True, alpha=0.25, axis="y")
    for sp in ax.spines.values():
        sp.set_color(C_GRAY)

    fig.suptitle("PMF дискретных распределений", fontsize=13, weight="bold", y=1.01)
    fig.tight_layout(pad=2.0)
    _save(fig, out_name)


def _gamma_pdf(x: np.ndarray, alpha: float, beta: float) -> np.ndarray:
    """Гамма-распределение с масштабом beta."""
    coeff = 1.0 / (math.gamma(alpha) * beta**alpha)
    return coeff * x**(alpha - 1) * np.exp(-x / beta)


def _beta_pdf(x: np.ndarray, a: float, b: float) -> np.ndarray:
    from math import gamma
    beta_fn = gamma(a) * gamma(b) / gamma(a + b)
    return x**(a - 1) * (1 - x)**(b - 1) / beta_fn


def _weibull_pdf(x: np.ndarray, k: float, lam: float) -> np.ndarray:
    with np.errstate(divide="ignore", invalid="ignore"):
        result = (k / lam) * (x / lam)**(k - 1) * np.exp(-(x / lam)**k)
    return np.where(x >= 0, result, 0.0)


def draw_continuous_pdfs(out_name: str = "continuous_pdfs.png") -> None:
    """PDF для четырёх ключевых непрерывных семейств."""
    _apply_style()
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    # --- Нормальное ---
    ax = axes[0, 0]
    x = np.linspace(-4, 4, 400)
    for mu, sigma, color, lbl in [
        (0, 1, C_BLUE,  r"$\mathcal{N}(0,1)$"),
        (0, 0.5, C_ORANGE, r"$\mathcal{N}(0,0.25)$"),
        (1, 1.5, C_GREEN,  r"$\mathcal{N}(1,2.25)$"),
    ]:
        pdf = np.exp(-0.5 * ((x - mu) / sigma)**2) / (sigma * math.sqrt(2 * math.pi))
        ax.plot(x, pdf, lw=2.2, color=color, label=lbl)
    ax.set_title("Нормальное распределение", fontsize=10, weight="bold")
    ax.set_xlabel("$x$")
    ax.set_ylabel("PDF")
    ax.legend(fontsize=8.5)
    ax.set_xlim(-4, 5)
    ax.grid(True, alpha=0.25)
    for sp in ax.spines.values():
        sp.set_color(C_GRAY)

    # --- Гамма ---
    ax = axes[0, 1]
    x = np.linspace(0.001, 15, 500)
    configs = [
        (1, 2, C_BLUE,   r"$\Gamma(1,2)=\mathrm{Exp}(0.5)$"),
        (2, 2, C_ORANGE, r"$\Gamma(2,2)$"),
        (5, 1, C_GREEN,  r"$\Gamma(5,1)$"),
    ]
    for alpha, beta, color, lbl in configs:
        ax.plot(x, _gamma_pdf(x, alpha, beta), lw=2.2, color=color, label=lbl)
    ax.set_title("Гамма-распределение", fontsize=10, weight="bold")
    ax.set_xlabel("$x$")
    ax.set_ylabel("PDF")
    ax.legend(fontsize=8.5)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, None)
    ax.grid(True, alpha=0.25)
    for sp in ax.spines.values():
        sp.set_color(C_GRAY)

    # --- Бета ---
    ax = axes[1, 0]
    x = np.linspace(0.005, 0.995, 500)
    configs_b = [
        (0.5, 0.5, C_PURPLE, r"$\mathrm{Beta}(0.5,0.5)$"),
        (1,   1,   C_GRAY,   r"$\mathrm{Beta}(1,1)=\mathrm{Unif}$"),
        (2,   5,   C_BLUE,   r"$\mathrm{Beta}(2,5)$"),
        (5,   2,   C_ORANGE, r"$\mathrm{Beta}(5,2)$"),
    ]
    for a, b, color, lbl in configs_b:
        try:
            pdf = _beta_pdf(x, a, b)
            ax.plot(x, np.clip(pdf, 0, 6), lw=2.2, color=color, label=lbl)
        except Exception:
            pass
    ax.set_title("Бета-распределение", fontsize=10, weight="bold")
    ax.set_xlabel("$x$")
    ax.set_ylabel("PDF")
    ax.legend(fontsize=8.5)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 4)
    ax.grid(True, alpha=0.25)
    for sp in ax.spines.values():
        sp.set_color(C_GRAY)

    # --- Вейбулл ---
    ax = axes[1, 1]
    x = np.linspace(0, 3.5, 500)
    lam_w = 1.0
    configs_w = [
        (0.5, C_BLUE,   "$k=0.5$ (убыв. $h$)"),
        (1.0, C_GREEN,  "$k=1$ (Exp)"),
        (2.0, C_ORANGE, "$k=2$ (возр. $h$)"),
        (5.0, C_PURPLE, "$k=5$"),
    ]
    for k, color, lbl in configs_w:
        ax.plot(x, _weibull_pdf(x, k, lam_w), lw=2.2, color=color, label=lbl)
    ax.set_title(f"Вейбулл $\\lambda={lam_w}$", fontsize=10, weight="bold")
    ax.set_xlabel("$x$")
    ax.set_ylabel("PDF")
    ax.legend(fontsize=8.5)
    ax.set_xlim(0, 3.5)
    ax.set_ylim(0, 2.5)
    ax.grid(True, alpha=0.25)
    for sp in ax.spines.values():
        sp.set_color(C_GRAY)

    fig.suptitle("PDF непрерывных распределений", fontsize=13, weight="bold", y=1.01)
    fig.tight_layout(pad=2.0)
    _save(fig, out_name)


def draw_distributions_relations(out_name: str = "distributions_relations.png") -> None:
    """Схема связей между распределениями."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis("off")

    def box(cx: float, cy: float, text: str, color: str, w: float = 2.2,
            h: float = 0.7) -> None:
        import matplotlib.patches as mp
        rect = mp.FancyBboxPatch(
            (cx - w / 2, cy - h / 2), w, h,
            boxstyle="round,pad=0.12",
            linewidth=1.6,
            edgecolor=color,
            facecolor=color + "22",
        )
        ax.add_patch(rect)
        ax.text(cx, cy, text, ha="center", va="center",
                fontsize=9, weight="bold", color=C_INK)

    def arrow(x1: float, y1: float, x2: float, y2: float,
              label: str = "", color: str = C_GRAY) -> None:
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=color,
                                   lw=1.4, mutation_scale=12))
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(mx + 0.07, my, label, fontsize=7.5, color=color,
                    ha="left", va="center")

    # Расположение узлов (x, y, label, color)
    nodes = {
        "Bernoulli":    (2.0,  7.0, "Bernoulli(p)",        C_BLUE),
        "Binomial":     (5.5,  7.0, "Binomial(n,p)",       C_BLUE),
        "Poisson":      (9.0,  7.0, "Poisson(λ)",          C_GREEN),
        "Geom":         (2.0,  5.5, "Geometric(p)",        C_ORANGE),
        "NegBin":       (5.5,  5.5, "NegBin(r,p)",         C_ORANGE),
        "HGeom":        (9.0,  5.5, "HGeom(N,K,n)",        C_GRAY),
        "Uniform":      (2.0,  3.8, "Uniform(a,b)",        C_BLUE),
        "Beta":         (5.5,  3.8, "Beta(α,β)",           C_PURPLE),
        "Normal":       (9.0,  3.8, "Normal(μ,σ²)",        C_BLUE),
        "Exp":          (2.0,  2.2, "Exp(λ)",              C_GREEN),
        "Gamma":        (5.5,  2.2, "Gamma(α,β)",          C_GREEN),
        "Chi2":         (9.0,  2.2, "Chi²(n)",             C_ORANGE),
        "Weibull":      (2.0,  0.8, "Weibull(k,λ)",        C_ORANGE),
    }

    for (x, y, lbl, color) in nodes.values():
        box(x, y, lbl, color)

    # Стрелки
    arrow(3.1, 7.0, 4.4, 7.0, "×n")
    arrow(6.6, 7.0, 8.0, 7.0, "n→∞, np→λ", C_GREEN)
    arrow(3.1, 5.5, 4.4, 5.5, "×r")
    arrow(5.5, 6.65, 5.5, 5.85, "r=1")
    arrow(9.0, 5.15, 9.0, 4.15, "N→∞", C_GREEN)

    arrow(2.0, 3.45, 2.0, 2.55, "")
    arrow(3.1, 3.8, 4.4, 3.8, "X_(k)")
    arrow(6.6, 3.8, 8.0, 3.8, "ЦПТ", C_BLUE)
    arrow(3.1, 2.2, 4.4, 2.2, "×n")
    arrow(6.6, 2.2, 8.0, 2.2, "α=n/2,β=2")
    arrow(2.0, 1.85, 2.0, 1.15, "k=1")
    arrow(5.5, 1.85, 5.5, 1.15, "", C_GRAY)
    ax.text(5.7, 1.5, "α=1", fontsize=7.5, color=C_GRAY)

    ax.set_title("Связи между стандартными распределениями",
                 fontsize=13, weight="bold", pad=10)
    _save(fig, out_name)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_discrete_pmfs()
    print("  discrete_pmfs.png — OK")
    draw_continuous_pdfs()
    print("  continuous_pdfs.png — OK")
    draw_distributions_relations()
    print("  distributions_relations.png — OK")
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
