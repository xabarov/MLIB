"""Точные схемы для темы «Типизированные решающие модели».

Все числа на картинках — результат прогона, а не подобранные вручную значения:
скорер по парам обучается градиентным спуском на игрушечном «пространстве смысла»,
перестановочная инвариантность проверяется численно, позиционное смещение при
рендеринге вариантов буквами моделируется явно и снимается оценкой по позициям,
порядковая голова сравнивается с плоским softmax на одних и тех же данных,
а стоимость прохода считается по формулам префилла.
"""

import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from scipy.optimize import minimize, minimize_scalar
from sklearn.linear_model import LogisticRegression

warnings.filterwarnings("ignore")

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


def _blank(ax, xlim=(0, 10), ylim=(0, 6)):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


def _box(ax, x, y, w, h, text, fc=C_PANEL, ec=C_INK, fs=9.5, lw=1.2, tc=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06",
                                facecolor=fc, edgecolor=ec, lw=lw))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=tc or C_INK)


def _arrow(ax, p1, p2, color=C_GRAY, lw=1.3):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=12,
                                 color=color, lw=lw, shrinkA=2, shrinkB=2))


def softmax(z, axis=-1):
    z = z - z.max(axis=axis, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=axis, keepdims=True)


# ==========================================================================
# Игрушечный мир: «понятия» и состояния
# ==========================================================================

D_LAT, D_OBS, N_CONCEPTS, NOISE = 24, 48, 200, 0.45


def make_world(seed=0):
    r = np.random.default_rng(seed)
    psi = r.normal(size=(N_CONCEPTS, D_LAT))
    psi /= np.linalg.norm(psi, axis=1, keepdims=True)
    M = r.normal(size=(D_LAT, D_OBS)) / np.sqrt(D_LAT)
    return psi, M


def sample_states(psi, M, concepts, n_per, seed=0):
    r = np.random.default_rng(seed)
    y = np.repeat(concepts, n_per)
    z = psi[y] + NOISE * r.normal(size=(len(y), D_LAT))
    x = z @ M + 0.2 * r.normal(size=(len(y), D_OBS))
    return x / np.linalg.norm(x, axis=1, keepdims=True), y


def make_questions(psi, M, pool, n_per, N, seed):
    """Вопрос = состояние + N РАЗНЫХ вариантов, один из которых верный."""
    r = np.random.default_rng(seed)
    x, y = sample_states(psi, M, pool, n_per, seed=seed)
    opts = np.empty((len(y), N), dtype=int)
    for i, gold in enumerate(y):
        others = pool[pool != gold]
        opts[i, 0] = gold
        opts[i, 1:] = r.choice(others, N - 1, replace=False)
    perm = np.argsort(r.random(opts.shape), axis=1)
    opts = np.take_along_axis(opts, perm, axis=1)
    return x, opts, np.argmax(opts == y[:, None], axis=1)


def train_scorer(x, y, psi, n_opts=6, steps=8000, lr=0.8, seed=0):
    """s(x, o) = φ(x)ᵀ W ψ(o). Softmax по ПРЕДЛОЖЕННЫМ вариантам, кросс-энтропия."""
    r = np.random.default_rng(seed)
    W = r.normal(size=(D_OBS, D_LAT)) * 0.01
    classes = np.unique(y)
    for _ in range(steps):
        idx = r.integers(0, len(y), 256)
        xb, yb = x[idx], y[idx]
        opts = np.empty((len(idx), n_opts), dtype=int)
        opts[:, 0] = yb
        for j in range(1, n_opts):
            opts[:, j] = r.choice(classes, len(idx))
        bad = opts[:, 1:] == yb[:, None]
        opts[:, 1:][bad] = r.choice(classes, bad.sum())
        pm = np.argsort(r.random(opts.shape), axis=1)
        opts = np.take_along_axis(opts, pm, axis=1)
        tgt = np.argmax(opts == yb[:, None], axis=1)

        E = psi[opts]
        p = softmax(np.einsum("bd,bnd->bn", xb @ W, E))
        g = p.copy()
        g[np.arange(len(idx)), tgt] -= 1
        W -= lr * (xb.T @ np.einsum("bn,bnd->bd", g, E)) / len(idx)
    return W


def score(W, x, psi, opts):
    return np.einsum("bd,bnd->bn", x @ W, psi[opts])


# ==========================================================================
# 1. Фиксированная голова против скорера по парам
# ==========================================================================


def run_head_vs_scorer(seed=0):
    psi, M = make_world(seed)
    seen, unseen = np.arange(120), np.arange(120, N_CONCEPTS)
    x_tr, y_tr = sample_states(psi, M, seen, 60, seed=1)
    W = train_scorer(x_tr, y_tr, psi, seed=seed)
    head = LogisticRegression(max_iter=1000).fit(x_tr, y_tr)
    lut = {c: i for i, c in enumerate(head.classes_)}

    Ns = (2, 4, 8, 20, 50)
    rows = {}
    for tag, pool in (("знакомые варианты", seen), ("новые варианты", unseen)):
        acc_s, acc_h, known = [], [], []
        for N in Ns:
            x, opts, tgt = make_questions(psi, M, pool, 40, N, seed=100 + N)
            acc_s.append(float(np.mean(score(W, x, psi, opts).argmax(1) == tgt)))
            kn = np.isin(opts, head.classes_)
            raw = head.decision_function(x)
            lg = np.full(opts.shape, -1e9)
            for j in range(N):
                ok = kn[:, j]
                if ok.any():
                    lg[ok, j] = raw[np.where(ok)[0], [lut[c] for c in opts[ok, j]]]
            acc_h.append(float(np.mean(np.where(kn.any(1), lg.argmax(1), -1) == tgt)))
            known.append(float(kn.mean()))
        rows[tag] = (acc_s, acc_h, known)
    return psi, M, W, Ns, rows, seen, unseen


def draw_head_vs_scorer(Ns, rows):
    _apply_style()
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(13.0, 4.6),
                                   gridspec_kw={"width_ratios": [1.15, 1]})
    _blank(axL, (0, 10), (0, 6.4))

    axL.text(2.4, 6.1, "фиксированная голова", ha="center", fontsize=11, color=C_ORANGE)
    _box(axL, 0.4, 4.6, 4.0, 0.75, "состояние $x$")
    _box(axL, 0.4, 3.3, 4.0, 0.75, "$W \\in \\mathbb{R}^{K \\times d}$ — обучаемая матрица",
         fc="#f2d9d0")
    _box(axL, 0.4, 2.0, 4.0, 0.75, "$K$ логитов → softmax")
    _box(axL, 0.4, 0.5, 4.0, 1.1,
         "$K$ зафиксировано при обучении:\nновый вариант = переобучение", fc=C_BG,
         ec=C_ORANGE)
    _arrow(axL, (2.4, 4.6), (2.4, 4.05))
    _arrow(axL, (2.4, 3.3), (2.4, 2.75))
    _arrow(axL, (2.4, 2.0), (2.4, 1.6))

    axL.text(7.6, 6.1, "скорер по парам", ha="center", fontsize=11, color=C_BLUE)
    _box(axL, 5.6, 4.6, 1.9, 0.75, "состояние $x$")
    _box(axL, 7.7, 4.6, 1.9, 0.75, "вариант $o$", fc="#dfe8f1")
    _box(axL, 5.6, 3.3, 4.0, 0.75, "$s(x, o) = \\varphi(x)^{\\top} W \\psi(o)$", fc="#dfe8f1")
    _box(axL, 5.6, 2.0, 4.0, 0.75, "softmax по предложенным вариантам", fs=9.0)
    _box(axL, 5.6, 0.5, 4.0, 1.1,
         "варианты — часть ВХОДА:\nих число и состав любые", fc=C_BG, ec=C_BLUE)
    _arrow(axL, (6.5, 4.6), (7.0, 4.05))
    _arrow(axL, (8.6, 4.6), (8.1, 4.05))
    _arrow(axL, (7.6, 3.3), (7.6, 2.75))
    _arrow(axL, (7.6, 2.0), (7.6, 1.6))

    for tag, (acc_s, acc_h, _), style in (
        ("знакомые варианты", rows["знакомые варианты"], "-"),
        ("новые варианты", rows["новые варианты"], "--"),
    ):
        axR.plot(Ns, acc_s, color=C_BLUE, lw=2.4, ls=style, marker="o", ms=6,
                 label=f"скорер, {tag}")
        axR.plot(Ns, acc_h, color=C_ORANGE, lw=2.0, ls=style, marker="s", ms=5,
                 label=f"фикс. голова, {tag}")
    axR.plot(Ns, [1 / n for n in Ns], color=C_GRAY, ls=":", lw=1.4,
             label="случайный выбор $1/N$")
    axR.set_xscale("log")
    axR.set_xticks(Ns, [str(n) for n in Ns])
    axR.set_xlabel("вариантов в вопросе, $N$")
    axR.set_ylabel("доля правильных ответов")
    axR.set_ylim(-0.03, 1.0)
    axR.set_title("одна и та же модель, варианты приходят на инференсе", fontsize=11.5)
    axR.legend(fontsize=8.8, loc="upper right")
    axR.grid(alpha=0.25, color=C_GRAY, lw=0.6)
    _despine(axR)

    fig.suptitle("Схема не зашита в веса: варианты подаются на вход и скорятся общей функцией",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "head_vs_scorer.png")


# ==========================================================================
# 2. Один проход: механика и стоимость
# ==========================================================================


def draw_one_pass(l_state=400, l_opt=8, l_q=12, d=2048, layers=24):
    _apply_style()
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(13.2, 4.8),
                                   gridspec_kw={"width_ratios": [1.25, 1]})
    _blank(axL, (0, 12), (0, 6.6))

    _box(axL, 0.3, 5.2, 11.4, 0.9,
         "вход: состояние + вопросы со своими вариантами (схема — это ТЕКСТ)",
         fc=C_PANEL, fs=9.5)
    _box(axL, 0.3, 3.9, 3.4, 0.85, "состояние\n$L_s$ токенов", fc="#e8e6dc")
    _box(axL, 4.0, 3.9, 3.6, 0.85, "вопрос 1: A) … B) … C) …", fc="#dfe8f1")
    _box(axL, 7.9, 3.9, 3.8, 0.85, "вопрос 2: да / нет", fc="#dfe8f1")
    _arrow(axL, (6.0, 5.2), (6.0, 4.78))

    _box(axL, 0.3, 2.5, 11.4, 0.85, "ОДИН проход трансформера (префилл)", fc="#f2d9d0",
         fs=10.5)
    for x0 in (2.0, 5.8, 9.8):
        _arrow(axL, (x0, 3.9), (x0, 3.38))

    _box(axL, 1.2, 1.2, 4.2, 0.85, "логиты в слоте ответа 1\n→ softmax($z/T$)", fc=C_BG)
    _box(axL, 6.6, 1.2, 4.2, 0.85, "логиты в слоте ответа 2\n→ softmax($z/T$)", fc=C_BG)
    _arrow(axL, (3.3, 2.5), (3.3, 2.08))
    _arrow(axL, (8.7, 2.5), (8.7, 2.08))
    axL.text(6.0, 0.55, "ни сэмплирования, ни парсинга, ни ответа вне множества",
             ha="center", fontsize=9.5, color=C_GRAY)

    Ns = np.arange(2, 60)
    tok_naive = Ns * (l_state + l_q + l_opt)
    tok_shared = l_state + Ns * (l_q + l_opt)
    tok_single = l_state + l_q + Ns * l_opt
    for v, color, label in ((tok_naive, C_ORANGE, "кросс-энкодер: $N$ проходов"),
                            (tok_shared, C_BLUE, "общий префикс состояния"),
                            (tok_single, C_INK, "один проход, логиты в слоте")):
        axR.plot(Ns, v, color=color, lw=2.4, label=label)
    axR.set_yscale("log")
    axR.set_xlabel("вариантов в вопросе, $N$")
    axR.set_ylabel("обработанных токенов (лог)")
    axR.set_title(f"состояние {l_state} токенов, вариант {l_opt}", fontsize=11.5)
    axR.legend(fontsize=9.5, loc="upper left")
    axR.grid(alpha=0.25, color=C_GRAY, lw=0.6, which="both")
    _despine(axR)
    k = 20
    axR.annotate(f"при $N$ = {k}: {tok_naive[k - 2]} против {tok_single[k - 2]} токенов, "
                 f"в {tok_naive[k - 2] / tok_single[k - 2]:.0f} раз меньше",
                 xy=(k, tok_single[k - 2]), xytext=(24, tok_single[k - 2] * 2.4),
                 fontsize=9.5, color=C_INK,
                 arrowprops=dict(arrowstyle="->", color=C_INK, lw=1.1))

    fig.suptitle("Цена решения — это цена префилла, а не цена $L$ шагов декодирования",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "one_pass.png")
    return dict(naive=int(tok_naive[18]), shared=int(tok_shared[18]),
                single=int(tok_single[18]))


# ==========================================================================
# 3. Порядок вариантов
# ==========================================================================


def run_order(psi, M, W, unseen, N=5, seed=3):
    """Один и тот же набор вопросов, два способа получить из него ответ."""
    rng = np.random.default_rng(seed)
    x, opts, tgt = make_questions(psi, M, unseen, 120, N, seed=seed)
    s_true = score(W, x, psi, opts)                  # оценки скорера по парам

    # 1. скорер: перестановка вариантов переставляет оценки и ничего больше
    pm = np.argsort(rng.random(opts.shape), axis=1)
    s_after = score(W, x, psi, np.take_along_axis(opts, pm, axis=1))
    inv = float(np.abs(np.take_along_axis(s_true, pm, axis=1) - s_after).max())
    pick_scorer = s_true.argmax(1)
    pick_scorer_perm = np.take_along_axis(pm, s_after.argmax(1)[:, None], 1).ravel()

    # 2. те же оценки, но варианты отрендерены буквами: позиция добавляет смещение
    bias = np.array([0.9, 0.35, 0.0, -0.25, -0.5])[:N]
    logits = s_true + bias
    pick_letters = logits.argmax(1)
    s_perm = np.take_along_axis(s_true, pm, axis=1)
    pick_letters_perm = np.take_along_axis(pm, (s_perm + bias).argmax(1)[:, None], 1).ravel()

    # 3. поправка: смещение позиций оценивается по средним логитам и вычитается
    b_hat = logits.mean(0) - logits.mean()
    fixed = logits - b_hat
    pick_fixed = fixed.argmax(1)
    pick_fixed_perm = np.take_along_axis(
        pm, ((s_perm + bias) - b_hat).argmax(1)[:, None], 1).ravel()

    return dict(
        scorer_inv=inv,
        acc=[float(np.mean(pick_scorer == tgt)), float(np.mean(pick_letters == tgt)),
             float(np.mean(pick_fixed == tgt))],
        flip=[float(np.mean(pick_scorer_perm != pick_scorer)),
              float(np.mean(pick_letters_perm != pick_letters)),
              float(np.mean(pick_fixed_perm != pick_fixed))],
        b_true=bias - bias.mean(), b_hat=b_hat, n=len(tgt))


def draw_order(res):
    _apply_style()
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.8, 4.5),
                                   gridspec_kw={"width_ratios": [1.05, 1]})

    xs = np.arange(3)
    labels = ["скорер\nпо парам", "варианты\nбуквами", "буквами\n+ поправка"]
    axL.bar(xs - 0.2, res["acc"], width=0.4, color=C_BLUE,
            label="доля правильных ответов")
    axL.bar(xs + 0.2, res["flip"], width=0.4, color=C_ORANGE,
            label="ответ изменился при перестановке")
    for x, a, f in zip(xs, res["acc"], res["flip"]):
        axL.text(x - 0.2, a + 0.02, f"{a:.3f}", ha="center", fontsize=9.5)
        axL.text(x + 0.2, f + 0.02, f"{f:.1%}", ha="center", fontsize=9.5)
    axL.set_xticks(xs, labels, fontsize=9.5)
    axL.set_ylim(0, 1.2)
    axL.set_title(f"одни и те же оценки, три способа выбрать ответ\n"
                  f"(перестановочная невязка скорера: {res['scorer_inv']:.1e})",
                  fontsize=11)
    axL.legend(fontsize=9, loc="upper left", ncol=1)
    axL.grid(alpha=0.25, color=C_GRAY, lw=0.6, axis="y")
    _despine(axL)

    pos = np.arange(len(res["b_true"]))
    axR.bar(pos - 0.2, res["b_true"], width=0.4, color=C_INK, label="истинное смещение")
    axR.bar(pos + 0.2, res["b_hat"], width=0.4, color=C_GREEN,
            label="оценка по средним логитам")
    axR.axhline(0, color=C_GRAY, lw=1.0)
    axR.set_xticks(pos, [chr(ord("A") + i) for i in pos])
    axR.set_xlabel("позиция варианта в промпте")
    axR.set_ylabel("добавка к логиту")
    axR.set_title("смещение позиций оценивается и вычитается", fontsize=11.5)
    axR.legend(fontsize=9.5)
    axR.grid(alpha=0.25, color=C_GRAY, lw=0.6, axis="y")
    _despine(axR)

    fig.suptitle("«Подставить варианты буквами» — не то же самое, что скорить их напрямую",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "order_invariance.png")


# ==========================================================================
# 4. Типы вопросов: плоский softmax против порядковой головы
# ==========================================================================


def run_ordinal(K=10, sizes=(100, 300, 1000, 4000), D=40, scale=2.6, seed=0):
    rows = []
    for n_tr in sizes:
        r = np.random.default_rng(seed + n_tr)
        w = r.normal(size=D)
        w /= np.linalg.norm(w)
        n = n_tr + 4000
        X = r.normal(size=(n, D))
        f = X @ w * scale + 0.8 * r.normal(size=n)
        th = np.quantile(f, np.linspace(0, 1, K + 1)[1:-1])
        y = np.digitize(f, th)
        Xtr, Xte, ytr, yte = X[:n_tr], X[n_tr:], y[:n_tr], y[n_tr:]

        flat = LogisticRegression(max_iter=3000).fit(Xtr, ytr)
        p_flat = np.zeros((len(yte), K))
        p_flat[:, flat.classes_] = flat.predict_proba(Xte)

        def fit_ordinal(X_, y_):
            d_ = X_.shape[1]

            def unpack(v):
                return v[:d_], np.cumsum(np.concatenate([v[d_:d_ + 1], np.exp(v[d_ + 1:])]))

            def nll(v):
                ww, t = unpack(v)
                z = X_ @ ww
                P = 1 / (1 + np.exp(-(t[None, :] - z[:, None])))
                P = np.concatenate([np.zeros((len(z), 1)), P, np.ones((len(z), 1))], 1)
                pk = np.clip(np.diff(P, axis=1), 1e-9, 1)
                return -np.mean(np.log(pk[np.arange(len(y_)), y_])) + 1e-3 * ww @ ww

            v0 = np.concatenate([np.zeros(d_), [-2.0], np.log(np.ones(K - 2) * 0.5)])
            return unpack(minimize(nll, v0, method="L-BFGS-B").x)

        ww, t = fit_ordinal(Xtr, ytr)
        z = Xte @ ww
        P = 1 / (1 + np.exp(-(t[None, :] - z[:, None])))
        P = np.concatenate([np.zeros((len(z), 1)), P, np.ones((len(z), 1))], 1)
        p_ord = np.clip(np.diff(P, axis=1), 1e-9, 1)
        p_ord /= p_ord.sum(1, keepdims=True)

        out = {}
        for tag, p_ in (("flat", p_flat), ("ord", p_ord)):
            pred = p_.argmax(1)
            out[tag] = (float(np.mean(np.abs(pred - yte))),
                        float(np.mean(np.abs(pred - yte) >= 2)),
                        float(np.mean(pred == yte)))
        rows.append((n_tr, out))
    return rows, K


def draw_typed(ordinal_rows):
    _apply_style()
    rows, K = ordinal_rows
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(13.0, 4.6),
                                   gridspec_kw={"width_ratios": [1.15, 1]})
    _blank(axL, (0, 10), (0, 6.2))

    axL.text(5.0, 5.9, "одна модель, один проход — разные типы вопросов",
             ha="center", fontsize=10.5, color=C_GRAY)
    rowsd = [
        ("choice", "2…255 именованных вариантов", "softmax по вариантам", C_BLUE),
        ("score", "2…10 УПОРЯДОЧЕННЫХ уровней",
         "порядковая голова:\n$P(y \\leq k) = \\sigma(\\theta_k - f(x))$", C_GREEN),
        ("bool", "да / нет", "одна сигмоида", C_ORANGE),
    ]
    for i, (name, what, head, color) in enumerate(rowsd):
        y0 = 4.3 - i * 1.55
        _box(axL, 0.3, y0, 1.7, 1.05, name, fc=C_BG, ec=color, fs=11, tc=color)
        _box(axL, 2.3, y0, 3.5, 1.05, what, fc=C_PANEL, fs=9.5)
        _box(axL, 6.1, y0, 3.6, 1.05, head, fc="#dfe8f1" if i != 2 else "#f2d9d0", fs=9.5)
        _arrow(axL, (2.0, y0 + 0.5), (2.28, y0 + 0.5))
        _arrow(axL, (5.8, y0 + 0.5), (6.08, y0 + 0.5))

    ns = [r[0] for r in rows]
    axR.plot(ns, [r[1]["flat"][0] for r in rows], color=C_ORANGE, lw=2.4, marker="o",
             ms=6, label="плоский softmax: MAE")
    axR.plot(ns, [r[1]["ord"][0] for r in rows], color=C_GREEN, lw=2.4, marker="s",
             ms=6, label="порядковая голова: MAE")
    axR.set_xscale("log")
    axR.set_xlabel("объектов в обучении (лог)")
    axR.set_ylabel("средняя ошибка в уровнях")
    ax2 = axR.twinx()
    ax2.plot(ns, [r[1]["flat"][1] for r in rows], color=C_ORANGE, lw=1.6, ls="--")
    ax2.plot(ns, [r[1]["ord"][1] for r in rows], color=C_GREEN, lw=1.6, ls="--")
    ax2.set_ylabel("доля ошибок на 2+ уровня (пунктир)", color=C_GRAY, fontsize=9.5)
    ax2.tick_params(colors=C_GRAY)
    for s in ax2.spines.values():
        s.set_visible(False)
    axR.set_title(f"вопрос «оценка 1…{K}»: порядок уровней нельзя терять", fontsize=11.5)
    axR.legend(fontsize=9.5, loc="upper right")
    axR.grid(alpha=0.25, color=C_GRAY, lw=0.6)
    _despine(axR)

    fig.suptitle("Тип вопроса меняет не модель, а голову и разметку вариантов",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "typed_heads.png")


# ==========================================================================
# 5. Калибровка зависит от кардинальности
# ==========================================================================


def ece_top(correct, conf, bins=12):
    edges = np.quantile(conf, np.linspace(0, 1, bins + 1))
    edges[0], edges[-1] = 0.0, 1.0
    idx = np.clip(np.digitize(conf, edges[1:-1]), 0, bins - 1)
    return float(sum((idx == b).mean() * abs(correct[idx == b].mean() - conf[idx == b].mean())
                     for b in range(bins) if (idx == b).sum()))


def fit_T(logits, target):
    def nll(T):
        p = softmax(logits / T)
        return -np.mean(np.log(p[np.arange(len(target)), target] + 1e-12))

    return float(minimize_scalar(nll, bounds=(0.05, 20), method="bounded").x)


def run_cardinality(psi, M, W, unseen, Ns=(2, 4, 8, 20, 50), seed=11):
    xv, ov, tv = make_questions(psi, M, unseen, 25, 4, seed=seed)
    T4 = fit_T(score(W, xv, psi, ov), tv)
    rows = []
    for N in Ns:
        x, o, t = make_questions(psi, M, unseen, 25, N, seed=seed + N)
        lg = score(W, x, psi, o)
        T_own = fit_T(lg, t)
        entry = {"N": N, "T_own": T_own, "acc": float(np.mean(lg.argmax(1) == t))}
        for tag, T in (("raw", 1.0), ("T4", T4), ("own", T_own)):
            p = softmax(lg / T)
            pred, conf = p.argmax(1), p.max(1)
            entry[tag] = (float(conf.mean()),
                          ece_top((pred == t).astype(float), conf))
        rows.append(entry)
    return rows, T4


def draw_cardinality(card):
    _apply_style()
    rows, T4 = card
    Ns = [r["N"] for r in rows]
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.8, 4.5))

    axL.plot(Ns, [r["acc"] for r in rows], color=C_INK, lw=2.4, marker="o", ms=6,
             label="доля правильных ответов")
    axL.plot(Ns, [r["raw"][0] for r in rows], color=C_ORANGE, lw=2.2, marker="s", ms=5,
             label="средняя уверенность без поправки")
    axL.plot(Ns, [r["own"][0] for r in rows], color=C_GREEN, lw=2.2, marker="^", ms=5,
             label="средняя уверенность со своей $T$")
    axL.plot(Ns, [1 / n for n in Ns], color=C_GRAY, ls=":", lw=1.4, label="уровень угадывания")
    axL.set_xscale("log")
    axL.set_xticks(Ns, [str(n) for n in Ns])
    axL.set_xlabel("вариантов в вопросе, $N$")
    axL.set_ylabel("доля")
    axL.set_title("уверенность должна следовать за точностью", fontsize=11.5)
    axL.legend(fontsize=9)

    w = 0.26
    xs = np.arange(len(Ns))
    for k, (tag, color, label) in enumerate((
        ("raw", C_ORANGE, "без поправки"),
        ("T4", C_BLUE, f"температура с вопросов на 4 варианта ($T$ = {T4:.2f})"),
        ("own", C_GREEN, "своя температура на каждую кардинальность"),
    )):
        vals = [r[tag][1] for r in rows]
        axR.bar(xs + (k - 1) * w, vals, width=w, color=color, label=label)
    axR.set_xticks(xs, [f"$N$ = {n}\n$T$ = {r['T_own']:.2f}" for n, r in zip(Ns, rows)],
                   fontsize=9)
    axR.set_ylabel("ECE по уверенности в своём ответе")
    axR.set_title("одна температура на все типы вопросов не работает", fontsize=11.5)
    axR.legend(fontsize=8.8, loc="upper left")
    axR.grid(alpha=0.25, color=C_GRAY, lw=0.6, axis="y")

    for ax in (axL, axR):
        _despine(ax)
    axL.grid(alpha=0.25, color=C_GRAY, lw=0.6)

    fig.suptitle("Калибровка типизированного ответа зависит от числа вариантов",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "calibration_by_cardinality.png")


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    print("Генерация схем «Типизированные решающие модели»:")
    psi, M, W, Ns, rows, seen, unseen = run_head_vs_scorer()
    draw_head_vs_scorer(Ns, rows)
    cost = draw_one_pass()
    order = run_order(psi, M, W, unseen)
    draw_order(order)
    ordinal = run_ordinal()
    draw_typed(ordinal)
    card = run_cardinality(psi, M, W, unseen)
    draw_cardinality(card)

    print("\nЧисла для текста лекции:")
    for tag, (acc_s, acc_h, known) in rows.items():
        print(f"  {tag}:")
        for N, a, h, k in zip(Ns, acc_s, acc_h, known):
            print(f"    N={N:>3}: скорер {a:.3f}, фикс. голова {h:.3f} "
                  f"(вариантов ей известно {k:.0%}), случайный выбор {1 / N:.3f}")
    print(f"  токены при N=20: {cost['naive']} (N проходов) / {cost['shared']} "
          f"(общий префикс) / {cost['single']} (один проход)")
    print(f"  перестановочная инвариантность скорера: {order['scorer_inv']:.1e}")
    for tag, a, f in zip(("скорер", "буквами", "буквами + поправка"),
                         order["acc"], order["flip"]):
        print(f"    {tag:<20}: точность {a:.3f}, ответ меняется при перестановке "
              f"у {f:.1%} из {order['n']} вопросов")
    print(f"  смещение позиций: истинное {np.round(order['b_true'], 2)}, "
          f"оценка {np.round(order['b_hat'], 2)}")
    rws, K = ordinal
    for n_tr, out in rws:
        print(f"  оценка 1…{K}, обучение {n_tr:>5}: плоский MAE {out['flat'][0]:.3f} "
              f"(ошибок 2+ {out['flat'][1]:.1%}), порядковый MAE {out['ord'][0]:.3f} "
              f"(ошибок 2+ {out['ord'][1]:.1%})")
    crows, T4 = card
    print(f"  температура, подобранная на 4 вариантах: {T4:.2f}")
    for r in crows:
        print(f"    N={r['N']:>3}: acc {r['acc']:.3f}, своя T {r['T_own']:.2f}; "
              f"ECE без поправки {r['raw'][1]:.4f}, с чужой T {r['T4'][1]:.4f}, "
              f"со своей {r['own'][1]:.4f}; уверенность {r['raw'][0]:.3f} → "
              f"{r['own'][0]:.3f}")


if __name__ == "__main__":
    main()
