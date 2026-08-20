"""
Иллюстрации для темы о теореме Гамильтона–Кэли и жордановой форме.

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


def draw_cayley_hamilton_polynomial_scheme(out_name: str = "cayley_hamilton_polynomial_scheme.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(9.0, 3.8))
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)

    blocks = [
        (0.6, 1.4, 1.3, 1.0, C_BLUE, r"$A^n$"),
        (2.3, 1.4, 1.7, 1.0, C_PURPLE, r"$c_{n-1}A^{n-1}$"),
        (4.4, 1.4, 1.0, 1.0, C_PANEL, r"$\cdots$"),
        (5.8, 1.4, 1.6, 1.0, C_ORANGE, r"$c_1A$"),
        (7.8, 1.4, 1.4, 1.0, C_GREEN, r"$c_0E$"),
    ]
    for x, y, w, h, color, label in blocks:
        ax.add_patch(Rectangle((x, y), w, h, facecolor=color if color != C_PANEL else "#f2f0e7", edgecolor=C_GRAY, linewidth=1.5, alpha=0.85))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=16)

    for plus_x in [2.05, 4.15, 5.55, 7.55]:
        ax.text(plus_x, 1.9, "+", fontsize=20, ha="center", va="center", color=C_INK)

    ax.text(9.45, 1.9, "= 0", fontsize=22, ha="left", va="center", color=C_INK, weight="bold")
    ax.text(0.6, 3.15, r"Теорема Гамильтона–Кэли: $\chi_A(A)=0$", fontsize=18, weight="bold", color=C_INK)
    ax.text(0.6, 2.6, "Характеристический многочлен после подстановки матрицы даёт нулевой оператор", fontsize=11, color=C_INK)
    _save(fig, out_name)


def draw_eigenspaces_directions(out_name: str = "eigenspaces_directions.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(7.4, 6.0))
    ax.set_aspect("equal")
    ax.set_xlim(-3.2, 3.2)
    ax.set_ylim(-3.2, 3.2)
    ax.axhline(0, color=C_GRAY, lw=1.0)
    ax.axvline(0, color=C_GRAY, lw=1.0)
    ax.grid(True)

    x = np.linspace(-3, 3, 200)
    ax.plot(x, np.zeros_like(x), color=C_BLUE, lw=3.0, label=r"$E_2=\operatorname{span}(1,0)$")
    ax.plot(np.zeros_like(x), x, color=C_ORANGE, lw=3.0, label=r"$E_3=\operatorname{span}(0,1)$")

    vectors = [
        (np.array([1.0, 0.0]), np.array([2.0, 0.0]), C_BLUE, r"$v$", r"$Av=2v$"),
        (np.array([0.0, 0.8]), np.array([0.0, 2.4]), C_ORANGE, r"$w$", r"$Aw=3w$"),
        (np.array([0.9, 0.7]), np.array([1.8, 2.1]), C_PURPLE, r"$u$", r"$Au$"),
    ]

    for start, end, color, label_start, label_end in vectors:
        ax.annotate("", xy=start, xytext=(0, 0), arrowprops=dict(arrowstyle="->", lw=2.1, color=color, alpha=0.55))
        ax.annotate("", xy=end, xytext=(0, 0), arrowprops=dict(arrowstyle="->", lw=2.8, color=color))
        ax.text(start[0] + 0.08, start[1] + 0.08, label_start, color=color, fontsize=11)
        ax.text(end[0] + 0.08, end[1] + 0.08, label_end, color=color, fontsize=11)

    ax.text(-3.0, 2.75, "На собственном подпространстве\nоператор не меняет направление", fontsize=11, color=C_INK)
    ax.text(0.95, -1.2, "обычный вектор\nобычно меняет направление", fontsize=10, color=C_PURPLE)
    ax.set_title("Собственные подпространства как устойчивые направления", fontsize=13, weight="bold")
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.legend(loc="lower left", fontsize=9, framealpha=0.95)
    _save(fig, out_name)


def draw_nilpotent_jordan_chain(out_name: str = "nilpotent_jordan_chain.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(8.8, 3.6))
    ax.axis("off")
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 3.5)

    points = [(1.0, 1.8), (3.0, 1.8), (5.0, 1.8), (7.0, 1.8), (9.0, 1.8)]
    labels = [r"$v_4$", r"$v_3$", r"$v_2$", r"$v_1$", r"$0$"]
    colors = [C_PURPLE, C_BLUE, C_GREEN, C_ORANGE, C_GRAY]

    for (x, y), label, color in zip(points, labels, colors):
        circ = plt.Circle((x, y), 0.35, facecolor=color if label != r"$0$" else "#efece2", edgecolor=C_INK, linewidth=1.3, alpha=0.9)
        ax.add_patch(circ)
        ax.text(x, y, label, ha="center", va="center", fontsize=15, color=C_INK)

    for i in range(len(points) - 1):
        arrow = FancyArrowPatch(points[i], points[i + 1], arrowstyle="->", mutation_scale=18, linewidth=2.0, color=C_INK)
        ax.add_patch(arrow)
        xm = 0.5 * (points[i][0] + points[i + 1][0])
        ax.text(xm, 2.25, r"$N$", ha="center", va="bottom", fontsize=12, color=C_INK)

    ax.text(0.8, 3.0, "Жорданова цепочка для нильпотентного оператора", fontsize=17, weight="bold")
    ax.text(0.8, 2.55, r"$Nv_1=0,\ Nv_2=v_1,\ Nv_3=v_2,\ Nv_4=v_3$", fontsize=12, color=C_INK)
    ax.text(0.8, 0.65, "Каждое применение оператора сдвигает вектор на один шаг к нулю", fontsize=11, color=C_INK)
    _save(fig, out_name)


def draw_kernel_growth_jordan_sizes(out_name: str = "kernel_growth_jordan_sizes.png") -> None:
    _apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.8))

    k = np.array([1, 2, 3, 4])
    dims = np.array([2, 4, 5, 5])
    axes[0].step(k, dims, where="mid", color=C_BLUE, lw=2.8)
    axes[0].scatter(k, dims, color=C_ORANGE, s=65, zorder=5, edgecolors=C_INK, linewidths=0.9)
    axes[0].set_xticks(k)
    axes[0].set_ylim(0, 5.6)
    axes[0].set_xlabel(r"$k$")
    axes[0].set_ylabel(r"$\dim\ker N^k$")
    axes[0].set_title(r"Рост ядер $\ker N^k$", fontsize=13, weight="bold")
    axes[0].grid(True)
    axes[0].text(1.1, 4.9, r"$2,\ 4,\ 5,\ 5$", color=C_INK, fontsize=11)

    sizes = [3, 2]
    x0 = np.arange(len(sizes))
    bars = axes[1].bar(x0, sizes, color=[C_PURPLE, C_GREEN], alpha=0.85, width=0.55, edgecolor=C_INK)
    axes[1].set_xticks(x0, ["блок 1", "блок 2"])
    axes[1].set_ylim(0, 4.0)
    axes[1].set_ylabel("размер блока")
    axes[1].set_title("Восстановленные размеры клеток", fontsize=13, weight="bold")
    axes[1].grid(True, axis="y")
    for rect, s in zip(bars, sizes):
        axes[1].text(rect.get_x() + rect.get_width() / 2, s + 0.08, str(s), ha="center", va="bottom", fontsize=12)

    fig.suptitle("Размерности ядер кодируют жорданову структуру нильпотентного оператора", fontsize=14, weight="bold")
    _save(fig, out_name)


def draw_root_subspaces_jordan_blocks(out_name: str = "root_subspaces_jordan_blocks.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(11.2, 5.0))
    ax.axis("off")
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 6)

    # Big space
    ax.add_patch(Rectangle((0.6, 1.3), 3.0, 3.4, facecolor="#f3f1e8", edgecolor=C_GRAY, linewidth=1.5))
    ax.text(2.1, 4.25, r"$V$", fontsize=22, weight="bold", ha="center")
    ax.text(2.1, 3.45, "пространство", fontsize=12, ha="center")

    # Root subspaces
    subs = [
        (4.8, 3.1, 2.2, 1.4, C_BLUE, r"$V_{\lambda_1}$"),
        (4.8, 1.4, 2.2, 1.4, C_ORANGE, r"$V_{\lambda_2}$"),
    ]
    for x, y, w, h, color, label in subs:
        ax.add_patch(Rectangle((x, y), w, h, facecolor=color, edgecolor=C_INK, linewidth=1.2, alpha=0.35))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=16)

    ax.text(4.15, 4.0, r"$=$", fontsize=24, ha="center")
    ax.text(4.1, 2.25, r"$\oplus$", fontsize=22, ha="center")

    ax.text(
        7.35,
        3.0,
        "в каждом корневом\nподпространстве\nпоявляются свои\nжордановы блоки",
        ha="center",
        va="center",
        fontsize=10.5,
        color=C_INK,
    )
    ax.annotate("", xy=(8.65, 3.7), xytext=(7.85, 3.45), arrowprops=dict(arrowstyle="->", lw=1.6, color=C_GRAY))
    ax.annotate("", xy=(8.65, 2.45), xytext=(7.85, 2.65), arrowprops=dict(arrowstyle="->", lw=1.6, color=C_GRAY))

    # Jordan blocks to the right
    ax.add_patch(Rectangle((8.9, 3.35), 2.6, 1.0, facecolor=C_BLUE, edgecolor=C_INK, linewidth=1.1, alpha=0.28))
    ax.add_patch(Rectangle((8.9, 2.0), 1.9, 1.0, facecolor=C_BLUE, edgecolor=C_INK, linewidth=1.1, alpha=0.18))
    ax.add_patch(Rectangle((8.9, 0.75), 1.2, 1.0, facecolor=C_ORANGE, edgecolor=C_INK, linewidth=1.1, alpha=0.28))
    ax.text(10.2, 3.85, r"$J_3(\lambda_1)$", ha="center", va="center", fontsize=14)
    ax.text(9.85, 2.5, r"$J_2(\lambda_1)$", ha="center", va="center", fontsize=14)
    ax.text(9.5, 1.25, r"$J_1(\lambda_2)$", ha="center", va="center", fontsize=14)
    ax.text(0.6, 5.35, "Разложение по корневым подпространствам и жордановы клетки", fontsize=16, weight="bold")
    _save(fig, out_name)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_cayley_hamilton_polynomial_scheme()
    draw_eigenspaces_directions()
    draw_nilpotent_jordan_chain()
    draw_kernel_growth_jordan_sizes()
    draw_root_subspaces_jordan_blocks()
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
