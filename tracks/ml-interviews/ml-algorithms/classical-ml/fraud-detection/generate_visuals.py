"""Точные схемы для темы «Детекция мошенничества».

Все числа на картинках — результат прогона на симулированном потоке транзакций,
а не подобранные вручную значения: ROC и PR считаются на одних и тех же оценках
модели при разной доле мошенничества, стоимость — на настоящих суммах транзакций,
дрейф — на потоке, где смесь схем меняется от месяца к месяцу.

Данные симулированы намеренно: открытые датасеты по фроду либо анонимизированы до
неузнаваемости (PCA-компоненты вместо признаков), либо не содержат времени и сумм,
без которых половина выводов этой темы непроверяема.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier, IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)
from sklearn.preprocessing import StandardScaler

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


# ==========================================================================
# Симулятор потока транзакций
# ==========================================================================

FEATURES = ["log_amount", "hour", "account_age", "tx_1h", "device_share",
            "country_mismatch", "new_payee", "amount_vs_median"]

# три схемы мошенничества и признаки, на которых они выдают себя
ATTACKS = {
    "перебор карт": {"log_amount": -1.2, "tx_1h": 2.6, "new_payee": 0.9},
    "угон аккаунта": {"account_age": -1.4, "country_mismatch": 0.95,
                      "amount_vs_median": 2.2},
    "дропы": {"device_share": 2.4, "new_payee": 0.8, "log_amount": 0.9},
}
ATTACK_NAMES = list(ATTACKS)


def simulate(n, rng, prevalence=0.007, mix=(0.6, 0.4, 0.0)):
    """Поток транзакций: признаки, метка, сумма и схема мошенничества."""
    X = np.zeros((n, len(FEATURES)))
    X[:, 0] = rng.normal(0, 1, n)                      # логарифм суммы
    X[:, 1] = rng.normal(0, 1, n)                      # час суток
    X[:, 2] = rng.normal(0, 1, n)                      # возраст аккаунта
    X[:, 3] = rng.gamma(1.5, 0.7, n) - 1.05            # транзакций за час
    X[:, 4] = rng.gamma(1.2, 0.6, n) - 0.72            # устройство делят n аккаунтов
    X[:, 5] = (rng.random(n) < 0.08).astype(float)     # страна не совпала
    X[:, 6] = (rng.random(n) < 0.25).astype(float)     # новый получатель
    X[:, 7] = rng.normal(0, 1, n)                      # сумма против медианы клиента

    y = (rng.random(n) < prevalence).astype(int)
    idx = np.where(y == 1)[0]
    mix = np.array(mix, dtype=float)
    kinds = rng.choice(ATTACK_NAMES, size=len(idx), p=mix / mix.sum())
    for i, kind in zip(idx, kinds):
        for f, s in ATTACKS[kind].items():
            j = FEATURES.index(f)
            if f in ("country_mismatch", "new_payee"):
                X[i, j] = float(rng.random() < s)
            else:
                X[i, j] += s * rng.normal(1.0, 0.35)

    amount = np.exp(1.8 + 0.9 * X[:, 0]) * 10          # сумма в деньгах
    kind_all = np.full(n, "", dtype=object)
    kind_all[idx] = kinds
    return X, y, amount, kind_all


def fit_gbm(X, y, seed=0):
    return HistGradientBoostingClassifier(
        max_iter=150, learning_rate=0.08, max_leaf_nodes=15,
        early_stopping=False, random_state=seed,
    ).fit(X, y)


def recall_at_budget(y, score, budget):
    """Доля пойманного фрода, если проверять budget-долю транзакций с верхушки."""
    k = max(int(round(budget * len(score))), 1)
    top = np.argsort(score)[::-1][:k]
    caught = y[top].sum()
    return caught / max(y.sum(), 1), caught / k


# ==========================================================================
# 1. Доля класса: ROC не замечает, PR замечает
# ==========================================================================


def draw_imbalance_metrics(y_true, score, y_pool, score_pool, seed=0):
    """Одни и те же оценки модели при разной доле мошенничества."""
    _apply_style()
    rng = np.random.default_rng(seed)
    pos = np.where(y_true == 1)[0]
    neg_pool = np.where(y_pool == 0)[0]

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.4, 4.6))
    rows = []
    n_pos = 400
    take_pos = rng.choice(pos, size=n_pos, replace=False)
    for prev, color in [(0.05, C_GREEN), (0.01, C_BLUE), (0.002, C_ORANGE)]:
        n_neg = int(n_pos * (1 - prev) / prev)
        assert n_neg <= len(neg_pool), (prev, n_neg, len(neg_pool))
        take_neg = rng.choice(neg_pool, size=n_neg, replace=False)
        y = np.concatenate([np.ones(n_pos, int), np.zeros(n_neg, int)])
        s_ = np.concatenate([score[take_pos], score_pool[take_neg]])

        auc = roc_auc_score(y, s_)
        ap = average_precision_score(y, s_)
        fpr, tpr, _ = roc_curve(y, s_)
        prec, rec, _ = precision_recall_curve(y, s_)
        rows.append((prev, auc, ap, y.mean(), ap / y.mean()))

        axL.plot(fpr, tpr, color=color, lw=2.2,
                 label=f"доля фрода {prev:.1%}: ROC-AUC {auc:.3f}")
        axR.plot(rec, prec, color=color, lw=2.2,
                 label=f"доля фрода {prev:.1%}: AP {ap:.3f}")
        axR.axhline(y.mean(), color=color, ls=":", lw=1.2)

    axL.plot([0, 1], [0, 1], color=C_GRAY, ls="--", lw=1.2)
    axL.set_xlabel("FPR")
    axL.set_ylabel("TPR (recall)")
    axL.set_title("ROC: три кривые лежат друг на друге", fontsize=11.5)
    axL.legend(fontsize=9.5, loc="lower right")

    axR.set_xlabel("recall")
    axR.set_ylabel("precision")
    axR.set_title("PR на тех же оценках: пунктир — базовый уровень", fontsize=11.5)
    axR.legend(fontsize=9.5, loc="upper right")
    axR.set_ylim(0, 1.02)

    for ax in (axL, axR):
        ax.grid(alpha=0.25, color=C_GRAY, lw=0.6)
        _despine(ax)

    fig.suptitle(
        "Модель одна и та же; меняется только доля мошенничества в выборке",
        fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "imbalance_metrics.png")
    return rows


# ==========================================================================
# 2. Порог — это решение о деньгах, а не о классе
# ==========================================================================


def draw_cost_threshold(y, score, amount, c_fp=4.0, seed=0):
    """Ожидаемые потери против порога, бюджета проверок и правила с учётом суммы."""
    _apply_style()
    order = np.argsort(score)[::-1]
    y_s, a_s, p_s = y[order], amount[order], score[order]
    n = len(y)

    def cost_of(block):
        return c_fp * np.sum(block & (y == 0)) + np.sum(amount[(~block) & (y == 1)])

    missed = np.sum(a_s * y_s) - np.concatenate([[0], np.cumsum(a_s * y_s)])
    false_alarms = np.concatenate([[0], np.cumsum(1 - y_s)])
    total = missed + c_fp * false_alarms
    k_star = int(np.argmin(total))
    thr_star = p_s[min(k_star, len(p_s) - 1)]
    k_half = int((p_s > 0.5).sum())
    cost_none = total[0]

    # решение с учётом суммы: блокировать, если ожидаемая потеря больше цены отказа
    aware = score * amount > c_fp
    cost_aware = cost_of(aware)
    k_aware = int(aware.sum())

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.6, 4.6))

    frac = np.arange(len(total)) / n * 100
    rel = total / cost_none * 100
    axL.plot(frac[1:], rel[1:], color=C_INK, lw=2.4, label="фиксированный порог")
    axL.axhline(100, color=C_GRAY, ls="--", lw=1.3)
    axL.text(0.012, 101, "ничего не блокировать", fontsize=9.5, color=C_GRAY)

    axL.scatter([k_star / n * 100], [rel[k_star]], color=C_GREEN, s=55, zorder=5)
    axL.annotate(f"лучший порог {thr_star:.3f}\n{k_star / n * 100:.1f}% алертов, "
                 f"{rel[k_star]:.0f}% потерь",
                 xy=(k_star / n * 100, rel[k_star]),
                 xytext=(2.9, rel[k_star] - 3), fontsize=9.5, color=C_GREEN,
                 arrowprops=dict(arrowstyle="->", color=C_GREEN, lw=1.1))
    axL.scatter([k_half / n * 100], [rel[k_half]], color=C_ORANGE, s=55, zorder=5)
    axL.annotate(f"порог 0.5: {rel[k_half]:.0f}%",
                 xy=(k_half / n * 100, rel[k_half]),
                 xytext=(0.02, rel[k_half] + 6), fontsize=9.5, color=C_ORANGE,
                 arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=1.1))

    axL.axhline(cost_aware / cost_none * 100, color=C_BLUE, ls="-.", lw=1.8)
    axL.text(0.012, cost_aware / cost_none * 100 - 7,
             f"правило «$p \\cdot$ сумма > {c_fp:.0f}»: "
             f"{cost_aware / cost_none * 100:.0f}% потерь при {k_aware / n * 100:.1f}% алертов",
             fontsize=9.5, color=C_BLUE)

    axL.set_xscale("log")
    axL.set_xlim(0.01, 20)
    axL.set_ylim(min(rel.min(), cost_aware / cost_none * 100) - 12, 118)
    axL.set_xlabel("доля транзакций в алерте, % (лог)")
    axL.set_ylabel("потери, % от «ничего не делать»")
    axL.set_title("потери = пропущенные суммы + цена ложных тревог", fontsize=11.5)
    axL.legend(fontsize=9.5, loc="upper right")

    budgets = np.array([0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05])
    rec = [recall_at_budget(y, score, b)[0] for b in budgets]
    prec = [recall_at_budget(y, score, b)[1] for b in budgets]
    axR.plot(budgets * 100, rec, color=C_ORANGE, lw=2.2, marker="o", ms=5,
             label="recall: какую долю фрода ловим")
    axR.plot(budgets * 100, prec, color=C_BLUE, lw=2.2, marker="s", ms=5,
             label="precision: какая доля алертов — фрод")
    for b, r, pr in zip(budgets, rec, prec):
        if b in (0.001, 0.01):
            axR.annotate(f"{r:.0%}", xy=(b * 100, r), xytext=(b * 100, r + 0.05),
                         fontsize=9.5, color=C_ORANGE, ha="center")
            axR.annotate(f"{pr:.0%}", xy=(b * 100, pr), xytext=(b * 100, pr + 0.05),
                         fontsize=9.5, color=C_BLUE, ha="center")
    axR.set_xscale("log")
    axR.set_xlabel("бюджет проверок, % транзакций (лог)")
    axR.set_ylabel("доля")
    axR.set_ylim(0, 1.05)
    axR.set_title("рабочая точка задаётся ёмкостью команды", fontsize=11.5)
    axR.legend(fontsize=9.5, loc="center left")

    for ax in (axL, axR):
        ax.grid(alpha=0.25, color=C_GRAY, lw=0.6)
        _despine(ax)

    fig.suptitle("Порог не берут равным 0.5: его считают из стоимости ошибок",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "cost_threshold.png")
    return dict(k_star=k_star, thr_star=thr_star, cost_star=total[k_star],
                cost_half=total[k_half], k_half=k_half, n=n, cost_none=cost_none,
                cost_aware=cost_aware, k_aware=k_aware,
                cost_same_budget=total[min(k_aware, len(total) - 1)],
                budgets=budgets, recalls=rec, precisions=prec)


# ==========================================================================
# 3. Валидация по времени: случайное разбиение врёт
# ==========================================================================

MIX_BY_MONTH = [
    (0.60, 0.40, 0.00), (0.60, 0.40, 0.00), (0.58, 0.42, 0.00), (0.57, 0.43, 0.00),
    (0.55, 0.45, 0.00), (0.55, 0.42, 0.03), (0.50, 0.40, 0.10), (0.45, 0.37, 0.18),
    (0.38, 0.32, 0.30), (0.32, 0.28, 0.40), (0.28, 0.24, 0.48), (0.25, 0.20, 0.55),
]


def run_stream(rng, n_per_month=22_000):
    months = []
    for mix in MIX_BY_MONTH:
        months.append(simulate(n_per_month, rng, mix=mix))
    return months


def draw_temporal(months, train_upto=7, seed=0):
    """Случайная кросс-валидация против честной проверки на будущем."""
    _apply_style()
    Xtr = np.vstack([m[0] for m in months[: train_upto + 1]])
    ytr = np.concatenate([m[1] for m in months[: train_upto + 1]])

    # случайное разбиение внутри обучающего периода
    idx = np.arange(len(ytr))
    np.random.default_rng(seed).shuffle(idx)
    cut = int(0.75 * len(idx))
    m_rand = fit_gbm(Xtr[idx[:cut]], ytr[idx[:cut]], seed)
    ap_random = average_precision_score(ytr[idx[cut:]],
                                        m_rand.predict_proba(Xtr[idx[cut:]])[:, 1])

    # честно: обучаемся на прошлом, проверяемся на каждом будущем месяце
    model = fit_gbm(Xtr, ytr, seed)
    future = range(train_upto + 1, len(months))
    ap_future, ap_retrain = [], []
    for t in future:
        Xt, yt = months[t][0], months[t][1]
        ap_future.append(average_precision_score(yt, model.predict_proba(Xt)[:, 1]))
        Xr = np.vstack([m[0] for m in months[:t]])
        yr = np.concatenate([m[1] for m in months[:t]])
        m_r = fit_gbm(Xr, yr, seed)
        ap_retrain.append(average_precision_score(yt, m_r.predict_proba(Xt)[:, 1]))

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.6, 4.5),
                                   gridspec_kw={"width_ratios": [0.85, 1.15]})

    vals = [ap_random, ap_future[0], float(np.mean(ap_future))]
    labels = ["случайное\nразбиение", "первый месяц\nпосле обучения",
              "в среднем по\nчетырём месяцам"]
    axL.bar(np.arange(3), vals, color=[C_ORANGE, C_BLUE, C_GREEN], width=0.62)
    for x, v in enumerate(vals):
        axL.text(x, v + 0.012, f"{v:.3f}", ha="center", fontsize=10)
    axL.set_xticks(np.arange(3), labels, fontsize=9)
    axL.set_ylabel("average precision")
    axL.set_ylim(0, max(vals) * 1.25)
    axL.set_title("одна и та же модель, три оценки качества", fontsize=11.5)

    xs = list(future)
    axR.plot(xs, ap_future, color=C_BLUE, lw=2.2, marker="o", ms=5,
             label="модель заморожена")
    axR.plot(xs, ap_retrain, color=C_GREEN, lw=2.2, marker="s", ms=5,
             label="переобучение каждый месяц")
    axR.axhline(ap_random, color=C_ORANGE, ls="--", lw=1.4,
                label=f"оценка по случайному разбиению: {ap_random:.3f}")
    mule_share = [MIX_BY_MONTH[t][2] for t in xs]
    ax2 = axR.twinx()
    ax2.plot(xs, mule_share, color=C_GRAY, lw=1.6, ls=":")
    ax2.set_ylabel("доля новой схемы в потоке", color=C_GRAY, fontsize=9.5)
    ax2.tick_params(colors=C_GRAY)
    ax2.set_ylim(0, 0.75)
    for s in ax2.spines.values():
        s.set_visible(False)
    axR.set_xticks(xs, [str(t) for t in xs])
    axR.set_xlabel("месяц")
    axR.set_ylabel("average precision")
    axR.text(xs[-1], 0.10, "точками — доля новой схемы\nв потоке (правая ось)",
             fontsize=9, color=C_GRAY, ha="right")
    axR.set_ylim(0, max(ap_random, max(ap_retrain)) * 1.15)
    axR.set_title("качество падает вместе с приходом новой схемы", fontsize=11.5)
    axR.legend(fontsize=9.5, loc="lower left")

    for ax in (axL, axR):
        ax.grid(alpha=0.25, color=C_GRAY, lw=0.6, axis="y")
        _despine(ax)

    fig.suptitle("Противник меняется: случайная кросс-валидация меряет вчерашний мир",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "temporal_validation.png")
    return dict(ap_random=ap_random, ap_future=ap_future, ap_retrain=ap_retrain)


# ==========================================================================
# 4. Борьба с дисбалансом: что она делает с ранжированием и с калибровкой
# ==========================================================================


def smote(X, y, rng, k=5, ratio=1.0):
    """SMOTE вручную: интерполяция между соседями внутри миноритарного класса."""
    pos = X[y == 1]
    n_new = int(ratio * (np.sum(y == 0) - np.sum(y == 1)))
    d = ((pos[:, None, :] - pos[None, :, :]) ** 2).sum(-1)
    np.fill_diagonal(d, np.inf)
    nn = np.argsort(d, axis=1)[:, :k]
    i = rng.integers(0, len(pos), n_new)
    j = nn[i, rng.integers(0, k, n_new)]
    lam = rng.random((n_new, 1))
    X_new = pos[i] + lam * (pos[j] - pos[i])
    return np.vstack([X, X_new]), np.concatenate([y, np.ones(n_new, int)])


def draw_resampling(Xtr, ytr, Xte, yte, rng, seed=0):
    """AP, калибровка и порог у четырёх способов обращения с дисбалансом."""
    _apply_style()
    scaler = StandardScaler().fit(Xtr)
    Xs, Xts = scaler.transform(Xtr), scaler.transform(Xte)

    variants = {}
    variants["как есть"] = LogisticRegression(max_iter=2000).fit(Xs, ytr)
    variants["class_weight='balanced'"] = LogisticRegression(
        max_iter=2000, class_weight="balanced").fit(Xs, ytr)

    neg = np.where(ytr == 0)[0]
    pos = np.where(ytr == 1)[0]
    keep = np.concatenate([pos, rng.choice(neg, size=len(pos) * 3, replace=False)])
    variants["undersampling 1:3"] = LogisticRegression(max_iter=2000).fit(
        Xs[keep], ytr[keep])

    Xsm, ysm = smote(Xs[np.concatenate([pos, rng.choice(neg, 20_000, replace=False)])],
                     np.concatenate([np.ones(len(pos), int), np.zeros(20_000, int)]),
                     rng, ratio=1.0)
    variants["SMOTE до 1:1"] = LogisticRegression(max_iter=2000).fit(Xsm, ysm)

    colors = [C_INK, C_GREEN, C_BLUE, C_ORANGE]
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.6, 4.6),
                                   gridspec_kw={"width_ratios": [0.9, 1.1]})
    rows = []
    for (name, m), color in zip(variants.items(), colors):
        p = m.predict_proba(Xts)[:, 1]
        ap = average_precision_score(yte, p)
        brier = brier_score_loss(yte, p)
        rec5, _ = recall_at_budget(yte, p, 0.005)
        rows.append((name, ap, brier, p.mean(), rec5, color))

    xs = np.arange(len(rows))
    axL.bar(xs, [r[1] for r in rows], color=[r[5] for r in rows], width=0.62)
    for x, r in zip(xs, rows):
        axL.text(x, r[1] + 0.008, f"{r[1]:.3f}", ha="center", fontsize=10)
    axL.set_xticks(xs, [r[0].replace(" ", "\n", 1) for r in rows], fontsize=8.5)
    axL.set_ylabel("average precision")
    axL.set_ylim(0, max(r[1] for r in rows) * 1.3)
    axL.set_title("ранжирование почти не меняется", fontsize=11.5)
    axL.grid(alpha=0.25, color=C_GRAY, lw=0.6, axis="y")
    _despine(axL)

    # калибровка: средняя предсказанная вероятность против фактической доли
    axR.plot([0, 1], [0, 1], color=C_GRAY, ls="--", lw=1.2)
    for name, _ap, _brier, mean_p, _rec5, color in rows:
        m = variants[name]
        p = m.predict_proba(Xts)[:, 1]
        qs = np.quantile(p, np.linspace(0, 1, 11))
        qs[-1] += 1e-9
        b = np.digitize(p, qs[1:-1])
        xs_, ys_ = [], []
        for k in range(10):
            mask = b == k
            if mask.sum() > 50:
                xs_.append(p[mask].mean())
                ys_.append(yte[mask].mean())
        axR.plot(xs_, ys_, color=color, lw=2.0, marker="o", ms=4,
                 label=f"{name}: средний скор {mean_p:.3f} при доле фрода {yte.mean():.3f}")
    axR.set_xscale("log")
    axR.set_yscale("log")
    axR.set_xlabel("средняя предсказанная вероятность в децили (лог)")
    axR.set_ylabel("фактическая доля фрода (лог)")
    axR.set_title("калибровка: пунктир — идеал", fontsize=11.5)
    axR.legend(fontsize=8.5, loc="upper left")
    axR.grid(alpha=0.25, color=C_GRAY, lw=0.6, which="both")
    _despine(axR)

    fig.suptitle("Переcэмплирование не улучшает ранжирование, но ломает вероятности",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "resampling_calibration.png")
    return rows


# ==========================================================================
# 5. Supervised против поиска аномалий: известная схема и новая
# ==========================================================================


def draw_supervised_vs_anomaly(Xtr, ytr, months, seed=0):
    """Что ловит модель с учителем, а что — детектор аномалий."""
    _apply_style()
    model = fit_gbm(Xtr, ytr, seed)
    iso = IsolationForest(n_estimators=300, random_state=seed,
                          contamination=0.01).fit(Xtr[ytr == 0])

    Xte = np.vstack([m[0] for m in months[8:]])
    yte = np.concatenate([m[1] for m in months[8:]])
    kinds = np.concatenate([m[3] for m in months[8:]])

    p_sup = model.predict_proba(Xte)[:, 1]
    p_iso = -iso.score_samples(Xte)

    budget = 0.01
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.6, 4.5))

    rows = []
    for name in ATTACK_NAMES:
        mask = kinds == name
        rec_s = recall_at_budget_subset(yte, p_sup, mask, budget)
        rec_i = recall_at_budget_subset(yte, p_iso, mask, budget)
        rows.append((name, mask.sum(), rec_s, rec_i))

    xs = np.arange(len(rows))
    axL.bar(xs - 0.2, [r[2] for r in rows], width=0.4, color=C_ORANGE,
            label="модель с учителем")
    axL.bar(xs + 0.2, [r[3] for r in rows], width=0.4, color=C_BLUE,
            label="Isolation Forest")
    for x, r in zip(xs, rows):
        axL.text(x - 0.2, r[2] + 0.015, f"{r[2]:.2f}", ha="center", fontsize=9)
        axL.text(x + 0.2, r[3] + 0.015, f"{r[3]:.2f}", ha="center", fontsize=9)
    axL.set_xticks(xs, [f"{r[0]}\n(n = {r[1]})" for r in rows], fontsize=9)
    axL.set_ylabel(f"recall при бюджете {budget:.0%} транзакций")
    axL.set_ylim(0, 1.05)
    axL.axvline(1.5, color=C_GRAY, ls=":", lw=1.2)
    axL.text(2.0, 0.95, "новая схема:\nв обучении её не было",
             ha="center", fontsize=9.5, color=C_INK)
    axL.set_title("что ловит каждая модель по схемам", fontsize=11.5)
    axL.legend(fontsize=9.5, loc="upper left")

    for p, color, name in [(p_sup, C_ORANGE, "модель с учителем"),
                           (p_iso, C_BLUE, "Isolation Forest")]:
        prec, rec, _ = precision_recall_curve(yte, p)
        ap = average_precision_score(yte, p)
        axR.plot(rec, prec, color=color, lw=2.2, label=f"{name}: AP {ap:.3f}")
    axR.axhline(yte.mean(), color=C_GRAY, ls=":", lw=1.2)
    axR.text(0.55, yte.mean() * 1.5, f"базовый уровень {yte.mean():.3%}",
             fontsize=9.5, color=C_GRAY)
    axR.set_xlabel("recall")
    axR.set_ylabel("precision")
    axR.set_yscale("log")
    axR.set_title("на всём потоке вместе", fontsize=11.5)
    axR.legend(fontsize=9.5)

    for ax in (axL, axR):
        ax.grid(alpha=0.25, color=C_GRAY, lw=0.6)
        _despine(ax)

    fig.suptitle("Аномалия и мошенничество — не одно и то же, но иногда это спасает",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "supervised_vs_anomaly.png")
    return rows, average_precision_score(yte, p_sup), average_precision_score(yte, p_iso)


def recall_at_budget_subset(y, score, subset_mask, budget):
    """Какую долю подмножества (схемы) ловим в топ-budget всех транзакций."""
    k = max(int(round(budget * len(score))), 1)
    thr = np.partition(score, -k)[-k]
    if subset_mask.sum() == 0:
        return 0.0
    return float((score[subset_mask] >= thr).mean())


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    print("Генерация схем «Детекция мошенничества»:")
    rng = np.random.default_rng(0)

    months = run_stream(rng)
    Xtr = np.vstack([m[0] for m in months[:8]])
    ytr = np.concatenate([m[1] for m in months[:8]])
    Xte = np.vstack([m[0] for m in months[8:]])
    yte = np.concatenate([m[1] for m in months[8:]])

    # базовая модель на «спокойных» данных для метрик и порога
    X0, y0, a0, _ = simulate(90_000, rng)
    X1, y1, a1, _ = simulate(90_000, rng)
    base = fit_gbm(X0, y0)
    s1 = base.predict_proba(X1)[:, 1]
    # отдельный большой пул легитимных транзакций — чтобы собирать любую долю фрода
    X2, y2, _, _ = simulate(220_000, rng, prevalence=0.0)
    s2 = base.predict_proba(X2)[:, 1]
    print(f"  базовая модель: ROC-AUC {roc_auc_score(y1, s1):.3f}, "
          f"AP {average_precision_score(y1, s1):.3f}, доля фрода {y1.mean():.4f}")

    rows_imb = draw_imbalance_metrics(y1, s1, y2, s2)
    cost = draw_cost_threshold(y1, s1, a1)
    temporal = draw_temporal(months)
    resamp = draw_resampling(Xtr, ytr, Xte, yte, rng)
    attacks, ap_sup, ap_iso = draw_supervised_vs_anomaly(Xtr, ytr, months)

    print("\nЧисла для текста лекции:")
    for prev, auc, ap, real, lift in rows_imb:
        print(f"  доля фрода {prev:.3%}: ROC-AUC {auc:.3f}, AP {ap:.3f} "
              f"(базовый уровень {real:.3%}, во сколько раз лучше базового: {lift:.0f})")
    print(f"  порог по стоимости: {cost['thr_star']:.3f}, "
          f"{cost['k_star'] / cost['n']:.3%} алертов, потери {cost['cost_star']:.0f} "
          f"({cost['cost_star'] / cost['cost_none']:.0%} от «ничего не делать»)")
    print(f"  порог 0.5: {cost['k_half'] / cost['n']:.3%} алертов, "
          f"потери {cost['cost_half']:.0f} "
          f"({cost['cost_half'] / cost['cost_star']:.1f}× оптимума)")
    print(f"  ничего не блокировать: {cost['cost_none']:.0f}")
    print(f"  правило p·сумма: потери {cost['cost_aware']:.0f} "
          f"({cost['cost_aware'] / cost['cost_none']:.0%} от «ничего не делать») "
          f"при {cost['k_aware'] / cost['n']:.2%} алертов; "
          f"фикс. порог при том же числе алертов — {cost['cost_same_budget']:.0f}")
    for b, r, p in zip(cost["budgets"], cost["recalls"], cost["precisions"]):
        print(f"    бюджет {b:.2%}: recall {r:.3f}, precision {p:.3f}")
    print(f"  AP по случайному разбиению: {temporal['ap_random']:.3f}")
    print(f"  AP на будущих месяцах: "
          f"{', '.join(f'{v:.3f}' for v in temporal['ap_future'])}")
    print(f"  AP с ежемесячным переобучением: "
          f"{', '.join(f'{v:.3f}' for v in temporal['ap_retrain'])}")
    for name, ap, brier, mean_p, rec5, _ in resamp:
        print(f"  {name:<26}: AP {ap:.3f}, Brier {brier:.5f}, "
              f"средний скор {mean_p:.4f}, recall@0.5% {rec5:.3f}")
    for name, n, rec_s, rec_i in attacks:
        print(f"  {name:<14} (n={n:4d}): recall@1% — с учителем {rec_s:.3f}, "
              f"Isolation Forest {rec_i:.3f}")
    print(f"  AP на всём потоке: с учителем {ap_sup:.3f}, Isolation Forest {ap_iso:.3f}")


if __name__ == "__main__":
    main()
