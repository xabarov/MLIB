"""Точные схемы для темы «Векторные представления слов».

Корпус синтетический и порождается шаблонами: так заранее известно, какие
слова обязаны оказаться рядом, и утверждения лекции можно проверять, а не
принимать на веру. Матрица совстречаемости, PPMI, SVD и обучение SGNS
градиентным спуском считаются здесь настоящим кодом.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

C_BG = "#faf9f5"
C_INK = "#141413"
C_GRAY = "#b0aea5"
C_PANEL = "#e8e6dc"
C_ORANGE = "#d97757"
C_BLUE = "#6a9bcc"
C_GREEN = "#788c5d"

CMAP_WARM = LinearSegmentedColormap.from_list("warm", [C_BG, C_PANEL, C_ORANGE])

# ---------------------------------------------------------------------------
# Синтетический корпус: слова одной группы стоят в одинаковых окружениях
# ---------------------------------------------------------------------------
GROUPS = {
    "животное": ["собака", "кошка", "лошадь"],
    "еда": ["хлеб", "сыр", "яблоко"],
    "транспорт": ["машина", "поезд", "лодка"],
}
# антонимы намеренно живут в одних и тех же шаблонах
ANTONYMS = ["горячий", "холодный"]

TEMPLATES = {
    "животное": [
        "во дворе бегает {w}",
        "я кормлю {w} каждое утро",
        "{w} спит возле двери",
        "соседи завели {w} прошлым летом",
    ],
    "еда": [
        "на столе лежит свежий {w}",
        "я ем {w} на завтрак",
        "мама купила {w} в магазине",
        "{w} закончился ещё вчера",
    ],
    "транспорт": [
        "{w} стоит возле дома",
        "мы поехали на {w} до города",
        "{w} сломался посреди дороги",
        "новый {w} обошёлся дорого",
    ],
    "признак": [
        "чай сегодня очень {w}",
        "на улице совсем {w}",
        "суп оказался слишком {w}",
        "воздух в комнате {w}",
    ],
}


# у каждого слова есть и собственные контексты — иначе слова группы
# становятся полностью взаимозаменяемыми и сливаются в одну точку
WORD_TEMPLATES = {
    "собака": ["{w} громко лает ночью", "{w} виляет хвостом"],
    "кошка": ["{w} царапает диван", "{w} мурлычет на коленях"],
    "лошадь": ["{w} скачет по полю", "{w} тянет телегу"],
    "хлеб": ["{w} зачерствел за ночь", "{w} режут ножом"],
    "сыр": ["{w} пахнет очень резко", "{w} натирают на тёрке"],
    "яблоко": ["{w} упало с ветки", "{w} червивое внутри"],
    "машина": ["{w} заглохла на светофоре", "{w} требует бензина"],
    "поезд": ["{w} прибыл на платформу", "{w} опоздал на час"],
    "лодка": ["{w} качается на волнах", "{w} течёт по дну"],
}


def build_corpus(seed=0, repeats=60, own_share=0.35):
    """Каждое слово: общие для группы шаблоны + собственные.

    Антонимы намеренно оставлены без собственных контекстов — они делят
    все шаблоны признака, и это и есть проверяемое утверждение лекции.
    """
    rng = np.random.default_rng(seed)
    sentences = []
    for group, words in GROUPS.items():
        for _ in range(repeats):
            for w in words:
                own = WORD_TEMPLATES.get(w, [])
                if own and rng.random() < own_share:
                    tpl = own[rng.integers(len(own))]
                else:
                    tpl = TEMPLATES[group][rng.integers(len(TEMPLATES[group]))]
                sentences.append(tpl.format(w=w).split())
    for _ in range(repeats):
        for w in ANTONYMS:
            tpl = TEMPLATES["признак"][rng.integers(len(TEMPLATES["признак"]))]
            sentences.append(tpl.format(w=w).split())
    rng.shuffle(sentences)
    return sentences


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
# Ядро: совстречаемость → PPMI → SVD
# ===========================================================================
def cooccurrence(sentences, window=2):
    vocab = sorted({w for s in sentences for w in s})
    index = {w: i for i, w in enumerate(vocab)}
    m = np.zeros((len(vocab), len(vocab)))
    for s in sentences:
        for i, w in enumerate(s):
            lo, hi = max(0, i - window), min(len(s), i + window + 1)
            for j in range(lo, hi):
                if j != i:
                    m[index[w], index[s[j]]] += 1
    return m, vocab, index


def ppmi(counts):
    """Positive PMI: log(p(w,c) / (p(w) p(c))), отрицательные значения срезаны."""
    total = counts.sum()
    p_wc = counts / total
    p_w = p_wc.sum(axis=1, keepdims=True)
    p_c = p_wc.sum(axis=0, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log(p_wc / (p_w * p_c))
    return np.nan_to_num(np.maximum(pmi, 0.0), nan=0.0, posinf=0.0, neginf=0.0)


def svd_embed(matrix, dim=8):
    u, s, _ = np.linalg.svd(matrix, full_matrices=False)
    return u[:, :dim] * s[:dim]


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb)) if na and nb else 0.0


# ---------------------------------------------------------------------------
# 1. Дистрибутивная гипотеза: строка матрицы как «портрет окружения»
# ---------------------------------------------------------------------------
def draw_distributional():
    sents = build_corpus()
    counts, vocab, idx = cooccurrence(sents)

    focus = ["собака", "кошка", "хлеб", "сыр", "машина", "поезд"]
    ctx = ["бегает", "кормлю", "спит", "лежит", "ем", "купила",
           "стоит", "поехали", "сломался"]
    sub = np.array([[counts[idx[w], idx[c]] for c in ctx] for w in focus])
    sub_norm = sub / np.maximum(sub.sum(axis=1, keepdims=True), 1)

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.4),
                             gridspec_kw={"width_ratios": [1.45, 1]})

    ax = axes[0]
    ax.imshow(sub_norm, cmap=CMAP_WARM, aspect="auto", vmin=0, vmax=sub_norm.max())
    ax.set_xticks(range(len(ctx)), ctx, rotation=40, ha="right", fontsize=9)
    ax.set_yticks(range(len(focus)), focus, fontsize=10)
    for i in range(len(focus)):
        for j in range(len(ctx)):
            if sub_norm[i, j] > 1e-9:
                ax.text(j, i, f"{sub_norm[i, j]:.2f}", ha="center", va="center",
                        fontsize=8,
                        color=C_BG if sub_norm[i, j] > 0.62 * sub_norm.max() else C_INK)
    ax.set_title("Доля контекста в окружении слова", pad=10)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)

    ax = axes[1]
    pairs = [("собака", "кошка", "одна группа"),
             ("хлеб", "сыр", "одна группа"),
             ("машина", "поезд", "одна группа"),
             ("собака", "хлеб", "разные группы"),
             ("кошка", "машина", "разные группы")]
    labels, vals, colors = [], [], []
    for a, b, tag in pairs:
        labels.append(f"{a} ↔ {b}")
        vals.append(cos(sub_norm[focus.index(a)], sub_norm[focus.index(b)]))
        colors.append(C_GREEN if tag == "одна группа" else C_GRAY)
    ax.barh(labels, vals, color=colors, height=0.55)
    for i, v in enumerate(vals):
        ax.text(v + 0.015, i, f"{v:.2f}", va="center", fontsize=10)
    ax.invert_yaxis()
    ax.set_xlim(0, 1.15)
    ax.set_xlabel("сходство профилей окружения")
    ax.set_title("Похожие окружения — похожие слова", pad=10)
    _despine(ax)

    fig.suptitle("Дистрибутивная гипотеза: слово задаётся тем, "
                 "в какой компании оно встречается", fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "distributional_hypothesis.png")
    return sents, counts, vocab, idx


# ---------------------------------------------------------------------------
# 2. Зачем PPMI: сырые счётчики меряют частоту, а не связь
# ---------------------------------------------------------------------------
def draw_ppmi_svd(counts, idx):
    p = ppmi(counts)
    emb = svd_embed(p, dim=8)

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6),
                             gridspec_kw={"width_ratios": [1, 1.15]})

    # слева: у частого служебного слова большие счётчики, но нулевой PPMI
    ax = axes[0]
    probe = "собака"
    partners = ["виляет", "хвостом", "кормлю", "спит", "возле", "я"]
    raw = [counts[idx[probe], idx[c]] for c in partners]
    pp = [p[idx[probe], idx[c]] for c in partners]
    x = np.arange(len(partners))
    ax.bar(x - 0.2, np.array(raw) / max(raw), width=0.38, color=C_PANEL,
           edgecolor=C_GRAY, label="сырые счётчики (норм.)")
    ax.bar(x + 0.2, np.array(pp) / max(max(pp), 1e-9), width=0.38, color=C_ORANGE,
           label="PPMI (норм.)")
    ax.set_xticks(x, partners, rotation=30, ha="right", fontsize=9.5)
    ax.set_ylabel("вес, нормирован на максимум")
    ax.set_title(f"Соседи слова «{probe}»: счётчик почти равен, связь — нет",
                 pad=10, fontsize=11)
    ax.legend(loc="upper right", fontsize=9)
    _despine(ax)

    # справа: карта после SVD
    ax = axes[1]
    two = svd_embed(p, dim=2)
    colors = {"животное": C_ORANGE, "еда": C_GREEN, "транспорт": C_BLUE}
    for g, words in GROUPS.items():
        pts = np.array([two[idx[w]] for w in words])
        ax.scatter(pts[:, 0], pts[:, 1], s=90, color=colors[g], label=g, zorder=3)
        for w, pt in zip(words, pts):
            ax.annotate(w, pt, textcoords="offset points", xytext=(7, 4), fontsize=9.5)
    pts = np.array([two[idx[w]] for w in ANTONYMS])
    ax.scatter(pts[:, 0], pts[:, 1], s=90, color=C_INK, marker="s",
               label="антонимы", zorder=3)
    for w, pt in zip(ANTONYMS, pts):
        ax.annotate(w, pt, textcoords="offset points", xytext=(7, 4), fontsize=9.5)
    ax.set_xlabel("первая компонента SVD")
    ax.set_ylabel("вторая компонента")
    ax.set_title("Плотное представление: группы разошлись", pad=10)
    ax.legend(loc="best", fontsize=9)
    _despine(ax)

    fig.suptitle("Count-based рецепт: совстречаемость → PPMI → SVD",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "ppmi_svd.png")
    return p, emb


# ---------------------------------------------------------------------------
# 3. SGNS обучается тому же, что считает PPMI
# ---------------------------------------------------------------------------
def train_sgns(sents, vocab, idx, dim=12, window=2, neg=5, epochs=40, lr=0.05, seed=1):
    """Мини-word2vec (skip-gram с отрицательными примерами) на честном SGD."""
    rng = np.random.default_rng(seed)
    v = len(vocab)
    w_in = rng.normal(0, 0.1, (v, dim))
    w_out = rng.normal(0, 0.1, (v, dim))

    pairs = []
    for s in sents:
        for i, word in enumerate(s):
            lo, hi = max(0, i - window), min(len(s), i + window + 1)
            for j in range(lo, hi):
                if j != i:
                    pairs.append((idx[word], idx[s[j]]))
    pairs = np.array(pairs)

    counts = np.bincount(pairs[:, 1], minlength=v).astype(float)
    noise = counts ** 0.75
    noise /= noise.sum()

    for _ in range(epochs):
        rng.shuffle(pairs)
        for center, context in pairs:
            negatives = rng.choice(v, size=neg, p=noise)
            targets = np.concatenate([[context], negatives])
            labels = np.zeros(neg + 1)
            labels[0] = 1.0
            vec = w_in[center]
            scores = w_out[targets] @ vec
            pred = 1.0 / (1.0 + np.exp(-np.clip(scores, -30, 30)))
            err = pred - labels
            grad_in = err @ w_out[targets]
            w_out[targets] -= lr * np.outer(err, vec)
            w_in[center] -= lr * grad_in
    return w_in, w_out


def draw_sgns_is_pmi(sents, counts, vocab, idx):
    w_in, w_out = train_sgns(sents, vocab, idx)

    total = counts.sum()
    p_wc = counts / total
    p_w = p_wc.sum(axis=1, keepdims=True)
    p_c = p_wc.sum(axis=0, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log(p_wc / (p_w * p_c))
    shifted = pmi - np.log(5)          # сдвиг на log k, k — число отрицательных примеров

    mask = counts > 4                  # только надёжно оценённые пары
    dots = (w_in @ w_out.T)[mask]
    truth = shifted[mask]
    ok = np.isfinite(truth) & np.isfinite(dots)
    dots, truth = dots[ok], truth[ok]
    r = float(np.corrcoef(dots, truth)[0, 1])

    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    ax.scatter(truth, dots, s=14, color=C_BLUE, alpha=0.55, linewidths=0)
    lo, hi = truth.min(), truth.max()
    coef = np.polyfit(truth, dots, 1)
    xs = np.linspace(lo, hi, 50)
    ax.plot(xs, np.polyval(coef, xs), color=C_ORANGE, lw=2.4,
            label=f"линейная подгонка, r = {r:.3f}")
    ax.set_xlabel(r"сдвинутый PMI:  $\log \frac{p(w,c)}{p(w)p(c)} - \log k$")
    ax.set_ylabel(r"выученное $\vec{w} \cdot \vec{c}$")
    ax.legend(loc="upper left", fontsize=10)
    ax.set_title(f"SGNS неявно раскладывает матрицу сдвинутого PMI\n"
                 f"{len(dots)} пар с достаточной статистикой", pad=12, fontsize=11.5)
    _despine(ax)
    fig.tight_layout()
    _save(fig, "sgns_is_pmi.png")
    return r, w_in, len(dots)


# ---------------------------------------------------------------------------
# 4. Антонимы близки, потому что живут в одних контекстах
# ---------------------------------------------------------------------------
def draw_antonyms(counts, idx):
    p = ppmi(counts)
    emb = svd_embed(p, dim=8)

    def sim(a, b):
        return cos(emb[idx[a]], emb[idx[b]])

    rows = [
        ("горячий ↔ холодный", sim(*ANTONYMS), "антонимы", C_ORANGE),
        ("машина ↔ поезд", sim("машина", "поезд"), "одна группа", C_GREEN),
        ("хлеб ↔ сыр", sim("хлеб", "сыр"), "одна группа", C_GREEN),
        ("собака ↔ кошка", sim("собака", "кошка"), "одна группа", C_GREEN),
        ("собака ↔ хлеб", sim("собака", "хлеб"), "разные группы", C_GRAY),
        ("горячий ↔ поезд", sim("горячий", "поезд"), "разные группы", C_GRAY),
    ]

    fig, ax = plt.subplots(figsize=(9.5, 4.3))
    labels = [r[0] for r in rows]
    vals = [r[1] for r in rows]
    ax.barh(labels, vals, color=[r[3] for r in rows], height=0.55)
    for i, (v, r) in enumerate(zip(vals, rows)):
        ax.text(v + 0.02 if v >= 0 else v - 0.02, i, f"{v:.2f}", va="center",
                ha="left" if v >= 0 else "right", fontsize=10.5)
        ax.text(0.015, i - 0.3, r[2], fontsize=8.5, color=C_GRAY,
                transform=ax.get_yaxis_transform(which="grid"))
    ax.invert_yaxis()
    ax.axvline(0, color=C_GRAY, lw=1.0)
    ax.set_xlim(min(min(vals), 0) - 0.15, max(vals) * 1.25)
    ax.set_xlabel("косинусное сходство эмбеддингов")
    ax.set_title("Антоним — это слово с почти тем же окружением", pad=12)
    _despine(ax)

    fig.suptitle("Прямое следствие гипотезы: близость меряет взаимозаменяемость, "
                 "а не синонимию", fontsize=13, y=1.0)
    fig.tight_layout()
    _save(fig, "antonyms_close.png")
    return {r[0]: round(r[1], 3) for r in rows}


# ---------------------------------------------------------------------------
# 5. Полисемия: один вектор на все значения
# ---------------------------------------------------------------------------
def draw_polysemy():
    """«Лук» встречается и как еда, и как оружие — а вектор у него один.

    Корпус здесь строится отдельно и только из двух смысловых миров, чтобы
    опорные слова были однозначными: «каша» — только еда, «меч» — только оружие.
    """
    food_tpl = ["я ем {w} на завтрак", "мама купила {w} в магазине",
                "на столе лежит свежий {w}", "{w} закончился ещё вчера"]
    weapon_tpl = ["он натянул {w} и выстрелил", "старинный {w} висит на стене",
                  "воин взял {w} и стрелы", "{w} висит в оружейной палате"]

    def corpus_with(share_food, seed):
        rng = np.random.default_rng(seed)
        sents = []
        n = 200
        for _ in range(n):
            tpl = food_tpl if rng.random() < share_food else weapon_tpl
            sents.append(tpl[rng.integers(len(tpl))].format(w="лук").split())
        for _ in range(n):
            sents.append(food_tpl[rng.integers(len(food_tpl))].format(w="каша").split())
            sents.append(weapon_tpl[rng.integers(len(weapon_tpl))].format(w="меч").split())
        rng.shuffle(sents)
        return sents

    shares = [0.0, 0.25, 0.5, 0.75, 1.0]
    to_food, to_weapon = [], []
    for i, sh in enumerate(shares):
        sents = corpus_with(sh, seed=100 + i)
        c, _vocab, idx = cooccurrence(sents)
        emb = svd_embed(ppmi(c), dim=6)
        to_food.append(cos(emb[idx["лук"]], emb[idx["каша"]]))
        to_weapon.append(cos(emb[idx["лук"]], emb[idx["меч"]]))

    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    ax.plot(shares, to_food, "o-", color=C_GREEN, lw=2.4,
            label="близость к «каша» (еда)")
    ax.plot(shares, to_weapon, "o-", color=C_ORANGE, lw=2.4,
            label="близость к «меч» (оружие)")
    ax.axvline(0.5, color=C_GRAY, lw=1.0, ls=":")
    ax.text(0.5, ax.get_ylim()[0], "  смыслы поровну", fontsize=9.5, color=C_GRAY,
            va="bottom")
    ax.set_xlabel("доля «пищевых» употреблений слова «лук» в корпусе")
    ax.set_ylabel("косинусное сходство")
    ax.set_title("Вектор многозначного слова — взвешенное среднее его значений",
                 pad=12)
    ax.legend(loc="center right", fontsize=10)
    _despine(ax)
    fig.tight_layout()
    _save(fig, "polysemy.png")
    return list(zip(shares, [round(a, 3) for a in to_food],
                    [round(b, 3) for b in to_weapon]))


def main():
    _apply_style()
    ASSETS.mkdir(parents=True, exist_ok=True)
    print("Генерация схем для эмбеддингов:")
    sents, counts, vocab, idx = draw_distributional()
    draw_ppmi_svd(counts, idx)
    r, _, n_pairs = draw_sgns_is_pmi(sents, counts, vocab, idx)
    ant = draw_antonyms(counts, idx)
    poly = draw_polysemy()

    print("\nЧисла для текста лекции:")
    print(f"  корпус: {len(sents)} предложений, словарь {len(vocab)} слов")
    print(f"  корреляция SGNS-скалярпроизведения со сдвинутым PMI: r = {r:.3f} "
          f"на {n_pairs} парах")
    print(f"  сходства: {ant}")
    print("  полисемия (доля «еды», близость к «каша», к «меч»):")
    for sh, f, w in poly:
        print(f"    {sh:.1f}  {f:>6.3f}  {w:>6.3f}")


if __name__ == "__main__":
    main()
