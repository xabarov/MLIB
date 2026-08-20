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


def _apply_style(fig, ax_list=None):
    fig.patch.set_facecolor(C_BG)
    if ax_list is None:
        ax_list = fig.get_axes()
    for ax in ax_list:
        ax.set_facecolor(C_BG)
        ax.tick_params(colors=C_INK)
        for spine in ax.spines.values():
            spine.set_edgecolor(C_GRAY)


def _save(fig, name):
    ASSETS.mkdir(parents=True, exist_ok=True)
    path = ASSETS / f"{name}.png"
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)
    print(f"Saved: {path}")


def draw_quickselect():
    """Array [3,1,4,1,5,9,2,6], pivot=4 highlighted. After partition: left blue, pivot orange, right gray."""
    fig, axes = plt.subplots(2, 1, figsize=(10, 5))
    _apply_style(fig, axes)

    original = [3, 1, 4, 1, 5, 9, 2, 6]
    after = [3, 1, 1, 2, 4, 9, 6, 5]
    # After Lomuto with pivot=4 (moved to the end first): elements <=4 on left,
    # pivot at index 4, elements >4 on right
    # left part indices 0-3: [3,1,1,2], pivot at 4: [4], right part 5-7: [9,6,5]

    box_w = 0.8
    box_h = 0.6

    def draw_array(ax, arr, colors, title, arrow_idx=None):
        ax.set_xlim(-0.5, len(arr) - 0.5)
        ax.set_ylim(-0.3, 1.2)
        ax.axis("off")
        ax.set_title(title, color=C_INK, fontsize=11, pad=4)
        for i, (val, color) in enumerate(zip(arr, colors)):
            rect = mpatches.Rectangle(
                (i - box_w / 2, 0.3), box_w, box_h,
                linewidth=1.2, edgecolor=C_INK, facecolor=color
            )
            ax.add_patch(rect)
            ax.text(i, 0.3 + box_h / 2, str(val),
                    ha="center", va="center", fontsize=13,
                    color=C_INK, fontweight="bold")
            ax.text(i, 0.15, str(i), ha="center", va="center",
                    fontsize=8, color=C_GRAY)
        if arrow_idx is not None:
            ax.annotate(
                "ищем k=2 (0-инд.)\n→ рекурсия влево", xy=(arrow_idx, 0.3),
                xytext=(arrow_idx, -0.15),
                fontsize=9, color=C_ORANGE, ha="center",
                arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=1.5)
            )

    # Top: original array, pivot=4 (index 2) orange
    colors_orig = [C_PANEL] * len(original)
    colors_orig[2] = C_ORANGE  # pivot=4
    draw_array(axes[0], original, colors_orig,
               "Исходный массив: пивот = 4 (выделен оранжевым)")

    # Bottom: after partition
    # left [1,1,3,2] blue, pivot [4] orange, right [9,5,6] gray
    colors_after = [C_BLUE] * 4 + [C_ORANGE] + [C_GRAY] * 3
    draw_array(axes[1], after, colors_after,
               "После разбиения Lomuto: пивот на позиции 4",
               arrow_idx=2)

    # Labels for regions
    ax2 = axes[1]
    ax2.annotate("", xy=(3.5, 0.95), xytext=(-0.5, 0.95),
                 arrowprops=dict(arrowstyle="<->", color=C_BLUE, lw=1.5))
    ax2.text(1.5, 1.08, "левая часть ≤ 4", ha="center", fontsize=9, color=C_BLUE)

    ax2.annotate("", xy=(7.5, 0.95), xytext=(4.5, 0.95),
                 arrowprops=dict(arrowstyle="<->", color=C_GRAY, lw=1.5))
    ax2.text(6.0, 1.08, "правая часть > 4", ha="center", fontsize=9, color=C_GRAY)

    fig.suptitle("Quick-Select: шаг разбиения", fontsize=13,
                 color=C_INK, y=1.01, fontweight="bold")
    plt.tight_layout()
    _save(fig, "quickselect_partition")


def draw_median_of_medians():
    """12 elements in 3 groups. Medians highlighted orange. Final M circled."""
    elements = [7, 2, 10, 5, 3, 8, 1, 9, 4, 11, 6, 12]
    groups = [elements[0:5], elements[5:10], elements[10:12]]
    sorted_groups = [sorted(g) for g in groups]
    medians = [g[len(g) // 2] for g in sorted_groups]

    fig, ax = plt.subplots(figsize=(10, 7))
    _apply_style(fig, [ax])
    ax.set_xlim(-0.5, 10)
    ax.set_ylim(-1.2, 8)
    ax.axis("off")
    ax.set_title("Медиана медиан: 3 группы, выделение медиан", fontsize=13,
                 color=C_INK, fontweight="bold", pad=10)

    box_w = 1.4
    box_h = 0.7
    group_x_centers = [1.5, 5.0, 8.5]

    for g_idx, (sg, med, gx) in enumerate(zip(sorted_groups, medians, group_x_centers)):
        # Title for group
        ax.text(gx, 7.5, f"Группа {g_idx + 1}", ha="center", va="center",
                fontsize=10, color=C_INK, fontweight="bold")
        ax.text(gx, 7.0, "(отсортирована)", ha="center", va="center",
                fontsize=8, color=C_GRAY)

        for row, val in enumerate(sg):
            y = 6.0 - row * (box_h + 0.15)
            is_median = (val == med)
            color = C_ORANGE if is_median else C_PANEL
            rect = mpatches.Rectangle(
                (gx - box_w / 2, y), box_w, box_h,
                linewidth=1.5 if is_median else 1.0,
                edgecolor=C_ORANGE if is_median else C_INK,
                facecolor=color
            )
            ax.add_patch(rect)
            ax.text(gx, y + box_h / 2, str(val), ha="center", va="center",
                    fontsize=12, color=C_INK,
                    fontweight="bold" if is_median else "normal")
            if is_median:
                ax.text(gx + box_w / 2 + 0.1, y + box_h / 2, "← медиана",
                        ha="left", va="center", fontsize=8, color=C_ORANGE)

        # Arrow down to medians row
        med_y_src = 6.0 - (len(sg) // 2) * (box_h + 0.15)
        ax.annotate("", xy=(gx, -0.15), xytext=(gx, med_y_src - 0.05),
                    arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=1.5, linestyle="dashed"))

        # Median value box at bottom
        med_rect = mpatches.Rectangle(
            (gx - box_w / 2, -0.85), box_w, box_h,
            linewidth=2, edgecolor=C_ORANGE, facecolor=C_ORANGE
        )
        ax.add_patch(med_rect)
        ax.text(gx, -0.85 + box_h / 2, str(med), ha="center", va="center",
                fontsize=13, color="white", fontweight="bold")

    # Label medians row
    ax.text(-0.2, -0.85 + box_h / 2, "Медианы:", ha="right", va="center",
            fontsize=10, color=C_INK)

    # Final M: median of medians
    M_val = sorted(medians)[len(medians) // 2]
    M_x = 9.5
    M_y = -0.85 + box_h / 2

    # Circle around M
    circle = mpatches.Circle((M_x, M_y), 0.55, color=C_GREEN, fill=True, alpha=0.25, zorder=4)
    ax.add_patch(circle)
    circle_border = mpatches.Circle((M_x, M_y), 0.55, color=C_GREEN, fill=False, linewidth=2.5, zorder=5)
    ax.add_patch(circle_border)
    ax.text(M_x, M_y, f"M={M_val}", ha="center", va="center",
            fontsize=12, color=C_GREEN, fontweight="bold", zorder=6)
    ax.text(M_x, M_y - 0.85, "Пивот!", ha="center", va="center",
            fontsize=9, color=C_GREEN, fontweight="bold")

    # Arrow from medians to M
    ax.annotate("", xy=(M_x - 0.6, M_y), xytext=(group_x_centers[-1] + box_w / 2 + 0.1, M_y),
                arrowprops=dict(arrowstyle="->", color=C_GREEN, lw=2.0))
    ax.text((M_x - 0.6 + group_x_centers[-1] + box_w / 2) / 2, M_y + 0.35,
            "медиана медиан", ha="center", va="center", fontsize=8, color=C_GREEN)

    plt.tight_layout()
    _save(fig, "median_of_medians")


def draw_quickselect_recursion():
    """Recursion tree for Quick-Select showing O(log n) expected depth vs O(n) worst case."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    _apply_style(fig, axes)

    # Left: expected case (good pivots ~50% split)
    ax = axes[0]
    ax.set_facecolor(C_BG)
    ax.axis("off")
    ax.set_title("Ожидаемый случай\nO(n) сравнений", fontsize=12,
                 color=C_INK, fontweight="bold")

    levels_exp = [
        ("n", 0.5),
        ("≈n/2", 0.35),
        ("≈n/4", 0.25),
        ("≈n/8", 0.2),
        ("...", 0.17),
        ("1", 0.15),
    ]
    colors_exp = [C_ORANGE, C_BLUE, C_BLUE, C_BLUE, C_PANEL, C_GREEN]

    y_pos = 0.85
    x_prev = 0.5
    for level, (label, x_frac) in enumerate(levels_exp):
        y = y_pos - level * 0.13
        x = 0.1 + x_frac * 0.8
        color = colors_exp[level] if level < len(colors_exp) else C_PANEL

        if level > 0:
            ax.plot([x_prev, x], [y + 0.13 - 0.025, y + 0.025],
                    color=C_GRAY, lw=1.5, zorder=1)

        rect = mpatches.FancyBboxPatch(
            (x - 0.1, y - 0.028), 0.2, 0.056,
            boxstyle="round,pad=0.01",
            linewidth=1.5, edgecolor=C_INK, facecolor=color, zorder=2
        )
        ax.add_patch(rect)
        ax.text(x, y, label, ha="center", va="center",
                fontsize=11, color=C_INK, fontweight="bold", zorder=3)

        if level == 0:
            work_label = "O(n)"
        elif level < 5:
            frac = 2 ** level
            work_label = f"O(n/{frac})"
        else:
            work_label = "O(1)"

        ax.text(x + 0.14, y, work_label, ha="left", va="center",
                fontsize=8, color=C_GRAY)
        x_prev = x

    # Depth annotation
    ax.annotate("", xy=(0.05, 0.85 - 5 * 0.13), xytext=(0.05, 0.85),
                arrowprops=dict(arrowstyle="<->", color=C_BLUE, lw=1.5))
    ax.text(0.02, 0.85 - 2.5 * 0.13, "O(log n)\nуровней",
            ha="center", va="center", fontsize=8, color=C_BLUE)

    # Total work annotation
    ax.text(0.5, -0.25, "Суммарная работа:\n$n + n/2 + n/4 + \\ldots = 2n = O(n)$",
            ha="center", va="center", fontsize=9, color=C_INK,
            bbox=dict(boxstyle="round,pad=0.3", facecolor=C_PANEL, edgecolor=C_BLUE, lw=1.5))

    # Right: worst case (always bad pivot)
    ax2 = axes[1]
    ax2.set_facecolor(C_BG)
    ax2.axis("off")
    ax2.set_title("Худший случай\nO(n²) сравнений", fontsize=12,
                  color=C_INK, fontweight="bold")

    levels_worst = ["n", "n-1", "n-2", "n-3", "...", "1"]
    colors_worst = [C_ORANGE] + [C_GRAY] * 4 + [C_GREEN]

    y_pos2 = 0.85
    x_base = 0.5
    for level, label in enumerate(levels_worst):
        y = y_pos2 - level * 0.13
        x = x_base - level * 0.02
        color = colors_worst[level] if level < len(colors_worst) else C_PANEL

        if level > 0:
            x_p = x_base - (level - 1) * 0.02
            y_p = y_pos2 - (level - 1) * 0.13
            ax2.plot([x_p, x], [y_p - 0.025, y + 0.025],
                     color=C_GRAY, lw=1.5, zorder=1)

        rect = mpatches.FancyBboxPatch(
            (x - 0.1, y - 0.028), 0.2, 0.056,
            boxstyle="round,pad=0.01",
            linewidth=1.5, edgecolor=C_INK, facecolor=color, zorder=2
        )
        ax2.add_patch(rect)
        ax2.text(x, y, label, ha="center", va="center",
                 fontsize=11, color=C_INK, fontweight="bold", zorder=3)

        if level == 0:
            work_label = "O(n)"
        elif level < 5:
            work_label = f"O(n-{level})"
        else:
            work_label = "O(1)"
        ax2.text(x + 0.14, y, work_label, ha="left", va="center",
                 fontsize=8, color=C_GRAY)

    # Depth annotation
    ax2.annotate("", xy=(0.05, y_pos2 - 5 * 0.13), xytext=(0.05, y_pos2),
                 arrowprops=dict(arrowstyle="<->", color=C_ORANGE, lw=1.5))
    ax2.text(0.02, y_pos2 - 2.5 * 0.13, "O(n)\nуровней",
             ha="center", va="center", fontsize=8, color=C_ORANGE)

    ax2.text(0.5, -0.25, "Суммарная работа:\n$n + (n-1) + \\ldots + 1 = O(n^2)$",
             ha="center", va="center", fontsize=9, color=C_INK,
             bbox=dict(boxstyle="round,pad=0.3", facecolor=C_PANEL, edgecolor=C_ORANGE, lw=1.5))

    fig.suptitle("Дерево рекурсии Quick-Select: ожидаемый vs худший случай",
                 fontsize=13, color=C_INK, fontweight="bold", y=1.02)
    plt.tight_layout()
    _save(fig, "quickselect_recursion")


def draw_mom_guarantee():
    """Why the median of medians guarantees a 30/70 split: 7 groups of 5 as a grid."""
    m = 7          # number of groups (columns)
    rows = 5       # group size
    cell = 0.8
    mid_col = m // 2
    mid_row = rows // 2

    fig, ax = plt.subplots(figsize=(11, 6))
    _apply_style(fig, [ax])
    ax.set_facecolor(C_BG)
    ax.axis("off")
    ax.set_xlim(-2.6, m * cell + 3.6)
    ax.set_ylim(-1.7, rows * cell + 1.3)
    ax.set_aspect("equal")

    # Shaded regions (draw first, under the cells)
    # >= M: top 3 rows of columns mid_col..m-1
    ge_rect = mpatches.Rectangle(
        (mid_col * cell - 0.06, mid_row * cell - 0.06),
        (m - mid_col) * cell + 0.06, (rows - mid_row) * cell + 0.06,
        facecolor=C_GREEN, alpha=0.28, edgecolor=C_GREEN,
        linewidth=2.0, zorder=1)
    ax.add_patch(ge_rect)
    # <= M: bottom 3 rows of columns 0..mid_col
    le_rect = mpatches.Rectangle(
        (-0.06, -0.06),
        (mid_col + 1) * cell + 0.06, (mid_row + 1) * cell + 0.06,
        facecolor=C_BLUE, alpha=0.28, edgecolor=C_BLUE,
        linewidth=2.0, zorder=1)
    ax.add_patch(le_rect)

    # Cells
    for col in range(m):
        for row in range(rows):
            x = col * cell
            y = row * cell
            is_median = (row == mid_row)
            is_M = is_median and (col == mid_col)
            if is_M:
                fc = C_ORANGE
            elif is_median:
                fc = C_PANEL
            else:
                fc = C_BG
            rect = mpatches.Rectangle(
                (x + 0.05, y + 0.05), cell - 0.1, cell - 0.1,
                facecolor=fc, edgecolor=C_INK,
                linewidth=1.6 if is_median else 0.9, zorder=2)
            ax.add_patch(rect)
            if is_M:
                ax.text(x + cell / 2, y + cell / 2, "M", ha="center",
                        va="center", fontsize=13, color=C_BG,
                        fontweight="bold", zorder=3)
            elif is_median:
                ax.text(x + cell / 2, y + cell / 2, "мед.", ha="center",
                        va="center", fontsize=7.5, color=C_INK, zorder=3)
            else:
                ax.text(x + cell / 2, y + cell / 2, "•", ha="center",
                        va="center", fontsize=9, color=C_GRAY, zorder=3)

    # Axis-of-order annotations
    ax.annotate("", xy=(m * cell + 0.25, rows * cell - 0.1),
                xytext=(m * cell + 0.25, 0.1),
                arrowprops=dict(arrowstyle="->", color=C_GRAY, lw=1.3))
    ax.text(m * cell + 0.45, rows * cell / 2,
            "внутри группы:\nснизу меньшие,\nсверху большие",
            ha="left", va="center", fontsize=8.5, color=C_INK)

    ax.annotate("", xy=(m * cell - 0.1, -0.35), xytext=(0.1, -0.35),
                arrowprops=dict(arrowstyle="->", color=C_GRAY, lw=1.3))
    ax.text(m * cell / 2, -0.75,
            "группы упорядочены по возрастанию медиан",
            ha="center", va="top", fontsize=9, color=C_INK)

    # Region labels (outside the grid)
    ax.text((mid_col + m) / 2 * cell, rows * cell + 0.25,
            "все эти элементы ≥ M:  3 · ⌈m/2⌉ ≥ 3n/10",
            ha="center", va="bottom", fontsize=9.5, color=C_GREEN,
            fontweight="bold")
    ax.text(-0.3, (mid_row + 1) / 2 * cell,
            "все эти элементы ≤ M:\n3 · ⌈m/2⌉ ≥ 3n/10",
            ha="right", va="center", fontsize=9.5, color=C_BLUE,
            fontweight="bold")

    ax.set_title("Гарантия медианы медиан: не менее 3n/10 элементов "
                 "с каждой стороны от M\n(пример: n = 35, m = 7 групп по 5)",
                 fontsize=12, color=C_INK, fontweight="bold", pad=10)

    plt.tight_layout()
    _save(fig, "mom_guarantee")


def draw_quickselect_invariant():
    """Честная симуляция трассировки из раздела 2.3: A = [3,1,4,1,5,9,2,6], k = 2.
    Пивоты выбираются как в тексте лекции: 4, затем 1, затем 2."""

    def lomuto(a, l, r):
        x = a[r]
        i = l - 1
        for j in range(l, r):
            if a[j] <= x:
                i += 1
                a[i], a[j] = a[j], a[i]
        a[i + 1], a[r] = a[r], a[i + 1]
        return i + 1

    A = [3, 1, 4, 1, 5, 9, 2, 6]
    k = 2
    pivot_values = [4, 1, 2]  # порядок пивотов из трассировки лекции
    n = len(A)

    l, r = 0, n - 1
    rows = [(A.copy(), l, r, None,
             "старт: кандидаты — весь массив, ищем позицию k = 2")]
    for pv in pivot_values:
        idx = next(i for i in range(l, r + 1) if A[i] == pv)
        A[idx], A[r] = A[r], A[idx]
        p = lomuto(A, l, r)
        if p == k:
            note = f"пивот {pv} встал на p = {p} = k — ответ: A[{p}] = {A[p]}"
        elif p > k:
            note = f"пивот {pv} встал на p = {p} > k — отбрасываем [{p}..{r}]"
        else:
            note = f"пивот {pv} встал на p = {p} < k — отбрасываем [{l}..{p}]"
        rows.append((A.copy(), l, r, p, note))
        if p == k:
            break
        if p > k:
            r = p - 1
        else:
            l = p + 1

    cell_w, cell_h, row_gap = 1.0, 0.7, 0.6
    fig, ax = plt.subplots(figsize=(12.5, 5.6))
    _apply_style(fig, [ax])
    ax.axis("off")

    for row, (arr, li, ri, p, note) in enumerate(rows):
        y = -row * (cell_h + row_gap)
        for idx, val in enumerate(arr):
            if p is not None and idx == p:
                color = C_GREEN if p == k else C_ORANGE
            elif li <= idx <= ri:
                color = C_BLUE
            else:
                color = C_GRAY
            ax.add_patch(mpatches.Rectangle((idx * cell_w, y), cell_w * 0.92, cell_h,
                                            facecolor=color, edgecolor=C_INK, lw=1.1))
            ax.text(idx * cell_w + cell_w * 0.46, y + cell_h / 2, str(val),
                    ha="center", va="center", fontsize=11.5,
                    color="white", fontweight="bold")
        ax.text(n * cell_w + 0.25, y + cell_h / 2, note,
                ha="left", va="center", fontsize=10, color=C_INK)

    # пунктирная вертикаль на позиции k
    y_top = cell_h + 0.12
    y_bot = -(len(rows) - 1) * (cell_h + row_gap) - 0.35
    ax.plot([k * cell_w + cell_w * 0.46] * 2, [y_top, y_bot],
            color=C_INK, lw=1.2, linestyle=":", zorder=1)
    ax.text(k * cell_w + cell_w * 0.46, y_bot - 0.12, "k = 2",
            ha="center", va="top", fontsize=10.5, color=C_INK, fontweight="bold")

    legend_items = [
        mpatches.Patch(facecolor=C_BLUE, edgecolor=C_INK,
                       label="текущий отрезок [l..r] — будущие позиции l..r"),
        mpatches.Patch(facecolor=C_ORANGE, edgecolor=C_INK,
                       label="пивот на окончательном месте p"),
        mpatches.Patch(facecolor=C_GRAY, edgecolor=C_INK, label="отброшено навсегда"),
        mpatches.Patch(facecolor=C_GREEN, edgecolor=C_INK, label="ответ (p = k)"),
    ]
    ax.legend(handles=legend_items, loc="lower left", bbox_to_anchor=(0.0, -0.28),
              fontsize=9, ncol=2, framealpha=0.9, facecolor=C_BG, edgecolor=C_GRAY)

    ax.set_xlim(-0.3, n * cell_w + 6.4)
    ax.set_ylim(y_bot - 0.55, cell_h + 0.45)
    ax.set_title("Инвариант Quick-Select: отрезок кандидатов всегда накрывает позицию k\n"
                 "(A = [3, 1, 4, 1, 5, 9, 2, 6], ищем k = 2 — третий наименьший)",
                 fontsize=12, color=C_INK, fontweight="bold", pad=10)
    plt.tight_layout()
    _save(fig, "quickselect_invariant")


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_quickselect()
    draw_median_of_medians()
    draw_quickselect_recursion()
    draw_mom_guarantee()
    draw_quickselect_invariant()
    print("All visuals generated successfully.")


if __name__ == "__main__":
    main()
