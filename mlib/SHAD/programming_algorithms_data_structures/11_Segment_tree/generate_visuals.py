from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

C_BG     = "#faf9f5"
C_INK    = "#141413"
C_GRAY   = "#b0aea5"
C_PANEL  = "#e8e6dc"
C_ORANGE = "#d97757"
C_BLUE   = "#6a9bcc"
C_GREEN  = "#788c5d"

ROOT   = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"


def _apply_style():
    plt.rcParams.update({
        "figure.facecolor": C_BG,
        "axes.facecolor":   C_BG,
        "font.family":      "DejaVu Sans",
        "font.size":        10,
    })


def _save(fig, name):
    ASSETS.mkdir(exist_ok=True)
    path = ASSETS / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)
    print(f"Saved: {path}")


# ── helpers ──────────────────────────────────────────────────────────────────

def _draw_node(ax, x, y, label, fill, radius=0.38):
    circle = mpatches.Circle(
        (x, y), radius,
        facecolor=fill, edgecolor=C_INK, linewidth=1.5, zorder=3,
    )
    ax.add_patch(circle)
    ax.text(
        x, y, label,
        ha="center", va="center",
        fontsize=8, color=C_INK, zorder=4,
    )


def _edge(ax, x1, y1, x2, y2):
    ax.plot([x1, x2], [y1, y2], color=C_GRAY, linewidth=1.2, zorder=1)


# ── Figure 1: segment tree for A=[1,3,5,7,9,11] with query [2,4] highlighted ─

def draw_segment_tree():
    """
    Binary tree for A=[1,3,5,7,9,11].
    Each node shows [l,r] and sum. Query [2,4] nodes highlighted orange.
    """
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(-0.5, 11.5)
    ax.set_ylim(-0.5, 5.5)
    ax.axis("off")
    ax.set_facecolor(C_BG)
    fig.patch.set_facecolor(C_BG)
    ax.set_title(
        "Дерево отрезков: A = [1, 3, 5, 7, 9, 11]  |  запрос sum[2,4] (оранжевый)",
        color=C_INK, fontsize=11, pad=12,
    )

    # node layout: (x, y, label, color)
    # levels: y=4 root, y=3 level1, y=2 level2, y=1 level3 (leaves)
    # A=[1,3,5,7,9,11], n=6, mid=(0+5)/2=2
    # Node1 [0,5]=36
    # Node2 [0,2]=9,  Node3 [3,5]=27
    # Node4 [0,1]=4,  Node5 [2,2]=5,  Node6 [3,4]=16,  Node7 [5,5]=11
    # Node8 [0,0]=1,  Node9 [1,1]=3,  Node12 [3,3]=7,  Node13 [4,4]=9

    # Query [2,4]:
    #   Node1 partial, Node2 partial, Node3 partial
    #   Node4 outside, Node5 inside(orange), Node6 inside(orange), Node7 outside
    #   Node8 outside, Node9 outside, Node12 -, Node13 -

    nodes = {
        1:  (5.5, 4.2, "[0,5]\n36",   C_PANEL),
        2:  (2.5, 3.0, "[0,2]\n9",    C_PANEL),
        3:  (8.5, 3.0, "[3,5]\n27",   C_PANEL),
        4:  (1.0, 1.8, "[0,1]\n4",    C_GRAY),
        5:  (4.0, 1.8, "[2,2]\n5",    C_ORANGE),
        6:  (7.0, 1.8, "[3,4]\n16",   C_ORANGE),
        7:  (10.0, 1.8, "[5,5]\n11",  C_GRAY),
        8:  (0.2, 0.5, "[0,0]\n1",    C_GRAY),
        9:  (1.8, 0.5, "[1,1]\n3",    C_GRAY),
        12: (6.2, 0.5, "[3,3]\n7",    C_PANEL),
        13: (7.8, 0.5, "[4,4]\n9",    C_PANEL),
    }

    # edges
    edges = [
        (1, 2), (1, 3),
        (2, 4), (2, 5),
        (3, 6), (3, 7),
        (4, 8), (4, 9),
        (6, 12), (6, 13),
    ]
    for parent, child in edges:
        px, py = nodes[parent][0], nodes[parent][1]
        cx, cy = nodes[child][0],  nodes[child][1]
        _edge(ax, px, py, cx, cy)

    for _, (x, y, label, color) in nodes.items():
        _draw_node(ax, x, y, label, fill=color, radius=0.42)

    # legend
    legend_items = [
        mpatches.Patch(facecolor=C_ORANGE, edgecolor=C_INK, label="Полностью внутри [2,4]"),
        mpatches.Patch(facecolor=C_GRAY,   edgecolor=C_INK, label="Вне запроса"),
        mpatches.Patch(facecolor=C_PANEL,  edgecolor=C_INK, label="Частично / не задействован"),
    ]
    ax.legend(handles=legend_items, loc="lower left", fontsize=9,
              framealpha=0.8, facecolor=C_BG, edgecolor=C_GRAY)

    _save(fig, "segment_tree")


# ── Figure 2: query trace [2,4] with annotation ──────────────────────────────

def draw_query_trace():
    """
    Same tree, but annotated with query [2,4] trace:
    gray = outside (return 0), orange = fully inside (return value), blue = partial (recurse).
    """
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(-0.5, 11.5)
    ax.set_ylim(-0.5, 5.8)
    ax.axis("off")
    ax.set_facecolor(C_BG)
    fig.patch.set_facecolor(C_BG)
    ax.set_title(
        "Трассировка query sum[2,4]: серый=вне, синий=частично (рекурсия), оранжевый=внутри",
        color=C_INK, fontsize=11, pad=12,
    )

    # Colors: gray=outside, blue=partial, orange=fully inside
    nodes = {
        1:  (5.5, 4.2, "[0,5]\nreturn 21", C_BLUE),
        2:  (2.5, 3.0, "[0,2]\nreturn 5",  C_BLUE),
        3:  (8.5, 3.0, "[3,5]\nreturn 16", C_BLUE),
        4:  (1.0, 1.8, "[0,1]\nreturn 0",  C_GRAY),
        5:  (4.0, 1.8, "[2,2]\nreturn 5",  C_ORANGE),
        6:  (7.0, 1.8, "[3,4]\nreturn 16", C_ORANGE),
        7:  (10.0, 1.8, "[5,5]\nreturn 0", C_GRAY),
    }

    edges = [
        (1, 2), (1, 3),
        (2, 4), (2, 5),
        (3, 6), (3, 7),
    ]
    for parent, child in edges:
        px, py = nodes[parent][0], nodes[parent][1]
        cx, cy = nodes[child][0],  nodes[child][1]
        _edge(ax, px, py, cx, cy)

    for _, (x, y, label, color) in nodes.items():
        _draw_node(ax, x, y, label, fill=color, radius=0.48)

    # annotation arrows showing call order
    call_order = [
        (5.5, 4.2, "1. query(1,[0,5])"),
        (2.5, 3.0, "2. query(2,[0,2])"),
        (1.0, 1.8, "3. query(4,[0,1])\n→ 0"),
        (4.0, 1.8, "4. query(5,[2,2])\n→ 5"),
        (8.5, 3.0, "5. query(3,[3,5])"),
        (7.0, 1.8, "6. query(6,[3,4])\n→ 16"),
        (10.0, 1.8, "7. query(7,[5,5])\n→ 0"),
    ]
    for x, y, txt in call_order:
        ax.text(x, y - 0.65, txt, ha="center", va="top",
                fontsize=7, color=C_INK, style="italic")

    legend_items = [
        mpatches.Patch(facecolor=C_ORANGE, edgecolor=C_INK, label="Полностью внутри → возврат значения"),
        mpatches.Patch(facecolor=C_GRAY,   edgecolor=C_INK, label="Вне запроса → возврат 0"),
        mpatches.Patch(facecolor=C_BLUE,   edgecolor=C_INK, label="Частичное пересечение → рекурсия"),
    ]
    ax.legend(handles=legend_items, loc="lower left", fontsize=9,
              framealpha=0.8, facecolor=C_BG, edgecolor=C_GRAY)

    _save(fig, "query_trace")


# ── Figure 3: lazy propagation three-panel diagram ───────────────────────────

def draw_lazy_propagation():
    """
    Simplified 4-element tree with lazy tags.
    Three panels: initial, after range update (tag stored), after push-down.
    """
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    fig.patch.set_facecolor(C_BG)

    titles = [
        "Исходное дерево\nA=[1,2,3,4]",
        "После range_add([1,3], +5)\n(lazy тег в узлах)",
        "После push_down\n(теги переданы потомкам)",
    ]

    # Panel data: list of (x, y, label, fill, lazy_label)
    # n=4: tree[1]=[0,3], tree[2]=[0,1], tree[3]=[2,3]
    #       tree[4]=[0,0], tree[5]=[1,1], tree[6]=[2,2], tree[7]=[3,3]

    panels = [
        # Panel 0: initial  sum=[1,2,3,4]
        [
            (2.0, 3.2, "[0,3]\n10",  C_PANEL,  ""),
            (1.0, 2.0, "[0,1]\n3",   C_PANEL,  ""),
            (3.0, 2.0, "[2,3]\n7",   C_PANEL,  ""),
            (0.4, 0.8, "[0,0]\n1",   C_PANEL,  ""),
            (1.6, 0.8, "[1,1]\n2",   C_PANEL,  ""),
            (2.4, 0.8, "[2,2]\n3",   C_PANEL,  ""),
            (3.6, 0.8, "[3,3]\n4",   C_PANEL,  ""),
        ],
        # Panel 1: after range_add([1,3], +5)
        # tree[1]=10+14=24? No:
        # range_add([1,3],5): node1 partial→split
        #   node2 partial→split
        #     node4 [0,0]: outside
        #     node5 [1,1]: inside → tree[5]=2+5=7, lazy[5]=5
        #   tree[2] = 1+7=8
        #   node3 [2,3]: inside → tree[3]=7+10=17, lazy[3]=5
        # tree[1]=8+17=25
        [
            (2.0, 3.2, "[0,3]\n25",  C_PANEL,  ""),
            (1.0, 2.0, "[0,1]\n8",   C_PANEL,  ""),
            (3.0, 2.0, "[2,3]\n17",  C_ORANGE, "lazy=5"),
            (0.4, 0.8, "[0,0]\n1",   C_GRAY,   ""),
            (1.6, 0.8, "[1,1]\n7",   C_GREEN,  "lazy=5"),
            (2.4, 0.8, "[2,2]\n3",   C_GRAY,   "стар."),
            (3.6, 0.8, "[3,3]\n4",   C_GRAY,   "стар."),
        ],
        # Panel 2: after push_down(node3)
        # push_down node3 [2,3]: lazy=5 → передаём детям
        #   node6 [2,2]: tree=3+5*1=8, lazy=5
        #   node7 [3,3]: tree=4+5*1=9, lazy=5
        #   lazy[3]=0
        [
            (2.0, 3.2, "[0,3]\n25",  C_PANEL,  ""),
            (1.0, 2.0, "[0,1]\n8",   C_PANEL,  ""),
            (3.0, 2.0, "[2,3]\n17",  C_PANEL,  "lazy=0"),
            (0.4, 0.8, "[0,0]\n1",   C_GRAY,   ""),
            (1.6, 0.8, "[1,1]\n7",   C_GREEN,  "lazy=5"),
            (2.4, 0.8, "[2,2]\n8",   C_ORANGE, "lazy=5"),
            (3.6, 0.8, "[3,3]\n9",   C_ORANGE, "lazy=5"),
        ],
    ]

    tree_edges = [
        (0, 1), (0, 2),
        (1, 3), (1, 4),
        (2, 5), (2, 6),
    ]

    for panel_idx, ax in enumerate(axes):
        ax.set_facecolor(C_BG)
        ax.set_xlim(-0.2, 4.2)
        ax.set_ylim(0.0, 4.2)
        ax.axis("off")
        ax.set_title(titles[panel_idx], color=C_INK, fontsize=9, pad=8)

        node_data = panels[panel_idx]

        # draw edges
        for parent_i, child_i in tree_edges:
            px, py = node_data[parent_i][0], node_data[parent_i][1]
            cx, cy = node_data[child_i][0],  node_data[child_i][1]
            ax.plot([px, cx], [py, cy], color=C_GRAY, linewidth=1.2, zorder=1)

        # draw nodes
        for nd in node_data:
            x, y, label, fill, lazy_lbl = nd
            circle = mpatches.Circle(
                (x, y), 0.35,
                facecolor=fill, edgecolor=C_INK, linewidth=1.4, zorder=3,
            )
            ax.add_patch(circle)
            ax.text(x, y, label, ha="center", va="center",
                    fontsize=7.5, color=C_INK, zorder=4)
            if lazy_lbl:
                # small box for lazy tag
                rect = mpatches.FancyBboxPatch(
                    (x + 0.28, y + 0.22), 0.56, 0.24,
                    boxstyle="round,pad=0.03",
                    facecolor=C_ORANGE, edgecolor=C_INK,
                    linewidth=0.8, zorder=5,
                )
                ax.add_patch(rect)
                ax.text(x + 0.56, y + 0.34, lazy_lbl,
                        ha="center", va="center",
                        fontsize=6, color=C_BG, zorder=6, fontweight="bold")

    fig.suptitle(
        "Ленивая пропагация: range_add([1,3], +5)  →  push_down",
        color=C_INK, fontsize=11, y=1.01,
    )

    _save(fig, "lazy_propagation")


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    _apply_style()
    draw_segment_tree()
    draw_query_trace()
    draw_lazy_propagation()


if __name__ == "__main__":
    main()
