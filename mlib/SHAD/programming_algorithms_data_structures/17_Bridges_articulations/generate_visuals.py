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

    # Articulation points: 2, 3, 5
    # (removing 2 detaches {0,1}; removing 3 detaches {0,1,2};
    #  removing 5 detaches {6})
    articulations = {2, 3, 5}

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

    # Labels: what disconnects when each AP is removed
    ax.text(1.0, 3.3, "убрать 2 →\nотделится {0, 1}", color=C_BLUE, fontsize=9,
            ha="center", style="italic")
    ax.text(3.5, 3.3, "убрать 3 →\nотделится {0, 1, 2}", color=C_BLUE, fontsize=9,
            ha="center", style="italic")
    ax.text(6.3, 3.3, "убрать 5 →\nотделится {6}", color=C_BLUE, fontsize=9,
            ha="center", style="italic")

    # Arrows from labels to the APs
    ax.annotate("", xy=(2.0, 1.95), xytext=(1.4, 3.05),
                arrowprops={"arrowstyle": "->", "color": C_GRAY, "lw": 1.0})
    ax.annotate("", xy=(3.5, 1.95), xytext=(3.5, 3.05),
                arrowprops={"arrowstyle": "->", "color": C_GRAY, "lw": 1.0})
    ax.annotate("", xy=(5.15, 0.95), xytext=(6.1, 3.05),
                arrowprops={"arrowstyle": "->", "color": C_GRAY, "lw": 1.0})

    # Legend
    ap_patch = mpatches.Patch(color=C_ORANGE, label="Точка сочленения (AP)")
    normal_patch = mpatches.Patch(color=C_BLUE, label="Обычная вершина")
    ax.legend(handles=[ap_patch, normal_patch], loc="lower left",
              facecolor=C_PANEL, edgecolor=C_GRAY, fontsize=10)

    ax.set_title("Точки сочленения (оранжевые кольца)", color=C_INK,
                 fontsize=14, fontweight="bold", pad=10)
    _save(fig, "articulations.png")


def draw_block_cut_tree():
    """Left: graph colored by BCC. Right: its block-cut tree."""
    _apply_style()
    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor(C_BG)
    for ax in (ax_l, ax_r):
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_facecolor(C_BG)

    # ---- Left: graph {0-1,1-2,2-0, 2-3, 3-4,4-5,5-3} colored by BCC ----
    ax_l.set_xlim(-0.6, 6.2)
    ax_l.set_ylim(-0.6, 3.6)
    pos = {
        0: (0.5, 2.5),
        1: (0.5, 0.5),
        2: (2.0, 1.5),
        3: (3.8, 1.5),
        4: (5.3, 2.5),
        5: (5.3, 0.5),
    }
    bcc1 = [(0, 1), (1, 2), (0, 2)]          # triangle B1
    bcc2 = [(2, 3)]                           # bridge B2
    bcc3 = [(3, 4), (4, 5), (3, 5)]           # triangle B3

    for u, v in bcc1:
        _draw_edge(ax_l, pos[u], pos[v], C_BLUE, lw=3.0)
    for u, v in bcc2:
        _draw_edge(ax_l, pos[u], pos[v], C_ORANGE, lw=3.5)
    for u, v in bcc3:
        _draw_edge(ax_l, pos[u], pos[v], C_GREEN, lw=3.0)

    articulations = {2, 3}
    for node, (x, y) in pos.items():
        if node in articulations:
            ring = mpatches.Circle((x, y), 0.36, color=C_ORANGE, zorder=3)
            ax_l.add_patch(ring)
            inner = mpatches.Circle((x, y), 0.26, color=C_INK, zorder=4)
            ax_l.add_patch(inner)
            ax_l.text(x, y, str(node), ha="center", va="center", fontsize=12,
                      color="white", fontweight="bold", zorder=5)
        else:
            _draw_node(ax_l, x, y, str(node), C_INK, radius=0.26, fontsize=12)

    ax_l.text(0.9, 3.15, "B1", color=C_BLUE, fontsize=13, fontweight="bold")
    ax_l.text(2.75, 2.0, "B2", color=C_ORANGE, fontsize=13, fontweight="bold")
    ax_l.text(4.9, 3.15, "B3", color=C_GREEN, fontsize=13, fontweight="bold")
    ax_l.set_title("Двусвязные компоненты (BCC)", color=C_INK,
                   fontsize=13, fontweight="bold", pad=8)

    # ---- Right: block-cut tree  B1 - 2 - B2 - 3 - B3 ----
    ax_r.set_xlim(-0.7, 8.7)
    ax_r.set_ylim(0.2, 2.8)
    chain = [
        ("B1", C_BLUE, "block"),
        ("2", C_ORANGE, "cut"),
        ("B2", C_ORANGE, "block"),
        ("3", C_ORANGE, "cut"),
        ("B3", C_GREEN, "block"),
    ]
    xs = [0.0, 2.0, 4.0, 6.0, 8.0]
    y = 1.5
    for i in range(len(chain) - 1):
        _draw_edge(ax_r, (xs[i], y), (xs[i + 1], y), C_GRAY, lw=2.2)
    for (label, color, kind), x in zip(chain, xs):
        if kind == "block":
            sq = mpatches.FancyBboxPatch(
                (x - 0.42, y - 0.42), 0.84, 0.84,
                boxstyle="round,pad=0.04",
                facecolor=color, edgecolor=C_INK, linewidth=1.5, zorder=4)
            ax_r.add_patch(sq)
            ax_r.text(x, y, label, ha="center", va="center", fontsize=12,
                      color="white", fontweight="bold", zorder=5)
        else:
            ring = mpatches.Circle((x, y), 0.40, color=C_ORANGE, zorder=3)
            ax_r.add_patch(ring)
            inner = mpatches.Circle((x, y), 0.30, color=C_INK, zorder=4)
            ax_r.add_patch(inner)
            ax_r.text(x, y, label, ha="center", va="center", fontsize=12,
                      color="white", fontweight="bold", zorder=5)

    sq_patch = mpatches.Patch(color=C_BLUE, label="Узел-компонента (BCC)")
    ap_patch = mpatches.Patch(color=C_ORANGE, label="Точка сочленения")
    ax_r.legend(handles=[sq_patch, ap_patch], loc="lower center",
                facecolor=C_PANEL, edgecolor=C_GRAY, fontsize=9, ncol=2)
    ax_r.set_title("Block-cut дерево", color=C_INK,
                   fontsize=13, fontweight="bold", pad=8)

    _save(fig, "block_cut_tree.png")


def _dfs_disc_low(n, edges, start=0):
    """Честный DFS: возвращает disc, low, древесные и обратные рёбра, родителей."""
    adj = {v: [] for v in range(n)}
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    for v in adj:
        adj[v].sort()

    disc, low, parent = {}, {}, {start: None}
    tree_edges, back_edges = [], []
    timer = [0]

    def dfs(u):
        disc[u] = low[u] = timer[0]; timer[0] += 1
        for v in adj[u]:
            if v not in disc:
                parent[v] = u
                tree_edges.append((u, v))
                dfs(v)
                low[u] = min(low[u], low[v])
            elif v != parent[u] and disc[v] < disc[u]:
                back_edges.append((u, v))
                low[u] = min(low[u], disc[v])

    dfs(start)
    return disc, low, parent, tree_edges, back_edges


def _subtree(v, tree_edges):
    """Множество вершин поддерева v в DFS-дереве."""
    children = {}
    for a, b in tree_edges:
        children.setdefault(a, []).append(b)
    res, stack = set(), [v]
    while stack:
        x = stack.pop()
        res.add(x)
        stack.extend(children.get(x, []))
    return res


def draw_bridge_detour():
    """Почему обратное ребро спасает ребро от мостовости: обе стороны критерия.

    Данные (disc, low, обратные рёбра, обходной маршрут) вычисляются честной
    симуляцией DFS на сквозном графе лекции {0-1,1-2,2-0,2-3,3-4,4-5,5-3}.
    """
    _apply_style()
    n = 6
    edges = [(0, 1), (1, 2), (0, 2), (2, 3), (3, 4), (4, 5), (3, 5)]
    disc, low, parent, tree_edges, back_edges = _dfs_disc_low(n, edges)

    pos = {
        0: (0.5, 3.0),
        1: (0.5, 1.0),
        2: (2.0, 2.0),
        3: (3.8, 2.0),
        4: (5.3, 3.0),
        5: (5.3, 1.0),
    }

    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(12.5, 5.2))
    fig.patch.set_facecolor(C_BG)
    for ax in (ax_l, ax_r):
        ax.set_xlim(-0.6, 6.4)
        ax.set_ylim(-0.9, 4.3)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_facecolor(C_BG)

    def draw_graph(ax, focus_edge, removed=False):
        for (a, b) in edges:
            e = tuple(sorted((a, b)))
            if e == tuple(sorted(focus_edge)):
                continue
            _draw_edge(ax, pos[a], pos[b], C_GRAY, lw=2.2)
        fa, fb = focus_edge
        if removed:
            _draw_edge(ax, pos[fa], pos[fb], C_GRAY, lw=2.0, ls=":")
            mx, my = (pos[fa][0] + pos[fb][0]) / 2, (pos[fa][1] + pos[fb][1]) / 2
            ax.text(mx, my, "×", color=C_INK, fontsize=20, ha="center",
                    va="center", fontweight="bold", zorder=6)
        else:
            _draw_edge(ax, pos[fa], pos[fb], C_ORANGE, lw=3.5)

    # ---------- Левая панель: (u,v)=(3,4), обратное ребро спасает ----------
    u, v = 3, 4
    assert low[v] <= disc[u], "критерий: обратное ребро должно спасать (3,4)"
    # Ищем спасительное обратное ребро (x,w): x в поддереве v, disc[w] <= disc[u]
    sub_v = _subtree(v, tree_edges)
    x, w = next((x, w) for x, w in back_edges if x in sub_v and disc[w] <= disc[u])

    # Обходной маршрут: v -> ... -> x по древесным рёбрам, затем (x,w),
    # затем w -> ... -> u по древесному пути (вверх по родителям).
    def tree_path_up(a, b):  # путь b -> ... -> a по родителям (a — предок b)
        path = [b]
        while path[-1] != a:
            path.append(parent[path[-1]])
        return path[::-1]

    detour = tree_path_up(v, x)          # v .. x внутри поддерева
    detour += tree_path_up(w, u)[::-1] if disc[w] <= disc[u] and w != u else []
    # прыжок x -> w уже соединяет куски; если w == u, путь готов

    draw_graph(ax_l, (u, v), removed=True)
    # Спасительное обратное ребро
    ax_l.annotate("", xy=pos[w], xytext=pos[x],
                  arrowprops={"arrowstyle": "->", "color": C_GREEN, "lw": 2.6,
                              "linestyle": "--",
                              "connectionstyle": "arc3,rad=0.35"})
    # Обходной маршрут (древесная часть)
    full = detour + [w] if detour[-1] != w else detour
    for a, b in zip(full, full[1:]):
        if tuple(sorted((a, b))) in {tuple(sorted(e)) for e in edges}:
            _draw_edge(ax_l, pos[a], pos[b], C_GREEN, lw=3.2, zorder=3)

    for node, (px, py) in pos.items():
        col = C_BLUE if node in sub_v else C_INK
        _draw_node(ax_l, px, py, str(node), col, radius=0.26)
        ax_l.text(px - 0.02, py + 0.40, f"d={disc[node]} l={low[node]}",
                  color=C_INK, fontsize=7.5, ha="center", va="bottom", zorder=6)

    ax_l.text(3.0, -0.65,
              f"low[{v}]={low[v]} ≤ disc[{u}]={disc[u]}: обход {v}→{x}→{w} — не мост",
              color=C_GREEN, fontsize=10.5, ha="center", fontweight="bold")
    ax_l.set_title("Обратное ребро спасает: ребро (3,4)",
                   color=C_INK, fontsize=12.5, fontweight="bold", pad=8)

    # ---------- Правая панель: (u,v)=(2,3), мост ----------
    u2, v2 = 2, 3
    assert low[v2] > disc[u2], "критерий: (2,3) должно быть мостом"
    sub_v2 = _subtree(v2, tree_edges)

    # Серая область вокруг поддерева v2
    xs = [pos[t][0] for t in sub_v2]
    ys = [pos[t][1] for t in sub_v2]
    pad = 0.62
    box = mpatches.FancyBboxPatch(
        (min(xs) - pad, min(ys) - pad),
        max(xs) - min(xs) + 2 * pad, max(ys) - min(ys) + 2 * pad,
        boxstyle="round,pad=0.10", facecolor=C_PANEL, edgecolor=C_GRAY,
        linewidth=1.4, zorder=1)
    ax_r.add_patch(box)
    ax_r.text(max(xs) + pad - 0.1, min(ys) - pad + 0.05,
              f"поддерево {v2}", color=C_GRAY, fontsize=9, ha="right",
              va="bottom", style="italic")

    draw_graph(ax_r, (u2, v2), removed=False)
    # Все обратные рёбра из поддерева v2 — приземляются внутри
    for x2, w2 in back_edges:
        if x2 in sub_v2:
            ax_r.annotate("", xy=pos[w2], xytext=pos[x2],
                          arrowprops={"arrowstyle": "->", "color": C_GREEN,
                                      "lw": 2.2, "linestyle": "--",
                                      "connectionstyle": "arc3,rad=0.35"})

    for node, (px, py) in pos.items():
        col = C_BLUE if node in sub_v2 else C_INK
        _draw_node(ax_r, px, py, str(node), col, radius=0.26)
        ax_r.text(px - 0.02, py + 0.40, f"d={disc[node]} l={low[node]}",
                  color=C_INK, fontsize=7.5, ha="center", va="bottom", zorder=6)

    mx, my = (pos[u2][0] + pos[v2][0]) / 2, (pos[u2][1] + pos[v2][1]) / 2
    ax_r.text(mx, my + 0.30, "единственный выход", color=C_ORANGE,
              fontsize=9, ha="center", fontweight="bold")
    ax_r.text(3.0, -0.65,
              f"low[{v2}]={low[v2]} > disc[{u2}]={disc[u2]}: все обратные рёбра — внутри, мост",
              color=C_ORANGE, fontsize=10.5, ha="center", fontweight="bold")
    ax_r.set_title("Обратных рёбер наружу нет: ребро (2,3) — мост",
                   color=C_INK, fontsize=12.5, fontweight="bold", pad=8)

    fig.suptitle("Критерий моста low[v] > disc[u]: две стороны на одном графе",
                 color=C_INK, fontsize=13.5, fontweight="bold", y=1.00)
    fig.tight_layout()
    _save(fig, "bridge_detour.png")


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_bridges()
    draw_disc_low()
    draw_articulations()
    draw_block_cut_tree()
    draw_bridge_detour()


if __name__ == "__main__":
    main()
