"""Точные схемы для темы «Калибровка вероятностей».

Все числа на картинках — результат прогона, а не подобранные вручную значения:
диаграммы надёжности строятся по обученным моделям, ECE и разложение Брайера
считаются по одним и тем же предсказаниям, температура подбирается на валидации,
а денежный эксперимент сравнивает политики при неизменном ранжировании.
"""

import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize_scalar
from sklearn.datasets import make_classification
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier

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


# ==========================================================================
# Метрики калибровки
# ==========================================================================


def ece(y, p, bins=15, strategy="uniform"):
    """Expected Calibration Error: средний по бинам разрыв |точность − уверенность|."""
    if strategy == "uniform":
        edges = np.linspace(0, 1, bins + 1)
    else:
        edges = np.quantile(p, np.linspace(0, 1, bins + 1))
        edges[0], edges[-1] = 0.0, 1.0
    idx = np.clip(np.digitize(p, edges[1:-1]), 0, bins - 1)
    out = 0.0
    for b in range(bins):
        m = idx == b
        if m.sum():
            out += m.mean() * abs(y[m].mean() - p[m].mean())
    return float(out)


def reliability(y, p, bins=12):
    """Точки диаграммы надёжности: (средняя уверенность, фактическая доля, вес)."""
    edges = np.quantile(p, np.linspace(0, 1, bins + 1))
    edges[0], edges[-1] = 0.0, 1.0
    idx = np.clip(np.digitize(p, edges[1:-1]), 0, bins - 1)
    xs, ys, ws = [], [], []
    for b in range(bins):
        m = idx == b
        if m.sum() > 20:
            xs.append(p[m].mean())
            ys.append(y[m].mean())
            ws.append(m.mean())
    return np.array(xs), np.array(ys), np.array(ws)


def brier_decomposition(y, p, bins=15):
    """BS = reliability − resolution + uncertainty (Murphy, 1973)."""
    edges = np.linspace(0, 1, bins + 1)
    idx = np.clip(np.digitize(p, edges[1:-1]), 0, bins - 1)
    base = y.mean()
    rel = res = 0.0
    for b in range(bins):
        m = idx == b
        if m.sum():
            w = m.mean()
            rel += w * (p[m].mean() - y[m].mean()) ** 2
            res += w * (y[m].mean() - base) ** 2
    return float(rel), float(res), float(base * (1 - base))


def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def fit_temperature(y, p):
    """Температурная шкала: один параметр, подбирается по логлоссу на валидации."""
    z = logit(p)

    def nll(T):
        q = 1 / (1 + np.exp(-z / T))
        return -np.mean(y * np.log(q + 1e-12) + (1 - y) * np.log(1 - q + 1e-12))

    return float(minimize_scalar(nll, bounds=(0.05, 20), method="bounded").x)


def apply_temperature(p, T):
    return 1 / (1 + np.exp(-logit(p) / T))


# ==========================================================================
# Общие данные и модели
# ==========================================================================


def make_split(n=40_000, seed=0):
    X, y = make_classification(n_samples=n, n_features=20, n_informative=8,
                               n_redundant=4, class_sep=0.8, flip_y=0.03,
                               random_state=seed)
    Xtr, Xr, ytr, yr = train_test_split(X, y, test_size=0.7, random_state=seed,
                                        stratify=y)
    Xval, Xte, yval, yte = train_test_split(Xr, yr, test_size=0.5, random_state=seed,
                                            stratify=yr)
    return Xtr, ytr, Xval, yval, Xte, yte


def fit_models(Xtr, ytr, seed=0):
    return {
        "логистическая регрессия": LogisticRegression(max_iter=2000).fit(Xtr, ytr),
        "случайный лес": RandomForestClassifier(n_estimators=300,
                                                random_state=seed).fit(Xtr, ytr),
        "градиентный бустинг": HistGradientBoostingClassifier(
            max_iter=400, random_state=seed).fit(Xtr, ytr),
        "нейросеть 256×256": MLPClassifier(hidden_layer_sizes=(256, 256), max_iter=800,
                                           random_state=seed).fit(Xtr, ytr),
    }


# ==========================================================================
# 1. Диаграммы надёжности
# ==========================================================================


def draw_reliability(models, Xte, yte, Xval, yval):
    _apply_style()
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.4, 4.8),
                                   gridspec_kw={"width_ratios": [1.1, 1]})
    colors = [C_INK, C_BLUE, C_ORANGE, C_GREEN]
    rows = []

    axL.plot([0, 1], [0, 1], color=C_GRAY, ls="--", lw=1.4, label="идеальная калибровка")
    for (name, m), color in zip(models.items(), colors):
        p = m.predict_proba(Xte)[:, 1]
        xs, ys, _ = reliability(yte, p)
        e = ece(yte, p)
        T = fit_temperature(yval, m.predict_proba(Xval)[:, 1])
        rows.append((name, e, brier_score_loss(yte, p), roc_auc_score(yte, p),
                     m.score(Xte, yte), T, color))
        axL.plot(xs, ys, color=color, lw=2.2, marker="o", ms=5,
                 label=f"{name}: ECE {e:.3f}")
    axL.set_xlabel("предсказанная вероятность")
    axL.set_ylabel("фактическая доля положительных")
    axL.set_title("диаграмма надёжности (бины равной массы)", fontsize=11.5)
    axL.legend(fontsize=9.5, loc="upper left")
    axL.set_xlim(0, 1)
    axL.set_ylim(0, 1)

    xs = np.arange(len(rows))
    axR.bar(xs, [r[5] for r in rows], color=[r[6] for r in rows], width=0.6)
    axR.axhline(1.0, color=C_GRAY, ls="--", lw=1.4)
    for x, r in zip(xs, rows):
        axR.text(x, r[5] + 0.06, f"T = {r[5]:.2f}\nECE {r[1]:.3f}", ha="center",
                 fontsize=9.5)
    axR.text(-0.42, 1.05, "$T = 1$: поправка не нужна", fontsize=9.5, color=C_GRAY)
    axR.set_xticks(xs, [r[0].replace(" ", "\n", 1) for r in rows], fontsize=9)
    axR.set_ylim(0, max(r[5] for r in rows) * 1.45)
    axR.set_ylabel("подобранная температура $T$")
    axR.set_title("$T > 1$ — переуверенность, $T < 1$ — недоуверенность", fontsize=11.5)
    axR.grid(alpha=0.25, color=C_GRAY, lw=0.6, axis="y")

    for ax in (axL, axR):
        _despine(ax)
    axL.grid(alpha=0.25, color=C_GRAY, lw=0.6)

    fig.suptitle("Одинаково точные модели врут о своей уверенности по-разному",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "reliability_diagrams.png")
    return rows


# ==========================================================================
# 2. Калибровка — не полезность
# ==========================================================================


def draw_not_usefulness(models, Xte, yte, ytr):
    _apply_style()
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.4, 4.5),
                                   gridspec_kw={"width_ratios": [1, 1.25]})

    p_const = np.full(len(yte), ytr.mean())
    e_const = ece(yte, p_const)
    b_const = brier_score_loss(yte, p_const)
    rel_c, res_c, unc_c = brier_decomposition(yte, p_const)

    best_name, best_model = max(models.items(),
                                key=lambda kv: roc_auc_score(yte, kv[1].predict_proba(Xte)[:, 1]))
    p_best = best_model.predict_proba(Xte)[:, 1]

    labels = ["константа\n$p = \\bar{y}$", best_name.replace(" ", "\n", 1)]
    metrics = [("ECE", [e_const, ece(yte, p_best)], C_ORANGE),
               ("Brier", [b_const, brier_score_loss(yte, p_best)], C_BLUE),
               ("ROC-AUC", [0.5, roc_auc_score(yte, p_best)], C_GREEN)]
    xs = np.arange(2)
    w = 0.26
    for k, (mname, vals, color) in enumerate(metrics):
        axL.bar(xs + (k - 1) * w, vals, width=w, color=color, label=mname)
        for x, v in zip(xs, vals):
            axL.text(x + (k - 1) * w, v + 0.012, f"{v:.3f}", ha="center", fontsize=9)
    axL.set_xticks(xs, labels, fontsize=9.5)
    axL.set_ylim(0, 1.05)
    axL.set_ylabel("значение метрики")
    axL.set_title("идеальная калибровка при нулевой пользе", fontsize=11.5)
    axL.legend(fontsize=9.5, ncol=3, loc="upper center")

    names, rels, ress = ["константа"], [rel_c], [res_c]
    for name, m in models.items():
        p = m.predict_proba(Xte)[:, 1]
        rel, res, unc = brier_decomposition(yte, p)
        names.append(name)
        rels.append(rel)
        ress.append(res)
    xs = np.arange(len(names))
    axR.bar(xs, rels, width=0.6, color=C_ORANGE,
            label="reliability: штраф за плохую калибровку (меньше — лучше)")
    axR.bar(xs, ress, width=0.6, bottom=0, color=C_BLUE, alpha=0.0)
    axR2 = axR.twinx()
    axR2.plot(xs, ress, color=C_BLUE, lw=2.4, marker="s", ms=7,
              label="resolution: насколько модель различает объекты (больше — лучше)")
    axR2.set_ylabel("resolution", color=C_BLUE)
    axR2.tick_params(colors=C_BLUE)
    axR2.set_ylim(0, max(ress) * 1.25)
    for s in axR2.spines.values():
        s.set_visible(False)
    axR.set_xticks(xs, [n.replace(" ", "\n", 1) for n in names], fontsize=8.5)
    axR.set_ylabel("reliability", color=C_ORANGE)
    axR.tick_params(axis="y", colors=C_ORANGE)
    axR.set_ylim(0, max(rels) * 1.3)
    axR.set_title("разложение Брайера: $BS = \\mathrm{rel} - \\mathrm{res} + "
                  "\\mathrm{unc}$", fontsize=11.5)
    axR.legend(handles=[plt.Line2D([], [], color=C_ORANGE, lw=6),
                        plt.Line2D([], [], color=C_BLUE, lw=2.4, marker="s")],
               labels=["reliability (меньше — лучше)",
                       "resolution (больше — лучше)"],
               fontsize=9, loc="upper left")
    _despine(axR)
    _despine(axL)
    axL.grid(alpha=0.25, color=C_GRAY, lw=0.6, axis="y")
    axR.grid(alpha=0.25, color=C_GRAY, lw=0.6, axis="y")

    fig.suptitle("Калиброванная модель может быть совершенно бесполезной",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "calibration_is_not_accuracy.png")
    return dict(e_const=e_const, b_const=b_const, rel_c=rel_c, res_c=res_c, unc_c=unc_c,
                best_name=best_name, best_auc=roc_auc_score(yte, p_best),
                best_ece=ece(yte, p_best), best_brier=brier_score_loss(yte, p_best),
                names=names, rels=rels, ress=ress)


# ==========================================================================
# 3. Чему ECE не научит
# ==========================================================================


def run_subgroups(n=60_000, delta=0.18, seed=0):
    """Модель калибрована в среднем и провалена на каждой подгруппе."""
    rng = np.random.default_rng(seed)
    g = rng.integers(0, 2, n)
    p_hat = rng.uniform(0.05, 0.95, n)
    p_true = np.clip(p_hat + np.where(g == 1, delta, -delta), 0, 1)
    y = (rng.random(n) < p_true).astype(int)
    return g, p_hat, y


def draw_ece_traps(models, Xte, yte, subgroups):
    _apply_style()
    g, p_hat, y_sub = subgroups
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.4, 4.5))

    p = models["градиентный бустинг"].predict_proba(Xte)[:, 1]
    bins = np.array([5, 10, 15, 20, 30, 50, 100, 200])
    uni = [ece(yte, p, b, "uniform") for b in bins]
    qua = [ece(yte, p, b, "quantile") for b in bins]
    axL.plot(bins, uni, color=C_ORANGE, lw=2.4, marker="o", ms=5,
             label="бины равной ширины")
    axL.plot(bins, qua, color=C_BLUE, lw=2.4, marker="s", ms=5,
             label="бины равной массы")
    axL.set_xscale("log")
    axL.set_xlabel("число бинов (лог)")
    axL.set_ylabel("ECE")
    axL.set_ylim(0, max(uni) * 1.25)
    axL.set_title(f"одна и та же модель: ECE от {min(uni + qua):.3f} до "
                  f"{max(uni + qua):.3f}", fontsize=11.5)
    axL.legend(fontsize=9.5, loc="upper left")

    xs_all, ys_all, _ = reliability(y_sub, p_hat, bins=12)
    axR.plot([0, 1], [0, 1], color=C_GRAY, ls="--", lw=1.4)
    axR.plot(xs_all, ys_all, color=C_INK, lw=2.6, marker="o", ms=5,
             label=f"все объекты: ECE {ece(y_sub, p_hat):.3f}")
    for gi, color, label in ((1, C_ORANGE, "группа A"), (0, C_BLUE, "группа B")):
        m = g == gi
        xs, ys, _ = reliability(y_sub[m], p_hat[m], bins=12)
        axR.plot(xs, ys, color=color, lw=2.2, marker="o", ms=4,
                 label=f"{label}: ECE {ece(y_sub[m], p_hat[m]):.3f}")
    axR.set_xlabel("предсказанная вероятность")
    axR.set_ylabel("фактическая доля положительных")
    axR.set_title("калибровка — свойство популяции, а не объекта", fontsize=11.5)
    axR.legend(fontsize=9.5, loc="upper left")
    axR.set_xlim(0, 1)
    axR.set_ylim(0, 1)

    for ax in (axL, axR):
        ax.grid(alpha=0.25, color=C_GRAY, lw=0.6)
        _despine(ax)

    fig.suptitle("ECE зависит от разбиения и слепа к подгруппам", fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "ece_traps.png")
    return dict(bins=bins, uni=uni, qua=qua,
                ece_all=ece(y_sub, p_hat),
                ece_a=ece(y_sub[g == 1], p_hat[g == 1]),
                ece_b=ece(y_sub[g == 0], p_hat[g == 0]))


# ==========================================================================
# 4. Как чинят
# ==========================================================================


def draw_fixing(models, Xval, yval, Xte, yte, seed=0):
    _apply_style()
    m = models["нейросеть 256×256"]
    pv, pt = m.predict_proba(Xval)[:, 1], m.predict_proba(Xte)[:, 1]

    T = fit_temperature(yval, pv)
    p_temp = apply_temperature(pt, T)
    platt = LogisticRegression().fit(logit(pv).reshape(-1, 1), yval)
    p_platt = platt.predict_proba(logit(pt).reshape(-1, 1))[:, 1]
    iso = IsotonicRegression(out_of_bounds="clip").fit(pv, yval)
    p_iso = iso.predict(pt)

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.6, 4.6))
    axL.plot([0, 1], [0, 1], color=C_GRAY, ls="--", lw=1.4)
    rows = []
    for label, pp, color in (("без калибровки", pt, C_ORANGE),
                             (f"температура $T$ = {T:.2f}", p_temp, C_INK),
                             ("Платт", p_platt, C_BLUE),
                             ("изотоническая", p_iso, C_GREEN)):
        xs, ys, _ = reliability(yte, pp, bins=12)
        axL.plot(xs, ys, color=color, lw=2.2, marker="o", ms=4,
                 label=f"{label}: ECE {ece(yte, pp):.3f}, AUC {roc_auc_score(yte, pp):.4f}")
        rows.append((label, ece(yte, pp), roc_auc_score(yte, pp),
                     brier_score_loss(yte, pp)))
    axL.set_xlabel("предсказанная вероятность")
    axL.set_ylabel("фактическая доля положительных")
    axL.set_title("нейросеть 256×256 до и после поправки", fontsize=11.5)
    axL.legend(fontsize=9, loc="upper left")
    axL.set_xlim(0, 1)
    axL.set_ylim(0, 1)

    sizes = np.array([50, 100, 300, 1000, 3000, 10_000, len(yval)])
    rng = np.random.default_rng(seed)
    e_temp, e_iso = [], []
    for nv in sizes:
        idx = rng.choice(len(yval), min(nv, len(yval)), replace=False)
        Ti = fit_temperature(yval[idx], pv[idx])
        e_temp.append(ece(yte, apply_temperature(pt, Ti)))
        isoi = IsotonicRegression(out_of_bounds="clip").fit(pv[idx], yval[idx])
        e_iso.append(ece(yte, isoi.predict(pt)))
    axR.plot(sizes, e_temp, color=C_INK, lw=2.4, marker="o", ms=5,
             label="температура (1 параметр)")
    axR.plot(sizes, e_iso, color=C_GREEN, lw=2.4, marker="s", ms=5,
             label="изотоническая (непараметрическая)")
    axR.axhline(ece(yte, pt), color=C_ORANGE, ls="--", lw=1.4,
                label=f"без калибровки: {ece(yte, pt):.3f}")
    axR.set_xscale("log")
    axR.set_xlabel("размер валидационной выборки (лог)")
    axR.set_ylabel("ECE на тесте")
    axR.set_title("на маленькой валидации гибкий метод проигрывает", fontsize=11.5)
    axR.legend(fontsize=9.5)

    for ax in (axL, axR):
        ax.grid(alpha=0.25, color=C_GRAY, lw=0.6)
        _despine(ax)

    fig.suptitle("Калибровку чинят после обучения — на отдельной выборке",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "fixing_calibration.png")
    return dict(T=T, rows=rows, sizes=sizes, e_temp=e_temp, e_iso=e_iso,
                base=ece(yte, pt))


# ==========================================================================
# 5. Ёмкость и деньги
# ==========================================================================


def run_capacity(Xtr, ytr, Xval, yval, Xte, yte, seed=0):
    rows = []
    for h in ((8,), (32,), (128,), (256, 256), (512, 512)):
        m = MLPClassifier(hidden_layer_sizes=h, max_iter=600, random_state=seed)
        m.fit(Xtr, ytr)
        p = m.predict_proba(Xte)[:, 1]
        rows.append((h, m.score(Xte, yte), ece(yte, p),
                     float(np.maximum(p, 1 - p).mean()),
                     fit_temperature(yval, m.predict_proba(Xval)[:, 1])))
    return rows


def run_money(n=60_000, c_fp=4.0, seed=3):
    """Одинаковое ранжирование, разная калибровка — разные деньги."""
    rng = np.random.default_rng(seed)
    p_true = rng.beta(1.2, 30, n)
    y = (rng.random(n) < p_true).astype(int)
    amount = np.exp(rng.normal(3.2, 1.1, n))

    def cost(block):
        return float(c_fp * np.sum(block & (y == 0)) + np.sum(amount[(~block) & (y == 1)]))

    rows = []
    for T in (0.4, 0.55, 0.7, 0.85, 1.0, 1.2, 1.5, 2.0, 3.0):
        p_hat = apply_temperature(p_true, T)
        block = p_hat * amount > c_fp
        rows.append((T, ece(y, p_hat), roc_auc_score(y, p_hat), float(block.mean()),
                     cost(block)))
    return rows, cost(np.zeros(n, bool)), float(y.mean())


def draw_capacity_money(cap_rows, money):
    _apply_style()
    money_rows, cost_none, prevalence = money
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.6, 4.6))

    xs = np.arange(len(cap_rows))
    axL.plot(xs, [r[3] for r in cap_rows], color=C_ORANGE, lw=2.4, marker="o", ms=6,
             label="средняя уверенность")
    axL.plot(xs, [r[1] for r in cap_rows], color=C_INK, lw=2.4, marker="s", ms=6,
             label="accuracy")
    axL.set_xticks(xs, [str(r[0]) for r in cap_rows], fontsize=9)
    axL.set_xlabel("скрытые слои")
    axL.set_ylabel("доля")
    axL.set_ylim(0.9, 1.01)
    ax2 = axL.twinx()
    ax2.bar(xs, [r[2] for r in cap_rows], color=C_BLUE, alpha=0.35, width=0.5)
    ax2.set_ylabel("ECE", color=C_BLUE)
    ax2.tick_params(colors=C_BLUE)
    ax2.set_ylim(0, max(r[2] for r in cap_rows) * 2.2)
    for s in ax2.spines.values():
        s.set_visible(False)
    axL.set_title("точность почти не растёт, а уверенность — растёт", fontsize=11.5)
    axL.legend(fontsize=9.5, loc="lower right")
    _despine(axL)

    Ts = [r[0] for r in money_rows]
    costs = [r[4] for r in money_rows]
    eces = [r[1] for r in money_rows]
    axR.plot(Ts, np.array(costs) / cost_none * 100, color=C_INK, lw=2.6, marker="o",
             ms=6, label="потери, % от «ничего не делать»")
    axR.axhline(100, color=C_GRAY, ls="--", lw=1.3)
    k = int(np.argmin(costs))
    axR.scatter([Ts[k]], [costs[k] / cost_none * 100], color=C_GREEN, s=70, zorder=5)
    axR.annotate(f"калиброванные вероятности\n($T$ = 1, ECE {eces[k]:.3f}): "
                 f"{costs[k] / cost_none * 100:.0f}%",
                 xy=(Ts[k], costs[k] / cost_none * 100),
                 xytext=(1.55, costs[k] / cost_none * 100 + 6),
                 fontsize=9.5, color=C_GREEN,
                 arrowprops=dict(arrowstyle="->", color=C_GREEN, lw=1.1))
    ax3 = axR.twinx()
    ax3.plot(Ts, eces, color=C_ORANGE, lw=2.0, ls="--", label="ECE")
    ax3.set_ylabel("ECE", color=C_ORANGE)
    ax3.tick_params(colors=C_ORANGE)
    for s in ax3.spines.values():
        s.set_visible(False)
    axR.set_xlabel("искажение вероятностей: температура $T$")
    axR.set_ylabel("потери, % от бездействия")
    axR.set_title(f"ранжирование неизменно (AUC {money_rows[0][2]:.4f} при любом $T$)",
                  fontsize=11.5)
    axR.legend(fontsize=9.5, loc="upper left")
    _despine(axR)

    for ax in (axL, axR):
        ax.grid(alpha=0.25, color=C_GRAY, lw=0.6, axis="y")

    fig.suptitle("Чем больше модель, тем она самоувереннее; а цена ошибки — в деньгах",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "capacity_and_money.png")
    return dict(cap=cap_rows, money=money_rows, cost_none=cost_none,
                prevalence=prevalence)


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    print("Генерация схем «Калибровка вероятностей»:")
    Xtr, ytr, Xval, yval, Xte, yte = make_split()
    models = fit_models(Xtr, ytr)

    rel_rows = draw_reliability(models, Xte, yte, Xval, yval)
    nu = draw_not_usefulness(models, Xte, yte, ytr)
    traps = draw_ece_traps(models, Xte, yte, run_subgroups())
    fix = draw_fixing(models, Xval, yval, Xte, yte)
    cm = draw_capacity_money(run_capacity(Xtr, ytr, Xval, yval, Xte, yte), run_money())

    print("\nЧисла для текста лекции:")
    for name, e, b, auc, acc, T, _ in rel_rows:
        print(f"  {name:<24} acc {acc:.3f}  AUC {auc:.3f}  Brier {b:.4f}  "
              f"ECE {e:.4f}  T {T:.2f}")
    print(f"  константа: ECE {nu['e_const']:.4f}, Brier {nu['b_const']:.4f}, AUC 0.500, "
          f"reliability {nu['rel_c']:.4f}, resolution {nu['res_c']:.4f}, "
          f"uncertainty {nu['unc_c']:.4f}")
    print(f"  лучшая по AUC ({nu['best_name']}): AUC {nu['best_auc']:.3f}, "
          f"ECE {nu['best_ece']:.4f}, Brier {nu['best_brier']:.4f}")
    for n_, r_, s_ in zip(nu["names"], nu["rels"], nu["ress"]):
        print(f"    {n_:<24} reliability {r_:.4f}, resolution {s_:.4f}")
    print(f"  ECE против числа бинов: равномерные "
          f"{traps['uni'][0]:.4f} → {traps['uni'][-1]:.4f}, равночастотные "
          f"{traps['qua'][0]:.4f} → {traps['qua'][-1]:.4f}")
    print(f"  подгруппы: общий ECE {traps['ece_all']:.4f}, "
          f"A {traps['ece_a']:.4f}, B {traps['ece_b']:.4f}")
    for label, e, auc, b in fix["rows"]:
        print(f"  {label:<26} ECE {e:.4f}  AUC {auc:.4f}  Brier {b:.4f}")
    for nv, et, ei in zip(fix["sizes"], fix["e_temp"], fix["e_iso"]):
        print(f"    валидация {nv:>6}: температура {et:.4f}, изотоническая {ei:.4f}")
    for h, acc, e, conf, T in cm["cap"]:
        print(f"  сеть {str(h):<12} acc {acc:.3f}, ECE {e:.4f}, "
              f"средняя уверенность {conf:.3f}, T {T:.2f}")
    print(f"  деньги: доля события {cm['prevalence']:.4f}, бездействие {cm['cost_none']:.0f}")
    for T, e, auc, rate, cost in cm["money"]:
        print(f"    T={T:>4}: ECE {e:.4f}, AUC {auc:.4f}, алертов {rate:.2%}, "
              f"потери {cost:.0f} ({cost / cm['cost_none'] * 100:.0f}%)")


if __name__ == "__main__":
    main()
