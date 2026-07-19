"""Точные схемы для лекции про СНМ, КМП и бор."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
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
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "figure.facecolor": C_BG,
        "axes.facecolor": C_BG,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "axes.spines.bottom": False,
        "xtick.bottom": False,
        "ytick.left": False,
        "text.color": C_INK,
    })


def _save(fig, name):
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS / f"{name}.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {ASSETS / name}.png")


def _draw_node(ax, x, y, label, color, radius=0.32, fontsize=12, double=False):
    circle = mpatches.Circle((x, y), radius, color=color, zorder=3)
    ax.add_patch(circle)
    if double:
        inner = mpatches.Circle((x, y), radius * 0.75, color=C_BG, zorder=4)
        ax.add_patch(inner)
        inner2 = mpatches.Circle((x, y), radius * 0.72, color=color, zorder=4)
        ax.add_patch(inner2)
    ax.text(x, y, label, ha="center", va="center",
            fontsize=fontsize, color=C_BG, fontweight="bold", zorder=5)


def _arrow(ax, x1, y1, x2, y2, color=C_INK, lw=1.5):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=lw),
        zorder=2,
    )


def draw_dsu():
    """Two panels: DSU chain before path compression vs flat star after."""
    _apply_style()
    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor(C_BG)

    for ax in (ax_left, ax_right):
        ax.set_aspect("equal")
        ax.set_facecolor(C_BG)
        ax.set_xlim(-0.5, 5.5)
        ax.set_ylim(-0.8, 4.5)
        ax.axis("off")

    # --- LEFT: chain 0->1->2->3 plus 4,5 under root (before compression) ---
    chain_nodes = [(2.5, 3.5), (2.5, 2.5), (2.5, 1.5), (2.5, 0.5)]
    chain_labels = ["3\n(root)", "2", "1", "0"]
    chain_colors = [C_ORANGE, C_BLUE, C_BLUE, C_BLUE]

    for i, ((x, y), lbl, col) in enumerate(zip(chain_nodes, chain_labels, chain_colors)):
        _draw_node(ax_left, x, y, lbl, col, fontsize=10)
        if i > 0:
            # arrow from child to parent (upward)
            _arrow(ax_left, x, y + 0.35, chain_nodes[i - 1][0], chain_nodes[i - 1][1] - 0.35,
                   color=C_GRAY)

    # nodes 4 and 5 already hang directly under root 3
    for (x, y), lbl in [((1.0, 2.3), "4"), ((4.0, 2.3), "5")]:
        _draw_node(ax_left, x, y, lbl, C_BLUE, fontsize=10)
        _arrow(ax_left, x, y + 0.35, 2.5 - (2.5 - x) * 0.15, 3.5 - 0.4,
               color=C_GRAY)

    ax_left.text(2.5, 4.1, "До Find(0)", ha="center", va="bottom",
                 fontsize=13, color=C_INK, fontweight="bold")
    ax_left.text(2.5, -0.55, "parent = [1, 2, 3, 3, 3, 3]", ha="center", va="top",
                 fontsize=10, color=C_GRAY, family="monospace")

    # annotation: find path
    for i in range(3):
        xi, yi = chain_nodes[3 - i]
        ax_left.text(xi + 0.45, yi, "↑ parent", ha="left", va="center",
                     fontsize=8, color=C_ORANGE)

    # --- RIGHT: star (after path compression Find(0)) ---
    root_x, root_y = 2.5, 3.0
    star_children = [(0.8, 1.2), (1.8, 1.2), (2.5, 1.2), (3.2, 1.2), (4.2, 1.2)]
    star_labels = ["0", "1", "2", "4", "5"]

    _draw_node(ax_right, root_x, root_y, "3\n(root)", C_ORANGE, fontsize=10)

    for (cx, cy), lbl in zip(star_children, star_labels):
        _draw_node(ax_right, cx, cy, lbl, C_BLUE, fontsize=10)
        _arrow(ax_right, cx, cy + 0.35, root_x, root_y - 0.35, color=C_GREEN)

    ax_right.text(2.5, 4.1, "После Find(0) — сжатие пути", ha="center", va="bottom",
                  fontsize=13, color=C_INK, fontweight="bold")
    ax_right.text(2.5, -0.55, "parent = [3, 3, 3, 3, 3, 3]", ha="center", va="top",
                  fontsize=10, color=C_GRAY, family="monospace")

    # divider
    fig.text(0.5, 0.5, "→", ha="center", va="center", fontsize=24, color=C_ORANGE)

    fig.suptitle("СНМ: сжатие пути (path compression)", fontsize=14,
                 color=C_INK, fontweight="bold", y=0.97)
    _save(fig, "dsu_compression")


def draw_kmp():
    """KMP: pattern ABABC over text ABABABABC, state diagram."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(13, 5))
    ax.set_facecolor(C_BG)
    ax.set_xlim(-0.5, 9.5)
    ax.set_ylim(-1.0, 4.0)
    ax.axis("off")

    text = "ABABABABC"
    pat  = "ABABC"
    # pi for ABABC = [0,0,1,2,0]
    # pi for ABABC = [0,0,1,2,0] — used conceptually; jump positions shown statically
    cell_w = 1.0
    # Draw text row (y=2.5)
    text_y = 2.5
    pat_y  = 0.8
    box_h  = 0.6

    # Text row header
    ax.text(-0.4, text_y, "T:", ha="right", va="center", fontsize=12,
            color=C_INK, fontweight="bold")
    ax.text(-0.4, pat_y, "P:", ha="right", va="center", fontsize=12,
            color=C_INK, fontweight="bold")

    # Draw text cells
    for i, ch in enumerate(text):
        x = i * cell_w
        rect = mpatches.FancyBboxPatch(
            (x - 0.45, text_y - box_h / 2), 0.9, box_h,
            boxstyle="round,pad=0.05", linewidth=1,
            edgecolor=C_GRAY, facecolor=C_PANEL, zorder=2,
        )
        ax.add_patch(rect)
        ax.text(x, text_y, ch, ha="center", va="center",
                fontsize=13, color=C_INK, fontweight="bold", zorder=3)
        ax.text(x, text_y + 0.5, str(i), ha="center", va="center",
                fontsize=8, color=C_GRAY, zorder=3)

    # Draw pattern cells at offset 0 (first alignment)
    for j, ch in enumerate(pat):
        x = j * cell_w
        match = (text[j] == ch)
        col = C_GREEN if match else C_ORANGE
        rect = mpatches.FancyBboxPatch(
            (x - 0.45, pat_y - box_h / 2), 0.9, box_h,
            boxstyle="round,pad=0.05", linewidth=1.5,
            edgecolor=col, facecolor=C_BG, zorder=2,
        )
        ax.add_patch(rect)
        ax.text(x, pat_y, ch, ha="center", va="center",
                fontsize=13, color=col, fontweight="bold", zorder=3)

    # Mismatch at position 4: T[4]='A', P[4]='C'
    mismatch_i = 4
    ax.text(mismatch_i * cell_w, pat_y - 0.5, "≠", ha="center", va="center",
            fontsize=14, color=C_ORANGE)

    # State value above each text position (j AFTER processing T[i])
    j_states = [1, 2, 3, 4, 3, 4, 3, 4, 5]
    for i, st in enumerate(j_states):
        ax.text(i * cell_w, text_y + 1.0, f"j={st}", ha="center", va="center",
                fontsize=9, color=C_BLUE)

    # Arrow: at mismatch position 4, j falls back from 4 to pi[3]=2
    ax.annotate(
        "", xy=(2 * cell_w, pat_y + 0.5), xytext=(4 * cell_w, pat_y + 0.5),
        arrowprops=dict(arrowstyle="-|>", color=C_ORANGE, lw=2.0,
                        connectionstyle="arc3,rad=-0.4"),
        zorder=4,
    )
    ax.text(3.0 * cell_w, pat_y + 1.1, "j = π[j-1] = π[3] = 2", ha="center",
            va="center", fontsize=10, color=C_ORANGE)

    # Match indicator at position 8 (full match)
    ax.text(8 * cell_w, text_y - 0.6, "✓ вхождение\nна позиции 4", ha="center",
            va="top", fontsize=9, color=C_GREEN)

    ax.set_title("Алгоритм КМП: образец ABABC в тексте ABABABABC",
                 fontsize=14, color=C_INK, fontweight="bold", pad=12)

    _save(fig, "kmp_search")


def draw_trie():
    """Trie for words: car, cart, cat, dog, dot."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.set_facecolor(C_BG)
    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(-0.5, 5.5)
    ax.axis("off")

    # Node positions (x, y, label, is_terminal)
    nodes = {
        "root":  (5.0, 5.0, "",    False),
        "c":     (2.5, 3.8, "c",   False),
        "d":     (7.5, 3.8, "d",   False),
        "ca":    (2.5, 2.6, "a",   False),
        "do":    (7.5, 2.6, "o",   False),
        "car":   (1.5, 1.4, "r",   True),
        "cat":   (3.5, 1.4, "t",   True),
        "dog":   (6.5, 1.4, "g",   True),
        "dot":   (8.5, 1.4, "t",   True),
        "cart":  (1.5, 0.2, "t",   True),
    }

    # Edges: (parent_key, child_key, edge_label)
    edges = [
        ("root", "c",    "c"),
        ("root", "d",    "d"),
        ("c",    "ca",   "a"),
        ("d",    "do",   "o"),
        ("ca",   "car",  "r"),
        ("ca",   "cat",  "t"),
        ("do",   "dog",  "g"),
        ("do",   "dot",  "t"),
        ("car",  "cart", "t"),
    ]

    R = 0.32

    # Draw edges first
    for parent_key, child_key, edge_lbl in edges:
        px, py = nodes[parent_key][0], nodes[parent_key][1]
        cx, cy = nodes[child_key][0], nodes[child_key][1]
        # direction vector
        dx, dy = cx - px, cy - py
        dist = (dx ** 2 + dy ** 2) ** 0.5
        # start/end offset by radius
        sx = px + R * dx / dist
        sy = py + R * dy / dist
        ex = cx - R * dx / dist
        ey = cy - R * dy / dist
        ax.plot([sx, ex], [sy, ey], color=C_GRAY, lw=1.8, zorder=1)
        # edge label at midpoint
        mx = (px + cx) / 2
        my = (py + cy) / 2
        ax.text(mx + 0.18, my, edge_lbl, ha="center", va="center",
                fontsize=11, color=C_BLUE, fontweight="bold",
                bbox=dict(facecolor=C_BG, edgecolor="none", pad=1))

    # Draw nodes
    for key, (x, y, lbl, is_term) in nodes.items():
        color = C_ORANGE if is_term else C_BLUE
        if key == "root":
            color = C_INK
        circle = mpatches.Circle((x, y), R, color=color, zorder=3)
        ax.add_patch(circle)
        if is_term:
            # double circle for terminal nodes
            inner = mpatches.Circle((x, y), R * 0.72, color=C_BG, zorder=4)
            ax.add_patch(inner)
            inner2 = mpatches.Circle((x, y), R * 0.68, color=color, zorder=5)
            ax.add_patch(inner2)
        disp = lbl if key != "root" else "·"
        ax.text(x, y, disp, ha="center", va="center",
                fontsize=11, color=C_BG, fontweight="bold", zorder=6)

    # Legend
    legend_x, legend_y = 9.5, 5.0
    term_patch = mpatches.Circle((legend_x, legend_y), R * 0.6, color=C_ORANGE, zorder=3)
    ax.add_patch(term_patch)
    inner_leg = mpatches.Circle((legend_x, legend_y), R * 0.6 * 0.72, color=C_BG, zorder=4)
    ax.add_patch(inner_leg)
    inner_leg2 = mpatches.Circle((legend_x, legend_y), R * 0.6 * 0.68, color=C_ORANGE, zorder=5)
    ax.add_patch(inner_leg2)
    ax.text(legend_x + 0.4, legend_y, "= конец слова", ha="left", va="center",
            fontsize=9, color=C_INK)

    # Word labels at terminal nodes
    word_labels = {
        "car":  "\"car\"",
        "cart": "\"cart\"",
        "cat":  "\"cat\"",
        "dog":  "\"dog\"",
        "dot":  "\"dot\"",
    }
    offsets = {
        "car":  (-0.5, 0.0),
        "cart": (-0.5, -0.3),
        "cat":  (0.5, 0.0),
        "dog":  (-0.5, 0.0),
        "dot":  (0.5, 0.0),
    }
    for key, wlbl in word_labels.items():
        x, y = nodes[key][0], nodes[key][1]
        ox, oy = offsets[key]
        ax.text(x + ox, y + oy, wlbl, ha="center", va="center",
                fontsize=8, color=C_GREEN, style="italic")

    ax.set_title('Бор (trie): слова "car", "cart", "cat", "dog", "dot"',
                 fontsize=14, color=C_INK, fontweight="bold", pad=12)

    _save(fig, "trie_example")


def draw_prefix_function():
    """Prefix function table for ABABCABAB with prefix=suffix match shown."""
    _apply_style()
    s = "ABABCABAB"
    pi = [0, 0, 1, 2, 0, 1, 2, 3, 4]
    n = len(s)
    cell_w = 1.0
    box_h = 0.62

    fig, ax = plt.subplots(figsize=(11, 4.6))
    ax.set_facecolor(C_BG)
    ax.set_xlim(-1.6, n * cell_w + 0.6)
    ax.set_ylim(-2.6, 2.2)
    ax.axis("off")

    y_s = 1.0    # string row
    y_pi = 0.1   # pi row
    y_match = -1.6  # prefix=suffix illustration row

    ax.text(-0.7, y_s, "s[i]:", ha="right", va="center", fontsize=12,
            color=C_INK, fontweight="bold")
    ax.text(-0.7, y_pi, "π[i]:", ha="right", va="center", fontsize=12,
            color=C_INK, fontweight="bold")

    for i, ch in enumerate(s):
        x = i * cell_w
        # index above
        ax.text(x, y_s + 0.55, str(i), ha="center", va="center",
                fontsize=8, color=C_GRAY)
        # string cell
        rect = mpatches.FancyBboxPatch(
            (x - 0.45, y_s - box_h / 2), 0.9, box_h,
            boxstyle="round,pad=0.05", linewidth=1,
            edgecolor=C_GRAY, facecolor=C_PANEL, zorder=2)
        ax.add_patch(rect)
        ax.text(x, y_s, ch, ha="center", va="center",
                fontsize=13, color=C_INK, fontweight="bold", zorder=3)
        # pi cell (highlight the reset at i=4 and the max at i=8)
        col = C_ORANGE if i in (4, 8) else C_BLUE
        ax.text(x, y_pi, str(pi[i]), ha="center", va="center",
                fontsize=12, color=col, fontweight="bold")

    ax.annotate("π[4]=0: символ C\nне продолжает префикс",
                xy=(4 * cell_w, y_pi - 0.25), xytext=(4 * cell_w, y_pi - 1.0),
                ha="center", fontsize=8.5, color=C_ORANGE,
                arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=1.2))

    # Bottom: prefix ABAB (blue) vs suffix ABAB (orange) for i=8
    ax.text(-0.7, y_match, "π[8]=4:", ha="right", va="center", fontsize=11,
            color=C_INK, fontweight="bold")
    for i, ch in enumerate(s):
        x = i * cell_w
        if i < 4:
            edge, fill, tcol = C_BLUE, C_BG, C_BLUE       # prefix ABAB
        elif i >= 5:
            edge, fill, tcol = C_ORANGE, C_BG, C_ORANGE   # suffix ABAB
        else:
            edge, fill, tcol = C_GRAY, C_BG, C_GRAY
        rect = mpatches.FancyBboxPatch(
            (x - 0.45, y_match - box_h / 2), 0.9, box_h,
            boxstyle="round,pad=0.05", linewidth=1.6,
            edgecolor=edge, facecolor=fill, zorder=2)
        ax.add_patch(rect)
        ax.text(x, y_match, ch, ha="center", va="center",
                fontsize=12, color=tcol, fontweight="bold", zorder=3)
    ax.text(1.5 * cell_w, y_match - 0.65, "префикс ABAB", ha="center",
            va="top", fontsize=9, color=C_BLUE)
    ax.text(7.0 * cell_w, y_match - 0.65, "суффикс ABAB", ha="center",
            va="top", fontsize=9, color=C_ORANGE)

    ax.set_title("Префикс-функция строки ABABCABAB",
                 fontsize=14, color=C_INK, fontweight="bold", pad=12)
    _save(fig, "prefix_function")


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_dsu()
    draw_kmp()
    draw_trie()
    draw_prefix_function()


if __name__ == "__main__":
    main()
