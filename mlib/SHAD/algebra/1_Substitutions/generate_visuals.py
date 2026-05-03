"""
Графики и анимации для лекции SHAD/algebra/1_Substitutions (подстановки).

Палитра согласована с SHAD/lecture_visual_generation/lecture_visual_design_system.md
"""

from __future__ import annotations

import math
from pathlib import Path
from tempfile import TemporaryDirectory

import imageio.v2 as imageio
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

# Lecture visual tokens (Claude-inspired / MLIB SHAD)
C_BG = "#faf9f5"
C_INK = "#141413"
C_GRAY = "#b0aea5"
C_PANEL = "#e8e6dc"
C_ORANGE = "#d97757"
C_BLUE = "#6a9bcc"
C_GREEN = "#788c5d"


def _apply_style():
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
            "grid.alpha": 0.35,
            "font.size": 11,
        }
    )


def circle_positions(n: int, radius: float = 1.0, start_deg: float = 90.0):
    """Углы в градусах от start_deg против часовой (matplotlib-style)."""
    deg = np.linspace(0, 360, n, endpoint=False) + start_deg
    rad = np.deg2rad(deg)
    return radius * np.cos(rad), radius * np.sin(rad)


def draw_mapping_diagram(
    sigma: list[int],
    *,
    title: str,
    out_name: str,
    figsize=(9, 5.2),
):
    """
    sigma[i] — образ элемента (i+1), т.е. sigma[j] = sigma( j+1 ).
    """
    _apply_style()
    n = len(sigma)
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_facecolor(C_BG)
    y_top, y_bot = 1.0, 0.0
    xs = np.linspace(0.08, 0.92, n)
    for j, x in enumerate(xs):
        ax.text(x, y_top, str(j + 1), ha="center", va="center", fontsize=16, weight="bold", color=C_INK)
        ax.text(x, y_bot, str(sigma[j]), ha="center", va="center", fontsize=16, weight="bold", color=C_ORANGE)
    for j, x in enumerate(xs):
        ax.annotate(
            "",
            xy=(x, y_bot + 0.06),
            xytext=(x, y_top - 0.06),
            arrowprops=dict(arrowstyle="-|>", color=C_BLUE, lw=2.2, mutation_scale=12),
        )
    ax.plot([xs.min() - 0.06, xs.max() + 0.06], [y_top, y_top], color=C_GRAY, lw=1.5)
    ax.plot([xs.min() - 0.06, xs.max() + 0.06], [y_bot, y_bot], color=C_GRAY, lw=1.5)
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.12, 1.12)
    ax.axis("off")
    ax.set_title(title, fontsize=14, weight="bold", pad=12, color=C_INK)
    fig.patch.set_facecolor(C_BG)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def draw_cycle_on_circle(cycle: list[int], *, title: str, out_name: str, universe: int | None = None):
    """cycle — список вершин цикла в порядке обхода, например [1, 4, 3]. universe — число вершин 1..m (иначе m=max(cycle))."""
    _apply_style()
    m = universe if universe is not None else max(cycle)
    # позиции всех меток 1..m на одной окружности
    xs, ys = circle_positions(m, radius=1.15, start_deg=90)
    pos = {k: (xs[k - 1], ys[k - 1]) for k in range(1, m + 1)}
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_facecolor(C_BG)
    ax.set_aspect("equal")
    for k in range(1, m + 1):
        x, y = pos[k]
        color = C_ORANGE if k in cycle else C_PANEL
        ax.scatter([x], [y], s=900, c=color, edgecolors=C_INK, linewidths=1.6, zorder=3)
        ax.text(x, y, str(k), ha="center", va="center", fontsize=15, weight="bold", color=C_INK)
    for a, b in zip(cycle, cycle[1:] + cycle[:1]):
        x1, y1 = pos[a]
        x2, y2 = pos[b]
        arr = FancyArrowPatch(
            (x1, y1),
            (x2, y2),
            connectionstyle="arc3,rad=0.12",
            arrowstyle="-|>",
            mutation_scale=14,
            lw=2.4,
            color=C_BLUE,
            zorder=2,
        )
        ax.add_patch(arr)
    ax.set_xlim(-1.55, 1.55)
    ax.set_ylim(-1.55, 1.55)
    ax.axis("off")
    ax.set_title(title, fontsize=13, weight="bold", color=C_INK)
    fig.patch.set_facecolor(C_BG)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def draw_disjoint_transpositions(out_name: str = "disjoint_transpositions.png"):
    """Три независимых транспозиции из лекции: (1 3), (2 5), (4 6)."""
    _apply_style()
    pairs = [(1, 3), (2, 5), (4, 6)]
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.6))
    fig.patch.set_facecolor(C_BG)
    for ax, (a, b) in zip(axes, pairs):
        ax.set_facecolor(C_BG)
        ax.set_aspect("equal")
        for x, lab, c in ((-0.65, a, C_BLUE), (0.65, b, C_ORANGE)):
            ax.scatter([x], [0], s=700, c=c, edgecolors=C_INK, linewidths=1.4, zorder=3)
            ax.text(x, 0, str(lab), ha="center", va="center", fontsize=15, weight="bold", color=C_INK)
        arr = FancyArrowPatch(
            (-0.45, 0.08),
            (0.45, 0.08),
            arrowstyle="<->",
            mutation_scale=12,
            lw=2.2,
            color=C_INK,
        )
        ax.add_patch(arr)
        ax.set_xlim(-1.1, 1.1)
        ax.set_ylim(-0.55, 0.55)
        ax.axis("off")
        ax.set_title(rf"$( {a}\ {b} )$", fontsize=14, color=C_INK)
    fig.suptitle("Независимые транспозиции в разложении $\\sigma$", fontsize=14, weight="bold", y=1.05, color=C_INK)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def draw_factorial_growth(out_name: str = "factorial_growth.png"):
    _apply_style()
    ns = np.arange(1, 11)
    facts = np.array([math.factorial(int(n)) for n in ns])
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.set_facecolor(C_BG)
    fig.patch.set_facecolor(C_BG)
    ax.semilogy(ns, facts, "o-", color=C_ORANGE, lw=2.4, markersize=7, markerfacecolor=C_BLUE, markeredgecolor=C_INK)
    ax.set_xticks(ns)
    ax.set_xlabel("$n$", fontsize=13, color=C_INK)
    ax.set_ylabel("$n!$ (логарифмическая шкала)", fontsize=12, color=C_INK)
    ax.set_title("Рост числа подстановок: $|S_n| = n!$", fontsize=14, weight="bold", color=C_INK)
    ax.grid(True, which="both", linestyle="--", alpha=0.45)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def gif_cycle_highlight(
    cycle: list[int], *, out_name: str, duration: float = 0.22, universe: int | None = None
):
    """Подсветка рёбер цикла по очереди (метафора «обхода орбиты»)."""
    _apply_style()
    m = universe if universe is not None else max(cycle)
    xs, ys = circle_positions(m, radius=1.12, start_deg=90)
    pos = {k: (xs[k - 1], ys[k - 1]) for k in range(1, m + 1)}
    edges = list(zip(cycle, cycle[1:] + cycle[:1]))
    frames = []
    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for step in range(len(edges) + 6):
            fig, ax = plt.subplots(figsize=(6.6, 6.6))
            ax.set_facecolor(C_BG)
            ax.set_aspect("equal")
            for k in range(1, m + 1):
                x, y = pos[k]
                ax.scatter([x], [y], s=820, c=C_PANEL, edgecolors=C_INK, linewidths=1.4, zorder=3)
                ax.text(x, y, str(k), ha="center", va="center", fontsize=14, weight="bold", color=C_INK)
            highlight = step % len(edges) if step < len(edges) * 4 else len(edges) - 1
            for idx, (a, b) in enumerate(edges):
                x1, y1 = pos[a]
                x2, y2 = pos[b]
                col = C_ORANGE if idx == highlight else C_BLUE
                lw = 3.2 if idx == highlight else 1.9
                arr = FancyArrowPatch(
                    (x1, y1),
                    (x2, y2),
                    connectionstyle="arc3,rad=0.1",
                    arrowstyle="-|>",
                    mutation_scale=13,
                    lw=lw,
                    color=col,
                    alpha=0.95 if idx == highlight else 0.55,
                    zorder=2,
                )
                ax.add_patch(arr)
            ax.set_xlim(-1.45, 1.45)
            ax.set_ylim(-1.45, 1.45)
            ax.axis("off")
            ax.set_title("Цикл $(1\\ 4\\ 3)$: обход по стрелкам", fontsize=12, weight="bold", color=C_INK)
            fig.patch.set_facecolor(C_BG)
            fig.tight_layout()
            fp = tmp_path / f"f_{step:03d}.png"
            fig.savefig(fp, dpi=130, bbox_inches="tight", facecolor=C_BG)
            plt.close(fig)
            frames.append(imageio.imread(fp))
    imageio.mimsave(ASSETS / out_name, frames, duration=duration, loop=0)


def gif_transposition_swap(out_name: str = "transposition_swap.gif", duration: float = 0.12):
    """Две метки меняются местами на отрезке (транспозиция)."""
    _apply_style()
    frames = []
    n_frames = 36
    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for i in range(n_frames):
            t = i / (n_frames - 1)
            # плавная интерполяция позиций x=-1 и x=1
            u = 0.5 - 0.5 * np.cos(np.pi * t)
            x_left = -1.0 + 2.0 * u
            x_right = 1.0 - 2.0 * u
            fig, ax = plt.subplots(figsize=(7.2, 3.2))
            ax.set_facecolor(C_BG)
            fig.patch.set_facecolor(C_BG)
            ax.plot([-1.4, 1.4], [0, 0], color=C_GRAY, lw=2)
            ax.scatter([x_left], [0], s=700, c=C_BLUE, edgecolors=C_INK, linewidths=1.3, zorder=3)
            ax.scatter([x_right], [0], s=700, c=C_ORANGE, edgecolors=C_INK, linewidths=1.3, zorder=3)
            ax.text(x_left, 0, "1", ha="center", va="center", fontsize=15, weight="bold", color=C_INK)
            ax.text(x_right, 0, "3", ha="center", va="center", fontsize=15, weight="bold", color=C_INK)
            ax.set_xlim(-1.55, 1.55)
            ax.set_ylim(-0.55, 0.55)
            ax.axis("off")
            ax.set_title("Транспозиция $(1\\ 3)$: обмен двух элементов", fontsize=12, weight="bold", color=C_INK)
            fig.tight_layout()
            fp = tmp_path / f"sw_{i:03d}.png"
            fig.savefig(fp, dpi=130, bbox_inches="tight", facecolor=C_BG)
            plt.close(fig)
            frames.append(imageio.imread(fp))
    imageio.mimsave(ASSETS / out_name, frames, duration=duration, loop=0)


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    # Пример из §2.2: 1->3, 2->1, 3->4, 4->2
    sigma4 = [3, 1, 4, 2]
    draw_mapping_diagram(
        sigma4,
        title=r"Подстановка $\sigma$ на $\{1,2,3,4\}$ (образы внизу)",
        out_name="mapping_four_points.png",
    )
    draw_cycle_on_circle(
        [1, 4, 3],
        title=r"Цикл $(1\ 4\ 3)$ на $\{1,\dots,6\}$ (остальные элементы фиксированы)",
        out_name="cycle_1_4_3.png",
        universe=6,
    )
    draw_disjoint_transpositions()
    draw_factorial_growth()
    gif_cycle_highlight([1, 4, 3], out_name="cycle_1_4_3_trace.gif", universe=6)
    gif_transposition_swap()
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
