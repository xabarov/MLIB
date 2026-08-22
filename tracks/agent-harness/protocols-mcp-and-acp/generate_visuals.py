"""Точные схемы для темы «Протоколы: MCP и ACP».

Комбинаторика интеграций и вклад сетевой задержки считаются здесь; схема
слоёв структурная и числовых утверждений не содержит.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

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
    plt.rcParams.update(
        {
            "figure.facecolor": C_BG,
            "axes.facecolor": C_BG,
            "axes.edgecolor": C_GRAY,
            "axes.labelcolor": C_INK,
            "text.color": C_INK,
            "xtick.color": C_INK,
            "ytick.color": C_INK,
            "font.size": 11,
            "axes.titlesize": 12,
            "legend.frameon": False,
        }
    )


def _save(fig, name):
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS / name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)
    print(f"  {name}")


def _despine(ax, keep=("left", "bottom")):
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(side in keep)


# ---------------------------------------------------------------------------
# 1. N×M против N+M
# ---------------------------------------------------------------------------
def draw_combinatorics():
    n_harness = np.arange(1, 11)
    m_tools = 12

    pairwise = n_harness * m_tools
    with_protocol = n_harness + m_tools

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.4))

    ax = axes[0]
    ax.plot(n_harness, pairwise, "o-", color=C_ORANGE, lw=2.6, ms=5,
            label=f"каждый с каждым: N × {m_tools}")
    ax.plot(n_harness, with_protocol, "o-", color=C_GREEN, lw=2.6, ms=5,
            label=f"через протокол: N + {m_tools}")
    ax.set_xlabel("число харнессов")
    ax.set_ylabel("сколько интеграций писать")
    ax.set_title(f"При {m_tools} наборах инструментов", pad=10)
    ax.legend(loc="upper left", fontsize=9.5)
    _despine(ax)

    ax = axes[1]
    ratio = pairwise / with_protocol
    ax.plot(n_harness, ratio, "o-", color=C_BLUE, lw=2.6, ms=5)
    ax.axhline(1.0, color=C_INK, lw=1.2, ls="--")
    ax.text(1.1, 1.12, "ниже — протокол не нужен", fontsize=9.5, color=C_INK)
    ax.set_xlabel("число харнессов")
    ax.set_ylabel("во сколько раз меньше работы")
    ax.set_title("Выигрыш появляется не сразу", pad=10)
    _despine(ax)

    break_even = int(n_harness[np.argmax(ratio > 1.0)])
    return fig, break_even, pairwise, with_protocol, ratio


def draw_combinatorics_and_save():
    fig, break_even, pairwise, with_protocol, ratio = draw_combinatorics()
    fig.suptitle("Протокол окупается комбинаторикой, а не удобством",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "combinatorics.png")
    return break_even, int(pairwise[-1]), int(with_protocol[-1]), float(ratio[-1])


# ---------------------------------------------------------------------------
# 2. Где именно проходит граница
# ---------------------------------------------------------------------------
def draw_layers():
    fig, ax = plt.subplots(figsize=(12.5, 5.0))

    def block(x, y, w, h, color, title, sub=""):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04",
                                    facecolor=C_PANEL, edgecolor=color, lw=2.2))
        ax.text(x + w / 2, y + h / 2 + (0.12 if sub else 0), title, ha="center",
                va="center", fontsize=10.5, fontweight="bold")
        if sub:
            ax.text(x + w / 2, y + h / 2 - 0.16, sub, ha="center", va="center",
                    fontsize=8.3, color=C_GRAY)

    for i, (name, sub) in enumerate([("интерфейс", "терминал, IDE, веб"),
                                     ("агентный цикл", "модель, история, шаги"),
                                     ("инструменты", "файлы, оболочка, сеть")]):
        y = 2.9 - i * 1.25
        block(3.9, y, 3.6, 0.9, C_BLUE, name, sub)
        if i < 2:
            ax.add_patch(FancyArrowPatch((5.7, y), (5.7, y - 0.35),
                                         arrowstyle="-", color=C_GRAY, lw=1.6))

    # ACP режет выше цикла, MCP — ниже
    ax.plot([2.6, 8.8], [2.72, 2.72], color=C_ORANGE, lw=2.4, ls="--")
    ax.text(9.0, 2.72, "ACP\nагент как удалённый компонент", va="center",
            fontsize=10, color=C_ORANGE)

    ax.plot([2.6, 8.8], [1.47, 1.47], color=C_GREEN, lw=2.4, ls="--")
    ax.text(9.0, 1.47, "MCP\nинструменты как удалённый сервис", va="center",
            fontsize=10, color=C_GREEN)

    ax.text(5.7, 4.35, "Оба протокола делают одно и то же движение\n"
                       "на разных этажах: превращают внутренний вызов во внешний контракт",
            ha="center", fontsize=11, color=C_INK)

    ax.set_xlim(0.6, 13.4)
    ax.set_ylim(0.2, 4.8)
    ax.axis("off")
    fig.suptitle("Протокол — это выбор, где провести границу", fontsize=13, y=0.99)
    fig.tight_layout()
    _save(fig, "layers.png")


# ---------------------------------------------------------------------------
# 3. Сколько стоит лишний сетевой круг
# ---------------------------------------------------------------------------
def draw_latency():
    """Вклад задержки протокола в общее время прогона."""
    t_llm = 3.0            # секунд на вызов модели
    t_tool = 0.6           # собственно исполнение инструмента
    calls_per_turn = 1.6
    turns = 200

    overheads = np.array([0.0, 0.005, 0.02, 0.05, 0.15, 0.5])   # секунд на круг
    base = turns * (t_llm + calls_per_turn * t_tool)
    total = base + turns * calls_per_turn * overheads
    share = (total - base) / total

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.4))

    ax = axes[0]
    labels = [f"{o * 1000:.0f}" for o in overheads]
    ax.bar(labels, total / 60, color=C_PANEL, edgecolor=C_GRAY, width=0.6)
    ax.axhline(base / 60, color=C_GREEN, lw=2.0, ls="--")
    ax.text(0.05, base / 60 + 0.3, "без протокола", fontsize=9.5, color=C_GREEN)
    ax.set_xlabel("задержка протокола на вызов, мс")
    ax.set_ylabel("время прогона, минут")
    ax.set_title(f"{turns} ходов, вызов модели {t_llm} с", pad=10)
    _despine(ax)

    ax = axes[1]
    ax.plot(overheads * 1000, share * 100, "o-", color=C_ORANGE, lw=2.6, ms=6)
    ax.set_xlabel("задержка протокола на вызов, мс")
    ax.set_ylabel("доля времени прогона, %")
    ax.set_title("Даже 150 мс на круг — единицы процентов", pad=10)
    _despine(ax)

    fig.suptitle("Задержка протокола — не главная его цена",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "latency.png")
    return float(share[3] * 100), float(share[4] * 100)


def main():
    _apply_style()
    ASSETS.mkdir(parents=True, exist_ok=True)
    print("Генерация схем про протоколы:")
    break_even, pw, wp, ratio = draw_combinatorics_and_save()
    draw_layers()
    s50, s150 = draw_latency()

    print("\nЧисла для текста лекции:")
    print(f"  протокол начинает выигрывать с {break_even} харнессов")
    print(f"  при 10 харнессах и 12 наборах: {pw} интеграций против {wp} "
          f"(в {ratio:.1f} раза меньше)")
    print(f"  задержка 50 мс на вызов — {s50:.1f}% времени прогона, "
          f"150 мс — {s150:.1f}%")


if __name__ == "__main__":
    main()
