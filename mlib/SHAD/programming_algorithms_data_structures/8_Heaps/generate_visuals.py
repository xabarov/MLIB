"""Generate visual diagrams for Lecture 8: Heaps and Heap Sort."""

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
        "axes.edgecolor": C_GRAY,
        "text.color": C_INK,
        "font.family": "DejaVu Sans",
        "font.size": 11,
    })


def _save(fig, name):
    ASSETS.mkdir(parents=True, exist_ok=True)
    path = ASSETS / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)
    print(f"Saved: {path}")


def _draw_tree_node(ax, x, y, value, radius=0.32, color=C_BLUE, text_color="white"):
    """Draw a single tree node (circle with label)."""
    circle = mpatches.Circle((x, y), radius, color=color, zorder=3)
    ax.add_patch(circle)
    ax.text(x, y, str(value), ha="center", va="center",
            fontsize=12, fontweight="bold", color=text_color, zorder=4)


def _draw_edge(ax, x1, y1, x2, y2):
    """Draw an edge between two tree nodes."""
    ax.plot([x1, x2], [y1, y2], color=C_GRAY, linewidth=1.5, zorder=1)


def _draw_array_box(ax, x, y, value, width=0.7, height=0.5,
                    box_color=C_PANEL, text_color=C_INK, idx=None):
    """Draw a single array element box."""
    rect = mpatches.Rectangle(
        (x - width / 2, y - height / 2), width, height,
        linewidth=1.5, edgecolor=C_INK, facecolor=box_color, zorder=2
    )
    ax.add_patch(rect)
    ax.text(x, y, str(value), ha="center", va="center",
            fontsize=11, fontweight="bold", color=text_color, zorder=3)
    if idx is not None:
        ax.text(x, y - height / 2 - 0.18, str(idx), ha="center", va="top",
                fontsize=8, color=C_GRAY, zorder=3)


def draw_heap_structure():
    """Side-by-side: binary tree and array representation of heap [1,3,5,10,4]."""
    _apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))
    fig.patch.set_facecolor(C_BG)
    fig.suptitle("Бинарная куча: дерево и массив  [1, 3, 5, 10, 4]",
                 fontsize=14, fontweight="bold", color=C_INK, y=1.01)

    heap = [1, 3, 5, 10, 4]

    # ---------- LEFT: tree ----------
    ax_tree = axes[0]
    ax_tree.set_facecolor(C_BG)
    ax_tree.set_xlim(-0.5, 4.5)
    ax_tree.set_ylim(-0.5, 4.0)
    ax_tree.set_aspect("equal")
    ax_tree.axis("off")
    ax_tree.set_title("Дерево", fontsize=12, color=C_INK, pad=8)

    # Node positions (x, y) for indices 0..4
    pos = {
        0: (2.0, 3.2),
        1: (1.0, 2.0),
        2: (3.0, 2.0),
        3: (0.4, 0.8),
        4: (1.6, 0.8),
    }

    # Edges
    edges = [(0, 1), (0, 2), (1, 3), (1, 4)]
    for p, c in edges:
        x1, y1 = pos[p]
        x2, y2 = pos[c]
        _draw_edge(ax_tree, x1, y1, x2, y2)

    # Nodes
    node_colors = [C_GREEN, C_BLUE, C_BLUE, C_BLUE, C_BLUE]
    for i, val in enumerate(heap):
        x, y = pos[i]
        _draw_tree_node(ax_tree, x, y, val, color=node_colors[i])
        # Index label above/below
        ax_tree.text(x + 0.38, y + 0.22, f"[{i}]", fontsize=8,
                     color=C_GRAY, zorder=5)

    # Root annotation
    ax_tree.text(pos[0][0], pos[0][1] + 0.55, "корень (мин.)",
                 ha="center", fontsize=9, color=C_GREEN, fontweight="bold")

    # ---------- RIGHT: array ----------
    ax_arr = axes[1]
    ax_arr.set_facecolor(C_BG)
    ax_arr.set_xlim(-0.5, 5.5)
    ax_arr.set_ylim(-1.0, 3.5)
    ax_arr.axis("off")
    ax_arr.set_title("Массив + формулы индексов", fontsize=12, color=C_INK, pad=8)

    # Array boxes
    arr_y = 2.0
    arr_colors = [C_GREEN] + [C_PANEL] * 4
    for i, val in enumerate(heap):
        _draw_array_box(ax_arr, i + 0.5, arr_y, val,
                        box_color=arr_colors[i], idx=i)

    # Bracket label
    ax_arr.text(-0.3, arr_y, "h =", ha="right", va="center",
                fontsize=11, color=C_INK)

    # Index arithmetic table
    table_x = 0.2
    table_y_start = 1.0
    rows = [
        ("parent(i)", "= (i−1) / 2"),
        ("left(i)",   "= 2·i + 1"),
        ("right(i)",  "= 2·i + 2"),
    ]
    ax_arr.text(table_x, table_y_start + 0.35, "Формулы индексов:",
                fontsize=10, color=C_INK, fontweight="bold")
    for j, (label, formula) in enumerate(rows):
        row_y = table_y_start - 0.42 * j
        ax_arr.text(table_x + 0.1, row_y, label, fontsize=10,
                    color=C_ORANGE, fontweight="bold")
        ax_arr.text(table_x + 1.5, row_y, formula, fontsize=10, color=C_INK)

    # Arrows from tree node indices to array positions (show parent/child links)
    # Draw short annotations below array
    annot_y = arr_y - 0.65
    link_info = [
        (0.5, 1.5, "parent"),   # 0 -> 1
        (0.5, 2.5, "parent"),   # 0 -> 2
    ]
    for x1, x2, label in link_info:
        ax_arr.annotate("", xy=(x2, annot_y + 0.05), xytext=(x1, annot_y + 0.05),
                        arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=1.2))

    # Parent-child example annotation
    ax_arr.text(2.5, annot_y - 0.15,
                "parent(3) = 1,  parent(4) = 1",
                ha="center", fontsize=9, color=C_GRAY,
                style="italic")

    # Heap property reminder
    ax_arr.text(2.5, -0.7,
                "Свойство кучи:  h[parent(i)]  ≤  h[i]",
                ha="center", fontsize=10, color=C_INK,
                bbox=dict(boxstyle="round,pad=0.3", facecolor=C_PANEL,
                          edgecolor=C_GRAY))

    plt.tight_layout(pad=1.0)
    _save(fig, "heap_structure")


def draw_sift_down():
    """Four-panel showing sift_down steps after extracting min from [1,3,5,10,4]."""
    _apply_style()
    fig, axes = plt.subplots(1, 4, figsize=(15, 4.5))
    fig.patch.set_facecolor(C_BG)
    fig.suptitle("SiftDown после ExtractMin: пошаговая трассировка",
                 fontsize=13, fontweight="bold", color=C_INK, y=1.02)

    # States after extracting 1 from [1,3,5,10,4]:
    # Step 0: place last (4) at root → [4,3,5,10] (n=4), highlight index 0
    # Step 1: compare 4 with children 3,5 → swap with 3 → [3,4,5,10], highlight index 1
    # Step 2: compare 4 with children 10 → 4<10, stop → [3,4,5,10], highlight index 1 (done)
    # Step 3: final heap [3,4,5,10]

    panels = [
        {
            "heap": [4, 3, 5, 10],
            "n": 4,
            "title": "Шаг 0: last→root",
            "highlight": 0,
            "swap_to": 1,
            "note": "4 в корне\n(последний элемент)",
        },
        {
            "heap": [3, 4, 5, 10],
            "n": 4,
            "title": "Шаг 1: swap(0,1)",
            "highlight": 1,
            "swap_to": None,
            "note": "4 > min(3,5)=3\n→ swap с индексом 1",
        },
        {
            "heap": [3, 4, 5, 10],
            "n": 4,
            "title": "Шаг 2: проверка",
            "highlight": 1,
            "swap_to": None,
            "note": "4 < 10\n→ стоп, куча готова",
        },
        {
            "heap": [3, 4, 5, 10],
            "n": 4,
            "title": "Результат",
            "highlight": -1,
            "swap_to": None,
            "note": "ExtractMin вернул 1\nКуча: [3,4,5,10]",
        },
    ]

    # Tree positions for n=4
    pos4 = {
        0: (1.5, 2.6),
        1: (0.7, 1.5),
        2: (2.3, 1.5),
        3: (0.2, 0.4),
    }
    edges4 = [(0, 1), (0, 2), (1, 3)]

    for panel_idx, (ax, panel) in enumerate(zip(axes, panels)):
        ax.set_facecolor(C_BG)
        ax.set_xlim(-0.2, 3.2)
        ax.set_ylim(-0.5, 3.5)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(panel["title"], fontsize=10, color=C_INK, pad=4)

        heap = panel["heap"]
        highlight = panel["highlight"]
        swap_to = panel["swap_to"]

        # Draw edges
        for p, c in edges4:
            if c < len(heap):
                x1, y1 = pos4[p]
                x2, y2 = pos4[c]
                _draw_edge(ax, x1, y1, x2, y2)

        # Draw nodes
        for i in range(len(heap)):
            if i == highlight and panel_idx < 3:
                color = C_ORANGE
            elif i == swap_to:
                color = C_GREEN
            elif panel_idx == 3:
                color = C_GREEN  # all green in final
            else:
                color = C_BLUE
            x, y = pos4[i]
            _draw_tree_node(ax, x, y, heap[i], radius=0.28, color=color)
            ax.text(x + 0.32, y + 0.20, f"[{i}]", fontsize=7,
                    color=C_GRAY, zorder=5)

        # Swap arrow between highlight and swap_to
        if highlight >= 0 and swap_to is not None and swap_to < len(heap):
            x1, y1 = pos4[highlight]
            x2, y2 = pos4[swap_to]
            ax.annotate(
                "", xy=(x2, y2 + 0.32), xytext=(x1, y1 - 0.32),
                arrowprops=dict(arrowstyle="<->", color=C_ORANGE,
                                lw=2.0, connectionstyle="arc3,rad=0.3"),
                zorder=5,
            )

        # Array representation below tree
        arr_y = -0.1
        for i, val in enumerate(heap):
            bcolor = C_ORANGE if i == highlight and panel_idx < 3 else C_PANEL
            if panel_idx == 3:
                bcolor = C_GREEN if i == 0 else C_PANEL
            _draw_array_box(ax, 0.5 + i * 0.68, arr_y, val,
                            width=0.6, height=0.4, box_color=bcolor, idx=i)

        # Note text
        ax.text(1.5, -0.6, panel["note"], ha="center", va="top",
                fontsize=8, color=C_INK, style="italic",
                bbox=dict(boxstyle="round,pad=0.2", facecolor=C_PANEL,
                          edgecolor=C_GRAY, alpha=0.8))

    plt.tight_layout(pad=0.8)
    _save(fig, "sift_down")


def draw_build_heap():
    """Show BuildHeap transformation: [4,10,3,5,1] → step-by-step sift_down calls."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(11, 6.5))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(-0.5, 8.0)
    ax.axis("off")
    ax.set_title(
        "BuildHeap из [4, 10, 3, 5, 1]:  O(n) — каждый шаг = один вызов SiftDown",
        fontsize=13, fontweight="bold", color=C_INK, pad=10
    )

    # States after each sift_down call (n=5, internal nodes: i=1, i=0)
    # Start: [4, 10, 3, 5, 1]
    # i=1 (value 10): children are indices 3(5) and 4(1). min=1 at idx 4. swap(1,4) → [4,1,3,5,10]
    # i=0 (value 4): children are indices 1(1) and 2(3). min=1 at idx 1. swap(0,1) → [1,4,3,5,10]
    #   then sift_down continues at i=1 (value 4): children 3(5), 4(10). 4<5, stop.

    states = [
        {"arr": [4, 10, 3, 5, 1],  "label": "Исходный массив",
         "changed": [], "step_node": -1},
        {"arr": [4, 1, 3, 5, 10],  "label": "i=1: swap(h[1]=10, h[4]=1)",
         "changed": [1, 4], "step_node": 1},
        {"arr": [1, 4, 3, 5, 10],  "label": "i=0: swap(h[0]=4, h[1]=1)",
         "changed": [0, 1], "step_node": 0},
    ]

    row_height = 2.2
    box_w = 0.75
    box_h = 0.52
    n = 5

    for row_idx, state in enumerate(states):
        arr = state["arr"]
        changed = state["changed"]
        label = state["label"]
        step_node = state["step_node"]

        y_center = 7.0 - row_idx * row_height

        # Row label on left
        ax.text(-0.3, y_center, label, ha="left", va="center",
                fontsize=10, color=C_INK,
                fontweight="bold" if row_idx > 0 else "normal")

        # Boxes for this row
        x_start = 3.0
        for col, val in enumerate(arr):
            x = x_start + col * (box_w + 0.15)
            if col in changed:
                bcolor = C_ORANGE
            elif row_idx == len(states) - 1:
                bcolor = C_GREEN
            else:
                bcolor = C_PANEL
            _draw_array_box(ax, x, y_center, val,
                            width=box_w, height=box_h,
                            box_color=bcolor, idx=col)

        # Highlight current sift_down node with bracket
        if step_node >= 0:
            sx = x_start + step_node * (box_w + 0.15)
            ax.annotate(
                "", xy=(sx, y_center + box_h / 2 + 0.05),
                xytext=(sx, y_center + box_h / 2 + 0.35),
                arrowprops=dict(arrowstyle="-|>", color=C_ORANGE, lw=2),
            )
            ax.text(sx, y_center + box_h / 2 + 0.5,
                    f"SiftDown(i={step_node})", ha="center", fontsize=8,
                    color=C_ORANGE, fontweight="bold")

        # Downward arrow between rows (except last)
        if row_idx < len(states) - 1:
            ax.annotate(
                "", xy=(6.0, y_center - row_height + 0.4),
                xytext=(6.0, y_center - 0.35),
                arrowprops=dict(arrowstyle="-|>", color=C_GRAY, lw=1.5),
            )

    # Final heap tree visualization at bottom-right
    tree_cx = 8.5
    tree_cy = 3.8
    final_heap = [1, 4, 3, 5, 10]
    pos_rel = {
        0: (0.0,  1.0),
        1: (-0.7, 0.0),
        2: (0.7,  0.0),
        3: (-1.1, -1.0),
        4: (-0.3, -1.0),
    }
    tree_edges = [(0, 1), (0, 2), (1, 3), (1, 4)]

    ax.text(tree_cx, tree_cy + 2.0, "Итоговая куча",
            ha="center", fontsize=11, fontweight="bold", color=C_INK)

    for p, c in tree_edges:
        x1 = tree_cx + pos_rel[p][0]
        y1 = tree_cy + pos_rel[p][1]
        x2 = tree_cx + pos_rel[c][0]
        y2 = tree_cy + pos_rel[c][1]
        _draw_edge(ax, x1, y1, x2, y2)

    for i, val in enumerate(final_heap):
        x = tree_cx + pos_rel[i][0]
        y = tree_cy + pos_rel[i][1]
        color = C_GREEN if i == 0 else C_BLUE
        _draw_tree_node(ax, x, y, val, radius=0.28, color=color)

    # Legend
    legend_x = 0.0
    legend_y = 1.5
    patches = [
        mpatches.Patch(color=C_ORANGE, label="Изменённые элементы"),
        mpatches.Patch(color=C_GREEN,  label="Итоговый результат"),
        mpatches.Patch(color=C_PANEL,  label="Без изменений"),
    ]
    ax.legend(handles=patches, loc="lower left",
              bbox_to_anchor=(legend_x, legend_y),
              fontsize=9, framealpha=0.9,
              facecolor=C_BG, edgecolor=C_GRAY)

    # Complexity note
    ax.text(5.0, 0.1,
            "BuildHeap: O(n) — не O(n log n), потому что большинство SiftDown\n"
            "вызывается на узлах вблизи листьев (малая высота).",
            ha="center", fontsize=9, color=C_INK,
            bbox=dict(boxstyle="round,pad=0.4", facecolor=C_PANEL,
                      edgecolor=C_GRAY, alpha=0.9))

    # Unused variable guard — use n to annotate
    ax.text(x_start := 3.0, -0.35,
            f"n = {n} элементов, внутренние узлы: i = {n // 2 - 1} ... 0",
            ha="left", fontsize=9, color=C_GRAY)

    plt.tight_layout(pad=0.8)
    _save(fig, "build_heap")


def main():
    draw_heap_structure()
    draw_sift_down()
    draw_build_heap()


if __name__ == "__main__":
    main()
