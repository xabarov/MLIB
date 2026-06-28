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
            "frontier": {2},
            "dist": {0: 0, 1: 2, 2: 3, 3: 9, 4: "∞", 5: "∞"},
        },
        {
            "title": "Шаг 3: закрепляем вершину 2 (d=3)",
            "settled": {0, 1, 2},
            "frontier": {4},
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
    # rows: iteration 0 (init), 1, 2, 3, 4
    table_data = [
        [0, INF, INF, INF, INF],
        [0, 6,   7,   11,  2  ],
        [0, 2,   7,   4,   -2 ],
        [0, 2,   7,   4,   -2 ],
        [0, 2,   7,   4,   -2 ],
    ]
    # Cells that changed compared to previous row
    changed = [
        set(),
        {1, 2, 3, 4},
        {1, 3, 4},
        set(),
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
    row_labels = ["Начало", "Итер. 1", "Итер. 2", "Итер. 3", "Итер. 4"]

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

    # Highlight annotation for iteration 2
    note_x = x0 + total_w + 0.15
    note_y = y0 + (n_rows - 1 - 2) * cell_h + cell_h / 2
    ax.annotate(
        "Ребро (3,1,−2) улучшает d[1]:\n4+(−2)=2; d[4]=2+(−4)=−2",
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


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_dijkstra()
    draw_bellman_ford()
    draw_algorithm_comparison()
    print("All visuals generated successfully.")


if __name__ == "__main__":
    main()
