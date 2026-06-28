"""Точные схемы для лекции про простейшие структуры данных."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

C_BG     = "#faf9f5"
C_INK    = "#141413"
C_GRAY   = "#b0aea5"
C_PANEL  = "#e8e6dc"
C_ORANGE = "#d97757"
C_BLUE   = "#6a9bcc"
C_GREEN  = "#788c5d"


def _apply_style():
    plt.rcParams.update({
        "figure.facecolor": C_BG,
        "axes.facecolor":   C_BG,
        "axes.edgecolor":   C_GRAY,
        "axes.labelcolor":  C_INK,
        "xtick.color":      C_INK,
        "ytick.color":      C_INK,
        "text.color":       C_INK,
        "font.size":        11,
        "font.family":      "sans-serif",
        "axes.spines.top":   False,
        "axes.spines.right": False,
    })


def _save(fig, name):
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS / name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)
    print("Saved: assets/" + name)


# ---------------------------------------------------------------------------
# 1. Stack operations: bracket checking
# ---------------------------------------------------------------------------
def draw_stack_ops():
    """Стек для проверки скобочной последовательности."""
    _apply_style()

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.5, 6)
    ax.axis("off")

    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)

    # Title
    ax.text(5, 5.6, "Стек при проверке скобок: ( { [ ] } )",
            ha="center", va="center", fontsize=13, fontweight="bold", color=C_INK)

    # Draw stack boxes (bottom to top, left side)
    stack_items = ["(", "{", "["]   # items in stack after processing "({["
    box_w, box_h = 1.2, 0.7
    base_x = 1.0
    base_y = 0.3

    for i, ch in enumerate(stack_items):
        y = base_y + i * (box_h + 0.1)
        color = C_BLUE if ch in "([{" else C_ORANGE
        rect = mpatches.Rectangle((base_x, y), box_w, box_h,
                                   linewidth=1.5, edgecolor=C_INK,
                                   facecolor=color, zorder=3)
        ax.add_patch(rect)
        ax.text(base_x + box_w / 2, y + box_h / 2, ch,
                ha="center", va="center", fontsize=16,
                fontweight="bold", color="white", zorder=4)

    # TOP label and arrow
    top_y = base_y + len(stack_items) * (box_h + 0.1) - 0.1
    ax.annotate("TOP", xy=(base_x + box_w, top_y + box_h / 2),
                xytext=(base_x + box_w + 0.6, top_y + box_h / 2),
                fontsize=10, color=C_ORANGE,
                arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=1.5))

    # Stack label
    ax.text(base_x + box_w / 2, base_y - 0.35, "Стек",
            ha="center", va="center", fontsize=10, color=C_GRAY)

    # Input string display (right side)
    ax.text(4.5, 5.0, "Входная строка:  ( { [ ] } )",
            ha="left", va="center", fontsize=11, color=C_INK)

    # Legend
    legend_items = [
        mpatches.Patch(facecolor=C_BLUE,   label="Открывающая → push"),
        mpatches.Patch(facecolor=C_GREEN,  label="Закрывающая → pop (совпало)"),
        mpatches.Patch(facecolor=C_ORANGE, label="Закрывающая → ошибка (несовпадение)"),
    ]
    ax.legend(handles=legend_items, loc="lower right",
              fontsize=9, framealpha=0.0, handlelength=1.2)

    # Step annotations
    steps = [
        (4.5, 4.3, "1. push('(')  → стек: [(]"),
        (4.5, 3.7, "2. push('{')  → стек: [(, {]"),
        (4.5, 3.1, "3. push('[')  → стек: [(, {, []"),
        (4.5, 2.5, "4. ']' совпадает с '[' → pop"),
        (4.5, 1.9, "5. '}' совпадает с '{' → pop"),
        (4.5, 1.3, "6. ')' совпадает с '(' → pop"),
        (4.5, 0.7, "7. Стек пуст → последовательность верна"),
    ]
    for (x, y, text) in steps:
        ax.text(x, y, text, ha="left", va="center", fontsize=9.5, color=C_INK,
                fontfamily="monospace")

    _save(fig, "stack_ops.png")


# ---------------------------------------------------------------------------
# 2. Circular buffer queue
# ---------------------------------------------------------------------------
def draw_queue_circular():
    """Кольцевой буфер очереди: 8 слотов, head и tail."""
    _apply_style()

    M = 8
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_xlim(-3.5, 3.5)
    ax.set_ylim(-3.5, 3.5)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)

    ax.text(0, 3.2, "Кольцевой буфер (M = 8)",
            ha="center", va="center", fontsize=13, fontweight="bold", color=C_INK)

    # Filled slots: indices 2..5 (head=2, tail=6)
    head_idx = 2
    tail_idx = 6
    filled = set(range(head_idx, tail_idx))

    radius = 2.2
    slot_w = 0.55
    slot_h = 0.40
    values = {2: "10", 3: "20", 4: "30", 5: "40"}

    for k in range(M):
        angle = np.pi / 2 - 2 * np.pi * k / M
        cx = radius * np.cos(angle)
        cy = radius * np.sin(angle)

        is_filled = k in filled
        face = C_BLUE if is_filled else C_PANEL
        edge = C_INK  if is_filled else C_GRAY

        rect = mpatches.Rectangle((cx - slot_w / 2, cy - slot_h / 2),
                                    slot_w, slot_h,
                                    linewidth=1.5, edgecolor=edge,
                                    facecolor=face, zorder=3)
        ax.add_patch(rect)

        val_text = values.get(k, "")
        ax.text(cx, cy, val_text, ha="center", va="center",
                fontsize=10, fontweight="bold",
                color="white" if is_filled else C_GRAY, zorder=4)

        # Index label outside the circle
        label_r = radius + 0.55
        ax.text(label_r * np.cos(angle), label_r * np.sin(angle),
                str(k), ha="center", va="center",
                fontsize=9, color=C_GRAY)

    # HEAD arrow
    head_angle = np.pi / 2 - 2 * np.pi * head_idx / M
    hx = radius * np.cos(head_angle)
    hy = radius * np.sin(head_angle)
    ax.annotate("HEAD", xy=(hx, hy + slot_h / 2 + 0.05),
                xytext=(hx + 0.7, hy + 1.0),
                fontsize=10, color=C_GREEN, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C_GREEN, lw=1.8))

    # TAIL arrow
    tail_angle = np.pi / 2 - 2 * np.pi * tail_idx / M
    tx = radius * np.cos(tail_angle)
    ty = radius * np.sin(tail_angle)
    ax.annotate("TAIL", xy=(tx, ty + slot_h / 2 + 0.05),
                xytext=(tx + 0.7, ty + 1.0),
                fontsize=10, color=C_ORANGE, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=1.8))

    # Legend
    legend_items = [
        mpatches.Patch(facecolor=C_BLUE,  label="Занятые слоты (элементы в очереди)"),
        mpatches.Patch(facecolor=C_PANEL, label="Свободные слоты"),
    ]
    ax.legend(handles=legend_items, loc="lower center",
              fontsize=9, framealpha=0.0, bbox_to_anchor=(0.5, -0.08))

    # Formula hint
    ax.text(0, -2.9, "head = (head + 1) % M",
            ha="center", va="center", fontsize=10,
            color=C_INK, style="italic")

    _save(fig, "queue_circular.png")


# ---------------------------------------------------------------------------
# 3. Linked list: node deletion
# ---------------------------------------------------------------------------
def draw_linked_list():
    """Связный список: удаление среднего узла — перенаправление стрелки."""
    _apply_style()

    fig, axes = plt.subplots(2, 1, figsize=(9, 5.5),
                              gridspec_kw={"hspace": 0.6})
    fig.patch.set_facecolor(C_BG)

    node_w = 1.3
    node_h = 0.6
    gap = 0.6    # gap between nodes
    step = node_w + gap

    def draw_nodes(ax, nodes, title, delete_idx=None,
                   reroute_from=None, reroute_to=None):
        ax.set_xlim(-0.3, len(nodes) * step + 0.5)
        ax.set_ylim(-0.8, 1.4)
        ax.axis("off")
        ax.set_facecolor(C_BG)
        ax.text((len(nodes) * step) / 2, 1.2, title,
                ha="center", va="center", fontsize=11,
                fontweight="bold", color=C_INK)

        centers_x = []
        for i, (val, label) in enumerate(nodes):
            x = i * step
            centers_x.append(x + node_w / 2)
            is_deleted = (i == delete_idx)

            face = C_ORANGE if is_deleted else C_BLUE
            alpha = 0.3 if is_deleted else 1.0

            rect = mpatches.Rectangle((x, 0), node_w, node_h,
                                       linewidth=1.5, edgecolor=C_INK,
                                       facecolor=face, alpha=alpha, zorder=3)
            ax.add_patch(rect)
            ax.text(x + node_w / 2, node_h / 2, str(val),
                    ha="center", va="center", fontsize=13,
                    fontweight="bold", color="white", alpha=alpha, zorder=4)

            # NULL sentinel for last node
            if i == len(nodes) - 1:
                ax.text(x + node_w + gap / 2, node_h / 2, "NULL",
                        ha="center", va="center", fontsize=9, color=C_GRAY)
            else:
                # Next pointer arrow
                is_skipped = (reroute_from == i)
                if is_skipped:
                    # Draw arc over the deleted node
                    x_start = x + node_w
                    x_end   = centers_x[reroute_to] if (reroute_to is not None and reroute_to < len(centers_x)) else x_start + step
                    x_mid   = (x_start + x_end) / 2
                    ax.annotate("",
                                xy=(x_end - node_w / 2 + 0.02, node_h / 2),
                                xytext=(x_start, node_h / 2),
                                arrowprops=dict(
                                    arrowstyle="->",
                                    color=C_GREEN,
                                    lw=2.0,
                                    connectionstyle="arc3,rad=-0.5"
                                ))
                    ax.text(x_mid, -0.5, "перенаправлено",
                            ha="center", va="center", fontsize=8.5,
                            color=C_GREEN, style="italic")
                else:
                    ax.annotate("",
                                xy=(x + step, node_h / 2),
                                xytext=(x + node_w, node_h / 2),
                                arrowprops=dict(arrowstyle="->",
                                                color=C_INK, lw=1.5))

            # Index label below
            ax.text(x + node_w / 2, -0.25, label,
                    ha="center", va="center", fontsize=8.5, color=C_GRAY)

        # Strikethrough for deleted node
        if delete_idx is not None:
            dx = delete_idx * step
            ax.plot([dx + 0.1, dx + node_w - 0.1],
                    [node_h - 0.1, 0.1], color=C_ORANGE, lw=2, zorder=5)
            ax.plot([dx + 0.1, dx + node_w - 0.1],
                    [0.1, node_h - 0.1], color=C_ORANGE, lw=2, zorder=5)

    # Before deletion
    nodes_before = [(1, "head"), (2, ""), (3, "удалить"), (4, "")]
    draw_nodes(axes[0], nodes_before,
               "До удаления: 1 → 2 → 3 → 4",
               delete_idx=2)

    # After deletion
    nodes_after = [(1, "head"), (2, ""), (4, "")]
    draw_nodes(axes[1], nodes_after,
               "После удаления: 1 → 2 → 4",
               reroute_from=1, reroute_to=2)

    _save(fig, "linked_list.png")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_stack_ops()
    draw_queue_circular()
    draw_linked_list()
    print("All visuals generated successfully.")


if __name__ == "__main__":
    main()
