"""
Иллюстрации для лекции про билинейные и квадратичные формы.

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


def _save(fig: plt.Figure, name: str) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS / name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def _setup_2d(ax: plt.Axes, lim: float = 2.4) -> None:
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.axhline(0, color=C_GRAY, lw=0.9)
    ax.axvline(0, color=C_GRAY, lw=0.9)
    ax.grid(True, alpha=0.28)
    for spine in ax.spines.values():
        spine.set_color(C_GRAY)


def draw_bilinear_pairing_scheme(out_name: str = "bilinear_pairing_scheme.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(8.6, 3.8))
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)

    left1 = Rectangle((0.7, 1.1), 1.8, 1.5, facecolor="#eef3f9", edgecolor=C_BLUE, linewidth=2.0)
    left2 = Rectangle((3.0, 1.1), 1.8, 1.5, facecolor="#f9efe8", edgecolor=C_ORANGE, linewidth=2.0)
    right = Rectangle((7.2, 1.35), 1.5, 1.0, facecolor="#edf5e8", edgecolor=C_GREEN, linewidth=2.0)
    ax.add_patch(left1)
    ax.add_patch(left2)
    ax.add_patch(right)
    ax.text(1.6, 1.85, r"$x$", fontsize=22, color=C_BLUE, ha="center", va="center")
    ax.text(3.9, 1.85, r"$y$", fontsize=22, color=C_ORANGE, ha="center", va="center")
    ax.text(7.95, 1.85, r"$B(x,y)$", fontsize=18, color=C_GREEN, ha="center", va="center")

    ax.annotate("", xy=(6.7, 2.0), xytext=(4.9, 2.0), arrowprops=dict(arrowstyle="->", lw=2.6, color=C_INK))
    ax.annotate("", xy=(6.7, 1.7), xytext=(2.6, 1.7), arrowprops=dict(arrowstyle="->", lw=2.6, color=C_INK))
    ax.text(5.6, 2.35, "форма принимает два вектора", fontsize=11, color=C_INK, ha="center")
    ax.text(7.95, 0.8, "и возвращает одно число", fontsize=11, color=C_INK, ha="center")
    ax.text(0.7, 3.25, "Билинейная форма как двуместное линейное правило", fontsize=14, color=C_INK, weight="bold")
    _save(fig, out_name)


def draw_bilinear_matrix_from_basis(out_name: str = "bilinear_matrix_from_basis.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(9.4, 4.8))
    ax.axis("off")
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)

    coords = [(1.6, 4.2), (1.6, 2.7), (1.6, 1.2), (4.2, 4.2), (4.2, 2.7), (4.2, 1.2)]
    labels = [r"$B(e_1,e_1)$", r"$B(e_1,e_2)$", r"$B(e_1,e_3)$", r"$B(e_2,e_1)$", r"$B(e_2,e_2)$", r"$B(e_2,e_3)$"]
    colors = [C_BLUE, C_ORANGE, C_GREEN, C_ORANGE, C_BLUE, C_PURPLE]
    for (x, y), label, color in zip(coords, labels, colors):
        rect = Rectangle((x - 0.65, y - 0.42), 1.3, 0.84, facecolor=color, edgecolor=C_INK, linewidth=1.0, alpha=0.28)
        ax.add_patch(rect)
        ax.text(x, y, label, ha="center", va="center", fontsize=11)

    ax.text(2.9, 5.15, "значения формы на парах базисных векторов", ha="center", fontsize=12, color=C_INK)
    ax.annotate("", xy=(7.2, 3.0), xytext=(5.4, 3.0), arrowprops=dict(arrowstyle="->", lw=2.6, color=C_INK))

    matrix_box = Rectangle((7.5, 1.3), 3.3, 3.4, facecolor="#f3f1e8", edgecolor=C_GRAY, linewidth=1.4)
    ax.add_patch(matrix_box)
    ax.text(9.15, 3.95, r"$A=(a_{ij})$", ha="center", va="center", fontsize=16, color=C_INK)
    ax.text(9.15, 2.95, r"$a_{ij}=B(e_i,e_j)$", ha="center", va="center", fontsize=13, color=C_INK)
    ax.text(9.15, 2.05, r"$B(x,y)=X^TAY$", ha="center", va="center", fontsize=15, color=C_PURPLE)
    ax.text(0.7, 5.55, "Матрица билинейной формы строится по базису", fontsize=15, weight="bold", color=C_INK)
    _save(fig, out_name)


def draw_change_of_basis_congruence(out_name: str = "change_of_basis_congruence.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(10.0, 4.2))
    ax.axis("off")
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5)

    blocks = [
        (1.0, 1.65, 1.4, 1.1, C_BLUE, r"$C^T$"),
        (3.1, 1.65, 1.4, 1.1, C_ORANGE, r"$A$"),
        (5.2, 1.65, 1.4, 1.1, C_GREEN, r"$C$"),
        (8.7, 1.65, 1.7, 1.1, C_PURPLE, r"$A'$"),
    ]
    for x, y, w, h, color, label in blocks:
        ax.add_patch(Rectangle((x, y), w, h, facecolor=color, edgecolor=C_INK, linewidth=1.1, alpha=0.34))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=18)

    ax.text(2.75, 2.2, r"$\cdot$", fontsize=26, ha="center", va="center")
    ax.text(4.85, 2.2, r"$\cdot$", fontsize=26, ha="center", va="center")
    ax.annotate("", xy=(8.25, 2.2), xytext=(6.95, 2.2), arrowprops=dict(arrowstyle="->", lw=2.8, color=C_INK))
    ax.text(7.6, 2.55, "новая запись", fontsize=10, color=C_INK, ha="center")
    ax.text(1.0, 3.55, r"При замене базиса: $A' = C^TAC$", fontsize=18, weight="bold", color=C_INK)
    ax.text(1.0, 1.0, "Для билинейной формы матрица перехода действует с двух сторон.\nЭто конгруэнтность, а не подобие.", fontsize=11, color=C_INK)
    _save(fig, out_name)


def draw_orthogonal_complement_plane(out_name: str = "orthogonal_complement_plane.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(6.6, 6.0))
    _setup_2d(ax, lim=2.5)

    t = np.linspace(-2.3, 2.3, 200)
    ax.plot(t, t, color=C_BLUE, lw=3.0, label=r"$U=\mathrm{span}(1,1)$")
    ax.plot(t, -t, color=C_ORANGE, lw=3.0, label=r"$U^\perp=\mathrm{span}(1,-1)$")

    v1 = np.array([1.4, 1.4])
    v2 = np.array([1.5, -1.5])
    ax.annotate("", xy=v1, xytext=(0, 0), arrowprops=dict(arrowstyle="->", lw=2.4, color=C_BLUE))
    ax.annotate("", xy=v2, xytext=(0, 0), arrowprops=dict(arrowstyle="->", lw=2.4, color=C_ORANGE))
    ax.text(1.55, 1.45, r"$u$", color=C_BLUE, fontsize=11)
    ax.text(1.58, -1.42, r"$v$", color=C_ORANGE, fontsize=11)
    ax.text(-2.3, 2.05, r"$\langle u,v\rangle=0$", fontsize=12, color=C_INK, bbox=dict(boxstyle="round,pad=0.25", facecolor="#f3f1e8", edgecolor=C_GRAY))
    ax.set_title("Ортогональное дополнение на плоскости", fontsize=13, weight="bold")
    ax.legend(loc="lower left", fontsize=9, framealpha=0.95)
    _save(fig, out_name)


def draw_orthogonal_basis_diagonalization(out_name: str = "orthogonal_basis_diagonalization.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(8.8, 4.4))
    ax.axis("off")
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5)

    points = [(1.3, 2.5), (3.3, 2.5), (5.3, 2.5)]
    labels = [r"$e_1$", r"$e_2$", r"$e_3$"]
    colors = [C_BLUE, C_ORANGE, C_GREEN]
    for (x, y), label, color in zip(points, labels, colors):
        circ = plt.Circle((x, y), 0.34, facecolor=color, edgecolor=C_INK, linewidth=1.1, alpha=0.88)
        ax.add_patch(circ)
        ax.text(x, y, label, ha="center", va="center", fontsize=14)

    ax.text(2.3, 3.25, r"$B(e_1,e_2)=0$", fontsize=11, color=C_INK, ha="center")
    ax.text(4.3, 3.25, r"$B(e_2,e_3)=0$", fontsize=11, color=C_INK, ha="center")
    ax.text(3.3, 1.65, r"$B(e_1,e_3)=0$", fontsize=11, color=C_INK, ha="center")

    for i in range(len(points) - 1):
        arrow = FancyArrowPatch((points[i][0] + 0.45, 2.5), (points[i + 1][0] - 0.45, 2.5), arrowstyle="->", mutation_scale=18, linewidth=1.8, color=C_GRAY)
        ax.add_patch(arrow)

    box = Rectangle((7.0, 1.35), 2.8, 2.2, facecolor="#f3f1e8", edgecolor=C_GRAY, linewidth=1.3)
    ax.add_patch(box)
    ax.text(8.4, 3.0, r"$\mathrm{diag}(\lambda_1,\lambda_2,\lambda_3)$", ha="center", va="center", fontsize=15, color=C_PURPLE)
    ax.text(8.4, 2.2, "в ортогональном базисе\nматрица становится диагональной", ha="center", va="center", fontsize=11, color=C_INK)
    ax.annotate("", xy=(6.7, 2.45), xytext=(5.8, 2.45), arrowprops=dict(arrowstyle="->", lw=2.4, color=C_INK))
    ax.text(0.6, 4.2, "Ортогональный базис устраняет смешанные члены", fontsize=15, weight="bold", color=C_INK)
    _save(fig, out_name)


def draw_inertia_signature_bars(out_name: str = "inertia_signature_bars.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(8.3, 4.8))
    labels = ["плюсы", "минусы", "нули"]
    values = [3, 2, 1]
    colors = [C_GREEN, C_ORANGE, C_GRAY]
    bars = ax.bar(labels, values, color=colors, edgecolor=C_INK, alpha=0.82, width=0.58)
    ax.set_ylim(0, 3.8)
    ax.set_ylabel("число направлений")
    ax.set_title("Сигнатура формы: положительные, отрицательные и нулевые квадраты", fontsize=13, weight="bold")
    ax.grid(True, axis="y")
    for rect, val in zip(bars, values):
        ax.text(rect.get_x() + rect.get_width() / 2, val + 0.08, str(val), ha="center", va="bottom", fontsize=12, color=C_INK)
    ax.text(1.15, 3.25, r"нормальный вид: $z_1^2+\cdots+z_p^2-z_{p+1}^2-\cdots-z_{p+q}^2$", fontsize=11, color=C_INK, ha="center")
    _save(fig, out_name)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_bilinear_pairing_scheme()
    draw_bilinear_matrix_from_basis()
    draw_change_of_basis_congruence()
    draw_orthogonal_complement_plane()
    draw_orthogonal_basis_diagonalization()
    draw_inertia_signature_bars()
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
