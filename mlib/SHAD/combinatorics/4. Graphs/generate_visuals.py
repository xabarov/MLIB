"""Иллюстрации для лекции про графы."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import imageio.v2 as imageio
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, Polygon, Rectangle

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
            "font.size": 11,
        }
    )


def _save(fig: plt.Figure, out_name: str) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def _setup_axis(ax: plt.Axes, xlim: tuple[float, float], ylim: tuple[float, float]) -> None:
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")


def _draw_edge(
    ax: plt.Axes,
    p: tuple[float, float],
    q: tuple[float, float],
    *,
    color: str = C_GRAY,
    lw: float = 2.0,
    alpha: float = 1.0,
    zorder: int = 1,
    arrow: bool = False,
) -> None:
    if arrow:
        ax.add_patch(
            FancyArrowPatch(
                p,
                q,
                arrowstyle="-|>",
                mutation_scale=13,
                lw=lw,
                color=color,
                alpha=alpha,
                shrinkA=15,
                shrinkB=15,
                zorder=zorder,
            )
        )
        return
    ax.plot([p[0], q[0]], [p[1], q[1]], color=color, lw=lw, alpha=alpha, solid_capstyle="round", zorder=zorder)


def _draw_vertex(
    ax: plt.Axes,
    p: tuple[float, float],
    label: str,
    *,
    color: str = C_PANEL,
    edgecolor: str = C_INK,
    radius: float = 0.16,
    text_color: str = C_INK,
    zorder: int = 3,
) -> None:
    ax.add_patch(Circle(p, radius, facecolor=color, edgecolor=edgecolor, lw=1.3, zorder=zorder))
    ax.text(p[0], p[1], label, ha="center", va="center", fontsize=10, weight="bold", color=text_color, zorder=zorder + 1)


def _draw_graph(
    ax: plt.Axes,
    pos: dict[str, tuple[float, float]],
    edges: list[tuple[str, str]],
    *,
    vertex_colors: dict[str, str] | None = None,
    edge_colors: dict[tuple[str, str], str] | None = None,
    highlighted_edges: set[tuple[str, str]] | None = None,
) -> None:
    vertex_colors = vertex_colors or {}
    edge_colors = edge_colors or {}
    highlighted_edges = highlighted_edges or set()

    for u, v in edges:
        key = tuple(sorted((u, v)))
        is_highlighted = key in highlighted_edges
        _draw_edge(
            ax,
            pos[u],
            pos[v],
            color=edge_colors.get(key, C_ORANGE if is_highlighted else C_GRAY),
            lw=3.0 if is_highlighted else 1.8,
            alpha=0.95 if is_highlighted else 0.70,
            zorder=2 if is_highlighted else 1,
        )
    for v, p in pos.items():
        _draw_vertex(ax, p, v, color=vertex_colors.get(v, C_PANEL))


def draw_handshaking_lemma(out_name: str = "handshaking_lemma.png") -> None:
    """Граф со степенями вершин: сумма степеней считает каждое ребро дважды."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(8.8, 5.4))
    _setup_axis(ax, (-2.8, 4.8), (-2.1, 2.25))

    pos = {
        "A": (-1.55, 1.05),
        "B": (0.15, 1.25),
        "C": (1.45, 0.35),
        "D": (0.6, -1.05),
        "E": (-1.15, -1.25),
        "F": (-2.05, -0.1),
    }
    edges = [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E"), ("E", "F"), ("F", "A"), ("B", "D")]
    degrees = {v: 0 for v in pos}
    for u, v in edges:
        degrees[u] += 1
        degrees[v] += 1

    _draw_graph(ax, pos, edges, vertex_colors={"B": "#f8f3dc", "D": "#f8f3dc"})
    for v, (x, y) in pos.items():
        ax.text(x, y - 0.42, rf"$\deg={degrees[v]}$", ha="center", va="center", fontsize=9.5, color=C_INK)

    ax.text(-2.55, 1.95, "Лемма о рукопожатиях", fontsize=15, weight="bold")
    ax.text(2.15, 1.25, rf"$\sum \deg(v)={sum(degrees.values())}$", fontsize=16, bbox=dict(boxstyle="round,pad=0.28", facecolor="#f8f3dc", edgecolor=C_ORANGE))
    ax.text(2.15, 0.55, rf"$2|E|=2\cdot {len(edges)}={2 * len(edges)}$", fontsize=16, bbox=dict(boxstyle="round,pad=0.28", facecolor="#edf2f8", edgecolor=C_BLUE))
    ax.text(2.15, -0.35, "Каждое ребро даёт вклад\nв степени двух концов.", fontsize=11)
    fig.tight_layout(pad=0.6)
    _save(fig, out_name)


def draw_tree_properties(out_name: str = "tree_properties.png") -> None:
    """Дерево: n вершин, n-1 рёбер, листья и цикл после добавления ребра."""
    _apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.8))
    fig.patch.set_facecolor(C_BG)

    pos = {
        "1": (0.0, 1.25),
        "2": (-0.9, 0.35),
        "3": (0.75, 0.35),
        "4": (-1.45, -0.65),
        "5": (-0.45, -0.65),
        "6": (0.25, -0.7),
        "7": (1.25, -0.7),
        "8": (1.9, -1.45),
    }
    tree_edges = [("1", "2"), ("1", "3"), ("2", "4"), ("2", "5"), ("3", "6"), ("3", "7"), ("7", "8")]
    leaves = {"4", "5", "6", "8"}
    cycle_edges = {tuple(sorted(edge)) for edge in [("1", "2"), ("2", "5"), ("5", "6"), ("6", "3"), ("3", "1")]}

    for ax in axes:
        _setup_axis(ax, (-2.05, 2.25), (-1.9, 1.75))

    _draw_graph(axes[0], pos, tree_edges, vertex_colors={v: "#f8f3dc" for v in leaves})
    axes[0].text(-1.9, 1.52, r"Дерево: $V=8,\ E=7=V-1$", fontsize=12.5, weight="bold")
    axes[0].text(-1.9, -1.72, "Жёлтые вершины — листья степени 1.", fontsize=10.5)

    added_edges = tree_edges + [("5", "6")]
    _draw_graph(
        axes[1],
        pos,
        added_edges,
        vertex_colors={v: "#f8f3dc" for v in leaves},
        highlighted_edges=cycle_edges,
    )
    axes[1].text(-1.9, 1.52, "Добавление ребра создаёт цикл", fontsize=12.5, weight="bold")
    axes[1].text(-1.9, -1.72, "Оранжевым выделен единственный новый цикл.", fontsize=10.5)
    fig.tight_layout(pad=0.8)
    _save(fig, out_name)


def _complete_graph_positions(n: int = 5, radius: float = 1.15) -> dict[str, tuple[float, float]]:
    labels = [str(i) for i in range(n)]
    angles = np.linspace(np.pi / 2, np.pi / 2 + 2 * np.pi, n, endpoint=False)
    return {label: (radius * np.cos(a), radius * np.sin(a)) for label, a in zip(labels, angles)}


def _complete_graph_edges(labels: list[str]) -> list[tuple[str, str]]:
    return [(labels[i], labels[j]) for i in range(len(labels)) for j in range(i + 1, len(labels))]


def gif_euler_vs_hamilton(out_name: str = "gif_euler_vs_hamilton.gif", duration: float = 0.34) -> None:
    """GIF: эйлеров обход подсвечивает рёбра, гамильтонов — вершины."""
    _apply_style()
    pos = _complete_graph_positions()
    labels = list(pos)
    edges = _complete_graph_edges(labels)
    euler_walk = ["0", "1", "2", "0", "3", "1", "4", "2", "3", "4", "0"]
    hamilton_cycle = ["0", "1", "2", "3", "4", "0"]
    frames = []

    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for step in range(len(euler_walk) + 4):
            fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.8))
            fig.patch.set_facecolor(C_BG)
            for ax in axes:
                _setup_axis(ax, (-1.65, 1.65), (-1.6, 1.65))

            euler_edges = {
                tuple(sorted((euler_walk[i], euler_walk[i + 1])))
                for i in range(min(step, len(euler_walk) - 1))
            }
            h_steps = min(step, len(hamilton_cycle) - 1)
            hamilton_edges = {
                tuple(sorted((hamilton_cycle[i], hamilton_cycle[i + 1])))
                for i in range(h_steps)
            }
            hamilton_vertices = set(hamilton_cycle[: h_steps + 1])

            _draw_graph(axes[0], pos, edges, highlighted_edges=euler_edges)
            _draw_graph(
                axes[1],
                pos,
                edges,
                vertex_colors={v: "#f8f3dc" if v in hamilton_vertices else C_PANEL for v in pos},
                highlighted_edges=hamilton_edges,
            )
            axes[0].text(-1.55, 1.43, "Эйлеров обход: все рёбра", fontsize=12, weight="bold")
            axes[1].text(-1.55, 1.43, "Гамильтонов цикл: все вершины", fontsize=12, weight="bold")
            axes[0].text(-1.55, -1.45, f"пройдено рёбер: {min(step, 10)} из 10", fontsize=10.5)
            axes[1].text(-1.55, -1.45, f"посещено вершин: {min(step + 1, 5)} из 5", fontsize=10.5)
            fig.tight_layout(pad=0.7)
            fp = tmp_path / f"walk_{step:03d}.png"
            fig.savefig(fp, dpi=140, bbox_inches="tight", facecolor=C_BG)
            plt.close(fig)
            frames.append(imageio.imread(fp))

        for _ in range(4):
            frames.append(frames[-1])

    imageio.mimsave(ASSETS / out_name, frames, duration=duration, loop=0)


def draw_faces_intuition(out_name: str = "faces_intuition.png") -> None:
    """Несколько простых примеров граней планарного графа."""
    _apply_style()
    fig, axes = plt.subplots(1, 3, figsize=(11.0, 4.3))
    fig.patch.set_facecolor(C_BG)

    examples = [
        {
            "title": r"Цикл $C_4$",
            "note": r"$F=2$: внутри и снаружи",
            "pos": {"1": (-0.9, 0.75), "2": (0.9, 0.75), "3": (0.9, -0.75), "4": (-0.9, -0.75)},
            "edges": [("1", "2"), ("2", "3"), ("3", "4"), ("4", "1")],
            "faces": [[(-0.9, 0.75), (0.9, 0.75), (0.9, -0.75), (-0.9, -0.75)]],
        },
        {
            "title": "Диагональ делит грань",
            "note": r"$F=3$: две внутренние и внешняя",
            "pos": {"1": (-0.9, 0.75), "2": (0.9, 0.75), "3": (0.9, -0.75), "4": (-0.9, -0.75)},
            "edges": [("1", "2"), ("2", "3"), ("3", "4"), ("4", "1"), ("1", "3")],
            "faces": [[(-0.9, 0.75), (0.9, 0.75), (0.9, -0.75)], [(-0.9, 0.75), (0.9, -0.75), (-0.9, -0.75)]],
        },
        {
            "title": "Дерево",
            "note": r"$F=1$: только внешняя грань",
            "pos": {"1": (0.0, 0.9), "2": (-0.75, 0.15), "3": (0.75, 0.15), "4": (-1.1, -0.7), "5": (-0.35, -0.7), "6": (0.75, -0.7)},
            "edges": [("1", "2"), ("1", "3"), ("2", "4"), ("2", "5"), ("3", "6")],
            "faces": [],
        },
    ]

    for ax, example in zip(axes, examples):
        _setup_axis(ax, (-1.75, 1.75), (-1.35, 1.45))
        ax.add_patch(Rectangle((-1.55, -1.12), 3.1, 2.25, facecolor=C_PANEL, edgecolor=C_GRAY, lw=1.0, alpha=0.32, zorder=0))
        ax.text(0, -1.22, "внешняя грань", ha="center", va="center", fontsize=9.5, color=C_GRAY)

        for idx, polygon in enumerate(example["faces"]):
            color = [C_BLUE, C_GREEN, C_PURPLE][idx % 3]
            ax.add_patch(Polygon(polygon, closed=True, facecolor=color, edgecolor="none", alpha=0.18, zorder=1))

        _draw_graph(ax, example["pos"], example["edges"])
        ax.text(-1.55, 1.26, example["title"], fontsize=12, weight="bold")
        ax.text(-1.55, -1.0, example["note"], fontsize=10.5, color=C_INK)

    fig.suptitle("Грани — это области, на которые рисунок графа делит плоскость", fontsize=14, weight="bold", y=0.98)
    fig.tight_layout(pad=0.8)
    _save(fig, out_name)


def draw_bipartite_graph(out_name: str = "bipartite_k33.png") -> None:
    """Двудольный граф и полный двудольный граф K_{3,3}."""
    _apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.8))
    fig.patch.set_facecolor(C_BG)

    left_x, right_x = -0.9, 0.9
    left = {"a1": (left_x, 0.8), "a2": (left_x, 0.0), "a3": (left_x, -0.8)}
    right = {"b1": (right_x, 0.8), "b2": (right_x, 0.0), "b3": (right_x, -0.8)}
    pos = {**left, **right}

    for ax in axes:
        _setup_axis(ax, (-1.9, 1.9), (-1.35, 1.45))
        ax.add_patch(Rectangle((-1.35, -1.08), 0.9, 2.16, facecolor=C_BLUE, edgecolor="none", alpha=0.10, zorder=0))
        ax.add_patch(Rectangle((0.45, -1.08), 0.9, 2.16, facecolor=C_ORANGE, edgecolor="none", alpha=0.10, zorder=0))
        ax.text(left_x, 1.2, "доля 1", ha="center", fontsize=10.5, color=C_BLUE, weight="bold")
        ax.text(right_x, 1.2, "доля 2", ha="center", fontsize=10.5, color=C_ORANGE, weight="bold")

    sample_edges = [("a1", "b1"), ("a1", "b3"), ("a2", "b2"), ("a3", "b1"), ("a3", "b3")]
    _draw_graph(axes[0], pos, sample_edges, vertex_colors={**{v: "#edf2f8" for v in left}, **{v: "#f8f3dc" for v in right}})
    axes[0].plot([left_x - 0.28, left_x + 0.28], [0.38, 0.38], color=C_GRAY, lw=1.6, ls="--")
    axes[0].plot([left_x - 0.28, left_x + 0.28], [0.38, -0.38], color=C_GRAY, lw=1.6, ls="--")
    axes[0].plot([0.58, 1.22], [0.38, 0.38], color=C_GRAY, lw=1.6, ls="--")
    axes[0].plot([0.58, 1.22], [0.38, -0.38], color=C_GRAY, lw=1.6, ls="--")
    axes[0].text(0, -1.18, "рёбер внутри долей нет", ha="center", fontsize=10.5)
    axes[0].text(-1.75, 1.28, "Двудольный граф", fontsize=12.5, weight="bold")

    complete_edges = [(u, v) for u in left for v in right]
    _draw_graph(axes[1], pos, complete_edges, vertex_colors={**{v: "#edf2f8" for v in left}, **{v: "#f8f3dc" for v in right}})
    axes[1].text(-1.75, 1.28, r"Полный двудольный $K_{3,3}$", fontsize=12.5, weight="bold")
    axes[1].text(0, -1.18, r"$3\cdot 3=9$ рёбер между долями", ha="center", fontsize=10.5)

    fig.suptitle("В двудольном графе рёбра идут только между двумя долями", fontsize=14, weight="bold", y=0.98)
    fig.tight_layout(pad=0.9)
    _save(fig, out_name)


def _draw_directed_arc(
    ax: plt.Axes,
    p: tuple[float, float],
    q: tuple[float, float],
    *,
    color: str = C_GRAY,
    lw: float = 1.8,
    alpha: float = 0.9,
    rad: float = 0.0,
    zorder: int = 1,
) -> None:
    ax.add_patch(
        FancyArrowPatch(
            p,
            q,
            arrowstyle="-|>",
            mutation_scale=13,
            lw=lw,
            color=color,
            alpha=alpha,
            connectionstyle=f"arc3,rad={rad}",
            shrinkA=15,
            shrinkB=15,
            zorder=zorder,
        )
    )


def _tournament_positions(labels: list[str], radius: float = 1.1) -> dict[str, tuple[float, float]]:
    angles = np.linspace(np.pi / 2, np.pi / 2 + 2 * np.pi, len(labels), endpoint=False)
    return {label: (radius * np.cos(angle), radius * np.sin(angle)) for label, angle in zip(labels, angles)}


def draw_tournament_definition(out_name: str = "tournament_definition.png") -> None:
    """Турнир как ориентация полного графа."""
    _apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.8))
    fig.patch.set_facecolor(C_BG)

    labels = ["A", "B", "C", "D"]
    pos = _tournament_positions(labels)
    undirected_edges = _complete_graph_edges(labels)
    directed_edges = [("A", "B"), ("A", "C"), ("D", "A"), ("B", "C"), ("B", "D"), ("C", "D")]
    outdeg = {v: 0 for v in labels}
    for u, _ in directed_edges:
        outdeg[u] += 1

    for ax in axes:
        _setup_axis(ax, (-1.65, 1.65), (-1.55, 1.6))

    _draw_graph(axes[0], pos, undirected_edges)
    axes[0].text(-1.5, 1.35, r"Полный граф $K_4$", fontsize=12.5, weight="bold")
    axes[0].text(-1.5, -1.35, "между каждой парой есть ребро", fontsize=10.5)

    for idx, (u, v) in enumerate(directed_edges):
        rad = 0.08 if idx % 2 == 0 else -0.08
        _draw_directed_arc(axes[1], pos[u], pos[v], color=C_ORANGE, lw=2.0, rad=rad)
    for v, p in pos.items():
        _draw_vertex(axes[1], p, v, color="#f8f3dc")
        axes[1].text(p[0], p[1] - 0.38, rf"$d^+={outdeg[v]}$", ha="center", fontsize=9.0)

    axes[1].text(-1.5, 1.35, "Турнир", fontsize=12.5, weight="bold")
    axes[1].text(-1.5, -1.35, r"каждая пара получила ровно одну стрелку", fontsize=10.5)
    fig.suptitle(r"Турнир — это ориентация полного графа", fontsize=14, weight="bold", y=0.98)
    fig.tight_layout(pad=0.85)
    _save(fig, out_name)


def draw_tournament_hamilton_path(out_name: str = "tournament_hamilton_path.png") -> None:
    """Гамильтонов путь как выделенная цепочка в турнире."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(9.2, 4.8))
    _setup_axis(ax, (-0.8, 6.7), (-1.6, 1.7))

    labels = ["v1", "v2", "v3", "v4", "v5"]
    pos = {label: (0.25 + i * 1.35, 0.0) for i, label in enumerate(labels)}
    path_edges = [("v1", "v2"), ("v2", "v3"), ("v3", "v4"), ("v4", "v5")]
    extra_edges = [
        ("v1", "v3"),
        ("v4", "v1"),
        ("v1", "v5"),
        ("v2", "v4"),
        ("v5", "v2"),
        ("v3", "v5"),
    ]

    for idx, (u, v) in enumerate(extra_edges):
        rad = 0.28 if idx % 2 == 0 else -0.28
        _draw_directed_arc(ax, pos[u], pos[v], color=C_GRAY, lw=1.5, alpha=0.45, rad=rad)

    for u, v in path_edges:
        _draw_directed_arc(ax, pos[u], pos[v], color=C_ORANGE, lw=2.8, alpha=0.96, rad=0.0, zorder=3)

    for label, p in pos.items():
        _draw_vertex(ax, p, label[-1], color="#f8f3dc", radius=0.19, zorder=4)

    ax.text(-0.55, 1.35, "Гамильтонов путь в турнире", fontsize=15, weight="bold")
    ax.text(0.25, -1.05, r"Выделенная цепочка проходит через все вершины ровно один раз.", fontsize=11)
    ax.text(1.15, 0.62, r"$v_1\to v_2\to v_3\to v_4\to v_5$", fontsize=13, color=C_ORANGE, weight="bold")
    fig.tight_layout(pad=0.7)
    _save(fig, out_name)


def draw_planar_euler_formula(out_name: str = "planar_euler_formula.png") -> None:
    """Планарный граф с подсчитанными вершинами, рёбрами и гранями."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(8.8, 5.2))
    _setup_axis(ax, (-2.4, 4.6), (-1.8, 1.9))

    pos = {
        "1": (-1.35, 1.0),
        "2": (1.35, 1.0),
        "3": (1.35, -1.0),
        "4": (-1.35, -1.0),
        "5": (0.0, 0.0),
    }
    faces = [
        [pos["1"], pos["2"], pos["5"]],
        [pos["2"], pos["3"], pos["5"]],
        [pos["3"], pos["4"], pos["5"]],
        [pos["4"], pos["1"], pos["5"]],
    ]
    face_colors = [C_BLUE, C_ORANGE, C_GREEN, C_PURPLE]
    for polygon, color in zip(faces, face_colors):
        ax.add_patch(Polygon(polygon, closed=True, facecolor=color, edgecolor="none", alpha=0.16, zorder=0))
    ax.add_patch(Rectangle((-1.35, -1.0), 2.7, 2.0, facecolor="none", edgecolor=C_GRAY, lw=1.0, alpha=0.45, zorder=0))

    edges = [("1", "2"), ("2", "3"), ("3", "4"), ("4", "1"), ("1", "5"), ("2", "5"), ("3", "5"), ("4", "5")]
    _draw_graph(ax, pos, edges, vertex_colors={"5": "#f8f3dc"})

    ax.text(-2.22, 1.62, "Планарный граф и формула Эйлера", fontsize=15, weight="bold")
    ax.text(2.15, 0.95, r"$V=5$", fontsize=15, bbox=dict(boxstyle="round,pad=0.25", facecolor="#edf2f8", edgecolor=C_BLUE))
    ax.text(2.15, 0.35, r"$E=8$", fontsize=15, bbox=dict(boxstyle="round,pad=0.25", facecolor="#f8f3dc", edgecolor=C_ORANGE))
    ax.text(2.15, -0.25, r"$F=5$", fontsize=15, bbox=dict(boxstyle="round,pad=0.25", facecolor="#edf7ea", edgecolor=C_GREEN))
    ax.text(2.15, -1.03, r"$V-E+F=5-8+5=2$", fontsize=15, weight="bold")
    ax.text(-2.22, -1.55, "Четыре внутренние грани плюс внешняя грань дают $F=5$.", fontsize=10.5)
    fig.tight_layout(pad=0.6)
    _save(fig, out_name)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_handshaking_lemma()
    draw_tree_properties()
    gif_euler_vs_hamilton()
    draw_faces_intuition()
    draw_bipartite_graph()
    draw_tournament_definition()
    draw_tournament_hamilton_path()
    draw_planar_euler_formula()
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
