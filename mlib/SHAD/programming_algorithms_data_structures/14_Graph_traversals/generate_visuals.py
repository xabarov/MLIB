from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

C_BG = "#faf9f5"
C_INK = "#141413"
C_GRAY = "#b0aea5"
C_PANEL = "#e8e6dc"
C_ORANGE = "#d97757"
C_BLUE = "#6a9bcc"
C_GREEN = "#788c5d"

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

# Graph: 7 nodes (0..6), edges: 0-1, 0-2, 1-3, 1-4, 2-5, 2-6
_EDGES = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)]
_POS = {
    0: (3.5, 4.0),
    1: (2.0, 2.8),
    2: (5.0, 2.8),
    3: (1.0, 1.5),
    4: (3.0, 1.5),
    5: (4.0, 1.5),
    6: (6.0, 1.5),
}


def _apply_style():
    plt.rcParams.update({
        "figure.facecolor": C_BG,
        "axes.facecolor": C_BG,
        "text.color": C_INK,
        "font.size": 11,
    })


def _save(fig, name):
    ASSETS.mkdir(parents=True, exist_ok=True)
    path = ASSETS / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)
    print(f"Saved: {path}")


def _draw_node(ax, x, y, label, facecolor, r=0.32):
    circ = mpatches.Circle((x, y), r, facecolor=facecolor,
                            edgecolor=C_INK, linewidth=2.0, zorder=4)
    ax.add_patch(circ)
    ax.text(x, y, str(label), ha="center", va="center",
            fontsize=13, color="white", fontweight="bold", zorder=5)


def _draw_edge(ax, p1, p2, color=C_GRAY, lw=2.0, style="-"):
    x1, y1 = p1
    x2, y2 = p2
    ax.plot([x1, x2], [y1, y2], color=color, lw=lw,
            linestyle=style, zorder=2)


def draw_bfs():
    """BFS from node 0. Nodes colored by layer: 0=orange, 1=blue, 2=green."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(9, 6))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)

    # BFS distances from node 0
    dist = {0: 0, 1: 1, 2: 1, 3: 2, 4: 2, 5: 2, 6: 2}
    layer_colors = {0: C_ORANGE, 1: C_BLUE, 2: C_GREEN}

    # Draw edges first
    for u, v in _EDGES:
        _draw_edge(ax, _POS[u], _POS[v])

    # Draw nodes
    for node, (x, y) in _POS.items():
        d = dist[node]
        color = layer_colors[d]
        _draw_node(ax, x, y, node, color)
        # Distance label below node
        ax.text(x, y - 0.48, f"d={d}", ha="center", va="center",
                fontsize=9, color=C_INK, zorder=6)

    # Legend
    legend_items = [
        mpatches.Patch(facecolor=C_ORANGE, edgecolor=C_INK, label="Слой 0 (источник)"),
        mpatches.Patch(facecolor=C_BLUE, edgecolor=C_INK, label="Слой 1 (d=1)"),
        mpatches.Patch(facecolor=C_GREEN, edgecolor=C_INK, label="Слой 2 (d=2)"),
    ]
    ax.legend(handles=legend_items, loc="lower right", fontsize=9,
              facecolor=C_PANEL, edgecolor=C_GRAY)

    # Layer annotations
    ax.text(3.5, 4.55, "Слой 0", ha="center", fontsize=9, color=C_ORANGE, style="italic")
    ax.text(3.5, 3.3, "Слой 1", ha="center", fontsize=9, color=C_BLUE, style="italic")
    ax.text(3.5, 2.0, "Слой 2", ha="center", fontsize=9, color=C_GREEN, style="italic")

    ax.set_xlim(0.0, 7.0)
    ax.set_ylim(0.8, 5.1)
    ax.axis("off")
    ax.set_title("BFS от вершины 0: слои и расстояния",
                 fontsize=13, color=C_INK, pad=10)
    plt.tight_layout()
    _save(fig, "bfs_layers")


def draw_dfs_tree():
    """DFS tree: solid=tree edges, dashed=back/cross. tin/tout labels."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(9, 6))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)

    # DFS from 0, visiting neighbors in order: tree edges = all edges here
    # tin/tout for undirected tree (no back edges in this particular tree graph)
    # tin[v] = entry time, tout[v] = exit time
    # DFS order: 0->1->3->back->4->back->back->2->5->back->6->back->back
    tin = {0: 0, 1: 1, 3: 2, 4: 4, 2: 6, 5: 7, 6: 9}
    tout = {0: 11, 1: 5, 3: 3, 4: 5, 2: 10, 5: 8, 6: 10}

    # All edges are tree edges in this graph (it's a tree itself)
    tree_edges = set(_EDGES)

    for u, v in _EDGES:
        if (u, v) in tree_edges or (v, u) in tree_edges:
            _draw_edge(ax, _POS[u], _POS[v], color=C_BLUE, lw=2.5, style="-")

    # Draw nodes
    for node, (x, y) in _POS.items():
        _draw_node(ax, x, y, node, C_BLUE)
        # tin/tout label
        label = f"{tin[node]}/{tout[node]}"
        ax.text(x + 0.42, y + 0.25, label, ha="left", va="center",
                fontsize=8, color=C_INK, zorder=6,
                bbox=dict(facecolor=C_PANEL, edgecolor=C_GRAY,
                          boxstyle="round,pad=0.15", linewidth=0.8))

    # Legend for edge types
    solid = mpatches.Patch(facecolor=C_BLUE, edgecolor=C_INK,
                           label="Древесное ребро")
    ax.legend(handles=[solid], loc="lower right", fontsize=9,
              facecolor=C_PANEL, edgecolor=C_GRAY)

    ax.text(0.2, 4.8, "Формат метки: tin/tout", fontsize=9,
            color=C_GRAY, style="italic")

    ax.set_xlim(0.0, 7.5)
    ax.set_ylim(0.8, 5.1)
    ax.axis("off")
    ax.set_title("DFS-дерево: метки входа/выхода (tin/tout)",
                 fontsize=13, color=C_INK, pad=10)
    plt.tight_layout()
    _save(fig, "dfs_tree")


def draw_representations():
    """Two panels: left=adjacency matrix (7x7), right=adjacency list."""
    _apply_style()
    fig, (ax_m, ax_l) = plt.subplots(1, 2, figsize=(13, 6))
    fig.patch.set_facecolor(C_BG)

    n = 7
    # Build adjacency matrix
    adj_matrix = np.zeros((n, n), dtype=int)
    for u, v in _EDGES:
        adj_matrix[u][v] = 1
        adj_matrix[v][u] = 1

    # Build adjacency list
    adj_list = [[] for _ in range(n)]
    for u, v in _EDGES:
        adj_list[u].append(v)
        adj_list[v].append(u)

    # --- Left panel: adjacency matrix ---
    ax_m.set_facecolor(C_BG)
    ax_m.set_xlim(-0.5, n + 0.5)
    ax_m.set_ylim(-0.5, n + 0.5)
    ax_m.axis("off")
    ax_m.set_title("Матрица смежности\n(7×7, O(V²) памяти)",
                   fontsize=11, color=C_INK, pad=8)

    cell_size = 0.72
    x0, y0 = 0.3, 0.3

    # Column headers
    for j in range(n):
        ax_m.text(x0 + (j + 0.5) * cell_size, y0 + n * cell_size + 0.15,
                  str(j), ha="center", va="center",
                  fontsize=10, color=C_GRAY, fontweight="bold")
    # Row headers
    for i in range(n):
        ax_m.text(x0 - 0.15, y0 + (n - i - 0.5) * cell_size,
                  str(i), ha="center", va="center",
                  fontsize=10, color=C_GRAY, fontweight="bold")

    for i in range(n):
        for j in range(n):
            val = adj_matrix[i][j]
            fc = C_ORANGE if val == 1 else C_PANEL
            rect = mpatches.Rectangle(
                (x0 + j * cell_size, y0 + (n - i - 1) * cell_size),
                cell_size, cell_size,
                facecolor=fc, edgecolor=C_GRAY, linewidth=0.8, zorder=2
            )
            ax_m.add_patch(rect)
            ax_m.text(x0 + (j + 0.5) * cell_size,
                      y0 + (n - i - 0.5) * cell_size,
                      str(val), ha="center", va="center",
                      fontsize=10,
                      color="white" if val == 1 else C_GRAY,
                      fontweight="bold" if val == 1 else "normal",
                      zorder=3)

    ax_m.set_xlim(-0.1, x0 + n * cell_size + 0.2)
    ax_m.set_ylim(-0.1, y0 + n * cell_size + 0.6)

    # --- Right panel: adjacency list ---
    ax_l.set_facecolor(C_BG)
    ax_l.axis("off")
    ax_l.set_title("Список смежности\n(O(V+E) памяти, предпочтительно)",
                   fontsize=11, color=C_INK, pad=8)

    row_h = 0.55
    top_y = n * row_h + 0.3

    for i in range(n):
        row_y = top_y - i * row_h

        # Node box
        rect_v = mpatches.FancyBboxPatch(
            (0.05, row_y - 0.22), 0.38, 0.44,
            boxstyle="round,pad=0.04",
            facecolor=C_BLUE, edgecolor=C_INK, linewidth=1.5, zorder=2
        )
        ax_l.add_patch(rect_v)
        ax_l.text(0.24, row_y, str(i), ha="center", va="center",
                  fontsize=11, color="white", fontweight="bold", zorder=3)

        # Arrow
        ax_l.annotate("", xy=(0.58, row_y), xytext=(0.43, row_y),
                      arrowprops=dict(arrowstyle="->", color=C_INK, lw=1.2))

        # Neighbour boxes
        neighbors = sorted(adj_list[i])
        for k, nb in enumerate(neighbors):
            nb_x = 0.62 + k * 0.38
            rect_nb = mpatches.FancyBboxPatch(
                (nb_x, row_y - 0.20), 0.34, 0.40,
                boxstyle="round,pad=0.04",
                facecolor=C_PANEL, edgecolor=C_GRAY, linewidth=1.0, zorder=2
            )
            ax_l.add_patch(rect_nb)
            ax_l.text(nb_x + 0.17, row_y, str(nb), ha="center", va="center",
                      fontsize=10, color=C_INK, zorder=3)
            # Chain arrow between neighbour boxes (not after last)
            if k < len(neighbors) - 1:
                ax_l.annotate("", xy=(nb_x + 0.34 + 0.02, row_y),
                              xytext=(nb_x + 0.34, row_y),
                              arrowprops=dict(arrowstyle="-", color=C_GRAY, lw=0.8))

        # NULL terminator
        null_x = 0.62 + len(neighbors) * 0.38
        ax_l.text(null_x + 0.05, row_y, "∅", ha="left", va="center",
                  fontsize=9, color=C_GRAY)

    ax_l.set_xlim(0.0, 2.5)
    ax_l.set_ylim(-0.3, top_y + 0.5)

    fig.suptitle("Два способа хранения графа (7 вершин, 6 рёбер)",
                 fontsize=12, color=C_INK, y=1.01, fontweight="bold")
    plt.tight_layout()
    _save(fig, "graph_representations")


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_bfs()
    draw_dfs_tree()
    draw_representations()
    print("All visuals generated successfully.")


if __name__ == "__main__":
    main()
