from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

C_BG = "#faf9f5"
C_INK = "#141413"
C_GRAY = "#b0aea5"
C_PANEL = "#e8e6dc"
C_ORANGE = "#d97757"
C_BLUE = "#6a9bcc"
C_GREEN = "#788c5d"

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"


def _apply_style():
    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["axes.facecolor"] = C_BG
    plt.rcParams["figure.facecolor"] = C_BG
    plt.rcParams["text.color"] = C_INK
    plt.rcParams["axes.edgecolor"] = C_GRAY


def _save(fig, name):
    ASSETS.mkdir(parents=True, exist_ok=True)
    path = ASSETS / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)
    print(f"Saved: {path}")


def _draw_arrow(ax, x0, y0, x1, y1, color=C_INK, lw=1.5, node_r=0.22):
    """Draw arrow between two node centers, stopping at node boundary."""
    import math
    dx = x1 - x0
    dy = y1 - y0
    dist = math.sqrt(dx * dx + dy * dy)
    if dist < 1e-9:
        return
    ux, uy = dx / dist, dy / dist
    sx = x0 + ux * node_r
    sy = y0 + uy * node_r
    ex = x1 - ux * node_r
    ey = y1 - uy * node_r
    ax.annotate(
        "",
        xy=(ex, ey),
        xytext=(sx, sy),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=lw),
    )


def _draw_node(ax, x, y, label, face=C_PANEL, edge=C_INK, r=0.22, fontsize=12):
    circle = mpatches.Circle((x, y), r, facecolor=face, edgecolor=edge, lw=1.8, zorder=3)
    ax.add_patch(circle)
    ax.text(x, y, label, ha="center", va="center", fontsize=fontsize,
            color=C_INK, fontweight="bold", zorder=4)


def draw_dag_topo():
    """DAG with 7 nodes. Topological order shown as numbers next to each node."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(-0.5, 3.5)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.suptitle("Топологическая сортировка через DFS", fontsize=14,
                 color=C_INK, fontweight="bold", y=0.98)

    # Node positions (left to right in topological order)
    # Topo order: 0,1,2,3,4,5,6
    # Layout: 0 at left, some branches in middle, 6 at right
    pos = {
        0: (0.5, 1.5),
        1: (2.5, 2.5),
        2: (2.5, 0.5),
        3: (4.5, 2.5),
        4: (4.5, 0.5),
        5: (7.0, 1.5),
        6: (9.5, 1.5),
    }

    # Edges (all go left->right in topo order)
    edges = [
        (0, 1), (0, 2),
        (1, 3), (2, 4),
        (3, 5), (4, 5),
        (5, 6),
    ]

    # Topological order labels (position in sorted list, 1-indexed)
    topo_label = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7}
    node_names = ["A", "B", "C", "D", "E", "F", "G"]

    for u, v in edges:
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        _draw_arrow(ax, x0, y0, x1, y1, color=C_INK)

    for node_id, (x, y) in pos.items():
        _draw_node(ax, x, y, node_names[node_id], face=C_PANEL)
        # Topological order number above-right
        ax.text(x + 0.28, y + 0.28, str(topo_label[node_id]),
                fontsize=9, color=C_ORANGE, fontweight="bold", zorder=5,
                ha="center", va="center")

    # Legend
    ax.text(0.5, 3.2, "Рёбра направлены слева направо (в топологическом порядке)",
            fontsize=10, color=C_GRAY, ha="left")
    ax.text(0.5, 2.95, "Оранжевые цифры — позиция в топологическом порядке (1..7)",
            fontsize=10, color=C_GRAY, ha="left")

    # Show tout values below nodes
    tout_values = {0: 14, 1: 11, 2: 7, 3: 10, 4: 6, 5: 13, 6: 12}
    for node_id, (x, y) in pos.items():
        ax.text(x, y - 0.42, f"tout={tout_values[node_id]}",
                fontsize=7.5, color=C_BLUE, ha="center", va="center", zorder=5)

    _save(fig, "dag_topo")


def draw_kahns():
    """Three-panel animation of Kahn's algorithm."""
    _apply_style()
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("Алгоритм Кана (BFS): пошаговый разбор", fontsize=14,
                 color=C_INK, fontweight="bold")

    # Same DAG: nodes 0..5, edges 0->1,0->2,1->3,2->3,2->4,3->5
    edges_all = [(0, 1), (0, 2), (1, 3), (2, 3), (2, 4), (3, 5)]
    pos = {
        0: (1.0, 2.0),
        1: (2.5, 3.0),
        2: (2.5, 1.0),
        3: (4.0, 2.0),
        4: (4.0, 0.2),
        5: (5.5, 2.0),
    }
    node_names = ["0", "1", "2", "3", "4", "5"]

    # Initial in-degrees
    in_deg_init = {0: 0, 1: 1, 2: 1, 3: 2, 4: 1, 5: 1}

    def draw_panel(ax, title, active_edges, removed_nodes, queue_nodes,
                   in_degrees, result_seq):
        ax.set_xlim(0.0, 6.5)
        ax.set_ylim(-0.8, 4.0)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(title, fontsize=11, color=C_INK, pad=6)

        # Draw edges
        for u, v in edges_all:
            if u in removed_nodes or v in removed_nodes:
                color = C_PANEL
            elif (u, v) in active_edges:
                color = C_ORANGE
            else:
                color = C_GRAY
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            _draw_arrow(ax, x0, y0, x1, y1, color=color, lw=1.2)

        # Draw nodes
        for node_id, (x, y) in pos.items():
            if node_id in removed_nodes:
                face = C_PANEL
                edge_c = C_GRAY
                text_c = C_GRAY
            elif node_id in queue_nodes:
                face = C_ORANGE
                edge_c = C_INK
                text_c = C_BG
            else:
                face = C_PANEL
                edge_c = C_INK
                text_c = C_INK
            circle = mpatches.Circle((x, y), 0.3, facecolor=face,
                                     edgecolor=edge_c, lw=1.8, zorder=3)
            ax.add_patch(circle)
            ax.text(x, y, node_names[node_id], ha="center", va="center",
                    fontsize=11, color=text_c, fontweight="bold", zorder=4)
            # In-degree label
            deg = in_degrees.get(node_id, 0)
            deg_color = C_BLUE if node_id not in removed_nodes else C_GRAY
            ax.text(x, y + 0.42, f"d={deg}", fontsize=8,
                    color=deg_color, ha="center", va="center", zorder=5)

        # Result sequence
        if result_seq:
            seq_str = " → ".join(str(r) for r in result_seq)
            ax.text(3.25, -0.55, f"Результат: [{seq_str}]",
                    fontsize=10, color=C_GREEN, ha="center", va="center",
                    fontweight="bold")

    # Panel 1: Initial state. Queue: {0}
    draw_panel(
        axes[0],
        "Шаг 0: начальное состояние\n(in-degree=0 у вершины 0)",
        active_edges=[],
        removed_nodes=set(),
        queue_nodes={0},
        in_degrees=dict(in_deg_init),
        result_seq=[],
    )

    # Panel 2: After removing node 0. Queue: {1, 2}
    in_deg_2 = dict(in_deg_init)
    in_deg_2[1] = 0
    in_deg_2[2] = 0
    draw_panel(
        axes[1],
        "Шаг 1: удаляем 0\n(in-degree[1] и in-degree[2] → 0)",
        active_edges=[(0, 1), (0, 2)],
        removed_nodes={0},
        queue_nodes={1, 2},
        in_degrees=in_deg_2,
        result_seq=[0],
    )

    # Panel 3: After removing 0,1,2. Queue: {3,4}. Result: [0,1,2]
    in_deg_3 = dict(in_deg_init)
    in_deg_3[1] = 0
    in_deg_3[2] = 0
    in_deg_3[3] = 0
    in_deg_3[4] = 0
    draw_panel(
        axes[2],
        "Шаг 2: удалены 0,1,2\n(in-degree[3]=0, in-degree[4]=0)",
        active_edges=[(1, 3), (2, 3), (2, 4)],
        removed_nodes={0, 1, 2},
        queue_nodes={3, 4},
        in_degrees=in_deg_3,
        result_seq=[0, 1, 2],
    )

    plt.tight_layout()
    _save(fig, "kahns")


def draw_dp_on_dag():
    """DAG with edge weights. Longest path DP values in each node. Path highlighted."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.set_xlim(-0.3, 10.5)
    ax.set_ylim(-0.5, 3.5)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.suptitle("DP на DAG: длиннейший путь", fontsize=14,
                 color=C_INK, fontweight="bold", y=0.98)

    # DAG: 0->1(3), 0->2(2), 1->3(4), 2->3(6), 3->4(1)
    # Longest path: 0->2->3->4 = 2+6+1 = 9
    pos = {
        0: (0.5, 1.5),
        1: (3.0, 2.8),
        2: (3.0, 0.2),
        3: (6.0, 1.5),
        4: (9.0, 1.5),
    }
    edges = [(0, 1, 3), (0, 2, 2), (1, 3, 4), (2, 3, 6), (3, 4, 1)]
    dp_vals = {0: 0, 1: 3, 2: 2, 3: 8, 4: 9}
    longest_path_edges = {(0, 2), (2, 3), (3, 4)}
    node_names = ["0", "1", "2", "3", "4"]

    for u, v, w in edges:
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        is_highlight = (u, v) in longest_path_edges
        color = C_ORANGE if is_highlight else C_INK
        lw = 2.5 if is_highlight else 1.5
        _draw_arrow(ax, x0, y0, x1, y1, color=color, lw=lw)
        # Edge weight label at midpoint
        mx = (x0 + x1) / 2
        my = (y0 + y1) / 2
        # Slight offset perpendicular to edge
        import math
        dx = x1 - x0
        dy = y1 - y0
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 1e-9:
            px = -dy / dist * 0.28
            py = dx / dist * 0.28
        else:
            px, py = 0, 0.28
        w_color = C_ORANGE if is_highlight else C_GRAY
        ax.text(mx + px, my + py, str(w), fontsize=10,
                color=w_color, ha="center", va="center", fontweight="bold")

    for node_id, (x, y) in pos.items():
        is_on_path = node_id in {0, 2, 3, 4}
        face = C_ORANGE if is_on_path else C_PANEL
        text_c = C_BG if is_on_path else C_INK
        circle = mpatches.Circle((x, y), 0.32, facecolor=face,
                                  edgecolor=C_INK, lw=2.0, zorder=3)
        ax.add_patch(circle)
        ax.text(x, y, node_names[node_id], ha="center", va="center",
                fontsize=12, color=text_c, fontweight="bold", zorder=4)
        # dp value below node
        ax.text(x, y - 0.52, f"dp={dp_vals[node_id]}",
                fontsize=9, color=C_BLUE, ha="center", va="center",
                fontweight="bold", zorder=5)

    # Legend
    orange_patch = mpatches.Patch(facecolor=C_ORANGE, label="Длиннейший путь (длина 9)")
    panel_patch = mpatches.Patch(facecolor=C_PANEL, edgecolor=C_INK, label="Остальные вершины")
    ax.legend(handles=[orange_patch, panel_patch], loc="upper right",
              fontsize=9, framealpha=0.9)

    ax.text(4.75, 3.3,
            "dp[v] = max(dp[u] + w(u,v)) по всем u→v",
            fontsize=11, color=C_INK, ha="center", va="center",
            style="italic")

    _save(fig, "dp_on_dag")


def main():
    draw_dag_topo()
    draw_kahns()
    draw_dp_on_dag()


if __name__ == "__main__":
    main()
