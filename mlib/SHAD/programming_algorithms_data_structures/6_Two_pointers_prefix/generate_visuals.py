from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
C_BG = "#faf9f5"
C_INK = "#141413"
C_GRAY = "#b0aea5"
C_PANEL = "#e8e6dc"
C_ORANGE = "#d97757"
C_BLUE = "#6a9bcc"
C_GREEN = "#788c5d"

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)


def _apply_style(fig, ax_list):
    fig.patch.set_facecolor(C_BG)
    for ax in ax_list:
        ax.set_facecolor(C_BG)
        ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        for spine in ax.spines.values():
            spine.set_visible(False)


def _save(fig, name: str):
    path = ASSETS / f"{name}.png"
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)
    print(f"Saved: {path}")


# ---------------------------------------------------------------------------
# Visual 1: Two Pointers — three steps of convergence
# ---------------------------------------------------------------------------
def draw_two_pointers():
    arr = [1, 2, 3, 4, 5, 6, 7, 8]
    n = len(arr)
    target = 11

    # Steps: (l, r, label)
    steps = [
        (0, 7, f"A[0]+A[7] = {arr[0]}+{arr[7]} = {arr[0]+arr[7]} < {target}  →  l++"),
        (1, 7, f"A[1]+A[7] = {arr[1]}+{arr[7]} = {arr[1]+arr[7]} < {target}  →  l++"),
        (2, 7, f"A[2]+A[7] = {arr[2]}+{arr[7]} = {arr[2]+arr[7]} = {target}  →  найдено!"),
    ]

    cell_w = 0.9
    cell_h = 0.7
    fig, axes = plt.subplots(len(steps), 1, figsize=(10, 5))
    _apply_style(fig, axes)

    fig.suptitle(f"Метод двух указателей: поиск пары с суммой {target}",
                 fontsize=13, color=C_INK, fontweight="bold", y=1.01)

    for _, (ax, (l, r, label)) in enumerate(zip(axes, steps)):
        ax.set_xlim(-0.5, n * cell_w + 0.5)
        ax.set_ylim(-0.6, cell_h + 0.6)
        ax.set_aspect("equal")

        for i, val in enumerate(arr):
            x = i * cell_w
            # cell colour
            if i == l:
                fc = C_ORANGE
            elif i == r:
                fc = C_BLUE
            else:
                fc = C_PANEL
            rect = mpatches.Rectangle((x, 0), cell_w * 0.92, cell_h,
                                       facecolor=fc, edgecolor=C_GRAY,
                                       linewidth=0.8, zorder=2)
            ax.add_patch(rect)
            ax.text(x + cell_w * 0.46, cell_h / 2, str(val),
                    ha="center", va="center", fontsize=11,
                    color=C_BG if i in (l, r) else C_INK, fontweight="bold")

        # arrows below cells
        ax.annotate("l", xy=(l * cell_w + cell_w * 0.46, 0),
                    xytext=(l * cell_w + cell_w * 0.46, -0.45),
                    ha="center", va="center", fontsize=10, color=C_ORANGE,
                    fontweight="bold",
                    arrowprops=dict(arrowstyle="-|>", color=C_ORANGE, lw=1.5))
        ax.annotate("r", xy=(r * cell_w + cell_w * 0.46, 0),
                    xytext=(r * cell_w + cell_w * 0.46, -0.45),
                    ha="center", va="center", fontsize=10, color=C_BLUE,
                    fontweight="bold",
                    arrowprops=dict(arrowstyle="-|>", color=C_BLUE, lw=1.5))

        ax.text(n * cell_w + 0.1, cell_h / 2, label,
                ha="left", va="center", fontsize=9, color=C_INK)

    plt.tight_layout()
    _save(fig, "two_pointers")


# ---------------------------------------------------------------------------
# Visual 2: Prefix Sums — A array, P array, and query bracket
# ---------------------------------------------------------------------------
def draw_prefix_sums():
    A = [3, 1, 4, 1, 5, 9]
    n = len(A)
    P = [0] * (n + 1)
    for i in range(n):
        P[i + 1] = P[i] + A[i]

    query_l, query_r = 1, 4  # sum A[1..4]

    cell_w = 1.0
    cell_h = 0.65
    fig, ax = plt.subplots(figsize=(10, 4))
    _apply_style(fig, [ax])
    ax.set_xlim(-0.8, (n + 1) * cell_w + 0.2)
    ax.set_ylim(-1.5, 3.2)

    # ----- Row 1: A array -----
    row_y_A = 2.0
    ax.text(-0.6, row_y_A + cell_h / 2, "A", ha="right", va="center",
            fontsize=12, color=C_INK, fontweight="bold")
    for i, val in enumerate(A):
        x = i * cell_w
        rect = mpatches.Rectangle((x, row_y_A), cell_w * 0.92, cell_h,
                                   facecolor=C_PANEL, edgecolor=C_GRAY,
                                   linewidth=0.8, zorder=2)
        ax.add_patch(rect)
        ax.text(x + cell_w * 0.46, row_y_A + cell_h / 2, str(val),
                ha="center", va="center", fontsize=11, color=C_INK)
        ax.text(x + cell_w * 0.46, row_y_A - 0.25, f"[{i}]",
                ha="center", va="center", fontsize=8, color=C_GRAY)

    # ----- Row 2: P array -----
    row_y_P = 0.8
    ax.text(-0.6, row_y_P + cell_h / 2, "P", ha="right", va="center",
            fontsize=12, color=C_INK, fontweight="bold")
    for i, val in enumerate(P):
        x = i * cell_w
        # highlight P[query_l] and P[query_r+1]
        if i == query_l:
            fc = C_ORANGE
            tc = C_BG
        elif i == query_r + 1:
            fc = C_GREEN
            tc = C_BG
        else:
            fc = C_PANEL
            tc = C_INK
        rect = mpatches.Rectangle((x, row_y_P), cell_w * 0.92, cell_h,
                                   facecolor=fc, edgecolor=C_GRAY,
                                   linewidth=0.8, zorder=2)
        ax.add_patch(rect)
        ax.text(x + cell_w * 0.46, row_y_P + cell_h / 2, str(val),
                ha="center", va="center", fontsize=11, color=tc,
                fontweight="bold" if i in (query_l, query_r + 1) else "normal")
        ax.text(x + cell_w * 0.46, row_y_P - 0.25, f"[{i}]",
                ha="center", va="center", fontsize=8, color=C_GRAY)

    # ----- Bracket showing the query -----
    bx_l = query_l * cell_w + cell_w * 0.46
    bx_r = (query_r + 1) * cell_w + cell_w * 0.46
    by = row_y_P - 0.8
    ax.annotate("", xy=(bx_r, by + 0.15), xytext=(bx_l, by + 0.15),
                arrowprops=dict(arrowstyle="<->", color=C_ORANGE, lw=1.5))
    mid = (bx_l + bx_r) / 2
    ax.text(mid, by - 0.2,
            f"sum[{query_l}..{query_r}] = P[{query_r+1}] − P[{query_l}] = "
            f"{P[query_r+1]} − {P[query_l]} = {P[query_r+1]-P[query_l]}",
            ha="center", va="center", fontsize=10, color=C_ORANGE)

    ax.set_title("Префиксные суммы: построение и запрос", fontsize=13,
                 color=C_INK, fontweight="bold", pad=10)
    plt.tight_layout()
    _save(fig, "prefix_sums")


# ---------------------------------------------------------------------------
# Visual 3: 2D Prefix Sums — original grid and prefix grid + query highlight
# ---------------------------------------------------------------------------
def draw_2d_prefix():
    A = np.array([
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
        [13, 14, 15, 16],
    ], dtype=int)
    n, m = A.shape
    P = np.zeros((n + 1, m + 1), dtype=int)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            P[i][j] = A[i-1][j-1] + P[i-1][j] + P[i][j-1] - P[i-1][j-1]

    # Query rectangle (0-indexed in A): rows 1-2, cols 1-2
    r1, c1, r2, c2 = 1, 1, 2, 2

    cell = 0.9
    gap = 1.5  # gap between two grids
    fig, ax = plt.subplots(figsize=(12, 5))
    _apply_style(fig, [ax])

    def draw_grid(ax, data, rows, cols, ox, oy, highlight=None, title=""):
        """Draw a grid of data starting at (ox, oy). highlight = (r1,c1,r2,c2)."""
        for i in range(rows):
            for j in range(cols):
                x = ox + j * cell
                y = oy - i * cell
                if highlight and highlight[0] <= i <= highlight[2] and highlight[1] <= j <= highlight[3]:
                    fc = C_ORANGE
                    tc = C_BG
                else:
                    fc = C_PANEL
                    tc = C_INK
                rect = mpatches.Rectangle((x, y - cell * 0.92), cell * 0.92, cell * 0.92,
                                           facecolor=fc, edgecolor=C_GRAY,
                                           linewidth=0.7, zorder=2)
                ax.add_patch(rect)
                ax.text(x + cell * 0.46, y - cell * 0.46,
                        str(data[i][j]),
                        ha="center", va="center", fontsize=9,
                        color=tc)
        ax.text(ox + cols * cell / 2, oy + 0.25, title,
                ha="center", va="bottom", fontsize=11, color=C_INK, fontweight="bold")

    total_w = m * cell + gap + (m + 1) * cell
    ax.set_xlim(-0.3, total_w + 0.3)
    ax.set_ylim(-(n + 1) * cell - 0.5, 0.7)

    # Left grid: A (n x m), query highlighted
    draw_grid(ax, A, n, m, ox=0.0, oy=0.0,
              highlight=(r1, c1, r2, c2), title="Матрица A (запрос выделен)")

    # Right grid: P ((n+1) x (m+1)), corresponding P cells highlighted
    draw_grid(ax, P, n + 1, m + 1, ox=m * cell + gap, oy=0.0,
              highlight=None, title="Префиксная матрица P")

    # Highlight the four P cells used in the formula
    ox2 = m * cell + gap
    formula_cells = [
        (r2 + 1, c2 + 1, C_GREEN),
        (r1,     c2 + 1, C_BLUE),
        (r2 + 1, c1,     C_BLUE),
        (r1,     c1,     C_ORANGE),
    ]
    for (pi, pj, color) in formula_cells:
        x = ox2 + pj * cell
        y = -pi * cell
        rect = mpatches.Rectangle((x, y - cell * 0.92), cell * 0.92, cell * 0.92,
                                   facecolor=color, edgecolor=C_GRAY,
                                   linewidth=1.2, zorder=3)
        ax.add_patch(rect)
        ax.text(x + cell * 0.46, y - cell * 0.46,
                str(P[pi][pj]),
                ha="center", va="center", fontsize=9, color=C_BG,
                fontweight="bold")

    # Formula annotation at the bottom
    result = P[r2+1][c2+1] - P[r1][c2+1] - P[r2+1][c1] + P[r1][c1]
    formula = (f"sum({r1},{c1}→{r2},{c2}) = "
               f"P[{r2+1}][{c2+1}] − P[{r1}][{c2+1}] − P[{r2+1}][{c1}] + P[{r1}][{c1}] = "
               f"{P[r2+1][c2+1]} − {P[r1][c2+1]} − {P[r2+1][c1]} + {P[r1][c1]} = {result}")
    ax.text(total_w / 2, -(n + 1) * cell - 0.1, formula,
            ha="center", va="top", fontsize=9, color=C_ORANGE)

    ax.set_title("Двумерные префиксные суммы", fontsize=13,
                 color=C_INK, fontweight="bold", pad=8)
    plt.tight_layout()
    _save(fig, "2d_prefix")


# ---------------------------------------------------------------------------
# Visual 4: Monotonic deque — sliding window minimum trace
# ---------------------------------------------------------------------------
def draw_monotonic_deque():
    A = [3, 1, 2, 5, 4]
    n = len(A)
    k = 3

    # Simulate and record state after each r
    steps = []  # (r, deque_indices, min_or_None, note)
    from collections import deque
    dq = deque()
    for r in range(n):
        note_parts = []
        while dq and dq[0] <= r - k:
            note_parts.append(f"индекс {dq[0]} вне окна → pop_front")
            dq.popleft()
        while dq and A[dq[-1]] >= A[r]:
            note_parts.append(f"A[{dq[-1]}]={A[dq[-1]]} ≥ A[{r}]={A[r]} → pop_back")
            dq.pop()
        dq.append(r)
        cur_min = A[dq[0]] if r >= k - 1 else None
        steps.append((r, list(dq), cur_min,
                      ";  ".join(note_parts) if note_parts else "просто push_back"))

    cell_w = 0.9
    cell_h = 0.62
    fig, axes = plt.subplots(n, 1, figsize=(11, 8.2))
    _apply_style(fig, axes)
    fig.suptitle(f"Монотонная дека: минимум в окне k = {k} для A = {A}",
                 fontsize=13, color=C_INK, fontweight="bold", y=1.0)

    for ax, (r, dq_state, cur_min, note) in zip(axes, steps):
        ax.set_xlim(-0.5, 13.5)
        ax.set_ylim(-0.75, cell_h + 0.75)
        ax.set_aspect("equal")

        win_l = max(0, r - k + 1)
        # --- array cells ---
        for i, val in enumerate(A):
            x = i * cell_w
            in_window = win_l <= i <= r
            if i == r:
                fc = C_ORANGE
            elif in_window:
                fc = C_PANEL
            else:
                fc = C_BG
            rect = mpatches.Rectangle((x, 0), cell_w * 0.92, cell_h,
                                      facecolor=fc,
                                      edgecolor=C_INK if in_window else C_GRAY,
                                      linewidth=1.2 if in_window else 0.8,
                                      zorder=2)
            ax.add_patch(rect)
            ax.text(x + cell_w * 0.46, cell_h / 2, str(val),
                    ha="center", va="center", fontsize=11,
                    color=C_BG if i == r else C_INK,
                    fontweight="bold" if in_window else "normal")
            ax.text(x + cell_w * 0.46, -0.25, f"[{i}]",
                    ha="center", va="center", fontsize=7, color=C_GRAY)

        ax.text(-0.4, cell_h / 2, f"r={r}", ha="right", va="center",
                fontsize=10, color=C_ORANGE, fontweight="bold")

        # --- deque contents ---
        dq_x0 = 5.6
        ax.text(dq_x0 - 0.15, cell_h / 2, "дека:", ha="right", va="center",
                fontsize=9, color=C_INK)
        for j, idx in enumerate(dq_state):
            x = dq_x0 + j * cell_w * 0.8
            is_front = (j == 0)
            rect = mpatches.Rectangle((x, 0.06), cell_w * 0.7, cell_h * 0.82,
                                      facecolor=C_GREEN if is_front and r >= k - 1 else C_BLUE,
                                      edgecolor=C_INK, linewidth=1.0, zorder=2)
            ax.add_patch(rect)
            ax.text(x + cell_w * 0.35, cell_h / 2, f"{A[idx]}",
                    ha="center", va="center", fontsize=10,
                    color=C_BG, fontweight="bold")
            ax.text(x + cell_w * 0.35, -0.25, f"[{idx}]",
                    ha="center", va="center", fontsize=7, color=C_GRAY)

        # --- min output ---
        min_x = 8.6
        if cur_min is not None:
            ax.text(min_x, cell_h / 2,
                    f"min окна [{win_l}..{r}] = {cur_min}",
                    ha="left", va="center", fontsize=9.5,
                    color=C_GREEN, fontweight="bold")
        else:
            ax.text(min_x, cell_h / 2, "окно ещё не заполнено",
                    ha="left", va="center", fontsize=9, color=C_GRAY,
                    style="italic")

        # --- note ---
        ax.text(min_x, -0.42, note, ha="left", va="center",
                fontsize=8, color=C_INK, style="italic")

    plt.tight_layout()
    _save(fig, "monotonic_deque")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    draw_two_pointers()
    draw_prefix_sums()
    draw_2d_prefix()
    draw_monotonic_deque()


if __name__ == "__main__":
    main()
