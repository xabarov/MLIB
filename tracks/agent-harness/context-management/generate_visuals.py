"""Точные схемы для темы «Управление контекстом и его инварианты».

Инварианты реализованы кодом и проверяются на потоках событий: наивное
отсечение действительно их нарушает, и это считается, а не утверждается.
Конфликт сжатия с кэшированием префикса тоже посчитан.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

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


# ===========================================================================
# Модель истории: событие = (вид, id вызова, id ответа модели)
# ===========================================================================
def make_history(n_turns=40, seed=0, p_multi=0.35, p_crash=0.0):
    """Поток событий агента. Один ответ модели может содержать несколько вызовов.

    p_crash — вероятность того, что вызов попал под восстановление после сбоя:
    харнесс синтезировал событие-ошибку, а настоящее наблюдение пришло позже.
    Именно из-за этого на один вызов оказывается два результата.
    """
    rng = np.random.default_rng(seed)
    events, call_id = [], 0
    events.append({"kind": "user", "call": None, "batch": None})
    for turn in range(n_turns):
        batch = f"r{turn}"
        n_calls = int(rng.integers(2, 4)) if rng.random() < p_multi else 1
        ids = []
        for _ in range(n_calls):
            call_id += 1
            cid = f"c{call_id}"
            ids.append(cid)
            events.append({"kind": "action", "call": cid, "batch": batch})
        for cid in ids:
            if rng.random() < p_crash:
                events.append({"kind": "error", "call": cid, "batch": batch})
            events.append({"kind": "observation", "call": cid, "batch": batch})
    return events


# ---------------------------------------------------------------------------
# Инварианты
# ---------------------------------------------------------------------------
def check_tool_call_matching(view):
    """Каждому действию — ровно одно наблюдение, и наоборот."""
    actions = {e["call"] for e in view if e["kind"] == "action"}
    obs = [e["call"] for e in view if e["kind"] in ("observation", "error")]
    bad = len(actions ^ set(obs))
    return bad == 0, bad


def check_observation_uniqueness(view):
    """На один вызов не больше одного наблюдения."""
    obs = [e["call"] for e in view if e["kind"] in ("observation", "error")]
    dupes = len(obs) - len(set(obs))
    return dupes == 0, dupes


def check_batch_atomicity(view, full):
    """События одного ответа модели либо все в представлении, либо все выброшены."""
    from collections import defaultdict

    total = defaultdict(int)
    kept = defaultdict(int)
    for e in full:
        if e["batch"]:
            total[e["batch"]] += 1
    for e in view:
        if e["batch"]:
            kept[e["batch"]] += 1
    broken = sum(1 for b, k in kept.items() if 0 < k < total[b])
    return broken == 0, broken


def check_tool_loop_atomicity(view, full):
    """Цикл инструментов — непрерывная цепочка пар; рвать её нельзя.

    Здесь цикл отождествлён с ответом модели, как в большинстве реализаций.
    """
    return check_batch_atomicity(view, full)


INVARIANTS = {
    "парность действий\nи наблюдений": lambda v, _f: check_tool_call_matching(v),
    "единственность\nнаблюдения": lambda v, _f: check_observation_uniqueness(v),
    "атомарность\nответа модели": check_batch_atomicity,
    "атомарность\nцикла инструментов": check_tool_loop_atomicity,
}


# ---------------------------------------------------------------------------
# Стратегии сжатия
# ---------------------------------------------------------------------------
def naive_tail(events, keep):
    """Оставить последние keep событий — самое простое и самое ломкое."""
    return events[-keep:]


def safe_tail(events, keep):
    """То же, но с восстановлением инвариантов: доукомплектовать неполные батчи."""
    view = list(events[-keep:])
    kept_batches = {e["batch"] for e in view if e["batch"]}
    return [e for e in events if e["batch"] in kept_batches or e["kind"] == "user"]


def draw_naive_breaks():
    """Сколько прогонов ломает наивное отсечение — считаем, а не предполагаем."""
    keeps = [10, 20, 40, 80, 160]
    seeds = range(200)

    naive_bad = {name: [] for name in INVARIANTS}
    safe_bad = {name: [] for name in INVARIANTS}

    for keep in keeps:
        counts_n = dict.fromkeys(INVARIANTS, 0)
        counts_s = dict.fromkeys(INVARIANTS, 0)
        for seed in seeds:
            # в каждой пятой истории — восстановление после сбоя
            full = make_history(seed=seed, p_crash=0.08 if seed % 5 == 0 else 0.0)
            for name, check in INVARIANTS.items():
                if not check(naive_tail(full, keep), full)[0]:
                    counts_n[name] += 1
                if not check(safe_tail(full, keep), full)[0]:
                    counts_s[name] += 1
        for name in INVARIANTS:
            naive_bad[name].append(counts_n[name] / len(seeds))
            safe_bad[name].append(counts_s[name] / len(seeds))

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.4), sharey=True)
    colors = [C_ORANGE, C_BLUE, C_GREEN, C_INK]

    for ax, data, title in (
        (axes[0], naive_bad, "Наивное «оставить последние N событий»"),
        (axes[1], safe_bad, "С доукомплектованием неполных батчей"),
    ):
        for (name, vals), color in zip(data.items(), colors):
            ax.plot(keeps, vals, "o-", lw=2.4, ms=5, color=color,
                    label=name.replace("\n", " "))
        ax.set_xscale("log", base=2)
        ax.set_xticks(keeps, [str(k) for k in keeps])
        ax.set_xlabel("оставлено событий")
        ax.set_ylim(-0.05, 1.05)
        ax.set_title(title, pad=10, fontsize=11.5)
        _despine(ax)
    axes[0].set_ylabel("доля историй с нарушением")
    axes[0].legend(loc="center left", fontsize=9)

    fig.suptitle("Обрезать историю с конца нельзя: у неё есть структура",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "naive_breaks.png")
    return naive_bad, safe_bad, keeps


# ---------------------------------------------------------------------------
# Как выглядит нарушение
# ---------------------------------------------------------------------------
def draw_invariant_examples():
    rows = [
        ("исправная история",
         [("action", "c1"), ("observation", "c1"), ("action", "c2"), ("observation", "c2")],
         None),
        ("наблюдение осиротело",
         [("observation", "c1"), ("action", "c2"), ("observation", "c2")],
         "действие c1 выброшено — провайдер отвергнет запрос"),
        ("два результата на вызов",
         [("action", "c1"), ("error", "c1"), ("observation", "c1")],
         "сбой синтезировал ошибку, настоящий ответ пришёл позже"),
        ("батч разорван",
         [("action", "c1"), ("action", "c2"), ("observation", "c2")],
         "один ответ модели содержал два вызова, выброшен один"),
    ]

    fig, ax = plt.subplots(figsize=(12.5, 4.4))
    colors = {"action": C_BLUE, "observation": C_GREEN, "error": C_ORANGE}

    for r, (name, seq, note) in enumerate(rows):
        y = len(rows) - r - 1
        for i, (kind, cid) in enumerate(seq):
            ax.add_patch(FancyBboxPatch((i * 1.35, y - 0.18), 1.15, 0.38,
                                        boxstyle="round,pad=0.02",
                                        facecolor=colors[kind], edgecolor="none",
                                        alpha=0.9))
            ax.text(i * 1.35 + 0.575, y, f"{kind[:3]} {cid}", ha="center",
                    va="center", fontsize=9, color=C_BG)
        ax.text(-0.3, y, name, ha="right", va="center", fontsize=10.5)
        if note:
            ax.text(len(seq) * 1.35 + 0.15, y, "← " + note, ha="left", va="center",
                    fontsize=9.5, color=C_ORANGE)
        else:
            ax.text(len(seq) * 1.35 + 0.15, y, "← так и должно быть", ha="left",
                    va="center", fontsize=9.5, color=C_GREEN)

    ax.set_xlim(-4.6, 12.5)
    ax.set_ylim(-0.6, len(rows) - 0.35)
    ax.axis("off")
    fig.suptitle("Нарушенный инвариант делает запрос не «хуже», а недопустимым",
                 fontsize=13, y=0.99)
    fig.tight_layout()
    _save(fig, "invariant_examples.png")


# ---------------------------------------------------------------------------
# Сжатие против кэширования префикса
# ---------------------------------------------------------------------------
def draw_cache_conflict(system=2000, per_turn=800, window=12, discount=0.1):
    """Скользящее окно меняет префикс каждый ход и обнуляет кэш."""
    turns = np.arange(1, 301)

    # без сжатия: префикс растёт, свежими остаются только события последнего хода
    full_len = system + per_turn * turns
    cost_full = (full_len - per_turn) * discount + per_turn

    # окно: как только оно поехало, общий префикс — только системный промпт
    kept = np.minimum(turns, window)
    win_len = system + per_turn * kept
    moving = turns > window
    cached = np.where(moving, system, win_len - per_turn)
    cost_win = cached * discount + (win_len - cached)

    cum_full = np.cumsum(cost_full)
    cum_win = np.cumsum(cost_win)
    cross_idx = np.argmax(cum_win < cum_full)
    cross = int(turns[cross_idx]) if cum_win[-1] < cum_full[-1] else None

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.4))

    ax = axes[0]
    ax.plot(turns, cost_full / 1000, color=C_ORANGE, lw=2.6,
            label="без сжатия (префикс кэшируется)")
    ax.plot(turns, cost_win / 1000, color=C_GREEN, lw=2.6,
            label=f"окно {window} ходов (кэш сбивается)")
    ax.axvline(window, color=C_INK, lw=1.0, ls=":")
    ax.text(window + 2, cost_win.max() / 1000 * 0.55,
            "окно поехало —\nпрефикс меняется\nкаждый ход", fontsize=9.5, color=C_INK)
    ax.set_xlabel("ход")
    ax.set_ylabel("эффективных токенов за ход, тыс.")
    ax.set_title("Цена одного хода с учётом кэша", pad=10)
    ax.legend(loc="upper left", fontsize=9.5)
    _despine(ax)

    # с какого хода несжатая история перестаёт помещаться в окно 128k
    forced = int(turns[np.argmax(full_len >= 128_000)])

    ax = axes[1]
    ax.plot(turns, cum_full / 1e6, color=C_ORANGE, lw=2.6, label="без сжатия")
    ax.axvspan(forced, turns[-1], color=C_GRAY, alpha=0.18)
    ax.text(forced + 6, cum_full.max() / 1e6 * 0.12,
            f"с {forced}-го хода история\nне помещается в окно —\nсжимать придётся в любом случае",
            fontsize=9.5, color=C_INK)
    ax.plot(turns, cum_win / 1e6, color=C_GREEN, lw=2.6, label=f"окно {window} ходов")
    if cross:
        ax.axvline(cross, color=C_INK, lw=1.0, ls=":")
        ax.text(cross + 2, cum_full.max() / 1e6 * 0.45,
                f"сжатие окупается\nтолько с {cross}-го хода",
                fontsize=9.5, color=C_INK)
    ax.set_xlabel("ход")
    ax.set_ylabel("накопленная цена, млн эфф. токенов")
    ax.set_title("Накопленным итогом", pad=10)
    ax.legend(loc="upper left", fontsize=9.5)
    _despine(ax)

    fig.suptitle("Сжатие экономит токены, но ломает кэш префикса — "
                 "и до какого-то хода это дороже", fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "cache_conflict.png")
    per_turn_cross = int(turns[np.argmax(cost_full > cost_win)])
    return cross, float(cost_full[20] / cost_win[20]), per_turn_cross, forced


def main():
    _apply_style()
    ASSETS.mkdir(parents=True, exist_ok=True)
    print("Генерация схем управления контекстом:")
    naive_bad, safe_bad, keeps = draw_naive_breaks()
    draw_invariant_examples()
    cross, ratio20, per_turn_cross, forced = draw_cache_conflict()

    print("\nЧисла для текста лекции:")
    print("  доля историй с нарушением при наивном отсечении:")
    for name, vals in naive_bad.items():
        pretty = name.replace("\n", " ")
        print(f"    {pretty:>34}: " + ", ".join(
            f"{k}→{v:.0%}" for k, v in zip(keeps, vals)))
    print("  после доукомплектования батчей:")
    for name, vals in safe_bad.items():
        pretty = name.replace("\n", " ")
        print(f"    {pretty:>34}: " + ", ".join(
            f"{k}→{v:.0%}" for k, v in zip(keeps, vals)))
    print(f"  цена одного хода сравнивается на {per_turn_cross}-м ходу")
    print(f"  накопленным итогом сжатие окупается с {cross}-го хода")
    print(f"  но с {forced}-го хода несжатая история не помещается в окно вовсе")
    print(f"  на 21-м ходу сжатие дороже в {1 / ratio20:.2f} раза" if ratio20 < 1
          else f"  на 21-м ходу сжатие дешевле в {ratio20:.2f} раза")


if __name__ == "__main__":
    main()
