"""Точные схемы для лекции про характеристические функции и ЦПТ."""

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


def _erf(z: float) -> float:
    """Abramowitz & Stegun approximation."""
    t = 1.0 / (1.0 + 0.3275911 * abs(z))
    poly = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741
           + t * (-1.453152027 + t * 1.061405429))))
    result = 1.0 - poly * math.exp(-z * z)
    return float(result if z >= 0 else -result)


def draw_char_function_examples(out_name: str = "char_function_examples.png") -> None:
    """Вещественные части х.ф. для нормального, равномерного, Коши."""
    _apply_style()
    t = np.linspace(-6, 6, 800)

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))

    # --- N(0,1) ---
    ax = axes[0]
    phi_norm = np.exp(-t**2 / 2)
    ax.plot(t, phi_norm, color=C_BLUE, lw=2.5, label=r"$\mathrm{Re}[\varphi(t)]$")
    ax.axhline(0, color=C_GRAY, lw=0.8)
    ax.axvline(0, color=C_GRAY, lw=0.8)
    ax.set_title("$\\mathcal{N}(0,1)$\n$\\varphi(t)=e^{-t^2/2}$",
                 fontsize=11, weight="bold")
    ax.set_xlabel("$t$")
    ax.set_ylabel("$\\varphi(t)$")
    ax.set_ylim(-0.2, 1.1)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    for sp in ax.spines.values():
        sp.set_color(C_GRAY)

    # --- Uniform(-1,1): Re(phi) = sin(t)/t ---
    ax = axes[1]
    with np.errstate(divide="ignore", invalid="ignore"):
        phi_unif_re = np.where(np.abs(t) < 1e-10, 1.0, np.sin(t) / t)
    phi_unif_im = np.zeros_like(t)
    ax.plot(t, phi_unif_re, color=C_ORANGE, lw=2.5,
            label=r"$\mathrm{Re}[\varphi(t)]$")
    ax.plot(t, phi_unif_im, color=C_GRAY, lw=1.2, ls="--",
            label=r"$\mathrm{Im}[\varphi(t)]=0$")
    ax.axhline(0, color=C_GRAY, lw=0.8)
    ax.axvline(0, color=C_GRAY, lw=0.8)
    ax.set_title("$\\mathrm{Uniform}(-1,1)$\n$\\varphi(t)=\\sin(t)/t$",
                 fontsize=11, weight="bold")
    ax.set_xlabel("$t$")
    ax.set_ylim(-0.35, 1.1)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    for sp in ax.spines.values():
        sp.set_color(C_GRAY)

    # --- Cauchy(0,1): phi = e^{-|t|} ---
    ax = axes[2]
    phi_cauchy = np.exp(-np.abs(t))
    ax.plot(t, phi_cauchy, color=C_GREEN, lw=2.5, label=r"$\mathrm{Re}[\varphi(t)]$")
    ax.axhline(0, color=C_GRAY, lw=0.8)
    ax.axvline(0, color=C_GRAY, lw=0.8)
    ax.set_title("$\\mathrm{Cauchy}(0,1)$\n$\\varphi(t)=e^{-|t|}$",
                 fontsize=11, weight="bold")
    ax.set_xlabel("$t$")
    ax.set_ylim(-0.1, 1.1)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    for sp in ax.spines.values():
        sp.set_color(C_GRAY)

    fig.suptitle("Характеристические функции основных распределений",
                 fontsize=13, weight="bold", y=1.02)
    fig.tight_layout(pad=2.0)
    _save(fig, out_name)


def _norm_pdf(x: np.ndarray, mu: float, sigma: float) -> np.ndarray:
    return np.exp(-0.5 * ((x - mu) / sigma)**2) / (sigma * math.sqrt(2 * math.pi))


def draw_clt_convergence(out_name: str = "clt_convergence.png") -> None:
    """Сходимость суммы н.о.р. Uniform(0,1) к нормальному закону."""
    _apply_style()
    rng = np.random.default_rng(0)
    N_SAMPLES = 50000
    ns = [1, 2, 5, 30]
    colors = [C_GRAY, C_ORANGE, C_GREEN, C_BLUE]

    fig, axes = plt.subplots(1, 4, figsize=(14, 4.5))

    for ax, n, color in zip(axes, ns, colors):
        # Нормированная сумма: (S_n - n*0.5) / sqrt(n/12)
        samples = rng.uniform(0, 1, (N_SAMPLES, n)).sum(axis=1)
        sigma_n = math.sqrt(n / 12)
        z = (samples - n * 0.5) / sigma_n

        ax.hist(z, bins=60, density=True, color=color, alpha=0.55,
                edgecolor=C_BG, linewidth=0.3)

        x = np.linspace(-4, 4, 300)
        ax.plot(x, _norm_pdf(x, 0, 1), color=C_INK, lw=2.2, ls="--",
                label=r"$\mathcal{N}(0,1)$")

        ax.set_title(f"$n = {n}$", fontsize=12, weight="bold")
        ax.set_xlabel("$z$")
        if ax is axes[0]:
            ax.set_ylabel("плотность")
        ax.set_xlim(-4, 4)
        ax.set_ylim(0, None)
        ax.legend(fontsize=9, framealpha=0.7)
        ax.grid(True, alpha=0.25)
        for sp in ax.spines.values():
            sp.set_color(C_GRAY)

    fig.suptitle(
        "ЦПТ: нормированная сумма $\\mathrm{Uniform}(0,1)$ сходится к $\\mathcal{N}(0,1)$",
        fontsize=12, weight="bold", y=1.02,
    )
    fig.tight_layout(pad=2.0)
    _save(fig, out_name)


def draw_berry_esseen(out_name: str = "berry_esseen.png") -> None:
    """Скорость сходимости ЦПТ: sup|F_n - Phi| для Uniform(0,1)."""
    _apply_style()
    rng = np.random.default_rng(1)
    N_SAMPLES = 100000
    ns = [1, 2, 5, 10, 20, 50, 100, 200, 500]

    sup_errors = []
    x_grid = np.linspace(-4, 4, 2000)
    phi_vals = np.array([0.5 * (1 + _erf(x / math.sqrt(2))) for x in x_grid])

    for n in ns:
        samples = rng.uniform(0, 1, (N_SAMPLES, n)).sum(axis=1)
        sigma_n = math.sqrt(n / 12)
        z = (samples - n * 0.5) / sigma_n
        z_sorted = np.sort(z)
        ecdf = np.arange(1, N_SAMPLES + 1) / N_SAMPLES
        # Интерполируем ecdf в узлы x_grid
        fn_vals = np.interp(x_grid, z_sorted, ecdf)
        sup_errors.append(float(np.max(np.abs(fn_vals - phi_vals))))

    fig, ax = plt.subplots(figsize=(9, 4.5))

    ns_arr = np.array(ns, dtype=float)
    ax.loglog(ns_arr, sup_errors, "o-", color=C_BLUE, lw=2.2, ms=7,
              label="Эмпирич. $\\sup|F_n - \\Phi|$")

    # Граница Берри-Эссеена: C*rho/(sigma^3*sqrt(n))
    # Для Uniform(0,1): rho = E[|X-0.5|^3] = 1/32, sigma^3 = (1/12)^{3/2}
    rho3 = 1 / 32
    sigma3 = (1 / 12) ** 1.5
    C_be = 0.4748
    be_bound = C_be * rho3 / (sigma3 * np.sqrt(ns_arr))
    ax.loglog(ns_arr, be_bound, "--", color=C_ORANGE, lw=2.0,
              label="Берри-Эссеен: $C\\rho/(\\sigma^3\\sqrt{n})$")

    # Референс 1/sqrt(n)
    ax.loglog(ns_arr, 0.5 / np.sqrt(ns_arr), ":", color=C_GRAY, lw=1.5,
              label="$\\propto 1/\\sqrt{n}$")

    ax.set_xlabel("$n$", fontsize=12)
    ax.set_ylabel("$\\sup_x |F_n(x) - \\Phi(x)|$", fontsize=11)
    ax.set_title(
        "Скорость сходимости ЦПТ для $\\mathrm{Uniform}(0,1)$",
        fontsize=12, weight="bold",
    )
    ax.legend(fontsize=10, framealpha=0.8)
    ax.grid(True, alpha=0.3, which="both")
    for sp in ax.spines.values():
        sp.set_color(C_GRAY)

    fig.tight_layout(pad=1.5)
    _save(fig, out_name)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_char_function_examples()
    print("  char_function_examples.png — OK")
    draw_clt_convergence()
    print("  clt_convergence.png — OK")
    draw_berry_esseen()
    print("  berry_esseen.png — OK")
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
