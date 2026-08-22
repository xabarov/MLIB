"""Точные схемы для темы «Агентный цикл».

Квадратичный рост числа обработанных токенов, детекторы зацикливания и
распределение причин остановки считаются здесь настоящим кодом. Схематична
только одна картинка — сам цикл, и числовых утверждений в ней нет.
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
# 1. Сам цикл (схема, без числовых утверждений)
# ---------------------------------------------------------------------------
def draw_agent_loop():
    fig, ax = plt.subplots(figsize=(11.5, 5.0))

    def block(x, y, w, h, color, title, sub):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                                    facecolor=C_PANEL, edgecolor=color, lw=2.4))
        ax.text(x + w / 2, y + h / 2 + 0.16, title, ha="center", va="center",
                fontsize=11, fontweight="bold")
        ax.text(x + w / 2, y + h / 2 - 0.18, sub, ha="center", va="center",
                fontsize=8.8, color=C_GRAY)

    block(0.2, 2.3, 2.5, 1.0, C_BLUE, "модель", "предсказывает токены")
    block(4.0, 2.3, 2.6, 1.0, C_ORANGE, "харнесс", "разбирает вызов,\nисполняет инструмент")
    block(7.9, 2.3, 2.5, 1.0, C_GREEN, "наблюдение", "результат исполнения")
    block(4.0, 0.35, 2.6, 1.0, C_INK, "состояние", "поток событий,\nтолько дописывается")

    ax.add_patch(FancyArrowPatch((2.7, 2.8), (4.0, 2.8), arrowstyle="-|>",
                                 mutation_scale=15, color=C_GRAY, lw=1.8))
    ax.text(3.35, 2.95, "вызов\nинструмента", ha="center", fontsize=8.5, color=C_GRAY)
    ax.add_patch(FancyArrowPatch((6.6, 2.8), (7.9, 2.8), arrowstyle="-|>",
                                 mutation_scale=15, color=C_GRAY, lw=1.8))

    # возврат наблюдения в модель через состояние
    ax.add_patch(FancyArrowPatch((9.15, 2.3), (5.9, 1.35), arrowstyle="-|>",
                                 mutation_scale=15, color=C_ORANGE, lw=2.0,
                                 connectionstyle="arc3,rad=0.25"))
    ax.add_patch(FancyArrowPatch((4.7, 1.35), (1.45, 2.3), arrowstyle="-|>",
                                 mutation_scale=15, color=C_ORANGE, lw=2.0,
                                 connectionstyle="arc3,rad=0.25"))
    ax.text(5.3, 1.72, "вся история целиком —\nна каждом шаге заново",
            ha="center", fontsize=9.5, color=C_ORANGE)

    ax.text(5.3, 4.0, "Модель не помнит предыдущий шаг: память — это то,\n"
                      "что харнесс положил ей во вход",
            ha="center", fontsize=11.5, color=C_INK)

    ax.set_xlim(-0.2, 10.8)
    ax.set_ylim(0.0, 4.5)
    ax.axis("off")
    fig.suptitle("Агентность живёт в цикле, а не в модели", fontsize=13, y=0.99)
    fig.tight_layout()
    _save(fig, "agent_loop.png")


# ---------------------------------------------------------------------------
# 2. Цикл умножает токены квадратично
# ---------------------------------------------------------------------------
def draw_context_growth():
    """Каждый шаг посылает всю историю заново: суммарно это O(N^2)."""
    per_turn = 800          # токенов, добавляемых одним ходом (ответ + наблюдение)
    system = 2000           # системный промпт и описания инструментов
    turns = np.arange(1, 201)

    prompt_len = system + per_turn * turns          # длина запроса на шаге N
    processed = np.cumsum(prompt_len)               # всего обработано за run

    # сжатие: держим окно последних W ходов
    window = 12
    kept = np.minimum(turns, window)
    prompt_cond = system + per_turn * kept
    processed_cond = np.cumsum(prompt_cond)

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.4))

    ax = axes[0]
    ax.plot(turns, prompt_len / 1000, color=C_ORANGE, lw=2.6, label="без сжатия")
    ax.plot(turns, prompt_cond / 1000, color=C_GREEN, lw=2.6,
            label=f"окно последних {window} ходов")
    limit = 128
    ax.axhline(limit, color=C_INK, lw=1.4, ls="--")
    hit = int(turns[np.argmax(prompt_len / 1000 >= limit)])
    ax.axvline(hit, color=C_INK, lw=1.0, ls=":")
    ax.text(hit + 4, 60, f"на {hit}-м ходу история\nупирается в окно 128k",
            fontsize=9.5, color=C_INK)
    ax.set_xlabel("ход")
    ax.set_ylabel("длина запроса, тыс. токенов")
    ax.set_ylim(0, 175)
    ax.set_title("Длина одного запроса растёт линейно", pad=10)
    ax.legend(loc="upper left", fontsize=9.5)
    _despine(ax)

    ax = axes[1]
    ax.plot(turns, processed / 1e6, color=C_ORANGE, lw=2.6, label="без сжатия")
    ax.plot(turns, processed_cond / 1e6, color=C_GREEN, lw=2.6,
            label=f"окно последних {window} ходов")
    ax.set_xlabel("ход")
    ax.set_ylabel("обработано токенов за run, млн")
    ratio = processed[-1] / processed_cond[-1]
    ax.set_title(f"А суммарно за run — квадратично\n"
                 f"к {turns[-1]}-му ходу разница в {ratio:.1f} раза",
                 pad=10, fontsize=11)
    ax.legend(loc="upper left", fontsize=9.5)
    _despine(ax)

    fig.suptitle("Главная неожиданность цикла: платите не за последний запрос, "
                 "а за сумму всех", fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "context_growth.png")
    return int(prompt_len[-1]), int(processed[-1]), float(ratio), hit


# ===========================================================================
# Детектор зацикливания: те же четыре паттерна, что в openhands-sdk
# ===========================================================================
def is_stuck(events, thresholds=None):
    """Ищет четыре паттерна застревания в хвосте потока событий.

    events: список кортежей (вид, содержимое), где вид — action | observation |
    error | message. Возвращает имя сработавшего правила или None.
    """
    th = thresholds or {"repeat": 4, "error": 3, "monologue": 3, "alternating": 4}

    actions = [e for e in events if e[0] == "action"]
    observations = [e for e in events if e[0] in ("observation", "error")]

    # 1. одно и то же действие с одним и тем же результатом
    if len(actions) >= th["repeat"] and len(observations) >= th["repeat"]:
        last_a = actions[-th["repeat"]:]
        last_o = observations[-th["repeat"]:]
        if len({a[1] for a in last_a}) == 1 and len({o[1] for o in last_o}) == 1:
            return "повтор действия и результата"

    # 2. одно и то же действие, каждый раз с ошибкой
    if len(actions) >= th["error"]:
        last_a = actions[-th["error"]:]
        last_o = observations[-th["error"]:]
        if len({a[1] for a in last_a}) == 1 and all(o[0] == "error" for o in last_o):
            return "повтор действия с ошибкой"

    # 3. монолог: подряд идут сообщения без действий и без пользователя
    tail = events[-th["monologue"]:]
    if len(tail) >= th["monologue"] and all(e[0] == "message" for e in tail):
        return "монолог без действий"

    # 4. чередование двух действий по кругу
    if len(actions) >= th["alternating"] * 2:
        last = [a[1] for a in actions[-th["alternating"] * 2:]]
        if len(set(last)) == 2 and all(last[i] != last[i + 1] for i in range(len(last) - 1)):
            return "чередование двух действий"
    return None


def draw_stuck_patterns():
    traces = {
        "продуктивный ход": [
            ("action", "ls"), ("observation", "файлы"),
            ("action", "cat a.py"), ("observation", "код"),
            ("action", "edit a.py"), ("observation", "готово"),
            ("action", "pytest"), ("observation", "1 passed"),
        ],
        "повтор действия": [
            ("action", "pytest"), ("observation", "1 failed"),
            ("action", "pytest"), ("observation", "1 failed"),
            ("action", "pytest"), ("observation", "1 failed"),
            ("action", "pytest"), ("observation", "1 failed"),
        ],
        "повтор с ошибкой": [
            ("action", "cat нет.py"), ("error", "нет файла"),
            ("action", "cat нет.py"), ("error", "нет файла"),
            ("action", "cat нет.py"), ("error", "нет файла"),
        ],
        "монолог": [
            ("action", "ls"), ("observation", "файлы"),
            ("message", "надо подумать"), ("message", "пожалуй, так"),
            ("message", "или всё-таки иначе"),
        ],
        "чередование": [
            ("action", "edit a.py"), ("observation", "ок"),
            ("action", "edit b.py"), ("observation", "ок"),
            ("action", "edit a.py"), ("observation", "ок"),
            ("action", "edit b.py"), ("observation", "ок"),
            ("action", "edit a.py"), ("observation", "ок"),
            ("action", "edit b.py"), ("observation", "ок"),
            ("action", "edit a.py"), ("observation", "ок"),
            ("action", "edit b.py"), ("observation", "ок"),
        ],
    }
    verdicts = {name: is_stuck(tr) for name, tr in traces.items()}

    fig, ax = plt.subplots(figsize=(12.5, 4.8))
    kinds_color = {"action": C_BLUE, "observation": C_GREEN,
                   "error": C_ORANGE, "message": C_GRAY}

    for row, (name, trace) in enumerate(traces.items()):
        y = len(traces) - row - 1
        for i, (kind, _) in enumerate(trace):
            ax.add_patch(FancyBboxPatch((i * 0.62, y - 0.16), 0.5, 0.34,
                                        boxstyle="round,pad=0.02",
                                        facecolor=kinds_color[kind],
                                        edgecolor="none", alpha=0.9))
        verdict = verdicts[name]
        ax.text(-0.25, y, name, ha="right", va="center", fontsize=10.5)
        ax.text(len(trace) * 0.62 + 0.25, y,
                "— " + (verdict if verdict else "не застрял"),
                ha="left", va="center", fontsize=10,
                color=C_ORANGE if verdict else C_GREEN,
                fontweight="bold" if verdict else "normal")

    handles = [plt.Line2D([], [], marker="s", ls="", ms=10, color=c, label=k)
               for k, c in kinds_color.items()]
    ax.legend(handles=handles, loc="lower center", ncol=4, fontsize=9.5,
              bbox_to_anchor=(0.42, -0.16))

    ax.set_xlim(-3.4, 12.5)
    ax.set_ylim(-0.9, len(traces) - 0.3)
    ax.axis("off")
    fig.suptitle("Застревание — свойство траектории, а не отдельного ответа модели",
                 fontsize=13, y=0.99)
    fig.tight_layout()
    _save(fig, "stuck_patterns.png")
    return verdicts


# ---------------------------------------------------------------------------
# 4. Чем на самом деле заканчиваются прогоны
# ---------------------------------------------------------------------------
def simulate_runs(n_runs=4000, p_solve=0.06, p_stuck=0.02, max_iter=50,
                  budget_usd=2.0, cost_per_turn=0.05, seed=0):
    """Простая модель прогона: на каждом ходу агент может решить задачу,
    застрять или продолжить. Ограничения — лимит ходов и бюджет.
    """
    rng = np.random.default_rng(seed)
    reasons = {"решил задачу": 0, "застрял": 0, "лимит ходов": 0, "кончился бюджет": 0}
    turns_used = []
    for _ in range(n_runs):
        spent = 0.0
        for turn in range(1, max_iter + 1):
            spent += cost_per_turn
            if spent > budget_usd:
                reasons["кончился бюджет"] += 1
                turns_used.append(turn)
                break
            r = rng.random()
            if r < p_solve:
                reasons["решил задачу"] += 1
                turns_used.append(turn)
                break
            if r < p_solve + p_stuck:
                reasons["застрял"] += 1
                turns_used.append(turn)
                break
        else:
            reasons["лимит ходов"] += 1
            turns_used.append(max_iter)
    return reasons, np.array(turns_used)


def draw_stop_reasons():
    budgets = [0.5, 1.0, 2.0, 5.0]
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.4),
                             gridspec_kw={"width_ratios": [1.15, 1]})

    ax = axes[0]
    labels = ["решил задачу", "застрял", "лимит ходов", "кончился бюджет"]
    colors = [C_GREEN, C_ORANGE, C_BLUE, C_GRAY]
    bottom = np.zeros(len(budgets))
    shares = {lab: [] for lab in labels}
    for b in budgets:
        reasons, _ = simulate_runs(budget_usd=b)
        total = sum(reasons.values())
        for lab in labels:
            shares[lab].append(reasons[lab] / total)
    for lab, color in zip(labels, colors):
        vals = np.array(shares[lab])
        ax.bar([str(b) for b in budgets], vals, bottom=bottom, color=color,
               label=lab, width=0.6)
        for i, v in enumerate(vals):
            if v > 0.04:
                ax.text(i, bottom[i] + v / 2, f"{v:.0%}", ha="center",
                        va="center", fontsize=9.5,
                        color=C_BG if color != C_GRAY else C_INK)
        bottom += vals
    ax.set_xlabel("бюджет прогона, $")
    ax.set_ylabel("доля прогонов")
    ax.set_ylim(0, 1)
    ax.set_title("Чем закончился прогон", pad=10)
    ax.legend(loc="lower right", fontsize=9, ncol=2)
    _despine(ax)

    ax = axes[1]
    _, turns = simulate_runs(budget_usd=5.0)
    ax.hist(turns, bins=np.arange(1, 52) - 0.5, color=C_PANEL, edgecolor=C_GRAY)
    ax.axvline(float(np.median(turns)), color=C_ORANGE, lw=2.4)
    ax.text(np.median(turns) + 1, ax.get_ylim()[1] * 0.9,
            f"медиана {np.median(turns):.0f} ходов", color=C_ORANGE, fontsize=10)
    ax.set_xlabel("ходов до остановки")
    ax.set_ylabel("прогонов")
    ax.set_title("Длина прогона при щедром бюджете", pad=10)
    _despine(ax)

    fig.suptitle("Успех — лишь одна из четырёх причин остановки, "
                 "и в модели с $0.5 она не главная", fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "stop_reasons.png")
    return shares


def main():
    _apply_style()
    ASSETS.mkdir(parents=True, exist_ok=True)
    print("Генерация схем агентного цикла:")
    draw_agent_loop()
    last_prompt, total, ratio, hit = draw_context_growth()
    verdicts = draw_stuck_patterns()
    shares = draw_stop_reasons()

    print("\nЧисла для текста лекции:")
    print(f"  200-й ход посылает {last_prompt / 1000:.1f}k токенов, "
          f"всего за run обработано {total / 1e6:.1f} млн")
    print(f"  в окно 128k история упирается на {hit}-м ходу")
    print(f"  сжатие окном сокращает суммарный объём в {ratio:.1f} раза")
    print("  вердикты детектора:")
    for name, v in verdicts.items():
        print(f"    {name:>22}: {v or 'не застрял'}")
    print("  доля успеха по бюджету:",
          {b: f"{s:.0%}" for b, s in zip([0.5, 1.0, 2.0, 5.0], shares["решил задачу"])})


if __name__ == "__main__":
    main()
