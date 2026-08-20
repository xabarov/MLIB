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


def _apply_style(fig) -> None:
    fig.patch.set_facecolor(C_BG)


def _save(fig, name: str) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    path = ASSETS / f"{name}.png"
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)
    print(f"Saved: {path}")


# ── 1. Merge sort tree ────────────────────────────────────────────────────────

def draw_merge_sort_tree() -> None:
    """Recursion tree for [5, 3, 8, 1, 4, 2]: split phase then merge phase."""
    fig, ax = plt.subplots(figsize=(14, 8))
    _apply_style(fig)
    ax.set_facecolor(C_BG)
    ax.axis("off")
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)

    # Each level: list of (label, x_center, y_center, color)
    BOX_W = 1.7
    BOX_H = 0.45
    FONT_SZ = 8

    levels = [
        # level 0 — root (split)
        [("[5,3,8,1,4,2]", 7.0, 7.3, C_PANEL)],
        # level 1 — split
        [("[5,3,8]", 3.5, 6.2, C_PANEL), ("[1,4,2]", 10.5, 6.2, C_PANEL)],
        # level 2 — split
        [("[5,3]", 1.8, 5.1, C_PANEL), ("[8]", 5.2, 5.1, C_GRAY),
         ("[1,4]", 8.8, 5.1, C_PANEL), ("[2]", 12.2, 5.1, C_GRAY)],
        # level 3 — leaves
        [("[5]", 0.9, 4.0, C_GRAY), ("[3]", 2.7, 4.0, C_GRAY),
         ("[1]", 7.9, 4.0, C_GRAY), ("[4]", 9.7, 4.0, C_GRAY)],
        # level 4 — merge results (bottom-up)
        [("[3,5]", 1.8, 2.9, C_BLUE), ("[1,4]", 8.8, 2.9, C_BLUE)],
        # level 5 — merge results
        [("[3,5,8]", 3.5, 1.8, C_BLUE), ("[1,2,4]", 10.5, 1.8, C_BLUE)],
        # level 6 — final
        [("[1,2,3,4,5,8]", 7.0, 0.7, C_GREEN)],
    ]

    # Draw boxes and labels
    for level in levels:
        for label, xc, yc, color in level:
            rect = mpatches.Rectangle(
                (xc - BOX_W / 2, yc - BOX_H / 2),
                BOX_W, BOX_H,
                linewidth=1.2,
                edgecolor=C_INK,
                facecolor=color,
            )
            ax.add_patch(rect)
            ax.text(
                xc, yc, label,
                ha="center", va="center",
                fontsize=FONT_SZ, color=C_INK,
                fontfamily="monospace",
            )

    # Edges (parent -> child) — split phase
    split_edges = [
        # root -> level1
        ((7.0, 7.3 - BOX_H / 2), (3.5, 6.2 + BOX_H / 2)),
        ((7.0, 7.3 - BOX_H / 2), (10.5, 6.2 + BOX_H / 2)),
        # level1 -> level2
        ((3.5, 6.2 - BOX_H / 2), (1.8, 5.1 + BOX_H / 2)),
        ((3.5, 6.2 - BOX_H / 2), (5.2, 5.1 + BOX_H / 2)),
        ((10.5, 6.2 - BOX_H / 2), (8.8, 5.1 + BOX_H / 2)),
        ((10.5, 6.2 - BOX_H / 2), (12.2, 5.1 + BOX_H / 2)),
        # level2 -> level3
        ((1.8, 5.1 - BOX_H / 2), (0.9, 4.0 + BOX_H / 2)),
        ((1.8, 5.1 - BOX_H / 2), (2.7, 4.0 + BOX_H / 2)),
        ((8.8, 5.1 - BOX_H / 2), (7.9, 4.0 + BOX_H / 2)),
        ((8.8, 5.1 - BOX_H / 2), (9.7, 4.0 + BOX_H / 2)),
    ]
    for (x0, y0), (x1, y1) in split_edges:
        ax.annotate(
            "", xy=(x1, y1), xytext=(x0, y0),
            arrowprops=dict(arrowstyle="-", color=C_GRAY, lw=1.2),
        )

    # Edges — merge phase (bottom-up arrows)
    merge_edges = [
        # leaves -> merge level 4
        ((0.9, 4.0 - BOX_H / 2), (1.8, 2.9 + BOX_H / 2)),
        ((2.7, 4.0 - BOX_H / 2), (1.8, 2.9 + BOX_H / 2)),
        ((7.9, 4.0 - BOX_H / 2), (8.8, 2.9 + BOX_H / 2)),
        ((9.7, 4.0 - BOX_H / 2), (8.8, 2.9 + BOX_H / 2)),
        # [8] -> merge [3,5,8]
        ((5.2, 5.1 - BOX_H / 2), (3.5, 1.8 + BOX_H / 2)),
        # [2] -> merge [1,2,4]
        ((12.2, 5.1 - BOX_H / 2), (10.5, 1.8 + BOX_H / 2)),
        # level4 -> level5
        ((1.8, 2.9 - BOX_H / 2), (3.5, 1.8 + BOX_H / 2)),
        ((8.8, 2.9 - BOX_H / 2), (10.5, 1.8 + BOX_H / 2)),
        # level5 -> final
        ((3.5, 1.8 - BOX_H / 2), (7.0, 0.7 + BOX_H / 2)),
        ((10.5, 1.8 - BOX_H / 2), (7.0, 0.7 + BOX_H / 2)),
    ]
    for (x0, y0), (x1, y1) in merge_edges:
        ax.annotate(
            "", xy=(x1, y1), xytext=(x0, y0),
            arrowprops=dict(arrowstyle="->", color=C_BLUE, lw=1.2),
        )

    # Legend
    legend_items = [
        mpatches.Patch(facecolor=C_PANEL, edgecolor=C_INK, label="Разделение"),
        mpatches.Patch(facecolor=C_GRAY, edgecolor=C_INK, label="Базовый случай"),
        mpatches.Patch(facecolor=C_BLUE, edgecolor=C_INK, label="Слияние"),
        mpatches.Patch(facecolor=C_GREEN, edgecolor=C_INK, label="Результат"),
    ]
    ax.legend(handles=legend_items, loc="lower right", fontsize=8,
              framealpha=0.8, facecolor=C_BG)

    ax.set_title("Дерево рекурсии сортировки слиянием: [5, 3, 8, 1, 4, 2]",
                 fontsize=11, color=C_INK, pad=10)

    _save(fig, "merge_sort_tree")


# ── 2. Quicksort Lomuto partition ─────────────────────────────────────────────

def draw_quicksort_partition() -> None:
    """Array [3,6,8,10,1,2,1] before and after Lomuto partition with pivot=1."""
    fig, axes = plt.subplots(2, 1, figsize=(12, 5))
    _apply_style(fig)

    original = [3, 6, 8, 10, 1, 2, 1]
    partitioned = [1, 1, 8, 10, 3, 2, 6]  # after partition, pivot at index 1
    pivot_final_idx = 1

    titles = [
        "До разбиения: [3, 6, 8, 10, 1, 2, 1]  (pivot = 1, выделен оранжевым)",
        "После разбиения Ломуто  (pivot на позиции 1)",
    ]

    for ax_idx, (arr, title) in enumerate(zip([original, partitioned], titles)):
        ax = axes[ax_idx]
        ax.set_facecolor(C_BG)
        ax.axis("off")
        ax.set_xlim(-0.5, len(arr) - 0.5)
        ax.set_ylim(-0.6, 1.2)
        ax.set_title(title, fontsize=9, color=C_INK, pad=4)

        for idx, val in enumerate(arr):
            if ax_idx == 0:
                # Before: last element is pivot (orange)
                color = C_ORANGE if idx == len(arr) - 1 else C_PANEL
            else:
                # After: left partition green, pivot orange, right gray
                if idx < pivot_final_idx:
                    color = C_GREEN
                elif idx == pivot_final_idx:
                    color = C_ORANGE
                else:
                    color = C_GRAY

            rect = mpatches.Rectangle(
                (idx - 0.45, 0.05), 0.9, 0.7,
                linewidth=1.2, edgecolor=C_INK, facecolor=color,
            )
            ax.add_patch(rect)
            ax.text(idx, 0.4, str(val),
                    ha="center", va="center", fontsize=13,
                    fontweight="bold", color=C_INK)
            # index label below
            ax.text(idx, -0.15, str(idx),
                    ha="center", va="center", fontsize=8, color=C_GRAY)

        if ax_idx == 1:
            # Labels for sections
            ax.text(-0.1, 1.05, "все ≤ pivot",
                    ha="center", va="bottom", fontsize=8, color=C_GREEN)
            ax.text(pivot_final_idx, 1.05, "pivot",
                    ha="center", va="bottom", fontsize=8, color=C_ORANGE,
                    fontweight="bold")
            ax.text(4.5, 1.05, "все > pivot",
                    ha="center", va="bottom", fontsize=8, color=C_GRAY)

    # Legend for bottom plot
    legend_items = [
        mpatches.Patch(facecolor=C_GREEN, edgecolor=C_INK, label="Левый подмассив (≤ pivot)"),
        mpatches.Patch(facecolor=C_ORANGE, edgecolor=C_INK, label="Pivot"),
        mpatches.Patch(facecolor=C_GRAY, edgecolor=C_INK, label="Правый подмассив (> pivot)"),
    ]
    fig.legend(handles=legend_items, loc="lower center", ncol=3,
               fontsize=8, framealpha=0.8, facecolor=C_BG,
               bbox_to_anchor=(0.5, -0.02))

    fig.suptitle("Разбиение Ломуто: [3, 6, 8, 10, 1, 2, 1]",
                 fontsize=12, color=C_INK, y=1.01)
    fig.tight_layout()
    _save(fig, "quicksort_partition")


# ── 3. Sorting comparison chart ───────────────────────────────────────────────

def draw_sorting_comparison() -> None:
    """Grouped horizontal bar chart: 4 algorithms × 3 complexity cases."""
    algorithms = ["Пузырёк", "Вставки", "Слияние", "Быстрая"]
    cases = ["Лучшее", "Среднее", "Худшее"]
    # Values: 0 = O(n), 1 = O(n log n), 2 = O(n^2)
    data = np.array([
        [0, 2, 2],  # Bubble: best O(n), avg O(n^2), worst O(n^2)
        [0, 2, 2],  # Insertion: best O(n), avg O(n^2), worst O(n^2)
        [1, 1, 1],  # Merge: all O(n log n)
        [1, 1, 2],  # Quick: best/avg O(n log n), worst O(n^2)
    ])

    tick_labels = ["O(n)", "O(n log n)", "O(n²)"]
    colors = [C_GREEN, C_BLUE, C_ORANGE]
    n_alg = len(algorithms)
    n_cases = len(cases)
    bar_h = 0.22
    group_gap = 0.1

    fig, ax = plt.subplots(figsize=(10, 5))
    _apply_style(fig)
    ax.set_facecolor(C_BG)

    y_centers = np.arange(n_alg)

    for case_idx in range(n_cases):
        offsets = (case_idx - (n_cases - 1) / 2) * (bar_h + 0.03)
        y_positions = y_centers + offsets
        values = data[:, case_idx]
        ax.barh(
            y_positions, values + 0.05,  # small offset so O(n) bars are visible
            height=bar_h,
            color=colors[case_idx],
            alpha=0.88,
            label=cases[case_idx],
            edgecolor=C_INK,
            linewidth=0.7,
        )
        # Text labels inside bars
        for yi, val in zip(y_positions, values):
            ax.text(
                val / 2 + 0.025, yi, tick_labels[val],
                ha="center", va="center",
                fontsize=8, color=C_INK, fontweight="bold",
            )

    ax.set_yticks(y_centers)
    ax.set_yticklabels(algorithms, fontsize=11, color=C_INK)
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(tick_labels, fontsize=9, color=C_INK)
    ax.set_xlim(-0.1, 2.5)
    ax.tick_params(colors=C_INK)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(C_GRAY)
    ax.spines["bottom"].set_color(C_GRAY)
    ax.set_xlabel("Временная сложность", fontsize=10, color=C_INK)
    ax.set_title("Сравнение алгоритмов сортировки по временной сложности",
                 fontsize=11, color=C_INK, pad=12)

    # Stable/Memory annotations on the right
    props = [
        "Стаб. O(1)", "Стаб. O(1)",
        "Стаб. O(n)", "Нестаб. O(log n)",
    ]
    for yi, prop in zip(y_centers, props):
        ax.text(2.55, float(yi), prop, va="center", fontsize=7.5,
                color=C_GRAY, style="italic")

    ax.legend(loc="lower right", fontsize=9, framealpha=0.8, facecolor=C_BG)

    _ = group_gap  # consumed by layout intent; silence linter
    fig.tight_layout()
    _save(fig, "sorting_comparison")


# ── 4. Decision tree for sorting three elements ──────────────────────────────

def draw_decision_tree() -> None:
    """Decision tree for sorting three elements a, b, c: 6 leaves, height 3."""
    fig, ax = plt.subplots(figsize=(12, 6.5))
    _apply_style(fig)
    ax.set_facecolor(C_BG)
    ax.axis("off")
    ax.set_xlim(0, 12.8)
    ax.set_ylim(0.6, 7.2)

    # name: (x, y, label, is_leaf)
    nodes = {
        "root": (6.0, 6.6, "a ≤ b ?", False),
        "L":    (3.0, 5.0, "b ≤ c ?", False),
        "R":    (9.0, 5.0, "a ≤ c ?", False),
        "LL":   (1.4, 3.4, "a ≤ b ≤ c", True),
        "LR":   (4.6, 3.4, "a ≤ c ?", False),
        "RL":   (7.4, 3.4, "b ≤ a ≤ c", True),
        "RR":   (10.6, 3.4, "b ≤ c ?", False),
        "LRL":  (3.5, 1.8, "a ≤ c ≤ b", True),
        "LRR":  (5.7, 1.8, "c ≤ a ≤ b", True),
        "RRL":  (9.5, 1.8, "b ≤ c ≤ a", True),
        "RRR":  (11.6, 1.8, "c ≤ b ≤ a", True),
    }
    edges = [
        ("root", "L", "да"), ("root", "R", "нет"),
        ("L", "LL", "да"), ("L", "LR", "нет"),
        ("R", "RL", "да"), ("R", "RR", "нет"),
        ("LR", "LRL", "да"), ("LR", "LRR", "нет"),
        ("RR", "RRL", "да"), ("RR", "RRR", "нет"),
    ]

    BOX_W, BOX_H = 1.9, 0.6

    for parent, child, lab in edges:
        x0, y0 = nodes[parent][0], nodes[parent][1] - BOX_H / 2
        x1, y1 = nodes[child][0], nodes[child][1] + BOX_H / 2
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="-", color=C_GRAY, lw=1.2))
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        ax.text(mx, my, lab, ha="center", va="center", fontsize=8,
                color=C_GREEN if lab == "да" else C_ORANGE,
                fontstyle="italic",
                bbox=dict(boxstyle="round,pad=0.12", facecolor=C_BG,
                          edgecolor="none"))

    for _, (xc, yc, label, is_leaf) in nodes.items():
        rect = mpatches.FancyBboxPatch(
            (xc - BOX_W / 2, yc - BOX_H / 2), BOX_W, BOX_H,
            boxstyle="round,pad=0.03",
            linewidth=1.2, edgecolor=C_INK,
            facecolor=C_GREEN if is_leaf else C_PANEL,
        )
        ax.add_patch(rect)
        ax.text(xc, yc, label, ha="center", va="center",
                fontsize=9, color=C_BG if is_leaf else C_INK,
                fontweight="bold" if is_leaf else "normal",
                fontfamily="monospace")

    legend_items = [
        mpatches.Patch(facecolor=C_PANEL, edgecolor=C_INK,
                       label="Сравнение (внутренний узел)"),
        mpatches.Patch(facecolor=C_GREEN, edgecolor=C_INK,
                       label="Итоговый порядок (лист)"),
    ]
    ax.legend(handles=legend_items, loc="lower left", fontsize=8,
              framealpha=0.8, facecolor=C_BG)

    ax.set_title("Дерево решений для сортировки трёх элементов: "
                 "3! = 6 листьев,  высота 3 ≥ log₂6 ≈ 2.58",
                 fontsize=11, color=C_INK, pad=10)
    _save(fig, "decision_tree_3")


# ── 5. Lomuto invariant trace ─────────────────────────────────────────────────

def draw_lomuto_invariant() -> None:
    """Честная симуляция разбиения Ломуто на [3, 6, 8, 10, 1, 2, 1] (pivot = 1):
    состояние блоков инварианта после каждой итерации j."""
    a = [3, 6, 8, 10, 1, 2, 1]
    n = len(a)
    hi = n - 1
    pivot = a[hi]

    # (копия массива, i, последний обработанный j, подпись, финальное состояние?)
    states = []
    i = -1
    states.append((a.copy(), i, -1, "старт: оба блока пусты, i = −1", False))
    for j in range(hi):
        old = a[j]
        if a[j] <= pivot:
            i += 1
            a[i], a[j] = a[j], a[i]
            note = f"j={j}: a[j]={old} ≤ {pivot} → ++i, swap(a[{i}], a[{j}])"
        else:
            note = f"j={j}: a[j]={old} > {pivot} → блок «больших» растёт"
        states.append((a.copy(), i, j, note, False))
    a[i + 1], a[hi] = a[hi], a[i + 1]
    states.append((a.copy(), i, hi,
                   f"финал: swap(a[{i + 1}], a[{hi}]) — pivot на месте {i + 1}", True))

    cell_w, cell_h, row_gap = 1.0, 0.7, 0.55
    fig, ax = plt.subplots(figsize=(12.5, 9.2))
    _apply_style(fig)
    ax.set_facecolor(C_BG)
    ax.axis("off")

    for row, (arr, ii, j, note, final) in enumerate(states):
        y = -row * (cell_h + row_gap)
        for idx, val in enumerate(arr):
            if final:
                if idx <= ii:
                    color = C_GREEN
                elif idx == ii + 1:
                    color = C_ORANGE
                else:
                    color = C_GRAY
            else:
                if idx == hi:
                    color = C_ORANGE
                elif idx <= ii:
                    color = C_GREEN
                elif idx <= j:
                    color = C_GRAY
                else:
                    color = C_PANEL
            txt_color = C_INK if color == C_PANEL else "white"
            ax.add_patch(mpatches.Rectangle((idx * cell_w, y), cell_w * 0.92, cell_h,
                                            facecolor=color, edgecolor=C_INK, lw=1.1))
            ax.text(idx * cell_w + cell_w * 0.46, y + cell_h / 2, str(val),
                    ha="center", va="center", fontsize=11.5,
                    color=txt_color, fontweight="bold")
        # маркеры i и j под строкой
        if not final:
            if ii >= 0:
                ax.text(ii * cell_w + cell_w * 0.46, y - 0.1, "i",
                        ha="center", va="top", fontsize=9.5,
                        color=C_GREEN, fontweight="bold")
            if 0 <= j < hi:
                ax.text(j * cell_w + cell_w * 0.46, y - 0.1, "j",
                        ha="center", va="top", fontsize=9.5,
                        color=C_INK, fontweight="bold")
        ax.text(n * cell_w + 0.25, y + cell_h / 2, note,
                ha="left", va="center", fontsize=10, color=C_INK)

    legend_items = [
        mpatches.Patch(facecolor=C_GREEN, edgecolor=C_INK, label="блок «≤ pivot»  (a[lo..i])"),
        mpatches.Patch(facecolor=C_GRAY, edgecolor=C_INK, label="блок «> pivot»  (a[i+1..j])"),
        mpatches.Patch(facecolor=C_PANEL, edgecolor=C_INK, label="ещё не просмотрено"),
        mpatches.Patch(facecolor=C_ORANGE, edgecolor=C_INK, label="pivot"),
    ]
    ax.legend(handles=legend_items, loc="lower left", bbox_to_anchor=(0.0, -0.02),
              fontsize=9.5, ncol=2, framealpha=0.9, facecolor=C_BG, edgecolor=C_GRAY)

    total_h = len(states) * (cell_h + row_gap)
    ax.set_xlim(-0.3, n * cell_w + 6.8)
    ax.set_ylim(-total_h + row_gap - 1.3, cell_h + 0.5)
    ax.set_title("Инвариант Ломуто на [3, 6, 8, 10, 1, 2, 1], pivot = 1:\n"
                 "просмотренная часть — всегда блок «≤ pivot» + блок «> pivot»",
                 fontsize=12.5, color=C_INK, pad=12)
    _save(fig, "lomuto_invariant")


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    draw_merge_sort_tree()
    draw_quicksort_partition()
    draw_sorting_comparison()
    draw_decision_tree()
    draw_lomuto_invariant()
    print("All visuals generated.")


if __name__ == "__main__":
    main()
