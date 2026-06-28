"""Точные схемы для лекции про мосты и точки сочленения."""
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

C_BG = "#faf9f5"
C_INK = "#141413"
C_GRAY = "#b0aea5"
C_PANEL = "#e8e6dc"
C_ORANGE = "#d97757"
C_BLUE = "#6a9bcc"
C_GREEN = "#788c5d"


def _apply_style():
    plt.rcParams.update({
        "figure.facecolor": C_BG,
        "axes.facecolor": C_BG,
        "axes.edgecolor": C_GRAY,
        "text.color": C_INK,
        "font.size": 11,
    })


def _save(fig, name):
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS / name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)
    print(f"Saved: {ASSETS / name}")


def _draw_node(ax, x, y, label, color, radius=0.28, fontsize=13):
    circle = mpatches.Circle((x, y), radius, color=color, zorder=4)
    ax.add_patch(circle)
    ax.text(x, y, label, ha="center", va="center", fontsize=fontsize,
            color="white", fontweight="bold", zorder=5)


def _draw_edge(ax, p1, p2, color, lw=2.0, ls="-", zorder=2):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, lw=lw,
            linestyle=ls, zorder=zorder, solid_capstyle="round")


def draw_bridges():
    """Graph with 7 nodes; bridges highlighted in red, non-bridges in blue."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_xlim(-0.5, 7.5)
    ax.set_ylim(-0.5, 3.5)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(C_BG)

    # Positions: triangle {0,1,2}, bridge 2-3, triangle {3,4,5}, pendant 5-6
    pos = {
        0: (0.5, 2.5),
        1: (0.5, 0.5),
        2: (2.0, 1.5),
        3: (3.5, 1.5),
        4: (5.0, 2.5),
        5: (5.0, 0.5),
        6: (6.5, 1.5),
    }

    # Edges: cycle {0,1,2}, bridge {2-3}, cycle {3,4,5}, bridge {5-6}
    non_bridge_edges = [
        (0, 1), (1, 2), (0, 2),
        (3, 4), (4, 5), (3, 5),
    ]
    bridge_edges = [
        (2, 3),
        (5, 6),
    ]

    for u, v in non_bridge_edges:
        _draw_edge(ax, pos[u], pos[v], C_BLUE, lw=2.5)

    for u, v in bridge_edges:
        _draw_edge(ax, pos[u], pos[v], C_ORANGE, lw=3.5)

    for node, (x, y) in pos.items():
        _draw_node(ax, x, y, str(node), C_INK)

    # Label bridge edges
    bx, by = (pos[2][0] + pos[3][0]) / 2, (pos[2][1] + pos[3][1]) / 2 + 0.3
    ax.text(bx, by, "мост", color=C_ORANGE, fontsize=10, ha="center", fontweight="bold")

    bx2, by2 = (pos[5][0] + pos[6][0]) / 2, (pos[5][1] + pos[6][1]) / 2 + 0.3
    ax.text(bx2, by2, "мост", color=C_ORANGE, fontsize=10, ha="center", fontweight="bold")

    # Legend
    patch_bridge = mpatches.Patch(color=C_ORANGE, label="Мост (bridge)")
    patch_normal = mpatches.Patch(color=C_BLUE, label="Обычное ребро")
    ax.legend(handles=[patch_bridge, patch_normal], loc="upper right",
              facecolor=C_PANEL, edgecolor=C_GRAY, fontsize=10)

    ax.set_title("Мосты в графе", color=C_INK, fontsize=14, fontweight="bold", pad=10)
    _save(fig, "bridges.png")


def draw_disc_low():
    """DFS tree with disc and low values annotated; bridges highlighted."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.set_xlim(-0.5, 8.0)
    ax.set_ylim(-0.8, 4.2)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(C_BG)

    # Same graph as draw_bridges
    pos = {
        0: (0.5, 3.0),
        1: (0.5, 1.0),
        2: (2.0, 2.0),
        3: (3.8, 2.0),
        4: (5.3, 3.0),
        5: (5.3, 1.0),
        6: (7.0, 2.0),
    }

    # disc and low values from DFS starting at 0
    # DFS order: 0->1->2->3->4->5->6
    disc = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6}
    low  = {0: 0, 1: 0, 2: 0, 3: 3, 4: 3, 5: 3, 6: 6}

    # Tree edges (DFS)
    tree_edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6)]
    # Back edge: 2->0
    back_edges = [(2, 0), (5, 3)]
    # Bridge edges in tree
    bridge_tree_edges = {(2, 3), (5, 6)}

    for u, v in tree_edges:
        color = C_ORANGE if (u, v) in bridge_tree_edges else C_BLUE
        lw = 3.5 if (u, v) in bridge_tree_edges else 2.5
        _draw_edge(ax, pos[u], pos[v], color, lw=lw)

    for u, v in back_edges:
        _draw_edge(ax, pos[u], pos[v], C_GREEN, lw=1.8, ls="--")

    for node, (x, y) in pos.items():
        _draw_node(ax, x, y, str(node), C_INK, radius=0.26)
        # disc[v] top-right, low[v] bottom-right
        ax.text(x + 0.32, y + 0.22, f"d={disc[node]}", color=C_INK,
                fontsize=8.5, ha="left", va="bottom", zorder=6)
        ax.text(x + 0.32, y - 0.22, f"l={low[node]}", color=C_ORANGE,
                fontsize=8.5, ha="left", va="top", zorder=6)

    # Annotate bridge condition
    mx, my = (pos[2][0] + pos[3][0]) / 2, (pos[2][1] + pos[3][1]) / 2 + 0.45
    ax.text(mx, my, "low[3]=3 > disc[2]=2 → мост", color=C_ORANGE,
            fontsize=8.5, ha="center", fontweight="bold")

    mx2, my2 = (pos[5][0] + pos[6][0]) / 2, (pos[5][1] + pos[6][1]) / 2 + 0.45
    ax.text(mx2, my2, "low[6]=6 > disc[5]=5 → мост", color=C_ORANGE,
            fontsize=8.5, ha="center", fontweight="bold")

    # Legend
    patch_tree = mpatches.Patch(color=C_BLUE, label="Древесное ребро")
    patch_bridge = mpatches.Patch(color=C_ORANGE, label="Мост")
    patch_back = mpatches.Patch(color=C_GREEN, label="Обратное ребро (back edge)")
    ax.legend(handles=[patch_tree, patch_bridge, patch_back], loc="lower right",
              facecolor=C_PANEL, edgecolor=C_GRAY, fontsize=9)

    ax.set_title("DFS: значения disc (d=) и low (l=)", color=C_INK,
                 fontsize=14, fontweight="bold", pad=10)
    _save(fig, "disc_low.png")


def draw_articulations():
    """Graph with articulation points drawn as larger orange circles."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_xlim(-0.5, 7.5)
    ax.set_ylim(-0.8, 3.8)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(C_BG)

    pos = {
        0: (0.5, 2.5),
        1: (0.5, 0.5),
        2: (2.0, 1.5),
        3: (3.5, 1.5),
        4: (5.0, 2.5),
        5: (5.0, 0.5),
        6: (6.5, 1.5),
    }

    # Articulation points: 2, 5
    articulations = {2, 5}

    non_bridge_edges = [
        (0, 1), (1, 2), (0, 2),
        (3, 4), (4, 5), (3, 5),
    ]
    bridge_edges = [(2, 3), (5, 6)]

    for u, v in non_bridge_edges:
        _draw_edge(ax, pos[u], pos[v], C_GRAY, lw=2.2)

    for u, v in bridge_edges:
        _draw_edge(ax, pos[u], pos[v], C_GRAY, lw=2.2)

    for node, (x, y) in pos.items():
        if node in articulations:
            # Outer ring for AP
            ring = mpatches.Circle((x, y), 0.36, color=C_ORANGE, zorder=3)
            ax.add_patch(ring)
            inner = mpatches.Circle((x, y), 0.26, color=C_INK, zorder=4)
            ax.add_patch(inner)
            ax.text(x, y, str(node), ha="center", va="center", fontsize=13,
                    color="white", fontweight="bold", zorder=5)
        else:
            _draw_node(ax, x, y, str(node), C_BLUE, radius=0.26)

    # Labels for components that disconnect
    ax.text(1.0, 3.3, "компонента A\n{0, 1}", color=C_BLUE, fontsize=9,
            ha="center", style="italic")
    ax.text(4.25, 3.3, "компонента B\n{3, 4}", color=C_BLUE, fontsize=9,
            ha="center", style="italic")
    ax.text(6.5, 3.3, "компонента C\n{6}", color=C_BLUE, fontsize=9,
            ha="center", style="italic")

    # Arrows from labels
    ax.annotate("", xy=(0.9, 2.7), xytext=(1.0, 3.1),
                arrowprops={"arrowstyle": "->", "color": C_GRAY, "lw": 1.0})
    ax.annotate("", xy=(4.3, 2.7), xytext=(4.25, 3.1),
                arrowprops={"arrowstyle": "->", "color": C_GRAY, "lw": 1.0})
    ax.annotate("", xy=(6.5, 1.8), xytext=(6.5, 3.1),
                arrowprops={"arrowstyle": "->", "color": C_GRAY, "lw": 1.0})

    # Legend
    ap_patch = mpatches.Patch(color=C_ORANGE, label="Точка сочленения (AP)")
    normal_patch = mpatches.Patch(color=C_BLUE, label="Обычная вершина")
    ax.legend(handles=[ap_patch, normal_patch], loc="lower left",
              facecolor=C_PANEL, edgecolor=C_GRAY, fontsize=10)

    ax.set_title("Точки сочленения (оранжевые кольца)", color=C_INK,
                 fontsize=14, fontweight="bold", pad=10)
    _save(fig, "articulations.png")


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_bridges()
    draw_disc_low()
    draw_articulations()


if __name__ == "__main__":
    main()
