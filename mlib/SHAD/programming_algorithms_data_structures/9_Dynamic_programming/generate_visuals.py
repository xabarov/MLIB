"""Точные схемы для лекции про динамическое программирование."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
C_BG    = "#faf9f5"
C_INK   = "#141413"
C_GRAY  = "#b0aea5"
C_PANEL = "#e8e6dc"
C_ORANGE = "#d97757"
C_BLUE  = "#6a9bcc"
C_GREEN = "#788c5d"

ROOT   = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)


def _apply_style(fig, ax_list):
    fig.patch.set_facecolor(C_BG)
    for ax in ax_list:
        ax.set_facecolor(C_BG)
        ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        for spine in ax.spines.values():
            spine.set_visible(False)


def _save(fig, name):
    path = ASSETS / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)
    print(f"Saved: {path}")


# ---------------------------------------------------------------------------
# Visual 1: Fibonacci call tree for fib(5)
# Duplicate calls highlighted in orange
# ---------------------------------------------------------------------------
def draw_fib_tree():
    # Tree nodes: (label, x, y, parent_x, parent_y, is_duplicate)
    # Layout computed manually for a clean binary tree appearance
    nodes = [
        # (label, x,   y,    px,   py,   dup)
        ("F(5)",  4.0, 5.0,  None, None, False),
        ("F(4)",  2.5, 4.0,  4.0,  5.0,  False),
        ("F(3)",  5.5, 4.0,  4.0,  5.0,  True),   # duplicate F(3)
        ("F(3)",  1.5, 3.0,  2.5,  4.0,  True),   # duplicate F(3)
        ("F(2)",  3.5, 3.0,  2.5,  4.0,  True),   # duplicate F(2)
        ("F(4.1)", 4.7, 3.0, 5.5,  4.0,  False),  # not used — F(3) subtree
        ("F(2)",  5.0, 3.0,  5.5,  4.0,  True),   # duplicate F(2)
        ("F(1)",  6.0, 3.0,  5.5,  4.0,  False),
        ("F(2)",  1.0, 2.0,  1.5,  3.0,  True),   # dup
        ("F(1)",  2.0, 2.0,  1.5,  3.0,  False),
        ("F(1)",  3.2, 2.0,  3.5,  3.0,  False),
        ("F(0)",  3.8, 2.0,  3.5,  3.0,  False),
        ("F(0.a)", 4.5, 2.0, 5.0,  3.0,  False),  # F(2) children
        ("F(1.a)", 5.5, 2.0, 5.0,  3.0,  False),
        ("F(1.b)", 0.6, 1.0, 1.0,  2.0,  False),  # F(2) children
        ("F(0.b)", 1.4, 1.0, 1.0,  2.0,  False),
    ]

    # Clean representation: use simple tree structure
    # (label, x, y, parent_idx or None, is_duplicate)
    tree = [
        # idx  label  x     y     parent  dup
        (0,  "F(5)",  4.0,  6.0,  None,  False),
        (1,  "F(4)",  2.0,  5.0,  0,     False),
        (2,  "F(3)",  6.0,  5.0,  0,     True),
        (3,  "F(3)",  1.0,  4.0,  1,     True),
        (4,  "F(2)",  3.0,  4.0,  1,     True),
        (5,  "F(2)",  5.0,  4.0,  2,     True),
        (6,  "F(1)",  7.0,  4.0,  2,     False),
        (7,  "F(2)",  0.3,  3.0,  3,     True),
        (8,  "F(1)",  1.7,  3.0,  3,     False),
        (9,  "F(1)",  2.6,  3.0,  4,     False),
        (10, "F(0)",  3.4,  3.0,  4,     False),
        (11, "F(1)",  4.6,  3.0,  5,     False),
        (12, "F(0)",  5.4,  3.0,  5,     False),
        (13, "F(1)",  0.0,  2.0,  7,     False),
        (14, "F(0)",  0.6,  2.0,  7,     False),
    ]

    fig, ax = plt.subplots(figsize=(12, 7))
    _apply_style(fig, [ax])
    ax.set_xlim(-0.5, 8.5)
    ax.set_ylim(1.2, 7.0)

    # Draw edges first
    positions = {idx: (x, y) for idx, _, x, y, _, _ in tree}
    for idx, label, x, y, parent, _ in tree:
        if parent is not None:
            px, py = positions[parent]
            ax.plot([px, x], [py, y], color=C_GRAY, lw=1.2, zorder=1)

    # Draw nodes
    r = 0.35
    for idx, label, x, y, _, dup in tree:
        color = C_ORANGE if dup else C_BLUE
        circ = mpatches.Circle((x, y), r, facecolor=color,
                                edgecolor=C_INK, linewidth=1.0, zorder=3)
        ax.add_patch(circ)
        ax.text(x, y, label, ha="center", va="center",
                fontsize=8, color=C_BG, fontweight="bold", zorder=4)

    # Legend
    blue_patch = mpatches.Patch(color=C_BLUE,  label="Уникальный вызов")
    oran_patch = mpatches.Patch(color=C_ORANGE, label="Дублирующийся вызов")
    ax.legend(handles=[blue_patch, oran_patch],
              loc="lower right", fontsize=10,
              facecolor=C_BG, edgecolor=C_GRAY)

    ax.set_title("Дерево вызовов fib(5): оранжевые узлы — дублирующиеся вычисления",
                 fontsize=12, color=C_INK, fontweight="bold", pad=10)

    plt.tight_layout()
    _save(fig, "fib_tree")


# ---------------------------------------------------------------------------
# Visual 2: Edit Distance DP table for "cat" -> "cut"
# Traceback path highlighted in orange
# ---------------------------------------------------------------------------
def draw_edit_distance():
    s = "cat"
    t = "cut"
    m, n = len(s), len(t)

    # Compute DP table
    dp = np.zeros((m + 1, n + 1), dtype=int)
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s[i - 1] == t[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

    # Traceback: collect cells on optimal path
    path_cells = set()
    i, j = m, n
    while i > 0 or j > 0:
        path_cells.add((i, j))
        if i > 0 and j > 0 and s[i - 1] == t[j - 1]:
            i -= 1; j -= 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + 1:
            i -= 1; j -= 1
        elif i > 0 and dp[i][j] == dp[i - 1][j] + 1:
            i -= 1
        else:
            j -= 1
    path_cells.add((0, 0))

    cell_w = 1.0
    cell_h = 0.8
    rows = m + 1
    cols = n + 1

    fig, ax = plt.subplots(figsize=(8, 6))
    _apply_style(fig, [ax])

    total_w = cols * cell_w
    total_h = rows * cell_h
    ax.set_xlim(-1.5, total_w + 0.3)
    ax.set_ylim(-0.5, total_h + 1.2)

    # Column headers (t)
    ax.text(-0.5, total_h + 0.5, "", ha="center", va="center",
            fontsize=11, color=C_INK)
    ax.text(0.5 * cell_w, total_h + 0.5, "ε",
            ha="center", va="center", fontsize=13, color=C_GRAY)
    for j in range(n):
        ax.text((j + 1 + 0.5) * cell_w, total_h + 0.5, t[j],
                ha="center", va="center", fontsize=13,
                color=C_INK, fontweight="bold")

    # Row headers (s)
    ax.text(-0.5, (m + 0.5) * cell_h, "ε",
            ha="center", va="center", fontsize=13, color=C_GRAY)
    for i in range(m):
        ax.text(-0.5, (m - 1 - i + 0.5) * cell_h, s[i],
                ha="center", va="center", fontsize=13,
                color=C_INK, fontweight="bold")

    # Draw cells
    for i in range(rows):
        for j in range(cols):
            # Flip: row 0 of dp is displayed at top
            draw_row = m - i
            x = j * cell_w
            y = draw_row * cell_h

            if (i, j) in path_cells:
                fc = C_ORANGE
                tc = C_BG
            else:
                fc = C_PANEL
                tc = C_INK

            rect = mpatches.Rectangle(
                (x, y), cell_w * 0.93, cell_h * 0.88,
                facecolor=fc, edgecolor=C_GRAY, linewidth=0.8, zorder=2
            )
            ax.add_patch(rect)
            ax.text(x + cell_w * 0.465, y + cell_h * 0.44,
                    str(dp[i][j]),
                    ha="center", va="center",
                    fontsize=13, color=tc, fontweight="bold", zorder=3)

    ax.set_title(
        'Редакционное расстояние: "cat" → "cut"\nОранжевые ячейки — путь traceback',
        fontsize=11, color=C_INK, fontweight="bold", pad=10
    )
    plt.tight_layout()
    _save(fig, "edit_distance")


# ---------------------------------------------------------------------------
# Visual 3: 0/1 Knapsack DP table for 3 items, W=5
# Selected items' rows highlighted in green
# ---------------------------------------------------------------------------
def draw_knapsack():
    weights = [2, 3, 4]
    values  = [3, 4, 5]
    W = 5
    n = len(weights)

    # Compute DP table: dp[i][w]
    dp = np.zeros((n + 1, W + 1), dtype=int)
    for i in range(1, n + 1):
        for w in range(W + 1):
            dp[i][w] = dp[i - 1][w]
            if weights[i - 1] <= w:
                dp[i][w] = max(dp[i][w], dp[i - 1][w - weights[i - 1]] + values[i - 1])

    # Traceback: find selected items
    selected_items = set()
    cap = W
    for i in range(n, 0, -1):
        if dp[i][cap] != dp[i - 1][cap]:
            selected_items.add(i)
            cap -= weights[i - 1]

    # Cells on the traceback path
    traceback_cells = set()
    cap = W
    traceback_cells.add((n, W))
    for i in range(n, 0, -1):
        if dp[i][cap] != dp[i - 1][cap]:
            cap -= weights[i - 1]
        traceback_cells.add((i - 1, cap))

    cell_w = 1.0
    cell_h = 0.75
    rows = n + 2  # header + n+1 dp rows
    cols = W + 2  # label col + W+1 dp cols

    fig, ax = plt.subplots(figsize=(10, 5))
    _apply_style(fig, [ax])

    total_w = (W + 1) * cell_w
    total_h = (n + 1) * cell_h
    ax.set_xlim(-2.5, total_w + 0.5)
    ax.set_ylim(-0.5, total_h + 1.5)

    # Column headers: capacity 0..W
    for w in range(W + 1):
        ax.text(w * cell_w + cell_w * 0.5, total_h + 0.9,
                f"w={w}", ha="center", va="center",
                fontsize=9, color=C_GRAY)

    # Row labels and cells
    row_labels = ["i=0 (нет)"] + [f"i={i} (w={weights[i-1]},v={values[i-1]})"
                                    for i in range(1, n + 1)]
    for i in range(n + 1):
        draw_row = n - i  # flip: i=0 at top
        y = draw_row * cell_h

        # Row label
        label = row_labels[i]
        is_selected = i in selected_items
        label_color = C_GREEN if is_selected else C_INK
        ax.text(-0.1, y + cell_h * 0.44, label,
                ha="right", va="center", fontsize=9,
                color=label_color,
                fontweight="bold" if is_selected else "normal")

        for w in range(W + 1):
            x = w * cell_w

            on_trace = (i, w) in traceback_cells
            row_sel = i in selected_items

            if on_trace and row_sel:
                fc = C_GREEN
                tc = C_BG
            elif on_trace:
                fc = C_ORANGE
                tc = C_BG
            elif row_sel:
                fc = "#c5d9b0"  # light green tint
                tc = C_INK
            else:
                fc = C_PANEL
                tc = C_INK

            rect = mpatches.Rectangle(
                (x, y), cell_w * 0.93, cell_h * 0.88,
                facecolor=fc, edgecolor=C_GRAY, linewidth=0.8, zorder=2
            )
            ax.add_patch(rect)
            ax.text(x + cell_w * 0.465, y + cell_h * 0.44,
                    str(dp[i][w]),
                    ha="center", va="center",
                    fontsize=11, color=tc, fontweight="bold", zorder=3)

    # Legend
    sel_patch  = mpatches.Patch(color=C_GREEN,   label="Взятый предмет (traceback)")
    trc_patch  = mpatches.Patch(color=C_ORANGE,  label="Путь traceback")
    lite_patch = mpatches.Patch(color="#c5d9b0", label="Строка взятого предмета")
    ax.legend(handles=[sel_patch, trc_patch, lite_patch],
              loc="lower right", fontsize=9,
              facecolor=C_BG, edgecolor=C_GRAY)

    ax.set_title(
        "0/1 Knapsack: 3 предмета, W=5\n"
        "Зелёные ячейки — traceback (взяты предметы i=1 и i=2)",
        fontsize=11, color=C_INK, fontweight="bold", pad=10
    )
    plt.tight_layout()
    _save(fig, "knapsack")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    draw_fib_tree()
    draw_edit_distance()
    draw_knapsack()


if __name__ == "__main__":
    main()
