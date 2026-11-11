"""
Графики и анимации для лекции tracks/shad/algebra/1_Substitutions (подстановки).

Палитра согласована с shared/lecture_visual_generation/lecture_visual_design_system.md
"""

from __future__ import annotations

import math
from pathlib import Path
from tempfile import TemporaryDirectory

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Rectangle
from PIL import Image

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
MAIN_PERMUTATION = [4, 5, 1, 3, 2, 6]


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
    colors: list[str] | None = None,
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
    colors = colors or [C_BLUE] * n
    for j, x in enumerate(xs):
        ax.text(x, y_top, str(j + 1), ha="center", va="center", fontsize=16, weight="bold", color=C_INK)
        ax.text(x, y_bot, str(sigma[j]), ha="center", va="center", fontsize=16, weight="bold", color=colors[j])
    for j, x in enumerate(xs):
        ax.annotate(
            "",
            xy=(x, y_bot + 0.06),
            xytext=(x, y_top - 0.06),
            arrowprops=dict(arrowstyle="-|>", color=colors[j], lw=2.2, mutation_scale=12),
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
            shrinkA=19,
            shrinkB=19,
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


def draw_disjoint_cycles_commute(out_name: str = "disjoint_cycles_commute.png"):
    """Точная схема для независимых циклов: (1 3 5) и (2 4)."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(9.8, 4.8))
    ax.set_facecolor(C_BG)
    fig.patch.set_facecolor(C_BG)
    ax.set_aspect("equal")
    ax.axis("off")

    cycles = [
        ([1, 3, 5], (-1.8, 0.0), C_BLUE, r"$\alpha=(1\ 3\ 5)$"),
        ([2, 4], (2.0, 0.0), C_ORANGE, r"$\beta=(2\ 4)$"),
    ]

    for labels, center, color, title in cycles:
        cx, cy = center
        n = len(labels)
        angles = np.linspace(np.pi / 2, np.pi / 2 + 2 * np.pi, n, endpoint=False)
        pos = {}
        for label, angle in zip(labels, angles):
            x = cx + 0.82 * np.cos(angle)
            y = cy + 0.82 * np.sin(angle)
            pos[label] = (x, y)
            ax.scatter([x], [y], s=700, c=color, edgecolors=C_INK, linewidths=1.4, zorder=3)
            ax.text(x, y, str(label), ha="center", va="center", fontsize=14, weight="bold", color=C_INK)
        for a, b in zip(labels, labels[1:] + labels[:1]):
            x1, y1 = pos[a]
            x2, y2 = pos[b]
            ax.add_patch(
                FancyArrowPatch(
                    (x1, y1),
                    (x2, y2),
                    connectionstyle="arc3,rad=0.18",
                    arrowstyle="-|>",
                    mutation_scale=13,
                    lw=2.0,
                    color=C_INK,
                    alpha=0.82,
                    shrinkA=18,
                    shrinkB=18,
                    zorder=2,
                )
            )
        ax.text(cx, cy - 1.35, title, ha="center", va="center", fontsize=13, color=C_INK)

    ax.text(-1.8, 1.55, r"$\{1,3,5\}$", ha="center", fontsize=12, color=C_BLUE)
    ax.text(2.0, 1.55, r"$\{2,4\}$", ha="center", fontsize=12, color=C_ORANGE)
    ax.text(0.1, 0.15, r"$\alpha\beta=\beta\alpha$", ha="center", va="center", fontsize=18, weight="bold", color=C_INK)
    ax.text(
        0.1,
        -0.92,
        "циклы действуют на разных элементах",
        ha="center",
        va="center",
        fontsize=11,
        color=C_INK,
    )
    ax.set_xlim(-3.4, 3.4)
    ax.set_ylim(-1.9, 2.0)
    ax.set_title("Независимые циклы коммутируют", fontsize=15, weight="bold", color=C_INK)
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
    cycle: list[int], *, out_name: str, duration_ms: int = 850, universe: int | None = None
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
        for step in range(len(edges)):
            fig, ax = plt.subplots(figsize=(6.6, 6.6))
            ax.set_facecolor(C_BG)
            ax.set_aspect("equal")
            for k in range(1, m + 1):
                x, y = pos[k]
                ax.scatter([x], [y], s=820, c=C_PANEL, edgecolors=C_INK, linewidths=1.4, zorder=3)
                ax.text(x, y, str(k), ha="center", va="center", fontsize=14, weight="bold", color=C_INK)
            highlight = step
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
                    shrinkA=18,
                    shrinkB=18,
                    zorder=2,
                )
                ax.add_patch(arr)
            ax.set_xlim(-1.45, 1.45)
            ax.set_ylim(-1.45, 1.45)
            ax.axis("off")
            a, b = edges[step]
            ax.set_title(f"Шаг {step + 1}: {a} → {b}", fontsize=14, weight="bold", color=C_INK)
            fig.patch.set_facecolor(C_BG)
            fig.tight_layout()
            fp = tmp_path / f"f_{step:03d}.png"
            fig.savefig(fp, dpi=130, bbox_inches="tight", facecolor=C_BG)
            plt.close(fig)
            with Image.open(fp) as frame:
                frames.append(np.array(frame.convert("RGB")))
    images = [Image.fromarray(frame) for frame in frames]
    images[0].save(
        ASSETS / out_name, save_all=True, append_images=images[1:],
        duration=duration_ms, loop=0, disposal=2,
    )


def gif_transposition_swap(out_name: str = "transposition_swap.gif", duration_ms: int = 80):
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
            y_left = 0.3 * np.sin(np.pi * t)
            y_right = -y_left
            fig, ax = plt.subplots(figsize=(7.2, 3.2))
            ax.set_facecolor(C_BG)
            fig.patch.set_facecolor(C_BG)
            ax.plot([-1.4, 1.4], [0, 0], color=C_GRAY, lw=2)
            ax.scatter([x_left], [y_left], s=700, c=C_BLUE, edgecolors=C_INK, linewidths=1.3, zorder=3)
            ax.scatter([x_right], [y_right], s=700, c=C_ORANGE, edgecolors=C_INK, linewidths=1.3, zorder=3)
            ax.text(x_left, y_left, "1", ha="center", va="center", fontsize=15, weight="bold", color=C_INK)
            ax.text(x_right, y_right, "3", ha="center", va="center", fontsize=15, weight="bold", color=C_INK)
            ax.set_xlim(-1.55, 1.55)
            ax.set_ylim(-0.55, 0.55)
            ax.axis("off")
            ax.set_title("Два обмена $(1\\ 3)$ возвращают исходный порядок", fontsize=12, weight="bold", color=C_INK)
            fig.tight_layout()
            fp = tmp_path / f"sw_{i:03d}.png"
            fig.savefig(fp, dpi=130, bbox_inches="tight", facecolor=C_BG)
            plt.close(fig)
            with Image.open(fp) as frame:
                frames.append(np.array(frame.convert("RGB")))
    images = [Image.fromarray(frame) for frame in frames]
    # Обратный проход показывает второе применение, без скачка между концом и началом.
    images += images[-2:0:-1]
    durations = [duration_ms] * len(images)
    durations[0] = durations[n_frames - 1] = 750
    images[0].save(
        ASSETS / out_name, save_all=True, append_images=images[1:],
        duration=durations, loop=0, disposal=2,
    )


def _save(fig, filename):
    fig.tight_layout(pad=1.4)
    fig.savefig(ASSETS / filename, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def _node(ax, x, y, label, color=C_PANEL, size=600):
    ax.scatter([x], [y], s=size, color=color, edgecolor=C_INK, linewidth=1.3, zorder=3)
    ax.text(x, y, str(label), ha="center", va="center", fontsize=13, weight="bold", zorder=4)


def _arrow(ax, start, end, color=C_INK, rad=0.0, width=1.8):
    ax.add_patch(FancyArrowPatch(
        start, end, connectionstyle=f"arc3,rad={rad}", arrowstyle="-|>",
        mutation_scale=14, linewidth=width, color=color, shrinkA=17, shrinkB=17, zorder=2,
    ))


def permutation_cycles(permutation):
    unseen = set(range(1, len(permutation) + 1))
    cycles = []
    while unseen:
        start = min(unseen)
        cycle = []
        value = start
        while value in unseen:
            cycle.append(value)
            unseen.remove(value)
            value = permutation[value - 1]
        cycles.append(cycle)
    return cycles


def draw_composition_orders():
    _apply_style()
    alpha, beta = [2, 1, 3], [1, 3, 2]
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.7))
    for ax, first, second, label, names in [
        (axes[0], beta, alpha, r"$\alpha\beta=(1\ 2\ 3)$", [r"$\beta$", r"$\alpha$"]),
        (axes[1], alpha, beta, r"$\beta\alpha=(1\ 3\ 2)$", [r"$\alpha$", r"$\beta$"]),
    ]:
        route = [1, first[0], second[first[0] - 1]]
        for column in range(3):
            for value in range(1, 4):
                _node(ax, column * 1.6, 3 - value, value,
                      C_ORANGE if value == route[column] else C_PANEL)
        for column, permutation in enumerate([first, second]):
            for value, target in enumerate(permutation, 1):
                selected = value == route[column]
                _arrow(ax, (column * 1.6, 3 - value), ((column + 1) * 1.6, 3 - target),
                       color=C_ORANGE if selected else C_GRAY, width=2.6 if selected else 1.1)
            ax.text(column * 1.6 + 0.8, 2.55, names[column], ha="center", fontsize=15)
        for x, text in [(0, "вход"), (1.6, "шаг 1"), (3.2, "шаг 2")]:
            ax.text(x, -0.45, text, ha="center", fontsize=10)
        ax.text(1.6, -0.95, " → ".join(map(str, route)), ha="center", fontsize=16, color=C_ORANGE)
        ax.set_title(label, fontsize=17, pad=15)
        ax.set_xlim(-0.45, 3.65)
        ax.set_ylim(-1.2, 2.85)
        ax.axis("off")
    _save(fig, "composition_orders.png")


def draw_main_cycles():
    _apply_style()
    fig, axes = plt.subplots(1, 3, figsize=(9.6, 3.6), gridspec_kw={"width_ratios": [1.4, 1.1, 0.8]})
    for ax, cycle, color in zip(axes, permutation_cycles(MAIN_PERMUTATION), [C_BLUE, C_ORANGE, C_PANEL]):
        k = len(cycle)
        xs, ys = circle_positions(k, radius=0.75)
        if k == 1:
            xs, ys = [0], [0]
        positions = {label: (x, y) for label, x, y in zip(cycle, xs, ys)}
        for label, position in positions.items():
            _node(ax, *position, label, color, size=780)
        if k > 1:
            for label in cycle:
                _arrow(ax, positions[label], positions[MAIN_PERMUTATION[label - 1]], rad=0.16)
        ax.text(0, -1.1, "(" + "  ".join(map(str, cycle)) + ")", ha="center", fontsize=16)
        ax.set_title(f"Длина {k}" if k > 1 else "Неподвижная точка", fontsize=12)
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1.4, 1.1)
        ax.set_aspect("equal")
        ax.axis("off")
    _save(fig, "main_cycles.png")


def draw_cycle_returns():
    _apply_style()
    fig, ax = plt.subplots(figsize=(10.4, 3.4))
    starts = [cycle[0] for cycle in permutation_cycles(MAIN_PERMUTATION)]
    lengths = [len(cycle) for cycle in permutation_cycles(MAIN_PERMUTATION)]
    period = math.lcm(*lengths)
    for row, (start, length) in enumerate(zip(starts, lengths)):
        y = 2 - row
        value = start
        ax.text(-0.72, y, f"Элемент {start} · цикл длины {length}", ha="right", va="center", fontsize=11)
        for m in range(period + 1):
            color = C_BLUE if row == 0 else C_ORANGE if row == 1 else C_PANEL
            ax.add_patch(Rectangle((m - 0.38, y - 0.34), 0.76, 0.68,
                                   facecolor=color if value == start else C_BG,
                                   edgecolor=C_GRAY, linewidth=0.9))
            ax.text(m, y, str(value), ha="center", va="center", fontsize=15)
            value = MAIN_PERMUTATION[value - 1]
    for m in range(period + 1):
        ax.text(m, 2.8, str(m), ha="center", fontsize=12)
    ax.text(-0.72, 2.8, "Число применений m", ha="right", fontsize=11)
    ax.add_patch(Rectangle((period - 0.46, -0.43), 0.92, 2.86, fill=False, edgecolor=C_INK, linewidth=2))
    ax.text(0, -0.87, "начало", ha="center", fontsize=10)
    ax.text(period, -0.87, "первый возврат всех", ha="right", fontsize=11, weight="bold")
    ax.set_xlim(-3.1, period + 0.65)
    ax.set_ylim(-1.12, 3.05)
    ax.axis("off")
    _save(fig, "cycle_returns.png")


def draw_inversions_grid():
    _apply_style()
    p = MAIN_PERMUTATION
    n = len(p)
    inversions = [(i, j) for i in range(n) for j in range(i + 1, n) if p[i] > p[j]]
    fig, ax = plt.subplots(figsize=(8.3, 6.1))
    for i in range(n):
        for j in range(n):
            valid = i < j
            inverted = (i, j) in inversions
            color = C_ORANGE if inverted else C_BG if valid else C_PANEL
            ax.add_patch(Rectangle((j - 0.48, n - 1 - i - 0.48), 0.96, 0.96,
                                   facecolor=color, edgecolor=C_GRAY, linewidth=0.6))
            if valid:
                ax.text(j, n - 1 - i, f"{p[i]} > {p[j]}" if inverted else "—",
                        ha="center", va="center", fontsize=11, color=C_INK if inverted else C_GRAY)
        ax.text(-0.8, n - 1 - i, f"i={i + 1},  σ(i)={p[i]}", ha="right", va="center", fontsize=11)
        ax.text(i, n - 0.05, f"j={i + 1}", ha="center", fontsize=11)
    ax.text(2.5, -1.05, f"Выделено {len(inversions)} инверсий · серые клетки не считаем", ha="center", fontsize=12)
    ax.set_xlim(-2.6, n - 0.3)
    ax.set_ylim(-1.4, n + 0.3)
    ax.set_aspect("equal")
    ax.axis("off")
    _save(fig, "inversions_grid.png")


def draw_cycle_join_split():
    _apply_style()
    base = MAIN_PERMUTATION[:5]
    positions = {1: (-0.95, 0.7), 4: (-1.5, -0.5), 3: (-0.4, -0.5), 2: (0.9, 0.7), 5: (0.9, -0.5)}
    fig, axes = plt.subplots(2, 2, figsize=(10.5, 6.8))
    for row, (a, b) in enumerate([(1, 2), (1, 4)]):
        changed = base.copy()
        changed[a - 1], changed[b - 1] = changed[b - 1], changed[a - 1]
        for column, p in enumerate([base, changed]):
            ax = axes[row, column]
            for label, position in positions.items():
                _node(ax, *position, label, C_ORANGE if label in (a, b) else C_PANEL)
            for label, target in enumerate(p, 1):
                if label != target:
                    _arrow(ax, positions[label], positions[target],
                           color=C_ORANGE if label in (a, b) else C_INK,
                           rad=0.12, width=2.2 if label in (a, b) else 1.5)
                else:
                    x, y = positions[label]
                    ax.text(x, y - 0.48, "фиксирована", ha="center", fontsize=9)
            count = len(permutation_cycles(p))
            ax.set_title(("До обмена" if column == 0 else f"После правого умножения на ({a} {b})")
                         + f" · циклов: {count}", fontsize=11, pad=12)
            ax.set_xlim(-2.0, 1.65)
            ax.set_ylim(-1.2, 1.2)
            ax.set_aspect("equal")
            ax.axis("off")
    _save(fig, "cycle_join_split.png")


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_mapping_diagram(
        MAIN_PERMUTATION,
        title=r"Аргументы сверху, образы снизу: $\sigma=[4,5,1,3,2,6]$",
        out_name="mapping_six_points.png",
        figsize=(9, 2.7),
        colors=[C_BLUE, C_ORANGE, C_BLUE, C_BLUE, C_ORANGE, C_GRAY],
    )
    draw_cycle_on_circle(
        [1, 4, 3],
        title=r"Цикл $(1\ 4\ 3)$ на $\{1,\dots,6\}$ (остальные элементы фиксированы)",
        out_name="cycle_1_4_3.png",
        universe=6,
    )
    draw_composition_orders()
    draw_main_cycles()
    draw_cycle_returns()
    draw_cycle_join_split()
    draw_inversions_grid()
    gif_cycle_highlight([1, 4, 3], out_name="cycle_1_4_3_trace.gif", universe=6)
    gif_transposition_swap()
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
