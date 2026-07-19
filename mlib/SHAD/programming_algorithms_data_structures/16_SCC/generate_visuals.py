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

# Graph definition (8 nodes, 4 SCCs)
# SCC A = {0,1,2}, SCC D = {3}, SCC B = {4,5}, SCC C = {6,7}
# Edges within SCCs: 0->1, 1->2, 2->0 ; 4->5, 5->4 ; 6->7, 7->6
# Cross-SCC edges: 2->3 (A->D), 4->3 (B->D), 3->6 (D->C), 5->6 (B->C)
# NB: no edge out of 3 back into {0,1,2} — otherwise 3 would join SCC A

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


def _draw_arrow(ax, p1, p2, color, lw=1.5, style="solid", radius=0.0, r=0.22):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dist = (dx**2 + dy**2) ** 0.5
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

    # Draw SCC background regions: (xy, width, height, color)
    scc_regions = [
        ((0.4, 1.3), 2.6, 2.4, C_ORANGE),
        ((3.5, 2.0), 1.0, 1.0, C_GRAY),
        ((4.9, 1.3), 1.3, 2.4, C_BLUE),
        ((6.4, 1.3), 1.3, 2.4, C_GREEN),
    ]
    for xy, w, h, color in scc_regions:
        rect = mpatches.FancyBboxPatch(
            xy, w, h,
            boxstyle="round,pad=0.05", linewidth=0, color=color, alpha=0.18, zorder=0
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

    # Finish order from pass 1 (manual trace, DFS from 0 then from 4):
    # DFS(0): 0->1->2->(0 visited)->3->6->7; finishes 7, 6, 3, 2, 1, 0
    # DFS(4): 4->(3 visited)->5; finishes 5, 4
    # order (по времени завершения) = [7, 6, 3, 2, 1, 0, 5, 4]
    FINISH_ORDER = {7: 1, 6: 2, 3: 3, 2: 4, 1: 5, 0: 6, 5: 7, 4: 8}

    # Pass 2 SCC colors (DFS on G^T from 4 first -> SCC B, then 0 -> SCC A, etc.)
    PASS2_COLOR = {
        0: C_ORANGE, 1: C_ORANGE, 2: C_ORANGE,  # SCC A
        3: C_GRAY,                                # SCC D
        4: C_BLUE,   5: C_BLUE,                  # SCC B
        6: C_GREEN,  7: C_GREEN,                  # SCC C
    }

    for _, ax in enumerate(axes):
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
    # Edges in condensation (a DAG):
    # A(={0,1,2}) -> D(={3}) via edge 2->3
    # B(={4,5}) -> D(={3}) via edge 4->3
    # D(={3}) -> C(={6,7}) via edge 3->6
    # B(={4,5}) -> C(={6,7}) via edge 5->6
    COND_EDGES = [
        ("A", "D"),
        ("B", "D"),
        ("D", "C"),
        ("B", "C"),
    ]

    for u_scc, v_scc in COND_EDGES:
        pu = COND_POS[u_scc]
        pv = COND_POS[v_scc]
        _draw_arrow(ax1, pu, pv, C_INK, lw=1.8, radius=0.0, r=0.55)

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


def draw_kosaraju_lemma():
    """Condensation DAG labeled with f(C) = max finish time per SCC.

    All data (finish order, components, condensation edges) is computed by an
    honest simulation of Kosaraju's algorithm on the lecture graph — the
    figure demonstrates the lemma: every condensation edge goes from a
    component with larger f to one with smaller f.
    """
    _apply_style()

    n = 8
    edges = EDGES_INTRA + EDGES_CROSS
    adj = [[] for _ in range(n)]
    radj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        radj[v].append(u)

    # --- Pass 1: DFS on G, record finish order ---
    visited = [False] * n
    order = []

    def dfs1(v):
        visited[v] = True
        for u in adj[v]:
            if not visited[u]:
                dfs1(u)
        order.append(v)

    for v in range(n):
        if not visited[v]:
            dfs1(v)

    finish_pos = {v: i + 1 for i, v in enumerate(order)}  # 1-based

    # --- Pass 2: DFS on G^T in reverse finish order -> components ---
    comp = [-1] * n

    def dfs2(v, c):
        comp[v] = c
        for u in radj[v]:
            if comp[u] == -1:
                dfs2(u, c)

    num_scc = 0
    for v in reversed(order):
        if comp[v] == -1:
            dfs2(v, num_scc)
            num_scc += 1

    # Map component ids to the lecture's letter names via member sets
    comp_members = {}
    for v in range(n):
        comp_members.setdefault(comp[v], []).append(v)
    comp_letter = {}
    for cid, members in comp_members.items():
        for letter, ref in SCC_MEMBERS.items():
            if sorted(members) == sorted(ref):
                comp_letter[cid] = letter

    # f(C) = max finish position per component
    f_val = {comp_letter[cid]: max(finish_pos[v] for v in members)
             for cid, members in comp_members.items()}

    # Condensation edges (deduplicated), in letter names
    cond_edges = sorted({(comp_letter[comp[u]], comp_letter[comp[v]])
                         for u, v in edges if comp[u] != comp[v]})

    # --- Drawing ---
    fig, ax = plt.subplots(figsize=(9, 4.6))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 7.2)
    ax.set_ylim(-0.25, 4.0)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Лемма Косарайю: ребро конденсации $C \\to C'$ ⇒ $f(C) > f(C')$",
                 color=C_INK, fontsize=12, fontweight="bold", pad=10)

    # Layout: sources on the left, D above the B->C edge, C bottom-right
    POS = {"B": (1.1, 1.0), "A": (1.1, 3.1), "D": (3.4, 2.7), "C": (5.9, 1.4)}
    LABELS = {c: "{" + ",".join(map(str, sorted(vs))) + "}"
              for c, vs in SCC_MEMBERS.items()}

    for u_c, v_c in cond_edges:
        pu, pv = POS[u_c], POS[v_c]
        _draw_arrow(ax, pu, pv, C_INK, lw=1.8, r=0.75)
        # edge label: f(u) > f(v)
        mx, my = (pu[0] + pv[0]) / 2, (pu[1] + pv[1]) / 2
        dx, dy = pv[0] - pu[0], pv[1] - pu[1]
        norm = (dx**2 + dy**2) ** 0.5
        ox, oy = -dy / norm * 0.30, dx / norm * 0.30
        ax.text(mx + ox, my + oy, f"{f_val[u_c]} > {f_val[v_c]}",
                ha="center", va="center", fontsize=9, color=C_ORANGE,
                fontweight="bold")

    for c, pos in POS.items():
        box_w, box_h = 1.35, 0.72
        rect = mpatches.FancyBboxPatch(
            (pos[0] - box_w / 2, pos[1] - box_h / 2), box_w, box_h,
            boxstyle="round,pad=0.06",
            facecolor=SCC_COLORS[c], edgecolor=C_INK,
            linewidth=1.5, zorder=3, alpha=0.9)
        ax.add_patch(rect)
        ax.text(pos[0], pos[1] + 0.13, f"SCC {c} {LABELS[c]}",
                ha="center", va="center", fontsize=9.5, color="white",
                fontweight="bold", zorder=4)
        ax.text(pos[0], pos[1] - 0.17, f"$f = {f_val[c]}$",
                ha="center", va="center", fontsize=10, color="white", zorder=4)

    topo = " > ".join(f"{c}({f_val[c]})"
                      for c in sorted(f_val, key=f_val.get, reverse=True))
    ax.text(3.6, 0.12,
            f"Убывание f: {topo} — топологический порядок конденсации.\n"
            "f(C) = максимальный номер завершения вершины компоненты в первом проходе DFS",
            ha="center", va="center", fontsize=9, color=C_GRAY)

    _save(fig, "kosaraju_lemma")


def main():
    draw_sccs()
    draw_kosaraju()
    draw_condensation()
    draw_kosaraju_lemma()


if __name__ == "__main__":
    main()
