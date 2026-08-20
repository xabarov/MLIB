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


def _draw_node(ax, x, y, label, facecolor, r=0.30, fontsize=12):
    circ = mpatches.Circle(
        (x, y), r,
        facecolor=facecolor, edgecolor=C_INK, linewidth=2.0, zorder=4
    )
    ax.add_patch(circ)
    ax.text(x, y, str(label), ha="center", va="center",
            fontsize=fontsize, color="white", fontweight="bold", zorder=5)


def _draw_arrow(ax, x1, y1, x2, y2, color=C_GRAY, lw=1.8):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                        mutation_scale=14),
        zorder=3
    )


def draw_dijkstra():
    """Three-panel snapshot of Dijkstra's algorithm on a 6-node graph."""
    _apply_style()

    # Graph: 6 nodes, directed weighted edges
    # Positions
    pos = {
        0: (1.5, 3.5),
        1: (3.5, 4.5),
        2: (3.5, 2.5),
        3: (5.5, 4.5),
        4: (5.5, 2.5),
        5: (7.5, 3.5),
    }
    # Edges: (u, v, weight)
    edges = [
        (0, 1, 2), (0, 2, 4),
        (1, 2, 1), (1, 3, 7),
        (2, 4, 3),
        (3, 5, 1),
        (4, 3, 2), (4, 5, 5),
    ]

    # Three snapshots: (settled set, dist dict, frontier set)
    snapshots = [
        {
            "title": "Шаг 1: закрепляем вершину 0",
            "settled": {0},
            "frontier": {1, 2},
            "dist": {0: 0, 1: 2, 2: 4, 3: "∞", 4: "∞", 5: "∞"},
        },
        {
            "title": "Шаг 2: закрепляем вершину 1 (d=2)",
            "settled": {0, 1},
            "frontier": {2, 3},
            "dist": {0: 0, 1: 2, 2: 3, 3: 9, 4: "∞", 5: "∞"},
        },
        {
            "title": "Шаг 3: закрепляем вершину 2 (d=3)",
            "settled": {0, 1, 2},
            "frontier": {3, 4},
            "dist": {0: 0, 1: 2, 2: 3, 3: 9, 4: 6, 5: "∞"},
        },
    ]

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.patch.set_facecolor(C_BG)
    fig.suptitle("Алгоритм Дийкстры: прогресс по шагам",
                 fontsize=13, color=C_INK, fontweight="bold", y=1.02)

    for ax, snap in zip(axes, snapshots):
        ax.set_facecolor(C_BG)
        ax.set_xlim(0.8, 8.2)
        ax.set_ylim(1.8, 5.3)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(snap["title"], fontsize=10, color=C_INK, pad=6)

        # Draw edges
        for u, v, w in edges:
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            # Shorten arrow to not overlap node circles
            dx, dy = x2 - x1, y2 - y1
            length = (dx**2 + dy**2) ** 0.5
            shrink = 0.32 / length
            sx1 = x1 + dx * shrink
            sy1 = y1 + dy * shrink
            sx2 = x2 - dx * shrink
            sy2 = y2 - dy * shrink
            _draw_arrow(ax, sx1, sy1, sx2, sy2, color=C_GRAY, lw=1.5)
            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2
            ax.text(mx, my + 0.18, str(w), ha="center", va="bottom",
                    fontsize=8, color=C_INK,
                    bbox=dict(facecolor=C_BG, edgecolor="none", pad=1))

        # Draw nodes
        for node, (x, y) in pos.items():
            if node in snap["settled"]:
                color = C_GREEN
            elif node in snap["frontier"]:
                color = C_ORANGE
            else:
                color = C_GRAY
            _draw_node(ax, x, y, node, color)
            d = snap["dist"][node]
            ax.text(x, y - 0.48, f"d={d}", ha="center", va="center",
                    fontsize=8, color=C_INK, zorder=6)

    # Legend (on last axis)
    legend_items = [
        mpatches.Patch(facecolor=C_GREEN, edgecolor=C_INK, label="Закреплена"),
        mpatches.Patch(facecolor=C_ORANGE, edgecolor=C_INK, label="Граница (frontier)"),
        mpatches.Patch(facecolor=C_GRAY, edgecolor=C_INK, label="Не посещена"),
    ]
    axes[2].legend(handles=legend_items, loc="lower right", fontsize=8,
                   facecolor=C_PANEL, edgecolor=C_GRAY)

    plt.tight_layout()
    _save(fig, "dijkstra_progression")


def draw_bellman_ford():
    """Table: rows=iterations (0..4), columns=vertices (0..4)."""
    _apply_style()

    INF = "∞"
    # dist values per iteration for the 5-node example
    # (in-place relaxation, edges in order (0,1),(0,2),(1,2),(1,3),
    #  (1,4),(2,3),(2,4),(3,1),(4,0),(4,3) — updates cascade in pass 1)
    # rows: init, iteration 1, 2, 3 (no change -> early stop)
    table_data = [
        [0, INF, INF, INF, INF],
        [0, 2,   7,   4,   2  ],
        [0, 2,   7,   4,   -2 ],
        [0, 2,   7,   4,   -2 ],
    ]
    # Cells that changed compared to previous row
    changed = [
        set(),
        {1, 2, 3, 4},
        {4},
        set(),
    ]

    n_rows = len(table_data)
    n_cols = len(table_data[0])

    fig, ax = plt.subplots(figsize=(11, 5))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.axis("off")
    ax.set_title(
        "Форд-Беллман: dist[] по итерациям (источник = 0, V=5)",
        fontsize=13, color=C_INK, pad=10
    )

    col_labels = ["v=0", "v=1", "v=2", "v=3", "v=4"]
    row_labels = ["Начало", "Итер. 1", "Итер. 2", "Итер. 3 (стоп)"]

    cell_w = 1.2
    cell_h = 0.6
    x0 = 1.2   # start x (after row labels)
    y0 = 0.2   # bottom y

    total_h = n_rows * cell_h
    total_w = n_cols * cell_w

    # Column headers
    for j, label in enumerate(col_labels):
        cx = x0 + j * cell_w + cell_w / 2
        cy = y0 + total_h + 0.15
        ax.text(cx, cy, label, ha="center", va="bottom",
                fontsize=11, color=C_INK, fontweight="bold")

    # Row labels and cells
    for i, row_label in enumerate(row_labels):
        row_i = n_rows - 1 - i  # bottom-up
        cy = y0 + row_i * cell_h + cell_h / 2
        ax.text(x0 - 0.12, cy, row_label, ha="right", va="center",
                fontsize=10, color=C_INK)

        for j, val in enumerate(table_data[i]):
            cx = x0 + j * cell_w
            is_changed = j in changed[i]
            fc = C_ORANGE if is_changed else C_PANEL
            text_color = "white" if is_changed else C_INK

            rect = mpatches.Rectangle(
                (cx, y0 + row_i * cell_h), cell_w, cell_h,
                facecolor=fc, edgecolor=C_GRAY, linewidth=0.8, zorder=2
            )
            ax.add_patch(rect)
            ax.text(cx + cell_w / 2, cy, str(val),
                    ha="center", va="center",
                    fontsize=11, color=text_color,
                    fontweight="bold" if is_changed else "normal",
                    zorder=3)

    # Highlight annotation for iteration 1 (cascade of relaxations)
    note_x = x0 + total_w + 0.15
    note_y = y0 + (n_rows - 1 - 1) * cell_h + cell_h / 2
    ax.annotate(
        "Каскад в итерации 1:\n(2,3,−3): d[3]=7−3=4,\nзатем (3,1,−2): d[1]=4−2=2",
        xy=(x0 + 1.5 * cell_w, note_y),
        xytext=(note_x, note_y),
        fontsize=8.5, color=C_INK, va="center",
        arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=1.2),
        bbox=dict(facecolor=C_PANEL, edgecolor=C_ORANGE,
                  boxstyle="round,pad=0.3", linewidth=1.2)
    )

    # Legend
    changed_patch = mpatches.Patch(facecolor=C_ORANGE, edgecolor=C_INK,
                                   label="Значение обновлено")
    unchanged_patch = mpatches.Patch(facecolor=C_PANEL, edgecolor=C_GRAY,
                                     label="Без изменений")
    ax.legend(handles=[changed_patch, unchanged_patch],
              loc="lower right", fontsize=9,
              facecolor=C_BG, edgecolor=C_GRAY)

    ax.set_xlim(0.0, x0 + total_w + 3.8)
    ax.set_ylim(y0 - 0.3, y0 + total_h + 0.6)
    plt.tight_layout()
    _save(fig, "bellman_ford_table")


def draw_algorithm_comparison():
    """Comparison table: three algorithms × four properties."""
    _apply_style()

    algorithms = ["Форд-Беллман", "Флойд-Уоршелл", "Дийкстра"]
    columns = ["Сложность", "Отриц. веса", "SSSP / APSP", "Детект. цикла"]

    # (text, background color)
    cells = [
        [("O(VE)",          C_PANEL),
         ("Да",             C_GREEN),
         ("SSSP",           C_BLUE),
         ("Да (V-я итер.)", C_GREEN)],
        [("O(V³)",          C_PANEL),
         ("Да",             C_GREEN),
         ("APSP",           C_ORANGE),
         ("Да (диагональ)", C_GREEN)],
        [("O((V+E) log V)", C_PANEL),
         ("Нет",            C_ORANGE),
         ("SSSP",           C_BLUE),
         ("Нет",            C_ORANGE)],
    ]
    text_colors = {
        C_PANEL:  C_INK,
        C_GREEN:  "white",
        C_BLUE:   "white",
        C_ORANGE: "white",
    }

    n_rows = len(algorithms)
    n_cols = len(columns)
    cell_w = 2.4
    cell_h = 0.70
    label_w = 2.0
    x0 = label_w
    y0 = 0.2

    fig, ax = plt.subplots(figsize=(13, 4))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.axis("off")
    ax.set_title("Сравнение алгоритмов кратчайших путей",
                 fontsize=13, color=C_INK, fontweight="bold", pad=10)

    # Column headers
    for j, col in enumerate(columns):
        cx = x0 + j * cell_w + cell_w / 2
        cy = y0 + n_rows * cell_h + 0.12
        ax.text(cx, cy, col, ha="center", va="bottom",
                fontsize=10, color=C_INK, fontweight="bold")

    # Row labels and cells
    for i, algo in enumerate(algorithms):
        row_i = n_rows - 1 - i
        cy = y0 + row_i * cell_h + cell_h / 2
        ax.text(x0 - 0.12, cy, algo, ha="right", va="center",
                fontsize=10, color=C_INK, fontweight="bold")

        for j, (text, fc) in enumerate(cells[i]):
            cx = x0 + j * cell_w
            rect = mpatches.Rectangle(
                (cx, y0 + row_i * cell_h), cell_w, cell_h,
                facecolor=fc, edgecolor=C_GRAY, linewidth=0.8, zorder=2
            )
            ax.add_patch(rect)
            ax.text(cx + cell_w / 2, cy, text,
                    ha="center", va="center",
                    fontsize=9.5, color=text_colors[fc],
                    fontweight="bold", zorder=3)

    total_w = label_w + n_cols * cell_w
    total_h = n_rows * cell_h
    ax.set_xlim(0.0, total_w + 0.3)
    ax.set_ylim(y0 - 0.2, y0 + total_h + 0.6)
    plt.tight_layout()
    _save(fig, "algorithm_comparison")


def draw_dijkstra_negative():
    """Counterexample: Dijkstra fails with a negative edge (3 nodes)."""
    _apply_style()
    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(12, 4.6))
    fig.patch.set_facecolor(C_BG)

    pos = {0: (1.0, 1.5), 1: (5.0, 2.6), 2: (5.0, 0.4)}
    edges = [(0, 1, "2"), (0, 2, "3"), (2, 1, "−2")]

    def draw_graph(ax, edge_colors, node_colors, dist_lbl):
        ax.set_facecolor(C_BG)
        ax.set_xlim(0.0, 6.6)
        ax.set_ylim(-0.5, 3.4)
        ax.axis("off")
        for (u, v, w), col in zip(edges, edge_colors):
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            dx, dy = x2 - x1, y2 - y1
            length = (dx**2 + dy**2) ** 0.5
            s = 0.36 / length
            _draw_arrow(ax, x1 + dx * s, y1 + dy * s,
                        x2 - dx * s, y2 - dy * s, color=col, lw=2.2)
            ax.text((x1 + x2) / 2 + 0.15, (y1 + y2) / 2 + 0.18, w,
                    ha="center", va="bottom", fontsize=11,
                    color=col, fontweight="bold",
                    bbox=dict(facecolor=C_BG, edgecolor="none", pad=1))
        for node, (x, y) in pos.items():
            _draw_node(ax, x, y, node, node_colors[node])
            ax.text(x, y - 0.55, dist_lbl[node], ha="center", va="center",
                    fontsize=9, color=C_INK)

    # Left: what Dijkstra does (settles 1 with d=2 too early)
    draw_graph(
        ax_l,
        edge_colors=[C_GRAY, C_GRAY, C_ORANGE],
        node_colors={0: C_GREEN, 1: C_GREEN, 2: C_GREEN},
        dist_lbl={0: "d=0 (1-й)", 1: "d=2 (2-й!) — ошибка", 2: "d=3 (3-й)"},
    )
    ax_l.set_title("Дийкстра: вершина 1 закреплена с d=2\nдо обработки ребра 2→1",
                   fontsize=10.5, color=C_INK, pad=6)

    # Right: true shortest path 0 -> 2 -> 1 of length 1
    draw_graph(
        ax_r,
        edge_colors=[C_GRAY, C_BLUE, C_BLUE],
        node_colors={0: C_BLUE, 1: C_BLUE, 2: C_BLUE},
        dist_lbl={0: "δ=0", 1: "δ=1 (путь 0→2→1)", 2: "δ=3"},
    )
    ax_r.set_title("Истинные расстояния:\nкратчайший путь до 1 идёт через 2",
                   fontsize=10.5, color=C_INK, pad=6)

    fig.suptitle("Почему Дийкстре нужны неотрицательные веса",
                 fontsize=13, color=C_INK, fontweight="bold", y=1.02)
    plt.tight_layout()
    _save(fig, "dijkstra_negative")


def draw_bellman_ford_induction():
    """Индукция по длине кратчайшего пути: «плохой» порядок рёбер, при котором
    Форду-Беллману нужны все V−1 итераций.

    Все данные (таблица dist по итерациям, номера итераций финализации,
    сам кратчайший путь) вычисляются честной симуляцией алгоритма.
    """
    _apply_style()

    n = 5
    src = 0
    # Граф лекции; рёбра нарочно упорядочены «против» пути 0→2→3→1→4:
    # ребро (u,v) пути идёт в списке раньше рёбер, обновляющих dist[u],
    # поэтому каскад внутри одной итерации не срабатывает.
    edges = [
        (1, 4, -4), (3, 1, -2), (2, 3, -3),
        (0, 1, 6), (0, 2, 7), (1, 2, 8), (1, 3, 5),
        (2, 4, 9), (4, 0, 2), (4, 3, 7),
    ]

    INF = float("inf")
    dist = [INF] * n
    dist[src] = 0
    pred = [-1] * n
    snapshots = [list(dist)]
    changed_sets = [set()]
    for _ in range(n - 1):
        changed = set()
        for u, v, w in edges:
            if dist[u] < INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                pred[v] = u
                changed.add(v)
        snapshots.append(list(dist))
        changed_sets.append(changed)
        if not changed:
            break

    # Итерация, после которой значение вершины стало финальным
    final_iter = {v: 0 for v in range(n)}
    for it, ch in enumerate(changed_sets):
        for v in ch:
            final_iter[v] = it

    # Кратчайший путь до вершины 4 — восстановление по pred[]
    path = [4]
    while path[-1] != src:
        path.append(pred[path[-1]])
    path = path[::-1]
    w_of = {(u, v): w for u, v, w in edges}

    fig, (ax_top, ax_tab) = plt.subplots(
        2, 1, figsize=(11, 7.2), height_ratios=[1.0, 1.5])
    fig.patch.set_facecolor(C_BG)

    # ---------- Верх: цепочка кратчайшего пути ----------
    ax_top.set_facecolor(C_BG)
    ax_top.axis("off")
    ax_top.set_xlim(-0.8, 2.4 * (len(path) - 1) + 0.8)
    ax_top.set_ylim(-1.35, 1.15)
    ax_top.set_title(
        "Кратчайший путь до вершины 4: ровно одно ребро за итерацию",
        fontsize=12.5, color=C_INK, fontweight="bold", pad=6)

    for i, v in enumerate(path):
        x = 2.4 * i
        if i + 1 < len(path):
            u2 = path[i + 1]
            _draw_arrow(ax_top, x + 0.36, 0, x + 2.4 - 0.36, 0,
                        color=C_BLUE, lw=2.4)
            ax_top.text(x + 1.2, 0.20, str(w_of[(v, u2)]), ha="center",
                        va="bottom", fontsize=11, color=C_BLUE,
                        fontweight="bold")
        _draw_node(ax_top, x, 0, v, C_INK if v == src else C_BLUE)
        it = final_iter[v]
        lbl = "старт" if v == src else f"финал:\nитер. {it}"
        ax_top.text(x, -0.62, lbl, ha="center", va="top", fontsize=9.5,
                    color=C_ORANGE if v != src else C_INK,
                    fontweight="bold")

    # ---------- Низ: таблица dist по итерациям ----------
    ax_tab.set_facecolor(C_BG)
    ax_tab.axis("off")

    n_rows = len(snapshots)
    cell_w, cell_h = 1.2, 0.6
    x0, y0 = 1.6, 0.2
    total_h = n_rows * cell_h
    total_w = n * cell_w

    row_labels = ["Начало"] + [f"Итер. {i}" for i in range(1, n_rows)]

    for j in range(n):
        cx = x0 + j * cell_w + cell_w / 2
        ax_tab.text(cx, y0 + total_h + 0.12, f"v={j}", ha="center",
                    va="bottom", fontsize=11, color=C_INK, fontweight="bold")

    fmt = lambda d: "∞" if d == INF else str(int(d))
    for i in range(n_rows):
        row_i = n_rows - 1 - i
        cy = y0 + row_i * cell_h + cell_h / 2
        ax_tab.text(x0 - 0.12, cy, row_labels[i], ha="right", va="center",
                    fontsize=10, color=C_INK)
        for j in range(n):
            is_changed = j in changed_sets[i]
            fc = C_ORANGE if is_changed else C_PANEL
            rect = mpatches.Rectangle(
                (x0 + j * cell_w, y0 + row_i * cell_h), cell_w, cell_h,
                facecolor=fc, edgecolor=C_GRAY, linewidth=0.8, zorder=2)
            ax_tab.add_patch(rect)
            ax_tab.text(x0 + j * cell_w + cell_w / 2, cy,
                        fmt(snapshots[i][j]), ha="center", va="center",
                        fontsize=11,
                        color="white" if is_changed else C_INK,
                        fontweight="bold" if is_changed else "normal",
                        zorder=3)

    ax_tab.set_title(
        "«Плохой» порядок рёбер: нужны все V − 1 = 4 итерации",
        fontsize=12.5, color=C_INK, fontweight="bold", pad=8)

    changed_patch = mpatches.Patch(facecolor=C_ORANGE, edgecolor=C_INK,
                                   label="Значение обновлено")
    unchanged_patch = mpatches.Patch(facecolor=C_PANEL, edgecolor=C_GRAY,
                                     label="Без изменений")
    ax_tab.legend(handles=[changed_patch, unchanged_patch],
                  loc="center right", fontsize=9,
                  facecolor=C_BG, edgecolor=C_GRAY)

    ax_tab.set_xlim(0.0, x0 + total_w + 2.6)
    ax_tab.set_ylim(y0 - 0.3, y0 + total_h + 0.55)

    plt.tight_layout()
    _save(fig, "bellman_ford_induction")


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_dijkstra()
    draw_bellman_ford()
    draw_algorithm_comparison()
    draw_dijkstra_negative()
    draw_bellman_ford_induction()
    print("All visuals generated successfully.")


if __name__ == "__main__":
    main()
