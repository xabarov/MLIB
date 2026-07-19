"""Точные схемы для лекции 1: основы языка программирования и анализ алгоритмов."""
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as ticker
import numpy as np

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

C_BG    = "#faf9f5"
C_INK   = "#141413"
C_GRAY  = "#b0aea5"
C_PANEL = "#e8e6dc"
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
        "axes.spines.top":  False,
        "axes.spines.right": False,
    })


def _save(fig, name: str):
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS / name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Диаграмма 1: Классы сложности — рост функций
# ---------------------------------------------------------------------------

def draw_complexity_classes():
    _apply_style()
    n = np.linspace(1, 20, 400)

    classes = [
        ("O(1)",       np.ones_like(n),              C_GREEN,  "-"),
        ("O(log n)",   np.log2(n),                   C_BLUE,   "-"),
        ("O(n)",       n,                             C_INK,    "-"),
        ("O(n log n)", n * np.log2(n),               C_ORANGE, "-"),
        ("O(n²)",      n ** 2,                        C_ORANGE, "--"),
        ("O(2ⁿ)",      np.minimum(2.0 ** n, 1.5e6),  C_GRAY,   ":"),
    ]

    fig, ax = plt.subplots(figsize=(9, 5))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)

    for label, y, color, ls in classes:
        lw = 2.2 if ls == "-" else 1.5
        ax.plot(n, y, label=label, color=color, linewidth=lw, linestyle=ls)

    ax.set_xlim(1, 20)
    ax.set_ylim(0, 500)
    ax.set_xlabel("n (размер входа)", fontsize=11)
    ax.set_ylabel("Число операций", fontsize=11)
    ax.set_title("Классы сложности: рост функций", fontsize=13, color=C_INK, pad=14)

    # Аннотации у правого края
    label_positions = {
        "O(1)":       (20.3,   1,    "left"),
        "O(log n)":   (20.3,  np.log2(20) + 0.5, "left"),
        "O(n)":       (20.3,  20,   "left"),
        "O(n log n)": (20.3,  20 * np.log2(20) + 5, "left"),
        "O(n²)":      (20.3, 400 + 10, "left"),
    }
    for label, y, color, ls in classes:
        if label in label_positions:
            xp, yp, ha = label_positions[label]
            ax.annotate(label, xy=(xp, yp), color=color,
                        fontsize=9.5, ha=ha, va="center",
                        annotation_clip=False)

    # O(2^n) — отдельная пометка
    ax.annotate("O(2ⁿ) →∞", xy=(14, 470), color=C_GRAY, fontsize=9,
                ha="center", va="bottom")

    ax.spines["left"].set_color(C_GRAY)
    ax.spines["bottom"].set_color(C_GRAY)
    ax.tick_params(axis="both", which="both", length=3, color=C_GRAY)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x)}"))

    fig.tight_layout()
    _save(fig, "complexity_classes.png")
    print("Saved: assets/complexity_classes.png")


# ---------------------------------------------------------------------------
# Диаграмма 2: Стек вызовов при рекурсии (factorial(4))
# ---------------------------------------------------------------------------

def draw_call_stack():
    _apply_style()

    frames = [
        ("factorial(4)", "ожидает factorial(3)"),
        ("factorial(3)", "ожидает factorial(2)"),
        ("factorial(2)", "ожидает factorial(1)"),
        ("factorial(1)", "ожидает factorial(0)"),
        ("factorial(0)", "возвращает 1"),
    ]

    fig, ax = plt.subplots(figsize=(7, 4.8))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.axis("off")

    n = len(frames)
    box_w, box_h = 5.0, 0.55
    gap = 0.12
    x0 = 1.0

    for i, (title, subtitle) in enumerate(reversed(frames)):
        y = i * (box_h + gap)
        is_top = (i == n - 1)

        rect_color = C_PANEL
        edge_color = C_ORANGE if is_top else C_BLUE

        rect = mpatches.Rectangle((x0, y), box_w, box_h,
                              facecolor=rect_color, edgecolor=edge_color,
                              linewidth=2 if is_top else 1.2)
        ax.add_patch(rect)

        ax.text(x0 + 0.18, y + box_h * 0.62, title,
                fontsize=10.5, color=C_INK, fontweight="bold" if is_top else "normal",
                va="center")
        ax.text(x0 + 0.18, y + box_h * 0.28, subtitle,
                fontsize=8.5, color=C_GRAY, va="center")

    # Стрелка «вершина стека»
    top_y = (n - 1) * (box_h + gap) + box_h
    ax.annotate("вершина стека",
                xy=(x0 + box_w, top_y - box_h / 2),
                xytext=(x0 + box_w + 0.3, top_y - box_h / 2),
                fontsize=9, color=C_ORANGE,
                arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=1.4),
                va="center")

    # Метка «дно стека»
    ax.text(x0 + box_w + 0.3, 0 + box_h / 2,
            "дно стека", fontsize=9, color=C_GRAY, va="center")

    total_h = n * (box_h + gap)
    ax.set_xlim(0, 9)
    ax.set_ylim(-0.2, total_h + 0.4)
    ax.set_title("Стек вызовов: factorial(4)", fontsize=12, color=C_INK, pad=10)

    fig.tight_layout()
    _save(fig, "call_stack_recursion.png")
    print("Saved: assets/call_stack_recursion.png")


# ---------------------------------------------------------------------------
# Диаграмма 3: Схема RAM-модели
# ---------------------------------------------------------------------------

def draw_ram_model():
    _apply_style()

    fig, ax = plt.subplots(figsize=(8, 3.8))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.axis("off")

    # Ячейки памяти
    cell_w, cell_h = 0.9, 0.7
    n_cells = 10
    y_mem = 1.8

    for i in range(n_cells):
        x = 0.3 + i * (cell_w + 0.05)
        color = C_ORANGE if i == 3 else C_PANEL
        rect = mpatches.Rectangle((x, y_mem), cell_w, cell_h,
                              facecolor=color, edgecolor=C_INK, linewidth=1)
        ax.add_patch(rect)
        val = ["…", 17, 0, 42, 8, 255, 1, 0, "…", "…"][i]
        ax.text(x + cell_w / 2, y_mem + cell_h / 2, str(val),
                ha="center", va="center", fontsize=9, color=C_INK)
        if i not in (0, 8, 9):
            ax.text(x + cell_w / 2, y_mem - 0.22, str(i),
                    ha="center", va="top", fontsize=7.5, color=C_GRAY)

    ax.text(0.3 + n_cells * (cell_w + 0.05) / 2, y_mem + cell_h + 0.25,
            "Память (ячейки)",
            ha="center", va="bottom", fontsize=10, color=C_INK, fontweight="bold")

    # Подпись «адрес» под подсвеченной ячейкой
    hi_x = 0.3 + 3 * (cell_w + 0.05) + cell_w / 2
    ax.annotate("A[3] = 42", xy=(hi_x, y_mem - 0.08),
                xytext=(hi_x, y_mem - 0.85),
                fontsize=8.5, color=C_ORANGE, ha="center",
                arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=1.2))

    # Процессор
    cpu_x, cpu_y, cpu_w, cpu_h = 3.5, 0.1, 2.4, 0.9
    ax.add_patch(mpatches.Rectangle((cpu_x, cpu_y), cpu_w, cpu_h,
                                facecolor=C_BLUE, edgecolor=C_INK,
                                linewidth=1.5, alpha=0.85))
    ax.text(cpu_x + cpu_w / 2, cpu_y + cpu_h / 2, "Процессор",
            ha="center", va="center", fontsize=10, color="white", fontweight="bold")

    # Стрелки процессор <-> память
    for direction in ("up", "down"):
        dx = 0.2 if direction == "down" else -0.2
        ax.annotate("", xy=(hi_x + dx, y_mem),
                    xytext=(cpu_x + cpu_w / 2 + dx, cpu_y + cpu_h),
                    arrowprops=dict(arrowstyle="->", color=C_GRAY, lw=1.3))

    ax.text(cpu_x + cpu_w / 2 + 0.6, (y_mem + cpu_y + cpu_h) / 2,
            "чтение / запись\nO(1)",
            fontsize=8, color=C_GRAY, ha="left", va="center")

    ax.set_xlim(0, 10.5)
    ax.set_ylim(-0.1, 3.2)
    ax.set_title("RAM-модель вычислений", fontsize=12, color=C_INK, pad=10)

    fig.tight_layout()
    _save(fig, "ram_model.png")
    print("Saved: assets/ram_model.png")


# ---------------------------------------------------------------------------
# Диаграмма 4: Формальное определение O-нотации (f(n) <= C·g(n) при n >= n0)
# ---------------------------------------------------------------------------

def draw_big_o_definition():
    _apply_style()

    n = np.linspace(0.5, 14, 400)
    f = 3 * n**2 + 5 * n + 7          # f(n)
    cg = 4 * n**2                      # C·g(n) при C = 4
    n0 = 7                             # 4n^2 >= 3n^2+5n+7 при n >= 6.15, берём n0 = 7

    fig, ax = plt.subplots(figsize=(9, 5))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)

    ax.plot(n, f, color=C_ORANGE, lw=2.4, label=r"$f(n) = 3n^2 + 5n + 7$")
    ax.plot(n, cg, color=C_BLUE, lw=2.4, label=r"$C \cdot g(n) = 4n^2$")
    ax.plot(n, n**2, color=C_GRAY, lw=1.4, linestyle="--", label=r"$g(n) = n^2$")

    # Вертикальная линия n0 и заливка «рабочей зоны»
    ax.axvline(x=n0, color=C_INK, lw=1.3, linestyle=":")
    ax.text(n0 + 0.15, 30, r"$n_0 = 7$", fontsize=11, color=C_INK)
    mask = n >= n0
    ax.fill_between(n[mask], f[mask], cg[mask], color=C_GREEN, alpha=0.25,
                    label=r"здесь $f(n) \leq C\,g(n)$")

    # Пометка зоны, где неравенство ещё может нарушаться
    ax.annotate("при малых n\nнеравенство не обязано\nвыполняться",
                xy=(2.6, 3 * 2.6**2 + 5 * 2.6 + 7), xytext=(0.8, 320),
                fontsize=9, color=C_GRAY,
                arrowprops=dict(arrowstyle="->", color=C_GRAY, lw=1.2))

    ax.set_xlim(0, 14)
    ax.set_ylim(0, 800)
    ax.set_xlabel("n", fontsize=11)
    ax.set_ylabel("значение функции", fontsize=11)
    ax.set_title(r"Определение $f(n) = O(g(n))$: начиная с $n_0$ график $C \cdot g(n)$ идёт выше $f(n)$",
                 fontsize=12, color=C_INK, pad=12)
    ax.legend(loc="upper left", fontsize=10, framealpha=0)
    ax.spines["left"].set_color(C_GRAY)
    ax.spines["bottom"].set_color(C_GRAY)

    fig.tight_layout()
    _save(fig, "big_o_definition.png")
    print("Saved: assets/big_o_definition.png")


# ---------------------------------------------------------------------------
# Диаграмма 5: Ханойские башни — рекурсивный план (3 шага)
# ---------------------------------------------------------------------------

DISK_COLORS = [C_ORANGE, C_BLUE, C_GREEN, C_GRAY]


def _draw_hanoi_state(ax, pegs, n_disks, highlight=None):
    """Рисует одно состояние: pegs — список из трёх списков дисков (снизу вверх).

    Диск задаётся числом 1..n (1 — самый маленький). highlight — диск,
    который выделить свечением на этом кадре.
    """
    peg_x = [1.0, 3.0, 5.0]
    disk_h = 0.42
    max_w = 1.6
    min_w = 0.55

    ax.set_xlim(0, 6)
    ax.set_ylim(-0.35, n_disks * disk_h + 1.15)
    ax.axis("off")

    ax.add_patch(mpatches.Rectangle((0.2, -0.3), 5.6, 0.3,
                                    facecolor=C_PANEL, edgecolor=C_INK, lw=1.2))
    for x, label in zip(peg_x, "ABC"):
        ax.plot([x, x], [0, n_disks * disk_h + 0.75], color=C_INK, lw=2.2,
                solid_capstyle="round", zorder=1)
        ax.text(x, -0.62, label, ha="center", va="top", fontsize=13,
                fontweight="bold")

    for pi, stack in enumerate(pegs):
        for level, disk in enumerate(stack):
            w = min_w + (max_w - min_w) * (disk - 1) / max(n_disks - 1, 1)
            y = level * disk_h
            is_hl = (disk == highlight)
            color = DISK_COLORS[(disk - 1) % len(DISK_COLORS)]
            ax.add_patch(mpatches.FancyBboxPatch(
                (peg_x[pi] - w / 2, y + 0.04), w, disk_h - 0.10,
                boxstyle="round,pad=0.02,rounding_size=0.08",
                facecolor=color, edgecolor=C_INK,
                lw=2.6 if is_hl else 1.3, zorder=3))


def draw_hanoi_plan():
    """Три шага рекурсивного плана hanoi(n): n-1 наверх, большой диск, n-1 обратно."""
    _apply_style()
    n = 4
    fig, axes = plt.subplots(1, 4, figsize=(13.6, 3.4))

    states = [
        ([list(range(n, 0, -1)), [], []], None,
         "Исходно: башня из n дисков на A"),
        ([[n], list(range(n - 1, 0, -1)), []], None,
         "Шаг 1. hanoi(n−1, A→B):\nверхние n−1 дисков паркуются на B"),
        ([[], list(range(n - 1, 0, -1)), [n]], n,
         "Шаг 2. Один ход:\nсамый большой диск A→C"),
        ([[], [], list(range(n, 0, -1))], None,
         "Шаг 3. hanoi(n−1, B→C):\nn−1 дисков переезжают на большой"),
    ]
    for ax, (pegs, hl, title) in zip(axes, states):
        _draw_hanoi_state(ax, pegs, n, highlight=hl)
        ax.set_title(title, fontsize=10.5, pad=10)

    fig.suptitle("Рекурсивный план Ханойских башен: два «доверенных» подвызова и один свой ход",
                 fontsize=13, y=1.06)
    fig.tight_layout()
    _save(fig, "hanoi_plan.png")
    print("Saved: assets/hanoi_plan.png")


# ---------------------------------------------------------------------------
# Диаграмма 6: Ханойские башни — полная трассировка n = 3 (7 ходов)
# ---------------------------------------------------------------------------

def draw_hanoi_trace():
    """Все 8 состояний решения для n=3; фазы раскрашены по уровню рекурсии."""
    _apply_style()
    n = 3

    # Симуляция hanoi(3, A, C, B): список ходов (диск, откуда, куда)
    moves = []

    def hanoi(k, frm, to, aux):
        if k == 0:
            return
        hanoi(k - 1, frm, aux, to)
        moves.append((k, frm, to))
        hanoi(k - 1, aux, to, frm)

    hanoi(n, 0, 2, 1)

    pegs = [list(range(n, 0, -1)), [], []]
    states = [([list(s) for s in pegs], None, "Старт")]
    names = "ABC"
    for i, (disk, frm, to) in enumerate(moves, 1):
        pegs[to].append(pegs[frm].pop())
        states.append(([list(s) for s in pegs], disk,
                       f"Ход {i}: {names[frm]}→{names[to]} (диск {disk})"))

    fig, axes = plt.subplots(2, 4, figsize=(13.6, 6.4))
    for ax, (st, hl, title) in zip(axes.flat, states):
        _draw_hanoi_state(ax, st, n, highlight=hl)
        # Ход 4 — центральный: единственный ход самого большого диска
        color = C_ORANGE if hl == n else C_INK
        ax.set_title(title, fontsize=10.5, pad=8, color=color)

    fig.suptitle("hanoi(3): все 2³−1 = 7 ходов; ход 4 — единственный ход большого диска, "
                 "ходы 1–3 и 5–7 — это hanoi(2)",
                 fontsize=12.5, y=1.02)
    fig.tight_layout()
    _save(fig, "hanoi_trace.png")
    print("Saved: assets/hanoi_trace.png")


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_complexity_classes()
    draw_call_stack()
    draw_ram_model()
    draw_big_o_definition()
    draw_hanoi_plan()
    draw_hanoi_trace()
    print("Все диаграммы сгенерированы.")


if __name__ == "__main__":
    main()
