"""Точные схемы для темы «Подагенты, параллельность и делегирование».

Экономия контекста, точка окупаемости делегирования, предел параллельности
из-за разделяемых ресурсов и ценность критика считаются здесь кодом.
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
# 1. Что подагент получает и что возвращает
# ---------------------------------------------------------------------------
def draw_delegation_map():
    fig, ax = plt.subplots(figsize=(12.0, 4.8))

    def block(x, y, w, h, color, title, sub):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04",
                                    facecolor=C_PANEL, edgecolor=color, lw=2.2))
        ax.text(x + w / 2, y + h / 2 + 0.14, title, ha="center", va="center",
                fontsize=10.5, fontweight="bold")
        ax.text(x + w / 2, y + h / 2 - 0.17, sub, ha="center", va="center",
                fontsize=8.4, color=C_GRAY)

    block(0.3, 2.6, 3.0, 0.9, C_BLUE, "родительский агент", "своя история,\nсвой набор инструментов")
    block(0.3, 0.5, 3.0, 0.9, C_BLUE, "родительский агент", "история почти не выросла")
    block(7.4, 1.55, 3.4, 0.9, C_ORANGE, "подагент", "ЧИСТЫЙ контекст,\nсвой узкий набор")

    ax.add_patch(FancyArrowPatch((3.4, 3.0), (7.4, 2.25), arrowstyle="-|>",
                                 mutation_scale=15, color=C_GRAY, lw=1.9,
                                 connectionstyle="arc3,rad=-0.18"))
    ax.text(5.3, 3.15, "задача одной строкой", ha="center", fontsize=9.5, color=C_INK)

    ax.add_patch(FancyArrowPatch((7.4, 1.75), (3.4, 1.0), arrowstyle="-|>",
                                 mutation_scale=15, color=C_ORANGE, lw=2.2,
                                 connectionstyle="arc3,rad=-0.18"))
    ax.text(5.3, 0.95, "только итог: несколько сотен токенов\n"
                       "вместо десятков тысяч разведки",
            ha="center", fontsize=9.5, color=C_ORANGE)

    ax.text(9.1, 0.75, "всё, что подагент\nнапробовал и отбросил,\nостаётся у него",
            ha="center", fontsize=9.5, color=C_GRAY)

    ax.set_xlim(0, 11.4)
    ax.set_ylim(0.2, 3.9)
    ax.axis("off")
    fig.suptitle("Главный смысл делегирования — не разделение труда, "
                 "а изоляция контекста", fontsize=13, y=0.99)
    fig.tight_layout()
    _save(fig, "delegation_map.png")


# ---------------------------------------------------------------------------
# 2. Экономия контекста и точка окупаемости
# ---------------------------------------------------------------------------
def total_tokens_inline(explore_turns, tail_turns, per_turn=800, system=2000):
    """Разведка идёт прямо в родительской истории и потом тащится за ней."""
    total_turns = explore_turns + tail_turns
    turns = np.arange(1, total_turns + 1)
    return float(np.sum(system + per_turn * turns))


def total_tokens_delegated(explore_turns, tail_turns, per_turn=800, system=2000,
                           sub_system=3000, summary=300):
    """Разведка уходит подагенту; родитель получает только итог."""
    sub_turns = np.arange(1, explore_turns + 1)
    sub_cost = float(np.sum(sub_system + per_turn * sub_turns))

    parent_turns = np.arange(1, tail_turns + 2)          # +1 ход на сам вызов
    parent_len = system + summary + per_turn * parent_turns
    return sub_cost + float(np.sum(parent_len))


def draw_context_saving():
    explore = np.arange(1, 41)
    tail = 40

    inline = np.array([total_tokens_inline(e, tail) for e in explore])
    deleg = np.array([total_tokens_delegated(e, tail) for e in explore])
    cheaper = deleg < inline
    break_even = int(explore[np.argmax(cheaper)]) if cheaper.any() else None

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.4))

    ax = axes[0]
    ax.plot(explore, inline / 1e6, color=C_BLUE, lw=2.6, label="разведка в родителе")
    ax.plot(explore, deleg / 1e6, color=C_ORANGE, lw=2.6, label="разведка у подагента")
    if break_even:
        ax.axvline(break_even, color=C_INK, lw=1.0, ls=":")
        ax.text(break_even + 0.7, inline.max() / 1e6 * 0.35,
                f"делегирование окупается\nс {break_even} ходов разведки",
                fontsize=9.5, color=C_INK)
    ax.set_xlabel("ходов разведки")
    ax.set_ylabel("всего обработано токенов, млн")
    ax.set_title(f"При {tail} ходах основной работы после", pad=10)
    ax.legend(loc="upper left", fontsize=9.5)
    _despine(ax)

    ax = axes[1]
    tails = [10, 20, 40, 80]
    for t, color in zip(tails, (C_GRAY, C_GREEN, C_BLUE, C_ORANGE)):
        ratio = np.array([total_tokens_delegated(e, t) / total_tokens_inline(e, t)
                          for e in explore])
        ax.plot(explore, ratio, lw=2.4, color=color, label=f"{t} ходов после")
    ax.axhline(1.0, color=C_INK, lw=1.2, ls="--")
    ax.text(1, 1.03, "выше — делегировать дороже", fontsize=9, color=C_INK)
    ax.set_xlabel("ходов разведки")
    ax.set_ylabel("делегировано / встроено")
    ax.set_title("Чем длиннее работа после, тем выгоднее делегировать", pad=10)
    ax.legend(loc="upper right", fontsize=9)
    _despine(ax)

    fig.suptitle("Разведка, оставшаяся в родителе, оплачивается на каждом "
                 "последующем ходу", fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "context_saving.png")
    return break_even, float(deleg[19] / inline[19])


# ---------------------------------------------------------------------------
# 3. Параллельность упирается в разделяемые ресурсы
# ---------------------------------------------------------------------------
def simulate_parallel(n_calls, contended_share, t_tool=1.0, t_llm=2.0,
                      n_runs=2000, seed=0):
    """Вызовы идут параллельно, но конкурирующие за один ресурс — по очереди."""
    rng = np.random.default_rng(seed)
    times = []
    for _ in range(n_runs):
        contended = rng.random(n_calls) < contended_share
        n_c = int(contended.sum())
        n_free = n_calls - n_c
        # свободные исполняются одновременно, конкурирующие — цепочкой
        tool_time = max(t_tool if n_free else 0.0, n_c * t_tool)
        times.append(t_llm + tool_time)
    serial = t_llm + n_calls * t_tool
    return serial, float(np.mean(times))


def draw_parallel_limits():
    ns = np.arange(1, 13)
    shares = [0.0, 0.25, 0.5, 1.0]

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.4))

    ax = axes[0]
    for share, color in zip(shares, (C_GREEN, C_BLUE, C_ORANGE, C_GRAY)):
        speed = []
        for n in ns:
            serial, par = simulate_parallel(int(n), share)
            speed.append(serial / par)
        ax.plot(ns, speed, "o-", lw=2.4, ms=4, color=color,
                label=f"{share:.0%} конкурируют за ресурс")
    ax.set_xlabel("вызовов в одном ответе модели")
    ax.set_ylabel("ускорение против последовательного")
    ax.set_title("Блокировки съедают выигрыш", pad=10)
    ax.legend(loc="upper left", fontsize=9)
    _despine(ax)

    ax = axes[1]
    # даже при идеальной параллельности вызов модели остаётся последовательным
    t_llm_vals = np.linspace(0.5, 8, 40)
    n = 6
    ideal = [(t + n * 1.0) / (t + 1.0) for t in t_llm_vals]
    ax.plot(t_llm_vals, ideal, color=C_ORANGE, lw=2.6)
    ax.axhline(n, color=C_INK, lw=1.2, ls="--")
    ax.text(0.6, n - 0.45, f"теоретический предел ×{n}", fontsize=9.5, color=C_INK)
    ax.set_xlabel("время вызова модели / время инструмента")
    ax.set_ylabel("ускорение при 6 вызовах")
    ax.set_title("Вызов модели всё равно последовательный", pad=10)
    _despine(ax)

    fig.suptitle("Параллелить можно инструменты, но не рассуждение",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "parallel_limits.png")
    s4, p4 = simulate_parallel(6, 0.25)
    s_free, p_free = simulate_parallel(6, 0.0)
    return s_free / p_free, s4 / p4


# ---------------------------------------------------------------------------
# 4. Критик: вторая пара глаз и её цена
# ---------------------------------------------------------------------------
def simulate_critic(p_error=0.25, recall=0.7, false_alarm=0.15, rounds=1,
                    n_runs=20000, seed=1):
    """Критик перечитывает результат и может отправить на доработку.

    Параметры ПРЕДПОЛОЖЕНЫ: доля ошибочных результатов, доля ошибок, которые
    критик замечает, и доля ложных тревог на правильных результатах.
    """
    rng = np.random.default_rng(seed)
    bad_out, extra_calls = 0, 0
    for _ in range(n_runs):
        wrong = rng.random() < p_error
        calls = 0
        for _ in range(rounds):
            calls += 1                                   # прогон критика
            flagged = (rng.random() < recall) if wrong else (rng.random() < false_alarm)
            if not flagged:
                break
            calls += 1                                   # доработка
            if wrong:
                wrong = rng.random() < p_error           # переделали заново
        bad_out += int(wrong)
        extra_calls += calls
    return bad_out / n_runs, extra_calls / n_runs


def draw_critic():
    rounds = [0, 1, 2, 3]
    errs, costs = [], []
    for r in rounds:
        if r == 0:
            errs.append(0.25)
            costs.append(0.0)
        else:
            e, c = simulate_critic(rounds=r)
            errs.append(e)
            costs.append(c)

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.4))

    ax = axes[0]
    ax.bar([str(r) for r in rounds], errs, color=C_PANEL, edgecolor=C_GRAY, width=0.55)
    for i, v in enumerate(errs):
        ax.text(i, v + 0.005, f"{v:.1%}", ha="center", fontsize=10.5)
    ax.set_xlabel("раундов проверки критиком")
    ax.set_ylabel("доля неверных результатов")
    ax.set_title("Каждый следующий раунд помогает меньше", pad=10)
    _despine(ax)

    ax = axes[1]
    ax.plot(costs, errs, "o-", color=C_ORANGE, lw=2.4, ms=7)
    for r, c, e in zip(rounds, costs, errs):
        ax.annotate(f"{r}", (c, e), textcoords="offset points", xytext=(8, 6),
                    fontsize=10, color=C_INK)
    ax.set_xlabel("дополнительных вызовов модели на задачу")
    ax.set_ylabel("доля неверных результатов")
    ax.set_title("Цена качества: раунды подписаны у точек", pad=10)
    _despine(ax)

    fig.text(0.5, -0.06,
             "модель с предположенными вероятностями: 25% результатов неверны, "
             "критик замечает 70% ошибок\nи поднимает ложную тревогу в 15% случаев",
             ha="center", fontsize=9.5, color=C_GRAY)
    fig.suptitle("Критик — это ещё один прогон модели, и он тоже ошибается",
                 fontsize=13, y=1.03)
    fig.tight_layout()
    _save(fig, "critic.png")
    return errs, costs


def main():
    _apply_style()
    ASSETS.mkdir(parents=True, exist_ok=True)
    print("Генерация схем про делегирование:")
    draw_delegation_map()
    break_even, ratio20 = draw_context_saving()
    sp_free, sp_contended = draw_parallel_limits()
    errs, costs = draw_critic()

    print("\nЧисла для текста лекции:")
    print(f"  делегирование окупается с {break_even} ходов разведки")
    print(f"  при 20 ходах разведки делегирование стоит {ratio20:.0%} от встроенного")
    print(f"  ускорение 6 вызовов: без конкуренции ×{sp_free:.1f}, "
          f"при 25% конкурирующих ×{sp_contended:.1f}")
    print("  критик (модель, не замер):")
    for r, e, c in zip([0, 1, 2, 3], errs, costs):
        print(f"    {r} раундов: ошибок {e:.1%}, лишних вызовов {c:.2f}")


if __name__ == "__main__":
    main()
