"""
Точные схемы для лекции про собственные векторы и диагонализацию.

Запуск:
    python3 generate_visuals.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Rectangle

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
            "grid.alpha": 0.28,
            "font.size": 11,
        }
    )


def _save(fig: plt.Figure, out_name: str) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def _setup_plane(ax: plt.Axes, lim: float = 3.0) -> None:
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.axhline(0, color=C_GRAY, lw=0.9)
    ax.axvline(0, color=C_GRAY, lw=0.9)
    ax.grid(True, alpha=0.28)
    for spine in ax.spines.values():
        spine.set_color(C_GRAY)


def draw_eigen_direction_action(out_name: str = "eigen_direction_action.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(7.6, 5.8))
    _setup_plane(ax, 3.0)

    v = np.array([1.1, 0.7])
    av = 2.0 * v
    w = np.array([-0.6, 1.6])
    aw = np.array([-1.8, 1.1])

    t = np.linspace(-2.6, 2.6, 100)
    line = np.outer(t, v / np.linalg.norm(v))
    ax.plot(line[:, 0], line[:, 1], color=C_BLUE, lw=2.0, alpha=0.6)

    ax.annotate("", xy=v, xytext=(0, 0), arrowprops=dict(arrowstyle="->", lw=2.4, color=C_BLUE))
    ax.annotate("", xy=av, xytext=(0, 0), arrowprops=dict(arrowstyle="->", lw=2.8, color=C_GREEN))
    ax.annotate("", xy=w, xytext=(0, 0), arrowprops=dict(arrowstyle="->", lw=2.2, color=C_ORANGE))
    ax.annotate("", xy=aw, xytext=(0, 0), arrowprops=dict(arrowstyle="->", lw=2.2, color=C_PURPLE))

    ax.text(v[0] + 0.08, v[1], r"$v$", color=C_BLUE, fontsize=13)
    ax.text(av[0] + 0.08, av[1], r"$Av=\lambda v$", color=C_GREEN, fontsize=12)
    ax.text(w[0] - 0.55, w[1] + 0.1, r"$u$", color=C_ORANGE, fontsize=13)
    ax.text(aw[0] - 0.55, aw[1] - 0.15, r"$Au$", color=C_PURPLE, fontsize=13)
    ax.text(-2.75, 2.6, "собственное направление сохраняется", fontsize=12, weight="bold")
    ax.set_title("Собственный вектор меняет длину, но не направление", weight="bold")
    _save(fig, out_name)


def draw_eigen_algorithm_flow(out_name: str = "eigen_algorithm_flow.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(10.8, 4.8))
    ax.axis("off")
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5)

    boxes = [
        (0.7, 2.0, 2.0, 1.1, C_BLUE, r"$A$"),
        (3.25, 2.0, 2.1, 1.1, C_ORANGE, r"$\chi_A(t)=\det(tI-A)$"),
        (5.95, 2.0, 2.0, 1.1, C_GREEN, r"$\chi_A(\lambda)=0$"),
        (8.55, 2.0, 2.5, 1.1, C_PURPLE, r"$E_\lambda=\ker(A-\lambda I)$"),
    ]
    for x, y, w, h, color, label in boxes:
        ax.add_patch(Rectangle((x, y), w, h, facecolor=color, edgecolor=C_INK, linewidth=1.1, alpha=0.28))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=13)

    for x1, x2 in [(2.75, 3.18), (5.42, 5.88), (8.0, 8.48)]:
        ax.annotate("", xy=(x2, 2.55), xytext=(x1, 2.55), arrowprops=dict(arrowstyle="->", lw=2.2, color=C_INK))

    ax.text(0.7, 3.85, "Алгоритм поиска собственных значений и векторов", fontsize=15, weight="bold")
    ax.text(1.0, 1.25, "матрица", fontsize=10, color=C_INK)
    ax.text(3.55, 1.25, "многочлен", fontsize=10, color=C_INK)
    ax.text(6.15, 1.25, "собственные значения", fontsize=10, color=C_INK)
    ax.text(8.78, 1.25, "собственные подпространства", fontsize=10, color=C_INK)
    _save(fig, out_name)


def draw_eigenspaces_direct_sum(out_name: str = "eigenspaces_direct_sum.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(7.4, 5.8))
    _setup_plane(ax, 2.8)

    t = np.linspace(-2.5, 2.5, 100)
    ax.plot(t, 0.45 * t, color=C_BLUE, lw=3.0, label=r"$E_{\lambda_1}$")
    ax.plot(t, -1.05 * t, color=C_ORANGE, lw=3.0, label=r"$E_{\lambda_2}$")
    ax.scatter([0], [0], color=C_INK, s=35, zorder=5)
    ax.text(-2.55, 2.25, r"$\lambda_1\ne\lambda_2$", fontsize=12)
    ax.text(-2.55, 1.95, r"$E_{\lambda_1}\cap E_{\lambda_2}=\{0\}$", fontsize=12)
    ax.text(-2.55, 1.65, r"$E_{\lambda_1}+E_{\lambda_2}=E_{\lambda_1}\oplus E_{\lambda_2}$", fontsize=12)
    ax.set_title("Собственные подпространства для разных значений складываются прямо", weight="bold")
    ax.legend(loc="lower left", fontsize=10, framealpha=0.95)
    _save(fig, out_name)


def draw_diagonalization_basis_change(out_name: str = "diagonalization_basis_change.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    ax.axis("off")
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5)

    ax.text(0.7, 4.15, "Диагонализация: перейти в базис из собственных векторов", fontsize=15, weight="bold")

    blocks = [
        (0.9, 1.9, 1.35, 1.1, C_BLUE, r"$C^{-1}$"),
        (2.95, 1.9, 1.35, 1.1, C_ORANGE, r"$A$"),
        (5.0, 1.9, 1.35, 1.1, C_BLUE, r"$C$"),
        (8.25, 1.9, 1.65, 1.1, C_GREEN, r"$D$"),
    ]
    for x, y, w, h, color, label in blocks:
        ax.add_patch(Rectangle((x, y), w, h, facecolor=color, edgecolor=C_INK, linewidth=1.1, alpha=0.32))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=18)

    ax.text(2.55, 2.45, r"$\cdot$", fontsize=24, ha="center", va="center")
    ax.text(4.62, 2.45, r"$\cdot$", fontsize=24, ha="center", va="center")
    ax.annotate("", xy=(7.85, 2.45), xytext=(6.65, 2.45), arrowprops=dict(arrowstyle="->", lw=2.6, color=C_INK))
    ax.text(1.05, 1.15, r"$C=(v_1,\dots,v_n)$, где $Av_i=\lambda_i v_i$", fontsize=12)
    ax.text(8.0, 1.15, r"$D=\operatorname{diag}(\lambda_1,\dots,\lambda_n)$", fontsize=12)
    ax.text(3.0, 3.35, r"$C^{-1}AC=D$", fontsize=17, color=C_PURPLE)
    _save(fig, out_name)


def draw_diagonalizable_vs_defective(out_name: str = "diagonalizable_vs_defective.png") -> None:
    _apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.8))

    for ax in axes:
        _setup_plane(ax, 2.4)

    t = np.linspace(-2.2, 2.2, 100)
    axes[0].plot(t, 0.25 * t, color=C_BLUE, lw=3.0)
    axes[0].plot(t, -0.85 * t, color=C_ORANGE, lw=3.0)
    axes[0].text(-2.15, 1.9, "две независимые\nсобственные прямые", fontsize=11)
    axes[0].text(0.55, 0.15, r"$E_{\lambda_1}$", color=C_BLUE, fontsize=12)
    axes[0].text(0.65, -0.75, r"$E_{\lambda_2}$", color=C_ORANGE, fontsize=12)
    axes[0].set_title("Диагонализируема", weight="bold")

    axes[1].plot(t, 0 * t, color=C_BLUE, lw=3.0)
    axes[1].annotate("", xy=(1.8, 0), xytext=(0, 0), arrowprops=dict(arrowstyle="->", lw=2.6, color=C_BLUE))
    axes[1].annotate("", xy=(1.8, 1.25), xytext=(0.2, 1.25), arrowprops=dict(arrowstyle="->", lw=2.0, color=C_GRAY))
    axes[1].text(-2.15, 1.9, "только одно\nсобственное направление", fontsize=11)
    axes[1].text(0.7, 0.18, r"$E_\lambda$", color=C_BLUE, fontsize=12)
    axes[1].text(-1.85, -1.9, r"$m_g(\lambda)<m_a(\lambda)$", color=C_PURPLE, fontsize=12)
    axes[1].set_title("Не диагонализируема", weight="bold")

    fig.suptitle("Хватает ли собственных направлений на базис?", fontsize=14, weight="bold")
    _save(fig, out_name)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_eigen_direction_action()
    draw_eigen_algorithm_flow()
    draw_eigenspaces_direct_sum()
    draw_diagonalization_basis_change()
    draw_diagonalizable_vs_defective()
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
