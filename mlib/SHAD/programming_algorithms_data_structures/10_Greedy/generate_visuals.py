"""Точные схемы для лекции 10: Жадные алгоритмы."""
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
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)
    print(f"Saved: {path}")


# ── 1. Interval Scheduling ────────────────────────────────────────────────────

def draw_interval_scheduling() -> None:
    """Timeline 0-10. Intervals as horizontal bars, selected green, rejected gray."""
    # Intervals: (start, end, label)
    intervals = [
        (1, 3, "[1,3]", True),
        (2, 5, "[2,5]", False),
        (3, 6, "[3,6]", True),
        (5, 7, "[5,7]", False),
        (6, 8, "[6,8]", True),
    ]

    fig, ax = plt.subplots(figsize=(12, 5))
    _apply_style(fig)
    ax.set_facecolor(C_BG)

    y_positions = list(range(len(intervals)))
    bar_height = 0.5

    for idx, (start, end, label, selected) in enumerate(intervals):
        color = C_GREEN if selected else C_GRAY
        edge = C_INK
        rect = mpatches.Rectangle(
            (start, idx - bar_height / 2),
            end - start,
            bar_height,
            linewidth=1.5,
            edgecolor=edge,
            facecolor=color,
            alpha=0.85,
            zorder=3,
        )
        ax.add_patch(rect)
        # Label inside bar
        ax.text(
            (start + end) / 2, idx,
            label,
            ha="center", va="center",
            fontsize=9, color=C_INK, fontweight="bold",
            zorder=4,
        )
        # Finish-time marker
        if selected:
            ax.axvline(x=end, color=C_GREEN, linewidth=1.0, linestyle="--",
                       alpha=0.5, zorder=2)

    # Sort order annotation
    ax.text(0.5, 4.75,
            "Сортировка по финишу: [1,3] → [2,5] → [3,6] → [5,7] → [6,8]",
            fontsize=8.5, color=C_INK, style="italic",
            ha="left", va="top")

    # Timeline axis
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.8, 5.4)
    ax.set_xticks(range(0, 11))
    ax.set_xticklabels([str(i) for i in range(0, 11)], fontsize=9, color=C_INK)
    ax.set_yticks(y_positions)
    ax.set_yticklabels([iv[2] for iv in intervals], fontsize=9, color=C_INK)
    ax.tick_params(colors=C_INK, left=True, bottom=True)
    ax.set_xlabel("Время", fontsize=10, color=C_INK)
    ax.set_title(
        "Interval Scheduling: жадный выбор по времени окончания",
        fontsize=11, color=C_INK, pad=10,
    )
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(C_GRAY)
    ax.spines["bottom"].set_color(C_GRAY)

    # Legend
    legend_items = [
        mpatches.Patch(facecolor=C_GREEN, edgecolor=C_INK, label="Выбранные интервалы"),
        mpatches.Patch(facecolor=C_GRAY, edgecolor=C_INK, label="Отвергнутые (пересечение)"),
    ]
    ax.legend(handles=legend_items, loc="upper right", fontsize=9,
              framealpha=0.85, facecolor=C_BG)

    fig.tight_layout()
    _save(fig, "interval_scheduling")


# ── 2. Huffman Tree ───────────────────────────────────────────────────────────

def draw_huffman_tree() -> None:
    """Three panels: initial heap, after 2 merges, final Huffman tree."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 7))
    _apply_style(fig)

    titles = [
        "Шаг 0: начальная куча",
        "Шаги 1-2: слияния",
        "Итоговое дерево",
    ]

    def draw_node(ax, x, y, label, freq, color, radius=0.35):
        circ = mpatches.Circle((x, y), radius, linewidth=1.5,
                                edgecolor=C_INK, facecolor=color, zorder=3)
        ax.add_patch(circ)
        ax.text(x, y + 0.08, label, ha="center", va="center",
                fontsize=9, fontweight="bold", color=C_INK, zorder=4)
        ax.text(x, y - 0.18, str(freq), ha="center", va="center",
                fontsize=8, color=C_INK, zorder=4)

    def draw_edge(ax, x0, y0, x1, y1):
        ax.plot([x0, x1], [y0, y1], color=C_GRAY, linewidth=1.5, zorder=2)

    # ── Panel 0: initial heap ─────────────────────────────────────────────────
    ax0 = axes[0]
    ax0.set_facecolor(C_BG)
    ax0.set_xlim(0, 10)
    ax0.set_ylim(0, 5)
    ax0.axis("off")
    ax0.set_title(titles[0], fontsize=10, color=C_INK, pad=8)

    heap_nodes = [("C", 1), ("B", 2), ("D", 3), ("A", 5)]
    x_positions = [2.0, 4.0, 6.0, 8.0]
    colors_heap = [C_ORANGE, C_BLUE, C_PANEL, C_PANEL]

    for (sym, freq), xp, col in zip(heap_nodes, x_positions, colors_heap):
        draw_node(ax0, xp, 2.5, sym, freq, col)

    ax0.text(5.0, 1.2, "min-heap: C:1 ≤ B:2 ≤ D:3 ≤ A:5",
             ha="center", va="center", fontsize=8, color=C_INK,
             style="italic")
    ax0.text(2.0, 0.7, "Извлечём\nC и B", ha="center", va="center",
             fontsize=7.5, color=C_ORANGE)
    # Arrows under C and B
    ax0.annotate("", xy=(3.0, 1.8), xytext=(2.0, 2.1),
                 arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=1.2))
    ax0.annotate("", xy=(3.0, 1.8), xytext=(4.0, 2.1),
                 arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=1.2))

    # ── Panel 1: after 2 merges ───────────────────────────────────────────────
    ax1 = axes[1]
    ax1.set_facecolor(C_BG)
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 6)
    ax1.axis("off")
    ax1.set_title(titles[1], fontsize=10, color=C_INK, pad=8)

    # After merge 1: N1=C+B (freq 3), D:3, A:5
    # Show N1 node with children C and B
    draw_node(ax1, 5.0, 4.5, "N1", 3, C_BLUE)
    draw_node(ax1, 3.5, 3.0, "C", 1, C_ORANGE)
    draw_node(ax1, 6.5, 3.0, "B", 2, C_ORANGE)
    draw_edge(ax1, 5.0, 4.15, 3.5, 3.35)
    draw_edge(ax1, 5.0, 4.15, 6.5, 3.35)

    # D and A as siblings
    draw_node(ax1, 2.0, 4.5, "D", 3, C_PANEL)
    draw_node(ax1, 8.0, 4.5, "A", 5, C_PANEL)

    ax1.text(5.0, 1.8,
             "После шага 1:\nКуча = {D:3, N1:3, A:5}",
             ha="center", va="center", fontsize=8, color=C_INK)

    # After merge 2: N2=D+N1 (freq 6), A:5 — indicate next merge
    ax1.annotate("", xy=(3.5, 1.3), xytext=(2.0, 4.15),
                 arrowprops=dict(arrowstyle="->", color=C_BLUE,
                                 lw=1.2, connectionstyle="arc3,rad=0.3"))
    ax1.annotate("", xy=(4.5, 1.3), xytext=(5.0, 4.15),
                 arrowprops=dict(arrowstyle="->", color=C_BLUE,
                                 lw=1.2, connectionstyle="arc3,rad=-0.2"))
    ax1.text(4.0, 1.0, "Следующий: D + N1 → N2:6",
             ha="center", va="center", fontsize=7.5, color=C_BLUE,
             style="italic")

    # ── Panel 2: final tree ───────────────────────────────────────────────────
    ax2 = axes[2]
    ax2.set_facecolor(C_BG)
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 7)
    ax2.axis("off")
    ax2.set_title(titles[2], fontsize=10, color=C_INK, pad=8)

    # Tree structure:
    #        N3:11
    #       /      \
    #     A:5      N2:6
    #             /    \
    #           D:3   N1:3
    #                 /   \
    #               C:1   B:2
    draw_node(ax2, 5.0, 6.0, "N3", 11, C_PANEL, radius=0.38)
    draw_node(ax2, 2.5, 4.5, "A", 5, C_GREEN, radius=0.38)
    draw_node(ax2, 7.5, 4.5, "N2", 6, C_PANEL, radius=0.38)
    draw_node(ax2, 5.5, 3.0, "D", 3, C_GREEN, radius=0.38)
    draw_node(ax2, 9.0, 3.0, "N1", 3, C_PANEL, radius=0.38)
    draw_node(ax2, 7.5, 1.5, "C", 1, C_GREEN, radius=0.38)
    draw_node(ax2, 9.5, 1.5, "B", 2, C_GREEN, radius=0.38)  # narrower space

    draw_edge(ax2, 5.0, 5.62, 2.5, 4.88)
    draw_edge(ax2, 5.0, 5.62, 7.5, 4.88)
    draw_edge(ax2, 7.5, 4.12, 5.5, 3.38)
    draw_edge(ax2, 7.5, 4.12, 9.0, 3.38)
    draw_edge(ax2, 9.0, 2.62, 7.5, 1.88)
    draw_edge(ax2, 9.0, 2.62, 9.5, 1.88)

    # Edge labels (0/1)
    def edge_label(ax, x, y, text, color=C_GRAY):
        ax.text(x, y, text, ha="center", va="center",
                fontsize=8, color=color, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.15", facecolor=C_BG,
                          edgecolor="none", alpha=0.8))

    edge_label(ax2, 3.3, 5.35, "0")
    edge_label(ax2, 6.6, 5.35, "1")
    edge_label(ax2, 6.3, 3.85, "0")
    edge_label(ax2, 8.5, 3.85, "1")
    edge_label(ax2, 8.1, 2.3, "0")
    edge_label(ax2, 9.5, 2.3, "1")

    # Code table
    codes = [("A", "0", "1"), ("D", "10", "2"), ("C", "110", "3"), ("B", "111", "3")]
    table_x = 0.5
    table_y = 5.8
    ax2.text(table_x, table_y, "Символ  Код   Глуб.",
             fontsize=7.5, color=C_INK, fontfamily="monospace")
    for i, (sym, code, depth) in enumerate(codes):
        ax2.text(table_x, table_y - 0.45 * (i + 1),
                 f"   {sym}    {code:<5} {depth}",
                 fontsize=7.5, color=C_INK, fontfamily="monospace")

    fig.suptitle("Построение дерева Хаффмана: {A:5, B:2, C:1, D:3}",
                 fontsize=11, color=C_INK, y=1.01)
    fig.tight_layout()
    _save(fig, "huffman_tree")


# ── 3. Greedy vs DP (Coin Change) ─────────────────────────────────────────────

def draw_greedy_vs_dp() -> None:
    """Side-by-side: coin change {1,3,4}, amount=6. Greedy (orange) vs DP (green)."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    _apply_style(fig)

    def draw_path(ax, nodes, edges, colors, title, subtitle, coin_labels):
        ax.set_facecolor(C_BG)
        ax.set_xlim(-0.5, len(nodes) - 0.5)
        ax.set_ylim(-1.2, 2.5)
        ax.axis("off")
        ax.set_title(title, fontsize=11, color=C_INK, pad=8, fontweight="bold")

        node_radius = 0.32
        for i, (val, col) in enumerate(zip(nodes, colors)):
            circ = mpatches.Circle((i, 1.0), node_radius, linewidth=1.8,
                                   edgecolor=C_INK, facecolor=col, zorder=3)
            ax.add_patch(circ)
            ax.text(i, 1.0, str(val), ha="center", va="center",
                    fontsize=13, fontweight="bold", color=C_INK, zorder=4)

        for src, dst, lbl, col in edges:
            ax.annotate(
                "", xy=(dst, 1.0 - node_radius), xytext=(src, 1.0 - node_radius),
                arrowprops=dict(arrowstyle="->", color=col, lw=2.0,
                                connectionstyle="arc3,rad=-0.35"),
            )
            mid_x = (src + dst) / 2
            ax.text(mid_x, 0.28, f"−{lbl}", ha="center", va="center",
                    fontsize=9, color=col, fontweight="bold")

        ax.text(
            (len(nodes) - 1) / 2, 2.2, subtitle,
            ha="center", va="center", fontsize=9.5, color=C_INK,
            style="italic",
        )

        # Coin labels below nodes
        for i, cl in enumerate(coin_labels):
            if cl:
                ax.text(i, -0.55, cl, ha="center", va="center",
                        fontsize=8, color=C_GRAY)

    # Left: greedy — 6 -> 2 -> 1 -> 0 (coins: 4, 1, 1)
    draw_path(
        axes[0],
        nodes=[6, 2, 1, 0],
        edges=[(0, 1, "4", C_ORANGE), (1, 2, "1", C_ORANGE), (2, 3, "1", C_ORANGE)],
        colors=[C_PANEL, C_PANEL, C_PANEL, C_ORANGE],
        title="Жадный алгоритм",
        subtitle="3 монеты: 4 + 1 + 1 = 6  (не оптимум!)",
        coin_labels=["Сумма=6", "", "", "0"],
    )

    # Right: DP optimal — 6 -> 3 -> 0 (coins: 3, 3)
    draw_path(
        axes[1],
        nodes=[6, 3, 0],
        edges=[(0, 1, "3", C_GREEN), (1, 2, "3", C_GREEN)],
        colors=[C_PANEL, C_PANEL, C_GREEN],
        title="Оптимум (DP)",
        subtitle="2 монеты: 3 + 3 = 6  (оптимум!)",
        coin_labels=["Сумма=6", "", "0"],
    )

    # Common annotation
    fig.text(0.5, -0.04,
             "Монеты: {1, 3, 4}, сумма = 6. Жадность берёт монету 4 (наибольшая ≤ 6),\n"
             "но упускает оптимальную пару 3+3. DP находит глобальный минимум.",
             ha="center", fontsize=9, color=C_INK, style="italic")

    # Coin legend
    legend_items = [
        mpatches.Patch(facecolor=C_ORANGE, edgecolor=C_INK, label="Жадный путь (3 монеты)"),
        mpatches.Patch(facecolor=C_GREEN, edgecolor=C_INK, label="DP-оптимум (2 монеты)"),
    ]
    fig.legend(handles=legend_items, loc="upper center", ncol=2,
               fontsize=9, framealpha=0.85, facecolor=C_BG,
               bbox_to_anchor=(0.5, 1.02))

    fig.suptitle("Задача о сдаче монетами: жадность vs динамическое программирование",
                 fontsize=12, color=C_INK, y=1.06)

    # Add comparison box
    ax_left = axes[0]
    result_box_x = np.array([0.05, 0.95, 0.95, 0.05, 0.05])
    result_box_y = np.array([-0.85, -0.85, -1.1, -1.1, -0.85])
    ax_left.fill(result_box_x * 3, result_box_y, color=C_ORANGE, alpha=0.15)
    ax_left.text(1.5, -0.97, "Жадность: 3 монеты  СУБОПТИМАЛЬНО",
                 ha="center", va="center", fontsize=8.5,
                 color=C_ORANGE, fontweight="bold")

    ax_right = axes[1]
    ax_right.fill(np.array([0.05, 0.95, 0.95, 0.05, 0.05]) * 2,
                  result_box_y, color=C_GREEN, alpha=0.15)
    ax_right.text(1.0, -0.97, "DP: 2 монеты  ОПТИМАЛЬНО",
                  ha="center", va="center", fontsize=8.5,
                  color=C_GREEN, fontweight="bold")

    fig.tight_layout()
    _save(fig, "greedy_vs_dp")


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    draw_interval_scheduling()
    draw_huffman_tree()
    draw_greedy_vs_dp()
    print("All visuals generated.")


if __name__ == "__main__":
    main()
