"""Точные схемы для темы «Как понять, что харнесс работает».

Ширина доверительного интервала, размер выборки, искажение от неточного судьи
и различие агентов при равной доле успеха считаются здесь кодом.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

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
# 1. Сколько прогонов нужно, чтобы вообще что-то утверждать
# ---------------------------------------------------------------------------
def ci_halfwidth(p, n, z=1.96):
    return z * np.sqrt(p * (1 - p) / n)


def needed_n(p, delta, alpha_z=1.96, power_z=0.84):
    """Размер выборки на одну руку для обнаружения разницы delta."""
    return 2 * (alpha_z + power_z) ** 2 * p * (1 - p) / delta ** 2


def draw_sample_size():
    p = 0.40
    ns = np.array([5, 10, 20, 50, 100, 200, 500, 1000])
    half = ci_halfwidth(p, ns) * 100

    deltas = np.array([0.02, 0.05, 0.10, 0.20])
    need = np.array([needed_n(p, d) for d in deltas])

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.4))

    ax = axes[0]
    ax.plot(ns, half, "o-", color=C_ORANGE, lw=2.6, ms=5)
    ax.set_xscale("log")
    for n_mark, color in ((10, C_GRAY), (100, C_BLUE)):
        h = ci_halfwidth(p, n_mark) * 100
        ax.plot(n_mark, h, "o", color=color, ms=11, zorder=3)
        ax.annotate(f"n={n_mark}: ±{h:.0f} п.п.", (n_mark, h),
                    textcoords="offset points", xytext=(10, 8), fontsize=10,
                    color=color)
    ax.set_xlabel("прогонов в замере")
    ax.set_ylabel("полуширина 95% интервала, п.п.")
    ax.set_title(f"Насколько точно вы вообще знаете долю успеха (p≈{p:.0%})", pad=10,
                 fontsize=11)
    _despine(ax)

    ax = axes[1]
    labels = [f"{d * 100:.0f} п.п." for d in deltas]
    ax.bar(labels, need, color=C_PANEL, edgecolor=C_GRAY, width=0.6)
    for i, v in enumerate(need):
        ax.text(i, v * 1.05, f"{v:.0f}", ha="center", fontsize=10.5)
    ax.set_yscale("log")
    ax.set_xlabel("какую разницу хотим заметить")
    ax.set_ylabel("прогонов на каждый вариант")
    ax.set_title("Сколько нужно, чтобы разница была значимой", pad=10)
    _despine(ax)

    fig.suptitle("Три прогона не отличают улучшение от везения",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "sample_size.png")
    return (float(ci_halfwidth(p, 10) * 100), float(ci_halfwidth(p, 100) * 100),
            float(needed_n(p, 0.05)))


# ---------------------------------------------------------------------------
# 2. Судья ошибается, и это смещает измерение
# ---------------------------------------------------------------------------
def measured_rate(true_p, tpr, fpr):
    """Что покажет судья с чувствительностью tpr и долей ложных срабатываний fpr."""
    return true_p * tpr + (1 - true_p) * fpr


def draw_judge_bias():
    true_p = np.linspace(0, 1, 101)
    judges = {
        "идеальный": (1.0, 0.0),
        "хороший (0.9 / 0.05)": (0.90, 0.05),
        "средний (0.8 / 0.15)": (0.80, 0.15),
        "снисходительный (0.95 / 0.35)": (0.95, 0.35),
    }
    colors = [C_INK, C_GREEN, C_BLUE, C_ORANGE]

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.4))

    ax = axes[0]
    for (name, (tpr, fpr)), color in zip(judges.items(), colors):
        ax.plot(true_p * 100, measured_rate(true_p, tpr, fpr) * 100, lw=2.4,
                color=color, label=name)
    ax.set_xlabel("истинная доля успеха, %")
    ax.set_ylabel("что покажет судья, %")
    ax.set_title("Смещение зависит от того, где вы находитесь", pad=10)
    ax.legend(loc="upper left", fontsize=9)
    _despine(ax)

    # что происходит с РАЗНИЦЕЙ двух вариантов
    ax = axes[1]
    base = 0.40
    deltas = np.linspace(0, 0.2, 41)
    for (name, (tpr, fpr)), color in zip(judges.items(), colors):
        seen = (measured_rate(base + deltas, tpr, fpr)
                - measured_rate(base, tpr, fpr))
        ax.plot(deltas * 100, seen * 100, lw=2.4, color=color, label=name)
    ax.set_xlabel("истинное улучшение, п.п.")
    ax.set_ylabel("измеренное улучшение, п.п.")
    ax.set_title("Неточный судья сжимает разницу", pad=10)
    ax.legend(loc="upper left", fontsize=9)
    _despine(ax)

    fig.suptitle("Судья — тоже модель: его ошибки входят в ваш результат",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "judge_bias.png")
    shrink = (measured_rate(0.5, 0.8, 0.15) - measured_rate(0.4, 0.8, 0.15)) / 0.1
    return float(shrink)


# ---------------------------------------------------------------------------
# 3. Одинаковая доля успеха — разные агенты
# ---------------------------------------------------------------------------
def draw_beyond_success():
    rng = np.random.default_rng(0)
    n = 4000

    # оба решают 60% задач, но по-разному
    a_turns = rng.gamma(3.0, 4.0, n) + 3
    b_turns = rng.gamma(9.0, 3.2, n) + 3
    a_cost = a_turns * 0.05
    b_cost = b_turns * 0.05
    a_human = rng.poisson(0.4, n)
    b_human = rng.poisson(2.1, n)

    fig, axes = plt.subplots(1, 3, figsize=(14.5, 4.2))

    ax = axes[0]
    ax.bar(["агент A", "агент B"], [0.60, 0.60], color=[C_BLUE, C_ORANGE],
           edgecolor=C_GRAY, width=0.5)
    for i in range(2):
        ax.text(i, 0.61, "60%", ha="center", fontsize=12)
    ax.set_ylim(0, 0.75)
    ax.set_ylabel("доля решённых задач")
    ax.set_title("По этой метрике они равны", pad=10)
    _despine(ax)

    ax = axes[1]
    bins = np.linspace(0, 60, 45)
    ax.hist(a_turns, bins=bins, color=C_BLUE, alpha=0.65, label="агент A")
    ax.hist(b_turns, bins=bins, color=C_ORANGE, alpha=0.65, label="агент B")
    ax.set_xlabel("ходов до результата")
    ax.set_ylabel("прогонов")
    ax.set_title(f"медианы {np.median(a_turns):.0f} и {np.median(b_turns):.0f}",
                 pad=10)
    ax.legend(loc="upper right", fontsize=9.5)
    _despine(ax)

    ax = axes[2]
    labels = ["стоимость,\n$ за прогон", "вмешательств\nчеловека"]
    a_vals = [a_cost.mean(), a_human.mean()]
    b_vals = [b_cost.mean(), b_human.mean()]
    x = np.arange(len(labels))
    ax.bar(x - 0.2, a_vals, width=0.38, color=C_BLUE, label="агент A")
    ax.bar(x + 0.2, b_vals, width=0.38, color=C_ORANGE, label="агент B")
    for i, (a, b) in enumerate(zip(a_vals, b_vals)):
        ax.text(i - 0.2, a * 1.04, f"{a:.2f}", ha="center", fontsize=9.5)
        ax.text(i + 0.2, b * 1.04, f"{b:.2f}", ha="center", fontsize=9.5)
    ax.set_xticks(x, labels, fontsize=9.5)
    ax.legend(loc="upper left", fontsize=9.5)
    ax.set_title("А по этим — нет", pad=10)
    _despine(ax)

    fig.suptitle("Доля успеха не упорядочивает агентов: нужны стоимость, "
                 "длина и цена человеческого внимания", fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "beyond_success.png")
    return (float(np.median(a_turns)), float(np.median(b_turns)),
            float(a_cost.mean()), float(b_cost.mean()),
            float(a_human.mean()), float(b_human.mean()))


def main():
    _apply_style()
    ASSETS.mkdir(parents=True, exist_ok=True)
    print("Генерация схем про оценку:")
    h10, h100, n5 = draw_sample_size()
    shrink = draw_judge_bias()
    a_t, b_t, a_c, b_c, a_h, b_h = draw_beyond_success()

    print("\nЧисла для текста лекции:")
    print(f"  при 10 прогонах интервал ±{h10:.0f} п.п., при 100 — ±{h100:.0f} п.п.")
    print(f"  чтобы заметить разницу в 5 п.п., нужно {n5:.0f} прогонов на вариант")
    print(f"  судья 0.8/0.15 сжимает истинное улучшение до {shrink:.0%}")
    print(f"  агенты при равных 60%: ходов {a_t:.0f} против {b_t:.0f}, "
          f"стоимость ${a_c:.2f} против ${b_c:.2f}, "
          f"вмешательств {a_h:.1f} против {b_h:.1f}")


if __name__ == "__main__":
    main()
