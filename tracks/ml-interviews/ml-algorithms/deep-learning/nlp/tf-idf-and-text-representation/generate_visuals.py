"""Точные схемы для темы «TF-IDF и представление текста числами».

Все матрицы, ранжирования и кривые считаются здесь настоящим кодом на пяти
документах из формулировки вопроса. Реализация TF-IDF сверяется с
scikit-learn, чтобы числа в лекции нельзя было списать на ошибку в формуле.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
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

CMAP_WARM = LinearSegmentedColormap.from_list("warm", [C_BG, C_PANEL, C_ORANGE])

# ---------------------------------------------------------------------------
# Корпус из формулировки вопроса
# ---------------------------------------------------------------------------
DOCS = [
    "the early bird gets the worm",
    "an early duck loves the worm",
    "i love my duck and my cat",
    "the worm wakes early",
    "a bird in my garden",
]
QUERY = "the early bird gets the worm"


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
# Ядро: TF-IDF своими руками
# ===========================================================================
def build_vocab(docs):
    return sorted({w for d in docs for w in d.split()})


def term_freq(doc, vocab, sublinear=False):
    words = doc.split()
    counts = np.array([words.count(t) for t in vocab], dtype=float)
    if sublinear:
        return np.where(counts > 0, 1.0 + np.log(np.maximum(counts, 1e-12)), 0.0)
    return counts / max(len(words), 1)


def idf_textbook(docs, vocab):
    """Учебная формула: log(N / df)."""
    n = len(docs)
    df = np.array([sum(1 for d in docs if t in d.split()) for t in vocab], dtype=float)
    return np.log(n / np.maximum(df, 1e-12)), df


def idf_sklearn(docs, vocab):
    """Вариант scikit-learn: ln((1+N)/(1+df)) + 1 — сглаженный и без нулей."""
    n = len(docs)
    df = np.array([sum(1 for d in docs if t in d.split()) for t in vocab], dtype=float)
    return np.log((1 + n) / (1 + df)) + 1.0, df


def cosine(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb)) if na and nb else 0.0


def rank_documents(docs, query, sublinear=False, use_sklearn_idf=False):
    """Косинусное ранжирование документов по запросу. Возвращает (сходства, vocab)."""
    vocab = build_vocab(docs + [query])
    idf, _ = (idf_sklearn if use_sklearn_idf else idf_textbook)(docs, vocab)
    doc_vecs = [term_freq(d, vocab, sublinear) * idf for d in docs]
    q_vec = term_freq(query, vocab, sublinear) * idf
    return np.array([cosine(q_vec, dv) for dv in doc_vecs]), vocab


# ---------------------------------------------------------------------------
# 1. Матрицы TF, IDF и их произведение
# ---------------------------------------------------------------------------
def draw_tfidf_matrix():
    vocab = build_vocab(DOCS)
    tf = np.array([term_freq(d, vocab) for d in DOCS])
    idf, df = idf_textbook(DOCS, vocab)
    tfidf = tf * idf

    fig, axes = plt.subplots(
        3, 1, figsize=(13, 7.4), gridspec_kw={"height_ratios": [3, 0.85, 3]}
    )

    def heat(ax, mat, title, fmt="{:.2f}"):
        vmax = mat.max() if mat.max() > 0 else 1.0
        ax.imshow(mat, cmap=CMAP_WARM, vmin=0, vmax=vmax, aspect="auto")
        ax.set_xticks(range(len(vocab)), vocab, rotation=45, ha="right", fontsize=9)
        ax.set_yticks(range(mat.shape[0]), [f"D{i + 1}" for i in range(mat.shape[0])],
                      fontsize=10)
        for i in range(mat.shape[0]):
            for j in range(mat.shape[1]):
                if mat[i, j] > 1e-9:
                    ax.text(j, i, fmt.format(mat[i, j]), ha="center", va="center",
                            fontsize=7.5,
                            color=C_BG if mat[i, j] > 0.62 * vmax else C_INK)
        ax.set_title(title, pad=8, fontsize=11.5)
        ax.tick_params(length=0)
        for s in ax.spines.values():
            s.set_visible(False)

    heat(axes[0], tf, "TF — доля термина в документе: «the» доминирует")

    ax = axes[1]
    ax.imshow(idf[None, :], cmap=CMAP_WARM, vmin=0, vmax=idf.max(), aspect="auto")
    ax.set_xticks(range(len(vocab)), vocab, rotation=45, ha="right", fontsize=9)
    ax.set_yticks([0], ["IDF"], fontsize=10)
    for j, v in enumerate(idf):
        ax.text(j, 0, f"{v:.2f}", ha="center", va="center", fontsize=7.5,
                color=C_BG if v > 0.62 * idf.max() else C_INK)
    ax.set_title("IDF — редкость термина в коллекции: «the» и «early» обнулены или почти",
                 pad=8, fontsize=11.5)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)

    heat(axes[2], tfidf, "TF × IDF — остаются термины, различающие документы", "{:.3f}")

    fig.suptitle("Один множитель говорит «о чём документ», другой — «что различает документы»",
                 fontsize=13, y=1.0)
    fig.tight_layout()
    _save(fig, "tfidf_matrix.png")
    return vocab, idf, df


# ---------------------------------------------------------------------------
# 2. Ранжирование и эксперимент с тройным «bird»
# ---------------------------------------------------------------------------
def draw_ranking_bird():
    sims_before, _ = rank_documents(DOCS, QUERY)

    boosted = list(DOCS)
    boosted[4] = "a bird bird bird in my garden"
    sims_after, _ = rank_documents(boosted, QUERY)

    order_before = np.argsort(sims_before)[::-1]
    order_after = np.argsort(sims_after)[::-1]
    rank_before = int(np.where(order_before == 4)[0][0]) + 1
    rank_after = int(np.where(order_after == 4)[0][0]) + 1

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.6))
    labels = [f"D{i + 1}" for i in range(len(DOCS))]

    for ax, sims, order, title in (
        (axes[0], sims_before, order_before, "Исходный корпус"),
        (axes[1], sims_after, order_after, "В D5 слово «bird» встречается 3 раза"),
    ):
        colors = [C_ORANGE if i == 4 else C_PANEL for i in order]
        edge = [C_ORANGE if i == 4 else C_GRAY for i in order]
        ax.barh([labels[i] for i in order], [sims[i] for i in order],
                color=colors, edgecolor=edge, height=0.6)
        for y, i in enumerate(order):
            ax.text(sims[i] + 0.012, y, f"{sims[i]:.3f}", va="center", fontsize=10,
                    color=C_ORANGE if i == 4 else C_INK)
        ax.invert_yaxis()
        ax.set_xlim(0, max(sims_before.max(), sims_after.max()) * 1.22)
        ax.set_xlabel("косинусное сходство с запросом")
        ax.set_title(title, pad=10)
        _despine(ax)

    fig.suptitle(f"D5 поднялся с {rank_before}-го места на {rank_after}-е — "
                 f"и это ровно то, чем пользуется накрутка ключевых слов",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "ranking_bird.png")
    return sims_before, sims_after, rank_before, rank_after


# ---------------------------------------------------------------------------
# 3. Насыщение TF: сырая частота, сублинейная и BM25
# ---------------------------------------------------------------------------
def draw_tf_saturation():
    counts = np.arange(0, 21)
    raw = counts.astype(float)
    sub = np.where(counts > 0, 1 + np.log(np.maximum(counts, 1)), 0.0)
    k1 = 1.5
    bm25 = counts * (k1 + 1) / (counts + k1)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.4))

    ax = axes[0]
    ax.plot(counts, raw / raw.max(), "o-", color=C_GRAY, lw=2.2, ms=4,
            label="сырая частота (норм.)")
    ax.plot(counts, sub / sub.max(), "o-", color=C_BLUE, lw=2.4, ms=4,
            label=r"сублинейная $1+\log(\mathrm{tf})$")
    ax.plot(counts, bm25 / bm25.max(), "o-", color=C_ORANGE, lw=2.4, ms=4,
            label=f"BM25, $k_1={k1}$")
    ax.set_xlabel("сколько раз термин встречается в документе")
    ax.set_ylabel("вес (нормирован на максимум)")
    ax.set_title("Второе упоминание важно, двадцатое — нет", pad=10)
    ax.legend(loc="lower right", fontsize=9.5)
    _despine(ax)

    ax = axes[1]
    gains = {
        "сырая частота": raw[10] / raw[1],
        r"$1+\log(\mathrm{tf})$": sub[10] / sub[1],
        f"BM25 ($k_1={k1}$)": bm25[10] / bm25[1],
    }
    names = list(gains)
    vals = [gains[n] for n in names]
    ax.bar(names, vals, color=[C_GRAY, C_BLUE, C_ORANGE], width=0.55)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.15, f"×{v:.2f}", ha="center", fontsize=11)
    ax.set_ylabel("во сколько раз вырос вес")
    ax.set_ylim(0, max(vals) * 1.25)
    ax.set_title("Награда за накрутку с 1 до 10 упоминаний", pad=10)
    _despine(ax)

    fig.suptitle("Насыщение ограничивает, сколько веса способен набрать один термин",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "tf_saturation.png")
    return {k: float(v) for k, v in gains.items()}


# ---------------------------------------------------------------------------
# 4. Зачем косинус, а не скалярное произведение
# ---------------------------------------------------------------------------
def draw_cosine_vs_dot():
    """Два документа одинаковой тематической плотности, но разной длины."""
    short = "the early bird gets the worm"
    # тот же текст, повторённый пять раз: состав слов идентичен, длина впятеро больше
    long_doc = " ".join([short] * 5)

    corpus = [short, long_doc]
    vocab = build_vocab(corpus + [QUERY])
    idf, _ = idf_textbook(DOCS, vocab)          # IDF из основного корпуса
    q_counts = np.array([QUERY.split().count(t) for t in vocab], dtype=float)
    q = q_counts * idf

    rows = []
    for name, doc in (("короткий", short), ("тот же текст ×5", long_doc)):
        counts = np.array([doc.split().count(t) for t in vocab], dtype=float)
        raw = counts * idf
        rows.append((name, len(doc.split()), float(q @ raw), cosine(q, raw)))

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.2))
    names = [f"{r[0]}\n({r[1]} слов)" for r in rows]

    ax = axes[0]
    vals = [r[2] for r in rows]
    ax.bar(names, vals, color=[C_PANEL, C_ORANGE], edgecolor=C_GRAY, width=0.5)
    for i, v in enumerate(vals):
        ax.text(i, v * 1.03, f"{v:.2f}", ha="center", fontsize=11)
    ax.set_ylim(0, max(vals) * 1.28)
    ax.set_ylabel("скалярное произведение")
    ratio = vals[1] / vals[0] if vals[0] else float("nan")
    ax.set_title(f"Без нормировки длинный побеждает в {ratio:.0f} раз", pad=10)
    _despine(ax)

    ax = axes[1]
    vals = [r[3] for r in rows]
    ax.bar(names, vals, color=[C_PANEL, C_GREEN], edgecolor=C_GRAY, width=0.5)
    for i, v in enumerate(vals):
        ax.text(i, v * 1.03, f"{v:.3f}", ha="center", fontsize=11)
    ax.set_ylim(0, max(vals) * 1.28)
    ax.set_ylabel("косинусное сходство")
    ax.set_title("Косинус видит состав, а не объём", pad=10)
    _despine(ax)

    fig.suptitle("Один и тот же состав слов, разная длина документа",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "cosine_vs_dot.png")
    return rows


# ---------------------------------------------------------------------------
# 5. Потолок мешка слов: разные слова об одном и том же
# ---------------------------------------------------------------------------
def draw_vocabulary_mismatch():
    pairs = [
        ("автомобиль сломался", "машина неисправна", "синонимы"),
        ("кошка спит на диване", "кот дремлет на софе", "полный перефраз"),
        ("мать любит дочь", "дочь любит мать", "порядок решает смысл"),
        ("фильм совсем не плохой", "фильм совсем не хороший", "противоположный смысл"),
    ]
    docs = [p for pair in pairs for p in pair[:2]]
    vocab = build_vocab(docs)
    idf, _ = idf_textbook(docs, vocab)

    sims, labels = [], []
    for a, b, tag in pairs:
        va = term_freq(a, vocab) * idf
        vb = term_freq(b, vocab) * idf
        sims.append(cosine(va, vb))
        labels.append(tag)

    fig, ax = plt.subplots(figsize=(9.5, 4.3))
    colors = [C_ORANGE if s < 0.05 else C_BLUE for s in sims]
    ax.barh(labels, sims, color=colors, height=0.55)
    for i, (s, (a, b, _)) in enumerate(zip(sims, pairs)):
        ax.text(max(s, 0) + 0.012, i, f"{s:.2f}", va="center", fontsize=10.5,
                color=C_INK)
        ax.text(0.02, i - 0.32, f"«{a}»  ↔  «{b}»", fontsize=8.5, color=C_GRAY,
                transform=ax.get_yaxis_transform(which="grid"))
    ax.invert_yaxis()
    ax.set_xlim(0, max(max(sims), 0.1) * 1.35)
    ax.set_xlabel("косинусное сходство по TF-IDF")
    ax.set_title("Мешок слов судит по совпадению строк, а не по смыслу", pad=12)
    _despine(ax)

    fig.suptitle("Потолок TF-IDF: одинаковый смысл даёт ноль, "
                 "а разный — единицу", fontsize=13, y=1.0)
    fig.tight_layout()
    _save(fig, "vocabulary_mismatch.png")
    return list(zip(labels, [round(s, 3) for s in sims]))


# ---------------------------------------------------------------------------
# 6. Связывание весов: одна матрица вместо двух
# ---------------------------------------------------------------------------
def draw_weight_tying():
    vocab_size, dim = 50_000, 768
    per_matrix = vocab_size * dim

    fig, ax = plt.subplots(figsize=(11.5, 4.6))

    def block(x, y, w, h, color, title, sub):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04",
                                    facecolor=C_PANEL, edgecolor=color, lw=2.2))
        ax.text(x + w / 2, y + h / 2 + 0.13, title, ha="center", va="center",
                fontsize=10.5, fontweight="bold")
        ax.text(x + w / 2, y + h / 2 - 0.15, sub, ha="center", va="center",
                fontsize=9, color=C_GRAY)

    block(0.1, 1.55, 1.9, 0.8, C_BLUE, "вход: id слова", "one-hot по словарю")
    block(2.5, 1.55, 2.1, 0.8, C_ORANGE, "матрица E", f"{vocab_size:,}×{dim}".replace(",", " "))
    block(5.1, 1.55, 1.9, 0.8, C_GREEN, "скрытые слои", "трансформер")
    block(7.5, 1.55, 2.1, 0.8, C_ORANGE, "матрица $E^{\\top}$", f"{dim}×{vocab_size:,}".replace(",", " "))
    block(10.1, 1.55, 1.7, 0.8, C_BLUE, "softmax", "вероятности слов")

    for x0, x1 in ((2.0, 2.5), (4.6, 5.1), (7.0, 7.5), (9.6, 10.1)):
        ax.add_patch(FancyArrowPatch((x0, 1.95), (x1, 1.95), arrowstyle="-|>",
                                     mutation_scale=13, color=C_GRAY, lw=1.6))

    ax.add_patch(FancyArrowPatch((3.55, 1.55), (8.55, 1.55), arrowstyle="<|-|>",
                                 mutation_scale=13, color=C_ORANGE, lw=2.2, ls="--",
                                 connectionstyle="arc3,rad=0.28"))
    ax.text(6.05, 0.62, "одна и та же матрица весов", ha="center", fontsize=11,
            color=C_ORANGE, fontweight="bold")
    ax.text(6.05, 0.30, f"экономия {per_matrix / 1e6:.1f} млн параметров "
                        f"при словаре {vocab_size:,} и d={dim}".replace(",", " "),
            ha="center", fontsize=10, color=C_INK)

    ax.set_xlim(-0.1, 12.0)
    ax.set_ylim(0.05, 2.75)
    ax.axis("off")
    fig.suptitle("Связывание весов: слово на входе и слово на выходе — "
                 "одно и то же представление", fontsize=13, y=0.99)
    fig.tight_layout()
    _save(fig, "weight_tying.png")
    return per_matrix


# ===========================================================================
def _verify_against_sklearn():
    """Сверка своей реализации с scikit-learn на том же корпусе."""
    from sklearn.feature_extraction.text import TfidfVectorizer

    vocab = build_vocab(DOCS)
    idf_mine, _ = idf_sklearn(DOCS, vocab)
    vec = TfidfVectorizer(vocabulary={t: i for i, t in enumerate(vocab)},
                          token_pattern=r"(?u)\b\w+\b")
    vec.fit(DOCS)
    diff_idf = float(np.max(np.abs(idf_mine - vec.idf_)))

    # полные векторы: sklearn использует сырые счётчики и L2-нормировку
    mine = []
    for d in DOCS:
        counts = np.array([d.split().count(t) for t in vocab], dtype=float)
        v = counts * idf_mine
        n = np.linalg.norm(v)
        mine.append(v / n if n else v)
    diff_vec = float(np.max(np.abs(np.array(mine) - vec.transform(DOCS).toarray())))
    return diff_idf, diff_vec


def main():
    _apply_style()
    ASSETS.mkdir(parents=True, exist_ok=True)
    print("Генерация схем TF-IDF:")
    vocab, idf, _df = draw_tfidf_matrix()
    sims_b, sims_a, rank_b, rank_a = draw_ranking_bird()
    gains = draw_tf_saturation()
    length_rows = draw_cosine_vs_dot()
    mismatch = draw_vocabulary_mismatch()
    saved = draw_weight_tying()

    d_idf, d_vec = _verify_against_sklearn()

    print("\nЧисла для текста лекции:")
    print(f"  словарь корпуса: {len(vocab)} терминов")
    print(f"  IDF('the') = {idf[vocab.index('the')]:.3f}, "
          f"IDF('gets') = {idf[vocab.index('gets')]:.3f}")
    print(f"  сходства до накрутки : {np.round(sims_b, 3).tolist()}")
    print(f"  сходства после       : {np.round(sims_a, 3).tolist()}")
    print(f"  ранг D5: {rank_b} → {rank_a}")
    print("  рост веса при накрутке 1→10: "
          + ", ".join(f"{k}: ×{v:.2f}" for k, v in gains.items()))
    for name, n_words, dot, cos in length_rows:
        print(f"  {name:>32}: {n_words:>3} слов, скаляр {dot:.3f}, косинус {cos:.3f}")
    print(f"  сходства при рассогласовании словаря: {mismatch}")
    print(f"  экономия при связывании весов: {saved / 1e6:.1f} млн параметров")
    print("\nСверка с scikit-learn:")
    print(f"  max|IDF − sklearn.idf_|      = {d_idf:.2e}")
    print(f"  max|вектор − sklearn.matrix| = {d_vec:.2e}")


if __name__ == "__main__":
    main()
