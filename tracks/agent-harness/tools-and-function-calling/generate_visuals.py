"""Точные схемы для темы «Инструменты и function calling».

Устойчивость разбора, накладные расходы на описания инструментов и стратегии
усечения наблюдений считаются здесь настоящим кодом на настоящих строках.
"""

import json
import re
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
# 1. Два пути вызова инструмента
# ---------------------------------------------------------------------------
def draw_two_paths():
    fig, ax = plt.subplots(figsize=(12.5, 5.0))

    def block(x, y, w, h, color, title, sub):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04",
                                    facecolor=C_PANEL, edgecolor=color, lw=2.2))
        ax.text(x + w / 2, y + h / 2 + 0.13, title, ha="center", va="center",
                fontsize=10, fontweight="bold")
        ax.text(x + w / 2, y + h / 2 - 0.16, sub, ha="center", va="center",
                fontsize=8.2, color=C_GRAY)

    ax.text(5.6, 3.62, "Нативный вызов", ha="center", fontsize=12,
            color=C_GREEN, fontweight="bold")
    block(0.2, 2.75, 2.3, 0.72, C_GREEN, "схема в API", "поле tools")
    block(3.0, 2.75, 2.3, 0.72, C_GREEN, "модель", "структурный выход")
    block(5.8, 2.75, 2.3, 0.72, C_GREEN, "готовый объект", "имя + аргументы")
    block(8.6, 2.75, 2.3, 0.72, C_GREEN, "валидация", "типы, границы")
    for x0 in (2.5, 5.3, 8.1):
        ax.add_patch(FancyArrowPatch((x0, 3.11), (x0 + 0.5, 3.11), arrowstyle="-|>",
                                     mutation_scale=13, color=C_GRAY, lw=1.6))

    ax.text(5.6, 2.15, "Эмуляция через промпт", ha="center", fontsize=12,
            color=C_ORANGE, fontweight="bold")
    block(0.2, 1.25, 2.3, 0.72, C_ORANGE, "схема → текст", "рендер в промпт")
    block(3.0, 1.25, 2.3, 0.72, C_ORANGE, "few-shot", "примеры вызовов")
    block(5.8, 1.25, 2.3, 0.72, C_ORANGE, "модель", "свободный текст")
    block(8.6, 1.25, 2.3, 0.72, C_ORANGE, "разбор регуляркой", "и только потом\nвалидация")
    for x0 in (2.5, 5.3, 8.1):
        ax.add_patch(FancyArrowPatch((x0, 1.61), (x0 + 0.5, 1.61), arrowstyle="-|>",
                                     mutation_scale=13, color=C_GRAY, lw=1.6))

    ax.text(5.6, 0.55, "Схема работает дважды: как промпт для модели\n"
                       "и как контракт для валидации в харнессе",
            ha="center", fontsize=11.5, color=C_INK)

    ax.set_xlim(0, 11.1)
    ax.set_ylim(0.1, 4.0)
    ax.axis("off")
    fig.suptitle("Инструмент — граница между вероятностной стороной и детерминированной",
                 fontsize=13, y=0.99)
    fig.tight_layout()
    _save(fig, "two_paths.png")


# ===========================================================================
# Разбор вызова: что бывает на входе и кто это переживает
# ===========================================================================
def make_outputs():
    """Правдоподобные варианты того, что модель выдаёт вместо чистого JSON."""
    good = '{"name": "read_file", "arguments": {"path": "a.py", "lines": 40}}'
    return {
        "чистый JSON": good,
        "в markdown-заборе": f"```json\n{good}\n```",
        "с пояснением до": f"Сейчас прочитаю файл.\n{good}",
        "с пояснением после": f"{good}\nДальше проверю тесты.",
        "висячая запятая": good.replace("40}", "40,}"),
        "одинарные кавычки": good.replace('"', "'"),
        "не закрыта скобка": good[:-1],
        "число как строка": good.replace(": 40", ': "40"'),
    }


def parse_naive(text):
    """json.loads как есть."""
    try:
        return json.loads(text)
    except Exception:
        return None


def parse_regex(text):
    """Выцепить первый объект по фигурным скобкам и разобрать."""
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


def parse_tolerant(text):
    """То же плюс мелкий ремонт: забор, висячие запятые, одинарные кавычки."""
    t = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    m = re.search(r"\{.*\}", t, re.DOTALL)
    if not m:
        return None
    body = m.group(0)
    for attempt in (body,
                    re.sub(r",\s*([}\]])", r"\1", body),
                    re.sub(r",\s*([}\]])", r"\1", body).replace("'", '"')):
        try:
            return json.loads(attempt)
        except Exception:
            continue
    return None


SCHEMA = {
    "name": "read_file",
    "arguments": {"path": str, "lines": int},
}


def validate(obj):
    """Контракт: имя известно, аргументы нужного типа. Разбор ≠ валидность."""
    if not isinstance(obj, dict):
        return False
    if obj.get("name") != SCHEMA["name"]:
        return False
    args = obj.get("arguments")
    if not isinstance(args, dict):
        return False
    for key, typ in SCHEMA["arguments"].items():
        if key not in args or not isinstance(args[key], typ):
            return False
    return True


def draw_parsing():
    outputs = make_outputs()
    parsers = {"json.loads": parse_naive,
               "+ поиск скобок": parse_regex,
               "+ мелкий ремонт": parse_tolerant}

    table = {}
    for pname, parser in parsers.items():
        row = []
        for text in outputs.values():
            obj = parser(text)
            if obj is None:
                row.append(0)          # не разобрано
            elif not validate(obj):
                row.append(1)          # разобрано, но контракт нарушен
            else:
                row.append(2)          # всё хорошо
        table[pname] = row

    fig, axes = plt.subplots(1, 2, figsize=(13.5, 4.6),
                             gridspec_kw={"width_ratios": [1.7, 1]})

    ax = axes[0]
    mat = np.array([table[p] for p in parsers])
    from matplotlib.colors import ListedColormap
    ax.imshow(mat, cmap=ListedColormap([C_ORANGE, C_PANEL, C_GREEN]),
              vmin=0, vmax=2, aspect="auto")
    ax.set_xticks(range(len(outputs)), list(outputs), rotation=35, ha="right",
                  fontsize=9)
    ax.set_yticks(range(len(parsers)), list(parsers), fontsize=10)
    marks = {0: "✗", 1: "?", 2: "✓"}
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            ax.text(j, i, marks[mat[i, j]], ha="center", va="center",
                    fontsize=13, color=C_BG if mat[i, j] != 1 else C_INK)
    ax.set_title("✓ разобрано и прошло контракт · ? разобрано, но контракт нарушен · "
                 "✗ не разобрано", pad=10, fontsize=10)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)

    ax = axes[1]
    ok = [sum(1 for v in table[p] if v == 2) / len(outputs) for p in parsers]
    ax.barh(list(parsers), ok, color=[C_GRAY, C_BLUE, C_GREEN], height=0.5)
    for i, v in enumerate(ok):
        ax.text(v + 0.02, i, f"{v:.0%}", va="center", fontsize=11)
    ax.invert_yaxis()
    ax.set_xlim(0, 1.15)
    ax.set_xlabel("доля разобранных корректно")
    ax.set_title("Нативный вызов даёт 100% без всякого разбора", pad=10, fontsize=11)
    _despine(ax)

    fig.suptitle("Эмуляция вызова через текст — это парсер, который придётся чинить",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "parsing.png")
    return {p: ok[i] for i, p in enumerate(parsers)}


# ---------------------------------------------------------------------------
# 3. Описания инструментов оплачиваются каждый ход
# ---------------------------------------------------------------------------
def draw_tool_overhead():
    tokens_per_tool = 160        # схема, отрендеренная в текст
    turns = 200
    counts = np.array([3, 5, 10, 20, 40])

    per_request = counts * tokens_per_tool
    per_run = per_request * turns

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.4))

    ax = axes[0]
    ax.bar([str(c) for c in counts], per_request / 1000, color=C_PANEL,
           edgecolor=C_GRAY, width=0.6)
    for i, v in enumerate(per_request):
        ax.text(i, v / 1000 + 0.1, f"{v / 1000:.1f}k", ha="center", fontsize=10)
    ax.set_xlabel("число инструментов")
    ax.set_ylabel("токенов в каждом запросе")
    ax.set_title(f"Описания при {tokens_per_tool} токенах на инструмент", pad=10)
    _despine(ax)

    ax = axes[1]
    ax.bar([str(c) for c in counts], per_run / 1e6, color=C_ORANGE,
           edgecolor=C_GRAY, width=0.6)
    for i, v in enumerate(per_run):
        ax.text(i, v / 1e6 + 0.03, f"{v / 1e6:.2f}M", ha="center", fontsize=10)
    ax.set_xlabel("число инструментов")
    ax.set_ylabel("токенов за прогон, млн")
    ax.set_title(f"То же за {turns} ходов — они посылаются каждый раз", pad=10)
    _despine(ax)

    fig.suptitle("Каждый добавленный инструмент оплачивается на каждом ходу",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "tool_overhead.png")
    return int(per_request[3]), float(per_run[3] / 1e6)


# ---------------------------------------------------------------------------
# 4. Наблюдения не помещаются: как усекать
# ---------------------------------------------------------------------------
def draw_observation_truncation():
    """Вывод инструмента не ограничен, а место в контексте — да."""
    rng = np.random.default_rng(0)
    # правдоподобное распределение: почти всё короткое, редкое — огромное
    sizes = np.exp(rng.normal(5.5, 1.9, 20000)).astype(int) + 20

    budget = 2000
    over = float((sizes > budget).mean())

    # какая доля всего объёма приходится на длинный хвост
    tail_share = float(sizes[sizes > budget].sum() / sizes.sum())

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.4))

    ax = axes[0]
    ax.hist(np.log10(sizes), bins=60, color=C_PANEL, edgecolor=C_GRAY)
    ax.axvline(np.log10(budget), color=C_ORANGE, lw=2.4)
    ax.text(np.log10(budget) + 0.08, ax.get_ylim()[1] * 0.85,
            f"лимит {budget}\nне влезает {over:.0%}", color=C_ORANGE, fontsize=10)
    ax.set_xlabel("размер наблюдения, $\\log_{10}$ символов")
    ax.set_ylabel("наблюдений")
    ax.set_title("Почти всё короткое, но хвост огромен", pad=10)
    _despine(ax)

    ax = axes[1]
    labels = ["всего", "не влезает\nв лимит"]
    vals = [1.0, tail_share]
    ax.bar(labels, vals, color=[C_PANEL, C_ORANGE], edgecolor=C_GRAY, width=0.5)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.02, f"{v:.0%}", ha="center", fontsize=11)
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("доля суммарного объёма")
    ax.set_title(f"Эти {over:.0%} наблюдений дают {tail_share:.0%} всего объёма",
                 pad=10, fontsize=11)
    _despine(ax)

    fig.suptitle("Усечение наблюдений — не мелочь: длинный хвост съедает контекст",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "observation_truncation.png")
    return over, tail_share


def main():
    _apply_style()
    ASSETS.mkdir(parents=True, exist_ok=True)
    print("Генерация схем про инструменты:")
    draw_two_paths()
    ok = draw_parsing()
    per_req, per_run = draw_tool_overhead()
    over, tail_share = draw_observation_truncation()

    print("\nЧисла для текста лекции:")
    print("  доля корректно разобранных выходов:")
    for name, v in ok.items():
        print(f"    {name:>16}: {v:.0%}")
    print(f"  20 инструментов: {per_req} токенов в запросе, {per_run:.1f} млн за прогон")
    print(f"  наблюдений длиннее лимита: {over:.1%}, "
          f"на них приходится {tail_share:.0%} объёма")


if __name__ == "__main__":
    main()
