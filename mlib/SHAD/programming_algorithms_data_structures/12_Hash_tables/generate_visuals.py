from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

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
        "figure.facecolor":  C_BG,
        "axes.facecolor":    C_BG,
        "axes.edgecolor":    C_INK,
        "axes.labelcolor":   C_INK,
        "text.color":        C_INK,
        "xtick.color":       C_INK,
        "ytick.color":       C_INK,
        "font.family":       "sans-serif",
        "font.size":         11,
    })


def _save(fig, name):
    ASSETS.mkdir(parents=True, exist_ok=True)
    path = ASSETS / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)
    print(f"Saved: {path}")


def draw_chaining():
    """Hash table with m=7 slots and chaining. Keys: {10, 22, 4, 15, 28, 17}."""
    m = 7
    # Compute chains: h(k) = k mod 7
    keys = [10, 22, 4, 15, 28, 17]
    chains = {i: [] for i in range(m)}
    for k in keys:
        chains[k % m].append(k)

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.set_xlim(-0.5, 9)
    ax.set_ylim(-0.5, m + 0.5)
    ax.axis("off")
    ax.set_facecolor(C_BG)
    fig.patch.set_facecolor(C_BG)

    slot_w = 1.2
    slot_h = 0.7
    slot_x = 0.3

    for slot in range(m):
        y = m - 1 - slot
        # Draw slot box
        rect = mpatches.FancyBboxPatch(
            (slot_x, y - slot_h / 2), slot_w, slot_h,
            boxstyle="round,pad=0.05",
            facecolor=C_PANEL, edgecolor=C_INK, linewidth=1.2
        )
        ax.add_patch(rect)
        ax.text(slot_x + slot_w / 2, y, str(slot),
                ha="center", va="center", fontsize=12, color=C_INK, fontweight="bold")

        # Draw chain elements
        chain = chains[slot]
        node_x = slot_x + slot_w + 0.15
        node_w = 0.9
        for idx, key in enumerate(chain):
            # Arrow from previous
            if idx == 0:
                ax.annotate("", xy=(node_x, y), xytext=(slot_x + slot_w, y),
                            arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=1.5))
            else:
                prev_x = slot_x + slot_w + 0.15 + (idx - 1) * (node_w + 0.35) + node_w
                ax.annotate("", xy=(node_x + (idx) * (node_w + 0.35), y),
                            xytext=(prev_x, y),
                            arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=1.5))
            nx = slot_x + slot_w + 0.15 + idx * (node_w + 0.35)
            node_rect = mpatches.FancyBboxPatch(
                (nx, y - slot_h / 2), node_w, slot_h,
                boxstyle="round,pad=0.05",
                facecolor=C_BLUE, edgecolor=C_INK, linewidth=1.2, alpha=0.85
            )
            ax.add_patch(node_rect)
            ax.text(nx + node_w / 2, y, str(key),
                    ha="center", va="center", fontsize=11, color="white", fontweight="bold")

        if not chain:
            # NULL marker
            ax.annotate("", xy=(slot_x + slot_w + 0.5, y), xytext=(slot_x + slot_w, y),
                        arrowprops=dict(arrowstyle="->", color=C_GRAY, lw=1.2))
            ax.text(slot_x + slot_w + 0.55, y, "∅",
                    ha="left", va="center", fontsize=13, color=C_GRAY)

    alpha = len(keys) / m
    ax.text(0.02, 0.02,
            f"m = {m} слотов   |   n = {len(keys)} ключей   |   α = n/m = {alpha:.2f}",
            transform=ax.transAxes,
            fontsize=11, color=C_INK,
            bbox=dict(boxstyle="round,pad=0.3", facecolor=C_PANEL, edgecolor=C_GRAY))

    ax.set_title("Хеш-таблица с цепочками: h(k) = k mod 7", fontsize=13,
                 color=C_INK, pad=10)

    # Legend
    blue_patch  = mpatches.Patch(color=C_BLUE,  label="Ключи в цепочках")
    panel_patch = mpatches.Patch(facecolor=C_PANEL, edgecolor=C_INK, label="Слоты таблицы")
    ax.legend(handles=[panel_patch, blue_patch], loc="upper right",
              framealpha=0.9, facecolor=C_BG, edgecolor=C_GRAY, fontsize=10)

    _save(fig, "chaining")


def draw_load_factor():
    """Expected chain length vs load factor alpha."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_facecolor(C_BG)
    fig.patch.set_facecolor(C_BG)

    alphas = [x / 100.0 for x in range(0, 201)]
    chain_lengths = alphas  # E[L] = alpha

    ax.plot(alphas, chain_lengths, color=C_ORANGE, linewidth=2.5, label="E[длина цепочки] = α")

    # Mark alpha = 0.75
    ax.axvline(x=0.75, color=C_BLUE, linestyle="--", linewidth=1.8, label="α = 0.75 (типичный порог)")
    ax.plot(0.75, 0.75, "o", color=C_BLUE, markersize=8, zorder=5)
    ax.text(0.75 + 0.04, 0.75 + 0.08, "0.75", color=C_BLUE, fontsize=11, fontweight="bold")

    # Mark alpha = 1.0
    ax.axvline(x=1.0, color=C_GREEN, linestyle="--", linewidth=1.8, label="α = 1.0")
    ax.plot(1.0, 1.0, "o", color=C_GREEN, markersize=8, zorder=5)
    ax.text(1.0 + 0.04, 1.0 + 0.08, "1.0", color=C_GREEN, fontsize=11, fontweight="bold")

    ax.set_xlabel("Коэффициент загрузки α = n/m", fontsize=12, color=C_INK)
    ax.set_ylabel("Ожидаемая длина цепочки", fontsize=12, color=C_INK)
    ax.set_title("Ожидаемая длина цепочки при SUHA", fontsize=13, color=C_INK)
    ax.legend(fontsize=10, framealpha=0.9, facecolor=C_BG, edgecolor=C_GRAY)

    ax.set_xlim(0, 2)
    ax.set_ylim(0, 2)
    ax.grid(True, color=C_GRAY, alpha=0.4, linestyle=":")
    ax.tick_params(colors=C_INK)
    for spine in ax.spines.values():
        spine.set_edgecolor(C_INK)

    # Shade good region (alpha < 0.75)
    ax.axvspan(0, 0.75, alpha=0.08, color=C_GREEN, label="Хорошая зона")
    ax.axvspan(0.75, 2.0, alpha=0.06, color=C_ORANGE, label="Зона замедления")

    _save(fig, "load_factor")


def draw_open_addressing():
    """Array of 8 slots showing linear probing insertion with collision chain."""
    m = 8
    # Inserting keys: 3, 11, 19 — all hash to slot 3 (mod 8)
    # Linear probing: 3->3, 11->3(busy)->4, 19->3(busy)->4(busy)->5
    keys = [3, 11, 19]
    slot_assignments = [3, 4, 5]  # where each key lands

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.set_xlim(-0.5, m + 2)
    ax.set_ylim(-2.5, 3)
    ax.axis("off")
    ax.set_facecolor(C_BG)
    fig.patch.set_facecolor(C_BG)

    cell_w = 1.1
    cell_h = 0.75
    base_y = 1.0
    start_x = 0.2

    # Draw table cells
    for i in range(m):
        x = start_x + i * cell_w
        color = C_PANEL
        for j, slot in enumerate(slot_assignments):
            if slot == i:
                color = [C_BLUE, C_GREEN, C_ORANGE][j]
                break
        rect = mpatches.FancyBboxPatch(
            (x, base_y - cell_h / 2), cell_w - 0.08, cell_h,
            boxstyle="round,pad=0.04",
            facecolor=color, edgecolor=C_INK, linewidth=1.2,
            alpha=0.85
        )
        ax.add_patch(rect)

        # Index label below
        ax.text(x + (cell_w - 0.08) / 2, base_y - cell_h / 2 - 0.22,
                str(i), ha="center", va="top", fontsize=10, color=C_GRAY)

        # Content label
        label = ""
        for j, slot in enumerate(slot_assignments):
            if slot == i:
                label = str(keys[j])
                break
        if label:
            ax.text(x + (cell_w - 0.08) / 2, base_y,
                    label, ha="center", va="center", fontsize=12,
                    color="white", fontweight="bold")
        else:
            ax.text(x + (cell_w - 0.08) / 2, base_y,
                    "—", ha="center", va="center", fontsize=12, color=C_GRAY)

    # Draw probe arrows for key 11: tries slot 3, goes to slot 4
    def arrow(x1, y1, x2, y2, color, label=""):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=color, lw=1.8,
                                   connectionstyle="arc3,rad=-0.3"))
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + 0.4
            ax.text(mx, my, label, ha="center", va="bottom", fontsize=9, color=color)

    # Key 3: goes directly to slot 3
    x3 = start_x + 3 * cell_w + (cell_w - 0.08) / 2
    ax.annotate("", xy=(x3, base_y + cell_h / 2),
                xytext=(x3, base_y + 1.3),
                arrowprops=dict(arrowstyle="->", color=C_BLUE, lw=2.0))
    ax.text(x3, base_y + 1.5, f"k=3\nh(3)=3", ha="center", va="bottom",
            fontsize=9.5, color=C_BLUE, fontweight="bold")

    # Key 11: tries slot 3 (busy) -> slot 4
    x11_src = start_x + 3 * cell_w + (cell_w - 0.08) / 2 - 0.15
    x11_dst = start_x + 4 * cell_w + (cell_w - 0.08) / 2
    ax.annotate("", xy=(x11_src, base_y + cell_h / 2 + 0.05),
                xytext=(x11_src, base_y + 2.0),
                arrowprops=dict(arrowstyle="->", color=C_GREEN, lw=1.6, linestyle="dashed"))
    ax.annotate("", xy=(x11_dst, base_y + cell_h / 2),
                xytext=(x11_dst, base_y + 2.0),
                arrowprops=dict(arrowstyle="->", color=C_GREEN, lw=1.6))
    ax.annotate("", xy=(x11_dst - 0.1, base_y + 2.0),
                xytext=(x11_src + 0.15, base_y + 2.0),
                arrowprops=dict(arrowstyle="->", color=C_GREEN, lw=1.4))
    ax.text((x11_src + x11_dst) / 2, base_y + 2.25,
            "k=11, h(11)=3 занят → 4", ha="center", va="bottom",
            fontsize=9.5, color=C_GREEN, fontweight="bold")

    # Key 19: tries slot 3 (busy) -> slot 4 (busy) -> slot 5
    x19_src = start_x + 3 * cell_w + (cell_w - 0.08) / 2 + 0.15
    x19_mid = start_x + 4 * cell_w + (cell_w - 0.08) / 2 + 0.1
    x19_dst = start_x + 5 * cell_w + (cell_w - 0.08) / 2
    ax.annotate("", xy=(x19_src, base_y - cell_h / 2),
                xytext=(x19_src, base_y - 1.6),
                arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=1.6, linestyle="dashed"))
    ax.annotate("", xy=(x19_mid, base_y - cell_h / 2 - 0.05),
                xytext=(x19_mid, base_y - 1.6),
                arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=1.6, linestyle="dashed"))
    ax.annotate("", xy=(x19_dst, base_y - cell_h / 2),
                xytext=(x19_dst, base_y - 1.6),
                arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=1.6))
    ax.annotate("", xy=(x19_mid - 0.1, base_y - 1.6),
                xytext=(x19_src + 0.15, base_y - 1.6),
                arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=1.4))
    ax.annotate("", xy=(x19_dst - 0.1, base_y - 1.6),
                xytext=(x19_mid + 0.1, base_y - 1.6),
                arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=1.4))
    ax.text((x19_src + x19_dst) / 2 - 0.1, base_y - 1.9,
            "k=19, h(19)=3 занят → 4 занят → 5",
            ha="center", va="top", fontsize=9.5, color=C_ORANGE, fontweight="bold")

    # Cluster highlight
    cx = start_x + 3 * cell_w - 0.05
    cw = 3 * cell_w + 0.05
    cluster_rect = mpatches.FancyBboxPatch(
        (cx, base_y - cell_h / 2 - 0.08), cw, cell_h + 0.16,
        boxstyle="round,pad=0.08",
        facecolor="none", edgecolor=C_ORANGE, linewidth=2.5, linestyle="--"
    )
    ax.add_patch(cluster_rect)
    ax.text(cx + cw / 2, base_y - cell_h / 2 - 0.42,
            "кластер (primary clustering)",
            ha="center", va="top", fontsize=9, color=C_ORANGE, style="italic")

    ax.set_title("Открытая адресация: линейное зондирование, h(k) = k mod 8",
                 fontsize=12, color=C_INK, pad=8)

    # Legend
    blue_patch   = mpatches.Patch(color=C_BLUE,   label="k=3 (прямое попадание)")
    green_patch  = mpatches.Patch(color=C_GREEN,  label="k=11 (1 проверка)")
    orange_patch = mpatches.Patch(color=C_ORANGE, label="k=19 (2 проверки)")
    ax.legend(handles=[blue_patch, green_patch, orange_patch],
              loc="upper right", fontsize=9.5,
              framealpha=0.9, facecolor=C_BG, edgecolor=C_GRAY)

    _save(fig, "open_addressing")


def main():
    _apply_style()
    draw_chaining()
    draw_load_factor()
    draw_open_addressing()


if __name__ == "__main__":
    main()
