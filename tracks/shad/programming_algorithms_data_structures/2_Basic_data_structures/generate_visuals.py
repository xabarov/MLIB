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
# 4. Vector capacity doubling (amortized push_back)
# ---------------------------------------------------------------------------
def draw_vector_growth():
    """Удвоение capacity вектора: 9 операций push_back, копирования при удвоении."""
    _apply_style()

    # (size после push, capacity после push, скопировано элементов при realloc)
    pushes = [
        (1, 1, 0),
        (2, 2, 1),
        (3, 4, 2),
        (4, 4, 0),
        (5, 8, 4),
        (6, 8, 0),
        (7, 8, 0),
        (8, 8, 0),
        (9, 16, 8),
    ]
    max_cap = 16

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.axis("off")

    cell_w, cell_h = 0.5, 0.55
    gap_x, gap_y = 0.06, 0.35
    x0 = 2.1

    ax.text(x0 + (max_cap * (cell_w + gap_x)) / 2, len(pushes) * (cell_h + gap_y) + 0.5,
            "Рост std::vector: push_back и удвоение capacity",
            ha="center", va="center", fontsize=13, fontweight="bold", color=C_INK)

    total_copies = 0
    for row, (size, cap, copied) in enumerate(pushes):
        y = (len(pushes) - 1 - row) * (cell_h + gap_y)
        # Подпись слева: номер операции
        ax.text(x0 - 0.25, y + cell_h / 2, f"push #{size}",
                ha="right", va="center", fontsize=9.5, color=C_INK,
                fontfamily="monospace")
        for k in range(cap):
            x = x0 + k * (cell_w + gap_x)
            is_new = (k == size - 1)
            filled = k < size
            face = C_ORANGE if is_new else (C_BLUE if filled else C_BG)
            edge = C_INK if filled else C_GRAY
            rect = mpatches.Rectangle((x, y), cell_w, cell_h,
                                       linewidth=1.3, edgecolor=edge,
                                       facecolor=face, zorder=3)
            ax.add_patch(rect)
        # Аннотация копирования справа
        note_x = x0 + max_cap * (cell_w + gap_x) + 0.25
        if copied:
            total_copies += copied
            ax.text(note_x, y + cell_h / 2,
                    f"capacity {cap // 2} → {cap}, скопировано {copied}",
                    ha="left", va="center", fontsize=9, color=C_ORANGE)
        else:
            ax.text(note_x, y + cell_h / 2, "без копирования — O(1)",
                    ha="left", va="center", fontsize=9, color=C_GREEN)

    # Легенда и итоговая формула
    legend_items = [
        mpatches.Patch(facecolor=C_ORANGE, edgecolor=C_INK, label="Новый элемент"),
        mpatches.Patch(facecolor=C_BLUE, edgecolor=C_INK, label="Уже лежит в векторе"),
        mpatches.Patch(facecolor=C_BG, edgecolor=C_GRAY, label="Свободная capacity"),
    ]
    ax.legend(handles=legend_items, loc="lower left",
              bbox_to_anchor=(0.0, -0.09), fontsize=9, framealpha=0.0, ncol=3)
    ax.text(x0, -0.75,
            f"Всего копирований за 9 push_back: 1 + 2 + 4 + 8 = {total_copies} ≤ 2n  →  амортизированно O(1)",
            ha="left", va="center", fontsize=10, color=C_INK, style="italic")

    ax.set_xlim(0, x0 + max_cap * (cell_w + gap_x) + 3.6)
    ax.set_ylim(-1.1, len(pushes) * (cell_h + gap_y) + 0.9)
    _save(fig, "vector_growth.png")


# ---------------------------------------------------------------------------
# 5. Monotonic deque: sliding window minimum trace
# ---------------------------------------------------------------------------
def draw_deque_sliding_min():
    """Трассировка монотонного дека для sliding_min({3,1,2,5,4,6}, k=3).

    Состояния получаются честной симуляцией алгоритма из лекции.
    """
    _apply_style()
    from collections import deque

    a = [3, 1, 2, 5, 4, 6]
    k = 3
    n = len(a)

    # --- честная симуляция ---------------------------------------------
    dq = deque()
    steps = []  # (i, lo_окна, дек после шага, popped_front, popped_back, минимум|None)
    for i in range(n):
        popped_front, popped_back = [], []
        while dq and dq[0] < i - k + 1:
            popped_front.append(dq.popleft())
        while dq and a[dq[-1]] >= a[i]:
            popped_back.append(dq.pop())
        dq.append(i)
        mn = a[dq[0]] if i >= k - 1 else None
        steps.append((i, max(0, i - k + 1), list(dq), popped_front, popped_back, mn))

    # --- отрисовка -------------------------------------------------------
    fig, ax = plt.subplots(figsize=(12.5, 7.2))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.axis("off")

    cell_w, cell_h = 0.62, 0.62
    gap = 0.10
    row_h = 1.28
    x_arr = 1.1            # начало массива
    x_dq = 6.7             # начало дека
    x_min = 10.4           # колонка минимума
    top_y = (n - 1) * row_h

    ax.text((x_arr + x_min + 1.6) / 2, top_y + cell_h + 1.15,
            "Монотонный дек: минимум на окне k = 3, массив {3, 1, 2, 5, 4, 6}",
            ha="center", va="center", fontsize=13, fontweight="bold", color=C_INK)

    # Заголовки колонок
    hdr_y = top_y + cell_h + 0.45
    ax.text(x_arr + n * (cell_w + gap) / 2, hdr_y, "Массив (окно — серым)",
            ha="center", fontsize=10, color=C_GRAY)
    ax.text(x_dq + 1.1, hdr_y, "Дек после шага (голова слева)",
            ha="center", fontsize=10, color=C_GRAY)
    ax.text(x_min + 0.5, hdr_y, "Минимум окна",
            ha="center", fontsize=10, color=C_GRAY)

    for row, (i, lo, dqs, pf, pb, mn) in enumerate(steps):
        y = (n - 1 - row) * row_h

        # Подпись шага
        ax.text(x_arr - 0.35, y + cell_h / 2, f"i = {i}",
                ha="right", va="center", fontsize=10.5, color=C_INK,
                fontweight="bold")

        # Массив
        for j in range(n):
            x = x_arr + j * (cell_w + gap)
            in_win = lo <= j <= i
            face = C_PANEL if in_win else C_BG
            edge = C_ORANGE if j == i else (C_INK if in_win else C_GRAY)
            lw = 2.2 if j == i else 1.2
            ax.add_patch(mpatches.Rectangle((x, y), cell_w, cell_h,
                                            facecolor=face, edgecolor=edge,
                                            linewidth=lw, zorder=3))
            ax.text(x + cell_w / 2, y + cell_h / 2, str(a[j]),
                    ha="center", va="center", fontsize=11,
                    color=C_INK if in_win else C_GRAY, zorder=4)

        # Дек
        for pos, idx in enumerate(dqs):
            x = x_dq + pos * (cell_w + gap)
            is_head = (pos == 0)
            face = C_GREEN if is_head else C_BLUE
            ax.add_patch(mpatches.Rectangle((x, y), cell_w, cell_h,
                                            facecolor=face, edgecolor=C_INK,
                                            linewidth=1.3, zorder=3))
            ax.text(x + cell_w / 2, y + cell_h / 2, str(a[idx]),
                    ha="center", va="center", fontsize=11, fontweight="bold",
                    color="white", zorder=4)
            ax.text(x + cell_w / 2, y - 0.14, f"[{idx}]",
                    ha="center", va="top", fontsize=7.5, color=C_GRAY)

        # Что выброшено на этом шаге
        events = []
        if pb:
            events.append("pop_back: " + ", ".join(str(a[j]) for j in pb)
                          + (" ≥ " + str(a[i])))
        if pf:
            events.append("pop_front: " + ", ".join(str(a[j]) for j in pf)
                          + " (вышел из окна)")
        if events:
            ax.text(x_dq, y - 0.40, ";  ".join(events),
                    ha="left", va="top", fontsize=8,
                    color=C_ORANGE, style="italic")

        # Минимум
        if mn is not None:
            ax.text(x_min + 0.5, y + cell_h / 2, f"min = {mn}",
                    ha="center", va="center", fontsize=11.5,
                    fontweight="bold", color=C_GREEN)
        else:
            ax.text(x_min + 0.5, y + cell_h / 2, "окно не заполнено",
                    ha="center", va="center", fontsize=9, color=C_GRAY)

    # Легенда
    legend_items = [
        mpatches.Patch(facecolor=C_GREEN, edgecolor=C_INK,
                       label="Голова дека = минимум окна"),
        mpatches.Patch(facecolor=C_BLUE, edgecolor=C_INK,
                       label="Остальной дек (значения возрастают)"),
        mpatches.Patch(facecolor=C_PANEL, edgecolor=C_INK,
                       label="Текущее окно"),
    ]
    ax.legend(handles=legend_items, loc="lower center",
              bbox_to_anchor=(0.5, -0.06), fontsize=9, framealpha=0.0, ncol=3)

    ax.set_xlim(0, x_min + 2.0)
    ax.set_ylim(-0.9, top_y + cell_h + 1.5)
    _save(fig, "deque_sliding_min.png")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_stack_ops()
    draw_queue_circular()
    draw_linked_list()
    draw_vector_growth()
    draw_deque_sliding_min()
    print("All visuals generated successfully.")


if __name__ == "__main__":
    main()
