"""Точные схемы для темы «Self-attention и трансформеры».

Длина пути и сложность считаются по формулам из статьи, эффект деления на
sqrt(d) и перестановочная эквивариантность измеряются на случайных данных,
а карта внимания получается обучением настоящего слоя градиентным спуском.
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


def softmax(x, axis=-1):
    x = x - x.max(axis=axis, keepdims=True)
    e = np.exp(x)
    return e / e.sum(axis=axis, keepdims=True)


def attention(q, k, v, scale=True):
    d = q.shape[-1]
    scores = q @ k.T
    if scale:
        scores = scores / np.sqrt(d)
    w = softmax(scores)
    return w @ v, w


# ---------------------------------------------------------------------------
# 1. Зачем внимание: длина пути и сложность слоя
# ---------------------------------------------------------------------------
def draw_why_attention():
    n = np.array([16, 64, 256, 1024, 4096])
    d, kernel = 512, 3

    path = {
        "RNN": n.astype(float),
        "CNN (dilated)": np.ceil(np.log(n) / np.log(kernel)),
        "Self-attention": np.ones_like(n, dtype=float),
    }
    flops = {
        "RNN": n * d * d,
        "CNN (dilated)": kernel * n * d * d,
        "Self-attention": n * n * d,
    }
    colors = {"RNN": C_GRAY, "CNN (dilated)": C_BLUE, "Self-attention": C_ORANGE}

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.4))

    ax = axes[0]
    for name, vals in path.items():
        ax.plot(n, vals, "o-", color=colors[name], lw=2.4, ms=5, label=name)
    ax.set_xscale("log", base=2)
    ax.set_yscale("log", base=2)
    ax.set_xlabel("длина последовательности $n$")
    ax.set_ylabel("шагов между крайними позициями")
    ax.set_title("Максимальная длина пути: чем короче, тем легче градиенту", pad=10)
    ax.legend(loc="upper left", fontsize=9.5)
    _despine(ax)

    ax = axes[1]
    for name, vals in flops.items():
        ax.plot(n, vals, "o-", color=colors[name], lw=2.4, ms=5, label=name)
    ax.set_xscale("log", base=2)
    ax.set_yscale("log", base=10)
    cross = n[np.argmax(flops["Self-attention"] > flops["RNN"])]
    ax.axvline(cross, color=C_INK, lw=1.0, ls=":")
    ax.text(cross * 1.15, flops["RNN"][0], f"при $n > d = {d}$\nвнимание дороже",
            fontsize=9.5, color=C_INK)
    ax.set_xlabel("длина последовательности $n$")
    ax.set_ylabel("операций на слой")
    ax.set_title(f"Сложность слоя при $d = {d}$", pad=10)
    ax.legend(loc="upper left", fontsize=9.5)
    _despine(ax)

    fig.suptitle("Внимание покупает путь длины 1 ценой квадратичной сложности",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "why_attention.png")
    return int(cross)


# ---------------------------------------------------------------------------
# 2. Зачем делить на sqrt(d)
# ---------------------------------------------------------------------------
def draw_scaled_dot_product():
    rng = np.random.default_rng(0)
    dims = np.array([4, 8, 16, 32, 64, 128, 256, 512])
    trials = 4000

    stds, max_p_raw, max_p_scaled, grad_raw, grad_scaled = [], [], [], [], []
    for d in dims:
        q = rng.normal(0, 1, (trials, d))
        k = rng.normal(0, 1, (trials, d))
        dots = np.einsum("ij,ij->i", q, k)
        stds.append(float(dots.std()))

        # softmax по 8 конкурирующим ключам
        scores = rng.normal(0, 1, (trials, 8, d)) @ rng.normal(0, 1, (d,))
        p_raw = softmax(scores)
        p_scaled = softmax(scores / np.sqrt(d))
        max_p_raw.append(float(p_raw.max(axis=1).mean()))
        max_p_scaled.append(float(p_scaled.max(axis=1).mean()))
        # градиент softmax по логитам ~ p(1-p): при насыщении обращается в ноль
        grad_raw.append(float((p_raw * (1 - p_raw)).sum(axis=1).mean()))
        grad_scaled.append(float((p_scaled * (1 - p_scaled)).sum(axis=1).mean()))

    fig, axes = plt.subplots(1, 3, figsize=(14.5, 4.2))

    ax = axes[0]
    ax.plot(dims, stds, "o-", color=C_ORANGE, lw=2.4, ms=5, label="измерено")
    ax.plot(dims, np.sqrt(dims), "--", color=C_INK, lw=1.8, label=r"$\sqrt{d}$")
    ax.set_xscale("log", base=2)
    ax.set_yscale("log", base=2)
    ax.set_xlabel("размерность $d$")
    ax.set_ylabel("стандартное отклонение $q\\cdot k$")
    ax.set_title("Скалярное произведение растёт как $\\sqrt{d}$", pad=10, fontsize=11)
    ax.legend(loc="upper left", fontsize=9.5)
    _despine(ax)

    ax = axes[1]
    ax.plot(dims, max_p_raw, "o-", color=C_GRAY, lw=2.4, ms=5, label="без деления")
    ax.plot(dims, max_p_scaled, "o-", color=C_ORANGE, lw=2.4, ms=5,
            label=r"с делением на $\sqrt{d}$")
    ax.axhline(1 / 8, color=C_GREEN, lw=1.4, ls=":")
    ax.text(dims[0], 1 / 8 + 0.02, "равномерное внимание (1/8)", fontsize=9,
            color=C_GREEN)
    ax.set_xscale("log", base=2)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("размерность $d$")
    ax.set_ylabel("средний максимум softmax")
    ax.set_title("Без деления softmax вырождается в argmax", pad=10, fontsize=11)
    ax.legend(loc="center right", fontsize=9.5)
    _despine(ax)

    ax = axes[2]
    ax.plot(dims, grad_raw, "o-", color=C_GRAY, lw=2.4, ms=5, label="без деления")
    ax.plot(dims, grad_scaled, "o-", color=C_ORANGE, lw=2.4, ms=5,
            label=r"с делением на $\sqrt{d}$")
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xlabel("размерность $d$")
    ax.set_ylabel(r"$\sum_i p_i(1-p_i)$")
    ax.set_title("И вместе с ним исчезает градиент", pad=10, fontsize=11)
    ax.legend(loc="lower left", fontsize=9.5)
    _despine(ax)

    fig.suptitle("Деление на корень из размерности — не косметика, "
                 "а условие обучаемости", fontsize=13, y=1.03)
    fig.tight_layout()
    _save(fig, "scaled_dot_product.png")
    return stds[-1], max_p_raw[-1], max_p_scaled[-1], grad_raw[-1], grad_scaled[-1]


# ---------------------------------------------------------------------------
# 3. Внимание не знает о порядке
# ---------------------------------------------------------------------------
def draw_permutation_equivariance():
    rng = np.random.default_rng(2)
    n, d = 6, 16
    x = rng.normal(0, 1, (n, d))
    wq, wk, wv = (rng.normal(0, 0.5, (d, d)) for _ in range(3))

    def layer(inp):
        return attention(inp @ wq, inp @ wk, inp @ wv)[0]

    out = layer(x)
    perm = rng.permutation(n)
    out_perm = layer(x[perm])
    err = float(np.abs(out_perm - out[perm]).max())

    # то же самое, но с позиционным кодированием
    pos = positional_encoding(n, d)
    out_pe = layer(x + pos)
    out_pe_perm = layer(x[perm] + pos)
    err_pe = float(np.abs(out_pe_perm - out_pe[perm]).max())

    fig, axes = plt.subplots(1, 3, figsize=(13.5, 3.9))

    for ax, mat, title in (
        (axes[0], out, "выход на исходном порядке"),
        (axes[1], out[perm], "тот же выход, переставленный"),
        (axes[2], out_perm, "выход на переставленном входе"),
    ):
        ax.imshow(mat, cmap=CMAP_WARM, aspect="auto")
        ax.set_xlabel("канал")
        ax.set_ylabel("позиция")
        ax.set_title(title, pad=10, fontsize=11)
        ax.set_xticks([])
        ax.set_yticks(range(len(mat)))
        for s in ax.spines.values():
            s.set_visible(False)

    fig.text(0.5, -0.07,
             f"две правые панели совпадают до {err:.1e} — внимание перестановочно "
             f"эквивариантно;\nпосле добавления позиционного кодирования "
             f"расхождение становится {err_pe:.2f}",
             ha="center", fontsize=10.5, color=C_INK)
    fig.suptitle("Само по себе внимание — операция над множеством, а не над "
                 "последовательностью", fontsize=13, y=1.04)
    fig.tight_layout()
    _save(fig, "permutation_equivariance.png")
    return err, err_pe


# ---------------------------------------------------------------------------
# 4. Синусоидальное позиционное кодирование
# ---------------------------------------------------------------------------
def positional_encoding(n, d):
    pos = np.arange(n)[:, None]
    i = np.arange(d)[None, :]
    angle = pos / np.power(10000.0, (2 * (i // 2)) / d)
    pe = np.where(i % 2 == 0, np.sin(angle), np.cos(angle))
    return pe


def draw_positional_encoding():
    n, d = 64, 64
    pe = positional_encoding(n, d)

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.4),
                             gridspec_kw={"width_ratios": [1.15, 1]})

    ax = axes[0]
    im = ax.imshow(pe, cmap=LinearSegmentedColormap.from_list(
        "d", [C_BLUE, C_BG, C_ORANGE]), aspect="auto", vmin=-1, vmax=1)
    ax.set_xlabel("канал")
    ax.set_ylabel("позиция")
    ax.set_title("Матрица кодирования: низкие каналы быстрые, высокие медленные",
                 pad=10, fontsize=11)
    fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02).outline.set_visible(False)
    for s in ax.spines.values():
        s.set_visible(False)

    ax = axes[1]
    norm = pe / np.linalg.norm(pe, axis=1, keepdims=True)
    for anchor, color in ((8, C_BLUE), (32, C_ORANGE), (56, C_GREEN)):
        ax.plot(np.arange(n), norm @ norm[anchor], color=color, lw=2.2,
                label=f"позиция {anchor}")
    ax.set_xlabel("позиция")
    ax.set_ylabel("косинус с опорной позицией")
    ax.set_title("Похожесть зависит только от расстояния", pad=10, fontsize=11)
    ax.legend(loc="lower center", fontsize=9.5)
    _despine(ax)

    # проверка сдвиговой инвариантности: профиль одинаков для разных опор
    profiles = []
    for anchor in (8, 32, 56):
        prof = norm @ norm[anchor]
        offs = np.arange(n) - anchor
        keep = np.abs(offs) <= 8
        profiles.append(prof[keep])
    spread = float(np.max(np.abs(profiles[0] - profiles[1])))

    fig.text(0.5, -0.04,
             f"профили сходства вокруг разных опор совпадают с точностью {spread:.1e}: "
             f"кодирование несёт относительное расстояние",
             ha="center", fontsize=10, color=C_GRAY)
    fig.suptitle("Позиционное кодирование возвращает порядок, "
                 "потерянный вниманием", fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "positional_encoding.png")
    return spread


# ---------------------------------------------------------------------------
# 5. Обученное внимание: ассоциативный поиск
# ---------------------------------------------------------------------------
def train_lookup(seed=0, steps=3000, n_items=4, n_types=4, n_values=6, d=32, lr=0.1):
    """Обучаем ОДИН слой внимания задаче «найди по признаку».

    Вход: четыре предмета, у каждого свой тип и своё значение, плюс запрос —
    тип. Ответ: значение предмета этого типа. Задача решается одним слоем:
    сопоставить запрос с типами через Q·K и вынести значение через V.

    Важно, что ответ лежит НА совпавшей позиции. Классическая задача
    «значение стоит после ключа» одним слоем не решается — там нужна пара
    голов (previous-token и induction), то есть два слоя.
    """
    rng = np.random.default_rng(seed)
    n = n_items + 1
    n_tokens = n_types * n_values + n_types      # предметы + запросы
    emb = rng.normal(0, 0.3, (n_tokens, d))
    pos = positional_encoding(n, d)
    wq = rng.normal(0, 0.2, (d, d))
    wk = rng.normal(0, 0.2, (d, d))
    wv = rng.normal(0, 0.2, (d, d))
    wo = rng.normal(0, 0.2, (d, n_values))

    def make_batch(bs):
        types = np.array([rng.permutation(n_types)[:n_items] for _ in range(bs)])
        values = rng.integers(0, n_values, (bs, n_items))
        qi = rng.integers(0, n_items, bs)
        toks = np.zeros((bs, n), dtype=int)
        toks[:, :n_items] = types * n_values + values
        toks[:, -1] = n_types * n_values + types[np.arange(bs), qi]
        target = values[np.arange(bs), qi]
        return toks, target, qi

    for _ in range(steps):
        toks, target, _ = make_batch(64)
        x = emb[toks] + pos
        q, k, v = x @ wq, x @ wk, x @ wv
        scores = np.einsum("bid,bjd->bij", q, k) / np.sqrt(d)
        w = softmax(scores)
        ctx = np.einsum("bij,bjd->bid", w, v)
        last = ctx[:, -1, :]
        logits = last @ wo
        p = softmax(logits)

        bs = len(toks)
        dlogits = p.copy()
        dlogits[np.arange(bs), target] -= 1
        dlogits /= bs

        gwo = last.T @ dlogits
        dctx = np.zeros_like(ctx)
        dctx[:, -1, :] = dlogits @ wo.T
        dw = np.einsum("bid,bjd->bij", dctx, v)
        dv = np.einsum("bij,bid->bjd", w, dctx)
        ds = w * (dw - (dw * w).sum(axis=-1, keepdims=True)) / np.sqrt(d)
        dq = np.einsum("bij,bjd->bid", ds, k)
        dk = np.einsum("bij,bid->bjd", ds, q)

        gwq = np.einsum("bnd,bne->de", x, dq)
        gwk = np.einsum("bnd,bne->de", x, dk)
        gwv = np.einsum("bnd,bne->de", x, dv)
        dx = dq @ wq.T + dk @ wk.T + dv @ wv.T
        gemb = np.zeros_like(emb)
        np.add.at(gemb, toks.ravel(), dx.reshape(-1, d))

        for par, grad in ((wo, gwo), (wq, gwq), (wk, gwk), (wv, gwv), (emb, gemb)):
            par -= lr * grad

    toks, target, qi = make_batch(2000)
    x = emb[toks] + pos
    scores = np.einsum("bid,bjd->bij", x @ wq, x @ wk) / np.sqrt(d)
    w = softmax(scores)
    ctx = np.einsum("bij,bjd->bid", w, x @ wv)
    acc = float((np.argmax(ctx[:, -1, :] @ wo, axis=1) == target).mean())
    return acc, w, toks, qi, n_items


def draw_attention_learned():
    acc, w, toks, qi, n_items = train_lookup()
    n = w.shape[1]

    # строка запроса, выровненная так, чтобы нужный предмет всегда был первым
    rows = w[:, -1, :]
    aligned = np.array([np.roll(rows[b], -qi[b]) for b in range(len(qi))])
    mean_row = aligned.mean(axis=0)
    hit = float(mean_row[0])

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.3),
                             gridspec_kw={"width_ratios": [1, 1.05]})

    ax = axes[0]
    example = 0
    ax.imshow(w[example], cmap=CMAP_WARM, vmin=0, vmax=1)
    labels = [f"предмет {i + 1}" for i in range(n_items)] + ["запрос"]
    ax.set_xticks(range(n), labels, rotation=40, ha="right", fontsize=9)
    ax.set_yticks(range(n), labels, fontsize=9)
    ax.set_xlabel("на что смотрит")
    ax.set_ylabel("кто смотрит")
    target = int(qi[example])
    ax.add_patch(plt.Rectangle((target - 0.5, n - 1.5), 1, 1, fill=False,
                               edgecolor=C_GREEN, lw=3.0))
    ax.set_title(f"Один пример: запрос смотрит на предмет {target + 1}",
                 pad=10, fontsize=11)
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)

    ax = axes[1]
    xs = np.arange(n)
    colors = [C_ORANGE if i == 0 else C_PANEL for i in range(n)]
    ax.bar(xs, mean_row, color=colors, edgecolor=C_GRAY)
    ax.set_xticks(xs, ["нужный\nпредмет"] + [f"чужой {i}" for i in range(1, n_items)]
                  + ["сам\nзапрос"], fontsize=8.5)
    ax.set_ylabel("средний вес внимания")
    ax.set_ylim(0, 1.05)
    for i, v in enumerate(mean_row):
        ax.text(i, v + 0.02, f"{v:.2f}", ha="center", fontsize=9.5,
                color=C_ORANGE if i == 0 else C_GRAY)
    ax.set_title(f"Усреднение по 2000 примерам\nточность решения задачи: {acc:.1%}",
                 pad=10, fontsize=11)
    _despine(ax)

    fig.suptitle("Слой внимания сам выучивает поиск по признаку",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "attention_learned.png")
    return acc, hit


def main():
    _apply_style()
    ASSETS.mkdir(parents=True, exist_ok=True)
    print("Генерация схем для трансформеров:")
    cross = draw_why_attention()
    std_d, mp_raw, mp_scaled, g_raw, g_scaled = draw_scaled_dot_product()
    err, err_pe = draw_permutation_equivariance()
    spread = draw_positional_encoding()
    acc, peak = draw_attention_learned()

    print("\nЧисла для текста лекции:")
    print(f"  внимание дороже RNN начиная с n = {cross}")
    print(f"  при d=512: std(q·k) = {std_d:.1f}")
    print(f"  средний максимум softmax: без деления {mp_raw:.3f}, с делением {mp_scaled:.3f}")
    print(f"  сумма p(1-p): без деления {g_raw:.2e}, с делением {g_scaled:.3f}")
    print(f"  перестановочная эквивариантность: расхождение {err:.1e}")
    print(f"  с позиционным кодированием: расхождение {err_pe:.2f}")
    print(f"  профили позиционного сходства совпадают до {spread:.1e}")
    print(f"  обученный поиск: точность {acc:.1%}, вес на нужном значении {peak:.2f}")


if __name__ == "__main__":
    main()
