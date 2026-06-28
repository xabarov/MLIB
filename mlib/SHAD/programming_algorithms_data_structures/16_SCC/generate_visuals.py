from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"


def _apply_style():
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "axes.spines.bottom": False,
        "xtick.bottom": False,
        "ytick.left": False,
    })


def _save(fig, name):
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS / f"{name}.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {ASSETS / name}.png")


C_BG = "#faf9f5"
C_INK = "#141413"
C_GRAY = "#b0aea5"
C_PANEL = "#e8e6dc"
C_ORANGE = "#d97757"
C_BLUE = "#6a9bcc"
C_GREEN = "#788c5d"

# Graph definition (8 nodes, 3 + 1 SCCs)
# SCC A = {0,1,2}, SCC D = {3}, SCC B = {4,5}, SCC C = {6,7}
# Edges within SCCs: 0->1, 1->2, 2->0 ; 4->5, 5->4 ; 6->7, 7->6
# Cross-SCC edges: 2->3, 3->1, 3->2(within A? no — 3 is alone), 4->3, 3->6, 5->6

NODE_POS = {
    0: (1.0, 2.5),
    1: (2.5, 3.2),
    2: (2.5, 1.8),
    3: (4.0, 2.5),
    4: (5.5, 3.2),
    5: (5.5, 1.8),
    6: (7.0, 3.2),
    7: (7.0, 1.8),
}

EDGES_INTRA = [
    (0, 1), (1, 2), (2, 0),   # SCC A
    (4, 5), (5, 4),            # SCC B
    (6, 7), (7, 6),            # SCC C
]

EDGES_CROSS = [
    (2, 3),   # A -> D
    (4, 3),   # B -> D
    (3, 1),   # D -> A
    (3, 6),   # D -> C
    (5, 6),   # B -> C
]

SCC_COLORS = {
    "A": C_ORANGE,
    "B": C_BLUE,
    "C": C_GREEN,
    "D": C_GRAY,
}

SCC_MEMBERS = {
    "A": [0, 1, 2],
    "D": [3],
    "B": [4, 5],
    "C": [6, 7],
}

NODE_SCC = {}
for scc_name, members in SCC_MEMBERS.items():
    for node in members:
        NODE_SCC[node] = scc_name


def _draw_arrow(ax, p1, p2, color, lw=1.5, style="solid", radius=0.0):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dist = (dx**2 + dy**2) ** 0.5
    r = 0.22
    sx = p1[0] + dx / dist * r
    sy = p1[1] + dy / dist * r
    ex = p2[0] - dx / dist * r
    ey = p2[1] - dy / dist * r
    conn = f"arc3,rad={radius}" if radius != 0.0 else "arc3,rad=0.0"
    ax.annotate(
        "",
        xy=(ex, ey),
        xytext=(sx, sy),
        arrowprops=dict(
            arrowstyle="-|>",
            color=color,
            lw=lw,
            linestyle=style,
            connectionstyle=conn,
        ),
    )


def _draw_node(ax, node, pos, color, label=None):
    circle = mpatches.Circle(pos, 0.22, facecolor=color, edgecolor=C_INK,
                             zorder=3, linewidth=1.5)
    ax.add_patch(circle)
    txt = label if label is not None else str(node)
    ax.text(pos[0], pos[1], txt, ha="center", va="center",
            fontsize=11, fontweight="bold", color="white", zorder=4)


def draw_sccs():
    """Graph with 8 nodes and highlighted SCC regions."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 8.5)
    ax.set_ylim(1.0, 4.2)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Сильно связные компоненты орграфа", color=C_INK,
                 fontsize=13, fontweight="bold", pad=10)

    # Draw SCC background regions
    region_params = {
        "A": dict(xy=(0.4, 1.3), width=2.6, height=2.4, color=C_ORANGE, label="SCC A = {0,1,2}"),
        "D": dict(xy=(3.5, 2.0), width=1.0, height=1.0, color=C_GRAY,  label="SCC D = {3}"),
        "B": dict(xy=(4.9, 1.3), width=1.3, height=2.4, color=C_BLUE,  label="SCC B = {4,5}"),
        "C": dict(xy=(6.4, 1.3), width=1.3, height=2.4, color=C_GREEN, label="SCC C = {6,7}"),
    }
    for _, rp in region_params.items():
        rect = mpatches.FancyBboxPatch(
            rp["xy"], rp["width"], rp["height"],
            boxstyle="round,pad=0.05", linewidth=0, color=rp["color"], alpha=0.18, zorder=0
        )
        ax.add_patch(rect)

    # Draw intra-SCC edges (solid)
    for u, v in EDGES_INTRA:
        pu, pv = NODE_POS[u], NODE_POS[v]
        rad = 0.25 if (u, v) in [(4, 5), (5, 4), (6, 7), (7, 6)] else 0.0
        _draw_arrow(ax, pu, pv, color=NODE_SCC[u] and SCC_COLORS[NODE_SCC[u]],
                    lw=2.0, radius=rad)

    # Draw cross-SCC edges (dashed)
    for u, v in EDGES_CROSS:
        pu, pv = NODE_POS[u], NODE_POS[v]
        _draw_arrow(ax, pu, pv, color=C_INK, lw=1.2, style="dashed")

    # Draw nodes
    for node, pos in NODE_POS.items():
        scc = NODE_SCC[node]
        _draw_node(ax, node, pos, SCC_COLORS[scc])

    # Legend
    legend_patches = [
        mpatches.Patch(color=C_ORANGE, alpha=0.6, label="SCC A = {0,1,2}"),
        mpatches.Patch(color=C_GRAY,   alpha=0.6, label="SCC D = {3}"),
        mpatches.Patch(color=C_BLUE,   alpha=0.6, label="SCC B = {4,5}"),
        mpatches.Patch(color=C_GREEN,  alpha=0.6, label="SCC C = {6,7}"),
    ]
    ax.legend(handles=legend_patches, loc="upper left", fontsize=9,
              framealpha=0.7, facecolor=C_PANEL)

    ax.text(4.2, 0.85, "— — — рёбра между SCC   ——— рёбра внутри SCC",
            ha="center", va="center", fontsize=8, color=C_GRAY)

    _save(fig, "sccs")


def draw_kosaraju():
    """Two-panel: G with finish order (pass 1), G^T with DFS trees (pass 2)."""
    _apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.patch.set_facecolor(C_BG)
    fig.suptitle("Алгоритм Косарайю: два прохода DFS", fontsize=13,
                 fontweight="bold", color=C_INK)

    # Finish order from pass 1 (manual trace)
    # DFS from 0: finishes: 3(t=4), then 2(t=5 after 3), then 1(t=6), then 0(t=7)
    # DFS from 4: finishes: 6(t=?), 7(t=?), 5(t=?), 4(t=?)
    # Simplified order array index (position in order vector):
    # order = [3, 2, 1, 0, 7, 6, 5, 4] (approx)
    FINISH_ORDER = {0: 4, 1: 3, 2: 2, 3: 1, 4: 8, 5: 7, 6: 6, 7: 5}

    # Pass 2 SCC colors (DFS on G^T from 4 first -> SCC B, then 0 -> SCC A, etc.)
    PASS2_COLOR = {
        0: C_ORANGE, 1: C_ORANGE, 2: C_ORANGE,  # SCC A
        3: C_GRAY,                                # SCC D
        4: C_BLUE,   5: C_BLUE,                  # SCC B
        6: C_GREEN,  7: C_GREEN,                  # SCC C
    }

    for idx, ax in enumerate(axes):
        ax.set_facecolor(C_BG)
        ax.set_xlim(0, 8.5)
        ax.set_ylim(1.0, 4.2)
        ax.set_aspect("equal")
        ax.axis("off")

    # --- Panel 0: G with finish-order labels ---
    ax0 = axes[0]
    ax0.set_title("Проход 1: G, числа = порядок завершения", color=C_INK, fontsize=11)

    for u, v in EDGES_INTRA:
        pu, pv = NODE_POS[u], NODE_POS[v]
        rad = 0.25 if (u, v) in [(4, 5), (5, 4), (6, 7), (7, 6)] else 0.0
        _draw_arrow(ax0, pu, pv, C_GRAY, lw=1.5, radius=rad)
    for u, v in EDGES_CROSS:
        _draw_arrow(ax0, NODE_POS[u], NODE_POS[v], C_GRAY, lw=1.2, style="dashed")

    for node, pos in NODE_POS.items():
        _draw_node(ax0, node, pos, C_PANEL)
        ax0.text(pos[0] + 0.26, pos[1] + 0.26,
                 str(FINISH_ORDER[node]),
                 ha="center", va="center", fontsize=9, color=C_INK,
                 fontweight="bold", zorder=5)

    # Node labels (dark text on light node)
    for node, pos in NODE_POS.items():
        circle = mpatches.Circle(pos, 0.22, facecolor=C_PANEL, edgecolor=C_INK,
                                 zorder=3, linewidth=1.5)
        ax0.add_patch(circle)
        ax0.text(pos[0], pos[1], str(node), ha="center", va="center",
                 fontsize=10, color=C_INK, fontweight="bold", zorder=4)

    # --- Panel 1: G^T with DFS-tree colors ---
    ax1 = axes[1]
    ax1.set_title("Проход 2: $G^T$, цвет = найденная SCC", color=C_INK, fontsize=11)

    # Reversed edges
    GT_INTRA = [(v, u) for u, v in EDGES_INTRA]
    GT_CROSS = [(v, u) for u, v in EDGES_CROSS]

    for u, v in GT_INTRA:
        pu, pv = NODE_POS[u], NODE_POS[v]
        rad = 0.25 if abs(u - v) == 1 and u > 3 else 0.0
        _draw_arrow(ax1, pu, pv, C_GRAY, lw=1.5, radius=rad)
    for u, v in GT_CROSS:
        _draw_arrow(ax1, NODE_POS[u], NODE_POS[v], C_GRAY, lw=1.2, style="dashed")

    for node, pos in NODE_POS.items():
        circle = mpatches.Circle(pos, 0.22, facecolor=PASS2_COLOR[node],
                                 edgecolor=C_INK, zorder=3, linewidth=1.5)
        ax1.add_patch(circle)
        ax1.text(pos[0], pos[1], str(node), ha="center", va="center",
                 fontsize=10, color="white", fontweight="bold", zorder=4)

    legend_patches = [
        mpatches.Patch(color=C_ORANGE, label="SCC A"),
        mpatches.Patch(color=C_GRAY,   label="SCC D"),
        mpatches.Patch(color=C_BLUE,   label="SCC B"),
        mpatches.Patch(color=C_GREEN,  label="SCC C"),
    ]
    ax1.legend(handles=legend_patches, loc="upper left", fontsize=9,
               framealpha=0.7, facecolor=C_PANEL)

    plt.tight_layout()
    _save(fig, "kosaraju")


def draw_condensation():
    """Left: original graph. Right: condensation DAG with SCC boxes."""
    _apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.patch.set_facecolor(C_BG)
    fig.suptitle("Конденсация орграфа", fontsize=13, fontweight="bold", color=C_INK)

    # --- Left panel: original graph ---
    ax0 = axes[0]
    ax0.set_facecolor(C_BG)
    ax0.set_xlim(0, 8.5)
    ax0.set_ylim(1.0, 4.2)
    ax0.set_aspect("equal")
    ax0.axis("off")
    ax0.set_title("Исходный орграф", color=C_INK, fontsize=11)

    for u, v in EDGES_INTRA:
        rad = 0.25 if (u, v) in [(4, 5), (5, 4), (6, 7), (7, 6)] else 0.0
        _draw_arrow(ax0, NODE_POS[u], NODE_POS[v], SCC_COLORS[NODE_SCC[u]],
                    lw=2.0, radius=rad)
    for u, v in EDGES_CROSS:
        _draw_arrow(ax0, NODE_POS[u], NODE_POS[v], C_INK, lw=1.2, style="dashed")

    for node, pos in NODE_POS.items():
        _draw_node(ax0, node, pos, SCC_COLORS[NODE_SCC[node]])

    # --- Right panel: condensation DAG ---
    ax1 = axes[1]
    ax1.set_facecolor(C_BG)
    ax1.set_xlim(0, 6)
    ax1.set_ylim(0.5, 4.0)
    ax1.set_aspect("equal")
    ax1.axis("off")
    ax1.set_title("Конденсация (DAG)", color=C_INK, fontsize=11)

    # Condensation node positions
    COND_POS = {
        "A": (1.0, 2.5),
        "D": (2.8, 2.5),
        "B": (2.8, 1.0),
        "C": (4.6, 2.5),
    }
    COND_LABELS = {
        "A": "{0,1,2}",
        "D": "{3}",
        "B": "{4,5}",
        "C": "{6,7}",
    }
    # Edges in condensation: A->D, D->A(? no, 3->1 means D->A), B->D(4->3), D->C, B->C
    # A(={0,1,2}) -> D(={3}) via edge 2->3
    # D(={3}) -> A(={0,1,2}) via edge 3->1
    # B(={4,5}) -> D(={3}) via edge 4->3
    # D(={3}) -> C(={6,7}) via edge 3->6
    # B(={4,5}) -> C(={6,7}) via edge 5->6
    COND_EDGES = [
        ("A", "D"),
        ("D", "A"),
        ("B", "D"),
        ("D", "C"),
        ("B", "C"),
    ]

    for u_scc, v_scc in COND_EDGES:
        pu = COND_POS[u_scc]
        pv = COND_POS[v_scc]
        rad = 0.2 if (u_scc, v_scc) in [("A", "D"), ("D", "A")] else 0.0
        _draw_arrow(ax1, pu, pv, C_INK, lw=1.8, radius=rad)

    for scc_name, pos in COND_POS.items():
        box_w, box_h = 1.1, 0.55
        rect = mpatches.FancyBboxPatch(
            (pos[0] - box_w / 2, pos[1] - box_h / 2),
            box_w, box_h,
            boxstyle="round,pad=0.06",
            facecolor=SCC_COLORS[scc_name], edgecolor=C_INK,
            linewidth=1.5, zorder=3, alpha=0.85
        )
        ax1.add_patch(rect)
        ax1.text(pos[0], pos[1] + 0.1, f"SCC {scc_name}",
                 ha="center", va="center", fontsize=10, color="white",
                 fontweight="bold", zorder=4)
        ax1.text(pos[0], pos[1] - 0.14, COND_LABELS[scc_name],
                 ha="center", va="center", fontsize=8, color="white", zorder=4)

    plt.tight_layout()
    _save(fig, "condensation")


def main():
    draw_sccs()
    draw_kosaraju()
    draw_condensation()


if __name__ == "__main__":
    main()
