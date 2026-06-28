"""Точные схемы для лекции про линейный и бинарный поиск."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

C_BG    = "#faf9f5"
C_INK   = "#141413"
C_GRAY  = "#b0aea5"
C_PANEL = "#e8e6dc"
C_ORANGE = "#d97757"
C_BLUE  = "#6a9bcc"
C_GREEN = "#788c5d"


def _apply_style():
    plt.rcParams.update({
        "figure.facecolor": C_BG,
        "axes.facecolor": C_BG,
        "axes.edgecolor": C_GRAY,
        "axes.labelcolor": C_INK,
        "xtick.color": C_INK,
        "ytick.color": C_INK,
        "text.color": C_INK,
        "font.size": 11,
        "font.family": "sans-serif",
        "axes.spines.top": False,
        "axes.spines.right": False,
    })


def _save(fig, name):
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS / name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)
    print("Saved: assets/" + name)


def draw_binary_search():
    """
    Horizontal array of 8 elements. Show 3 iterations with lo/hi/mid pointers.
    Target = 7 found in step 3. Eliminated halves grayed out.
    Array: [1, 3, 5, 7, 9, 11, 13, 15]
    """
    _apply_style()

    values = [1, 3, 5, 7, 9, 11, 13, 15]
    n = len(values)

    # Iterations: (lo, hi, mid, description)
    # Step 1: lo=0, hi=8, mid=4, a[4]=9 > 7 => hi=4
    # Step 2: lo=0, hi=4, mid=2, a[2]=5 < 7 => lo=3
    # Step 3: lo=3, hi=4, mid=3, a[3]=7 == 7 => found
    iterations = [
        (0, 8, 4, "Шаг 1: a[4]=9 > 7 → hi=4"),
        (0, 4, 2, "Шаг 2: a[2]=5 < 7 → lo=3"),
        (3, 4, 3, "Шаг 3: a[3]=7 = 7 → найден!"),
    ]

    fig, axes = plt.subplots(3, 1, figsize=(10, 7))
    fig.patch.set_facecolor(C_BG)
    fig.suptitle("Бинарный поиск: target = 7 в [1,3,5,7,9,11,13,15]",
                 fontsize=13, color=C_INK, fontweight="bold", y=1.01)

    cell_w = 1.0
    cell_h = 0.6
    y0 = 0.5  # center y of cell row

    for row_idx, (ax, (lo, hi, mid, desc)) in enumerate(zip(axes, iterations)):
        ax.set_xlim(-0.2, n + 0.2)
        ax.set_ylim(-1.2, 1.8)
        ax.axis("off")
        ax.set_facecolor(C_BG)

        for i in range(n):
            # Determine color
            if i == mid:
                color = C_ORANGE  # mid element
            elif i < lo or i >= hi:
                color = C_PANEL   # eliminated (grayed out)
            else:
                color = C_BG      # active range

            rect = mpatches.Rectangle(
                (i, y0 - cell_h / 2), cell_w, cell_h,
                linewidth=1.5,
                edgecolor=C_GRAY if (i < lo or i >= hi) else C_INK,
                facecolor=color,
                zorder=2,
            )
            ax.add_patch(rect)

            # Value text
            txt_color = C_BG if i == mid else (C_GRAY if (i < lo or i >= hi) else C_INK)
            ax.text(i + 0.5, y0, str(values[i]),
                    ha="center", va="center", fontsize=12,
                    color=txt_color, fontweight="bold", zorder=3)

        # Pointer labels below cells
        arrow_y = y0 - cell_h / 2 - 0.15
        label_y = y0 - cell_h / 2 - 0.55

        # lo pointer
        ax.annotate("", xy=(lo + 0.5, y0 - cell_h / 2),
                    xytext=(lo + 0.5, arrow_y),
                    arrowprops=dict(arrowstyle="->", color=C_GREEN, lw=2),
                    zorder=4)
        ax.text(lo + 0.5, label_y, f"lo={lo}", ha="center", va="top",
                fontsize=9, color=C_GREEN, fontweight="bold")

        # hi pointer (points to position hi, which is outside array if hi==n)
        hi_x = min(hi, n - 1) + 0.5
        ax.annotate("", xy=(hi_x, y0 - cell_h / 2),
                    xytext=(hi_x, arrow_y),
                    arrowprops=dict(arrowstyle="->", color=C_BLUE, lw=2),
                    zorder=4)
        ax.text(hi_x, label_y, f"hi={hi}", ha="center", va="top",
                fontsize=9, color=C_BLUE, fontweight="bold")

        # mid pointer (above cells)
        ax.annotate("", xy=(mid + 0.5, y0 + cell_h / 2),
                    xytext=(mid + 0.5, y0 + cell_h / 2 + 0.4),
                    arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=2),
                    zorder=4)
        ax.text(mid + 0.5, y0 + cell_h / 2 + 0.55, f"mid={mid}",
                ha="center", va="bottom", fontsize=9,
                color=C_ORANGE, fontweight="bold")

        # Description
        ax.text(n / 2, 1.55, desc, ha="center", va="center",
                fontsize=10, color=C_INK,
                style="italic")

        # Index labels above cells (top row only)
        if row_idx == 0:
            for i in range(n):
                ax.text(i + 0.5, y0 + cell_h / 2 + 1.05, str(i),
                        ha="center", va="bottom", fontsize=8, color=C_GRAY)

    plt.tight_layout(h_pad=1.5)
    _save(fig, "binary_search_trace.png")


def draw_linear_vs_binary():
    """
    Two subplots side by side:
    Left: linear scan of 16 elements (all touched = orange).
    Right: binary search of 16 (only log2(16)=4 touched = orange, rest gray).
    """
    _apply_style()

    n = 16
    fig, (ax_lin, ax_bin) = plt.subplots(1, 2, figsize=(13, 4))
    fig.patch.set_facecolor(C_BG)
    fig.suptitle("Линейный O(n) vs Бинарный O(log n)  [n = 16]",
                 fontsize=14, color=C_INK, fontweight="bold")

    # Binary search: which indices are visited when searching for element at index 10
    # [1..16]: target = element at index 10
    # Step 1: mid=8 (lo=0,hi=16) → a[8] < target → lo=9
    # Step 2: mid=12 (lo=9,hi=16) → a[12] > target → hi=12
    # Step 3: mid=10 (lo=9,hi=12) → a[10] > target → hi=10
    # Step 4: mid=9 (lo=9,hi=10) → a[9] < target → lo=10 → lo==hi → done
    # So visited: 8, 12, 10, 9 — but let's use a cleaner example
    # Search for target at index 11 in array of size 16:
    # Step1: mid=8, a[8]<target → lo=9
    # Step2: mid=12, a[12]>target → hi=12
    # Step3: mid=10, a[10]<target → lo=11
    # Step4: mid=11, a[11]==target → found
    visited_binary = {8, 12, 10, 11}  # 4 = log2(16)

    cell_w = 0.8
    cell_h = 0.6
    gap = 0.1
    total_w = n * (cell_w + gap)
    y_center = 1.0

    for ax, title, mode in [
        (ax_lin, f"Линейный поиск\n{n} сравнений (все элементы)", "linear"),
        (ax_bin, f"Бинарный поиск\n{len(visited_binary)} сравнений (log₂ {n} = 4)", "binary"),
    ]:
        ax.set_facecolor(C_BG)
        ax.set_xlim(-0.5, total_w + 0.5)
        ax.set_ylim(-0.2, 2.5)
        ax.axis("off")
        ax.set_title(title, fontsize=11, color=C_INK, pad=8)

        for i in range(n):
            x = i * (cell_w + gap)

            if mode == "linear":
                face = C_ORANGE  # all touched
                edge = C_INK
                txt_color = C_BG
            else:
                if i in visited_binary:
                    face = C_ORANGE
                    edge = C_INK
                    txt_color = C_BG
                else:
                    face = C_PANEL
                    edge = C_GRAY
                    txt_color = C_GRAY

            rect = mpatches.Rectangle(
                (x, y_center - cell_h / 2), cell_w, cell_h,
                linewidth=1.2,
                edgecolor=edge,
                facecolor=face,
                zorder=2,
            )
            ax.add_patch(rect)

            ax.text(x + cell_w / 2, y_center, str(i),
                    ha="center", va="center", fontsize=8,
                    color=txt_color, fontweight="bold", zorder=3)

        # Legend
        touched_patch = mpatches.Patch(facecolor=C_ORANGE, edgecolor=C_INK, label="Проверен")
        skipped_patch = mpatches.Patch(facecolor=C_PANEL, edgecolor=C_GRAY, label="Пропущен")
        if mode == "linear":
            ax.legend(handles=[touched_patch], loc="upper right",
                      fontsize=9, framealpha=0)
        else:
            ax.legend(handles=[touched_patch, skipped_patch], loc="upper right",
                      fontsize=9, framealpha=0)

    plt.tight_layout()
    _save(fig, "linear_vs_binary.png")


def draw_monotone_predicate():
    """
    X-axis 0..20, y-axis 0/1 (False/True).
    Stepped function: False for x<12, True for x>=12.
    Vertical dashed line at x=12 (answer).
    Binary search interval [lo, hi] shown as colored bracket shrinking.
    """
    _apply_style()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_facecolor(C_BG)
    fig.patch.set_facecolor(C_BG)

    threshold = 12
    x_min, x_max = 0, 21

    # Step function
    xs_false = np.arange(0, threshold, 0.01)
    xs_true  = np.arange(threshold, x_max, 0.01)

    ax.plot(xs_false, np.zeros_like(xs_false), color=C_GRAY, lw=3, label="f(x) = False")
    ax.plot(xs_true,  np.ones_like(xs_true),  color=C_GREEN, lw=3, label="f(x) = True")

    # Jump at threshold
    ax.plot([threshold, threshold], [0, 1], color=C_INK, lw=1.5, linestyle="--", alpha=0.5)
    ax.axvline(x=threshold, color=C_ORANGE, lw=2, linestyle="--", zorder=5,
               label=f"Ответ: x = {threshold}")

    # Dots at boundary
    ax.plot(threshold - 1, 0, "o", color=C_GRAY, ms=8, zorder=6)
    ax.plot(threshold, 1, "o", color=C_GREEN, ms=8, zorder=6)

    # Shrinking intervals — simulated binary search on [0, 20]
    # Step 1: [0, 20], mid=10, f(10)=False → lo=11
    # Step 2: [11, 20], mid=15, f(15)=True → hi=15
    # Step 3: [11, 15], mid=13, f(13)=True → hi=13
    # Step 4: [11, 13], mid=12, f(12)=True → hi=12
    # Step 5: [11, 12], mid=11, f(11)=False → lo=12 → lo==hi → done
    intervals = [
        (0,  20, 10, 1),
        (11, 20, 15, 2),
        (11, 15, 13, 3),
        (11, 13, 12, 4),
    ]

    bracket_y_base = -0.25
    step_height    = 0.12
    colors_iter    = [C_BLUE, C_ORANGE, C_GREEN, C_INK]

    for (lo, hi, mid, step), color in zip(intervals, colors_iter):
        y = bracket_y_base - (step - 1) * step_height

        # Bracket
        ax.plot([lo, hi], [y, y], color=color, lw=2.5, zorder=4)
        ax.plot([lo, lo], [y - 0.02, y + 0.02], color=color, lw=2.5, zorder=4)
        ax.plot([hi, hi], [y - 0.02, y + 0.02], color=color, lw=2.5, zorder=4)

        # Mid marker
        ax.plot(mid, y, "|", ms=10, markeredgewidth=2.5, color=color, zorder=5)

        # Label
        ax.text(hi + 0.3, y, f"шаг {step}: [{lo},{hi}], mid={mid}",
                va="center", fontsize=8, color=color)

    ax.set_xlim(-1, x_max + 3)
    ax.set_ylim(-0.7, 1.4)
    ax.set_xlabel("x", fontsize=12)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["False", "True"], fontsize=11)
    ax.set_xticks(range(0, x_max, 2))
    ax.set_title("Бинарный поиск по ответу: монотонный предикат f(x)",
                 fontsize=13, color=C_INK, fontweight="bold", pad=10)
    ax.legend(loc="upper left", fontsize=10, framealpha=0)
    ax.spines["bottom"].set_color(C_GRAY)
    ax.spines["left"].set_color(C_GRAY)

    plt.tight_layout()
    _save(fig, "monotone_predicate.png")


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_binary_search()
    draw_linear_vs_binary()
    draw_monotone_predicate()
    print("All visuals generated successfully.")


if __name__ == "__main__":
    main()
