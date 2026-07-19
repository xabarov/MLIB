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

# Shared BST layout for [5,3,7,1,4,6,8]
_BST_POS = {
    5: (4.5, 5.0),
    3: (2.5, 3.7),
    7: (6.5, 3.7),
    1: (1.5, 2.4),
    4: (3.5, 2.4),
    6: (5.5, 2.4),
    8: (7.5, 2.4),
}
_BST_EDGES = [(5, 3), (5, 7), (3, 1), (3, 4), (7, 6), (7, 8)]


def _apply_style():
    plt.rcParams.update({
        "figure.facecolor": C_BG,
        "axes.facecolor": C_BG,
        "text.color": C_INK,
    })


def _save(fig, name):
    ASSETS.mkdir(parents=True, exist_ok=True)
    path = ASSETS / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)
    print(f"Saved: {path}")


def _circle_node(ax, x, y, label, color, r=0.35):
    circ = mpatches.Circle((x, y), r, facecolor=color, edgecolor=C_INK,
                             linewidth=2, zorder=3)
    ax.add_patch(circ)
    ax.text(x, y, label, ha="center", va="center",
            fontsize=13, color="white", fontweight="bold", zorder=4)


def _draw_edges(ax, pos, edges):
    for p, c in edges:
        px, py = pos[p]
        cx, cy = pos[c]
        ax.plot([px, cx], [py, cy], color=C_GRAY, lw=2, zorder=1)


def draw_bst():
    """BST from [5,3,7,1,4,6,8] with inorder sequence below."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(10, 7))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)

    _draw_edges(ax, _BST_POS, _BST_EDGES)
    for val, (x, y) in _BST_POS.items():
        _circle_node(ax, x, y, str(val), C_BLUE)

    # Inorder sequence boxes below
    inorder = [1, 3, 4, 5, 6, 7, 8]
    bw, bh, gap = 0.58, 0.42, 0.1
    tw = len(inorder) * bw + (len(inorder) - 1) * gap
    x0 = 4.5 - tw / 2

    ax.text(4.5, 1.58, "Inorder (L → Root → R)  →  отсортированная последовательность:",
            ha="center", va="center", fontsize=9, color=C_INK)

    for i, v in enumerate(inorder):
        xb = x0 + i * (bw + gap)
        rect = mpatches.Rectangle((xb, 0.88), bw, bh,
                                   facecolor=C_PANEL, edgecolor=C_GREEN, linewidth=1.5, zorder=2)
        ax.add_patch(rect)
        ax.text(xb + bw / 2, 0.88 + bh / 2, str(v),
                ha="center", va="center", fontsize=11, color=C_INK, fontweight="bold", zorder=3)

    ax.annotate("", xy=(4.5, 1.52), xytext=(4.5, 2.05),
                arrowprops=dict(arrowstyle="->", color=C_GREEN, lw=1.5))

    ax.set_xlim(0.5, 8.5)
    ax.set_ylim(0.5, 5.7)
    ax.axis("off")
    ax.set_title("Двоичное дерево поиска (BST) из [5, 3, 7, 1, 4, 6, 8]",
                 fontsize=13, color=C_INK, pad=10)
    plt.tight_layout()
    _save(fig, "bst_tree")


def draw_bst_delete():
    """Two panels: before and after deleting node 3 (two-children case)."""
    _apply_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6))
    fig.patch.set_facecolor(C_BG)

    for ax in (ax1, ax2):
        ax.set_facecolor(C_BG)
        ax.set_xlim(0.5, 8.5)
        ax.set_ylim(1.0, 5.8)
        ax.axis("off")

    # --- Left panel: BEFORE deletion ---
    _draw_edges(ax1, _BST_POS, _BST_EDGES)
    for val, (x, y) in _BST_POS.items():
        if val == 3:
            color = C_ORANGE
        elif val == 4:
            color = C_GREEN
        else:
            color = C_BLUE
        _circle_node(ax1, x, y, str(val), color)

    x3, y3 = _BST_POS[3]
    x4, y4 = _BST_POS[4]
    ax1.text(x3, y3 - 0.62, "← удалить",
             ha="center", fontsize=8, color=C_ORANGE)
    ax1.annotate("inorder\nsuccessor", xy=(x4, y4 + 0.36),
                 xytext=(x4 + 1.3, y4 + 1.0),
                 fontsize=8, color=C_GREEN, ha="center",
                 arrowprops=dict(arrowstyle="->", color=C_GREEN, lw=1.2))
    ax1.set_title("До удаления: узел 3 (два потомка)",
                  fontsize=11, color=C_INK, pad=8)

    # --- Right panel: AFTER deletion ---
    pos_after = {
        5: (4.5, 5.0),
        4: (2.5, 3.7),
        7: (6.5, 3.7),
        1: (1.5, 2.4),
        6: (5.5, 2.4),
        8: (7.5, 2.4),
    }
    edges_after = [(5, 4), (5, 7), (4, 1), (7, 6), (7, 8)]

    _draw_edges(ax2, pos_after, edges_after)
    for val, (x, y) in pos_after.items():
        color = C_GREEN if val == 4 else C_BLUE
        _circle_node(ax2, x, y, str(val), color)

    x4n, y4n = pos_after[4]
    ax2.text(x4n, y4n - 0.62, "заменил 3",
             ha="center", fontsize=8, color=C_GREEN)
    ax2.set_title("После удаления: 4 занял место 3",
                  fontsize=11, color=C_INK, pad=8)

    fig.text(0.5, 0.48, "→", ha="center", va="center",
             fontsize=30, color=C_ORANGE)

    fig.suptitle("Удаление узла 3 (два потомка): inorder successor = 4",
                 fontsize=12, color=C_INK, y=1.01, fontweight="bold")
    plt.tight_layout()
    _save(fig, "bst_delete")


def draw_augmented_bst():
    """BST with size fields; select(3) path highlighted orange."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(11, 7))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)

    sizes = {5: 7, 3: 3, 7: 3, 1: 1, 4: 1, 6: 1, 8: 1}
    select_path = {5, 3, 4}

    _draw_edges(ax, _BST_POS, _BST_EDGES)

    for val, (x, y) in _BST_POS.items():
        color = C_ORANGE if val in select_path else C_BLUE
        _circle_node(ax, x, y, str(val), color)
        sz_box = mpatches.FancyBboxPatch(
            (x - 0.3, y - 0.68), 0.6, 0.24,
            boxstyle="round,pad=0.02",
            facecolor=C_PANEL, edgecolor=C_GRAY, linewidth=1.0, zorder=3
        )
        ax.add_patch(sz_box)
        ax.text(x, y - 0.56, f"sz={sizes[val]}", ha="center", va="center",
                fontsize=8, color=C_INK, zorder=4)

    x5, y5 = _BST_POS[5]
    x3, y3 = _BST_POS[3]
    x4, y4 = _BST_POS[4]

    ax.text(x5 + 0.5, y5 + 0.08,
            "k=3, sz_left=3≥k → идём влево",
            fontsize=7, color=C_ORANGE, va="center")
    ax.text(x3 + 0.5, y3 + 0.08,
            "k=3, sz_left+1=2<k → вправо, k=1",
            fontsize=7, color=C_ORANGE, va="center")
    ax.text(x4 + 0.5, y4 + 0.08,
            "k=1, sz_left+1=1=k → НАЙДЕНО!",
            fontsize=7, color=C_ORANGE, va="center", fontweight="bold")

    ax.set_xlim(0.5, 11.0)
    ax.set_ylim(1.2, 5.8)
    ax.axis("off")
    ax.set_title(
        "Расширенное BST с полем size"
        " — select(3): 3-й наименьший элемент (путь выделен)",
        fontsize=12, color=C_INK, pad=10)
    plt.tight_layout()
    _save(fig, "bst_augmented")


def _subtree(ax, x, y, label, color=C_PANEL, w=0.55, h=0.85):
    """Draw a subtree as a triangle with a label inside."""
    tri = mpatches.Polygon(
        [(x, y), (x - w, y - h), (x + w, y - h)],
        closed=True, facecolor=color, edgecolor=C_GRAY, linewidth=1.5, zorder=2)
    ax.add_patch(tri)
    ax.text(x, y - h * 0.62, label, ha="center", va="center",
            fontsize=11, color=C_INK, fontweight="bold", zorder=3)


def draw_avl_rotation():
    """Right rotation around y: before (bf(y)=+2) and after (balance restored)."""
    _apply_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 5.5))
    fig.patch.set_facecolor(C_BG)

    for ax in (ax1, ax2):
        ax.set_facecolor(C_BG)
        ax.set_xlim(0.0, 6.5)
        ax.set_ylim(0.4, 5.6)
        ax.set_aspect("equal")
        ax.axis("off")

    # --- Left panel: before rotation (left-heavy) ---
    y1, x1 = (3.9, 4.9), (2.5, 3.7)
    ax1.plot([y1[0], x1[0]], [y1[1], x1[1]], color=C_GRAY, lw=2, zorder=1)
    ax1.plot([x1[0], 1.4], [x1[1], 2.6], color=C_GRAY, lw=2, zorder=1)
    ax1.plot([x1[0], 3.5], [x1[1], 2.6], color=C_GRAY, lw=2, zorder=1)
    ax1.plot([y1[0], 5.1], [y1[1], 3.8], color=C_GRAY, lw=2, zorder=1)
    _subtree(ax1, 1.4, 2.6, "A")
    _subtree(ax1, 3.5, 2.6, "B")
    _subtree(ax1, 5.1, 3.8, "C")
    _circle_node(ax1, *y1, "y", C_ORANGE)
    _circle_node(ax1, *x1, "x", C_BLUE)
    ax1.text(y1[0] + 0.55, y1[1] + 0.05, "bf(y) = +2", fontsize=9,
             color=C_ORANGE, fontweight="bold")
    ax1.text(3.25, 0.85, "Левое поддерево слишком высокое",
             ha="center", fontsize=9, color=C_GRAY, style="italic")
    ax1.set_title("До: дисбаланс в y (перевес слева)",
                  fontsize=11, color=C_INK, pad=8)

    # --- Right panel: after right rotation ---
    x2, y2 = (3.2, 4.9), (4.6, 3.7)
    ax2.plot([x2[0], 1.8], [x2[1], 3.8], color=C_GRAY, lw=2, zorder=1)
    ax2.plot([x2[0], y2[0]], [x2[1], y2[1]], color=C_GRAY, lw=2, zorder=1)
    ax2.plot([y2[0], 3.7], [y2[1], 2.6], color=C_GRAY, lw=2, zorder=1)
    ax2.plot([y2[0], 5.5], [y2[1], 2.6], color=C_GRAY, lw=2, zorder=1)
    _subtree(ax2, 1.8, 3.8, "A")
    _subtree(ax2, 3.7, 2.6, "B")
    _subtree(ax2, 5.5, 2.6, "C")
    _circle_node(ax2, *x2, "x", C_BLUE)
    _circle_node(ax2, *y2, "y", C_ORANGE)
    ax2.text(x2[0] + 0.55, x2[1] + 0.05, "bf(x) = 0", fontsize=9,
             color=C_GREEN, fontweight="bold")
    ax2.text(3.25, 0.85, "Inorder-порядок сохранён: A < x < B < y < C",
             ha="center", fontsize=9, color=C_GREEN, style="italic")
    ax2.set_title("После rotateRight(y): x — новый корень",
                  fontsize=11, color=C_INK, pad=8)

    fig.text(0.5, 0.5, "→", ha="center", va="center",
             fontsize=30, color=C_ORANGE)
    fig.suptitle("Правое вращение: поддерево B «переезжает» от x к y",
                 fontsize=12, color=C_INK, y=1.0, fontweight="bold")
    plt.tight_layout()
    _save(fig, "avl_rotation")


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_bst()
    draw_bst_delete()
    draw_augmented_bst()
    draw_avl_rotation()
    print("All visuals generated successfully.")


if __name__ == "__main__":
    main()
