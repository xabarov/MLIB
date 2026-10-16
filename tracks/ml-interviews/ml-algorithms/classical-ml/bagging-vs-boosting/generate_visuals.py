"""Точные схемы для темы «Bagging и Boosting».

Все числа на картинках — результат прогона, а не подобранные вручную значения:
bias/variance считаются Монте-Карло по независимым обучающим выборкам,
корреляция деревьев измеряется по тем же прогонам и сверяется с формулой
Var = c + (sigma^2 - c) / B, кривые ошибок — настоящие staged-предсказания.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import make_friedman1
from sklearn.ensemble import (
    BaggingRegressor,
    GradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.tree import DecisionTreeRegressor

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
# Общая одномерная задача: гладкая функция плюс шум
# ==========================================================================

X_LO, X_HI = 0.0, 3.0
NOISE = 0.35
N_TRAIN = 120


def truth(x):
    return np.sin(4.0 * x) + 0.5 * x


def sample(rng, n=N_TRAIN):
    x = rng.uniform(X_LO, X_HI, size=n)
    return x.reshape(-1, 1), truth(x) + rng.normal(0, NOISE, size=n)


def _grid(n=200):
    g = np.linspace(X_LO, X_HI, n)
    return g.reshape(-1, 1), truth(g)


# ==========================================================================
# 1. Два рычага: что именно снижают bagging и boosting
# ==========================================================================


def _decompose(preds, f_true):
    """preds: (R, ..., n_points). Возвращает bias^2 и variance, усреднённые по точкам."""
    mean_pred = preds.mean(axis=0)
    bias2 = ((mean_pred - f_true) ** 2).mean(axis=-1)
    var = preds.var(axis=0).mean(axis=-1)
    return bias2, var


def run_bias_variance(R=120, B_MAX=50, M_MAX=400, seed=0):
    """Монте-Карло по R независимым обучающим выборкам."""
    rng = np.random.default_rng(seed)
    Xg, f_true = _grid()

    bag_preds = np.zeros((R, B_MAX, len(f_true)))
    boost_preds = np.zeros((R, M_MAX, len(f_true)))

    for r in range(R):
        X, y = sample(rng)
        seed_r = int(rng.integers(0, 10**6))

        bag = BaggingRegressor(
            DecisionTreeRegressor(max_depth=None),
            n_estimators=B_MAX,
            random_state=seed_r,
        ).fit(X, y)
        single = np.array([est.predict(Xg) for est in bag.estimators_])
        bag_preds[r] = np.cumsum(single, axis=0) / np.arange(1, B_MAX + 1)[:, None]

        gbr = GradientBoostingRegressor(
            n_estimators=M_MAX, max_depth=2, learning_rate=0.1, random_state=seed_r
        ).fit(X, y)
        boost_preds[r] = np.array(list(gbr.staged_predict(Xg)))

    bag_b2, bag_v = _decompose(bag_preds, f_true)
    bst_b2, bst_v = _decompose(boost_preds, f_true)
    return (bag_b2, bag_v), (bst_b2, bst_v)


def draw_bias_variance(res):
    """Bagging сбивает дисперсию при неизменном смещении; boosting — наоборот."""
    _apply_style()
    (bag_b2, bag_v), (bst_b2, bst_v) = res
    B = np.arange(1, len(bag_b2) + 1)
    M = np.arange(1, len(bst_b2) + 1)

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.4, 4.3))

    for ax, xs, b2, v, title, xlabel in [
        (axL, B, bag_b2, bag_v, "bagging: глубокие деревья, усреднение", "число деревьев $B$"),
        (axR, M, bst_b2, bst_v, "boosting: пни глубины 2, $\\nu = 0.1$", "число итераций $M$"),
    ]:
        ax.plot(xs, b2 + v, color=C_INK, lw=2.2, label="ошибка = bias² + variance")
        ax.plot(xs, b2, color=C_ORANGE, lw=2.0, label="bias²")
        ax.plot(xs, v, color=C_BLUE, lw=2.0, label="variance")
        ax.set_xlabel(xlabel)
        ax.set_title(title, fontsize=11.5)
        ax.grid(alpha=0.25, color=C_GRAY, lw=0.6)
        _despine(ax)

    axL.set_ylabel("средний по точкам вклад в MSE")
    axL.legend(fontsize=9.5, loc="upper right")
    axR.set_xscale("log")
    axR.legend(fontsize=9.5, loc="upper right")

    # отметить минимум суммарной ошибки у бустинга
    tot = bst_b2 + bst_v
    m_star = int(np.argmin(tot)) + 1
    axR.axvline(m_star, color=C_GREEN, ls="--", lw=1.4)
    axR.annotate(
        f"минимум при $M$ = {m_star}\nдальше растёт дисперсия",
        xy=(m_star, tot[m_star - 1]),
        xytext=(m_star * 1.25, tot.max() * 0.55),
        fontsize=9.5, color=C_GREEN,
        arrowprops=dict(arrowstyle="->", color=C_GREEN, lw=1.1),
    )

    # у бэггинга: смещение не двигается, а дисперсия упирается в полку
    B_last = len(B)
    cov_bag = (bag_v[-1] - bag_v[0] / B_last) / (1 - 1 / B_last)
    rho_bag = cov_bag / bag_v[0]
    axL.annotate(
        f"полка $\\rho\\sigma^2$ = {cov_bag:.3f}: деревья\nкоррелированы, ρ = {rho_bag:.2f}",
        xy=(B_last * 0.75, bag_v[-1]),
        xytext=(B_last * 0.30, bag_v[-1] + 0.028),
        fontsize=9.5, color=C_BLUE,
        arrowprops=dict(arrowstyle="->", color=C_BLUE, lw=1.1),
    )
    axL.text(B_last * 0.30, bag_b2[-1] + 0.004,
             f"bias² не двигается: {bag_b2[0]:.3f} → {bag_b2[-1]:.3f}",
             fontsize=9.5, color=C_ORANGE)

    fig.suptitle(
        "Одно и то же bias–variance-разложение, две противоположные траектории",
        fontsize=13, y=1.02,
    )
    fig.tight_layout()
    _save(fig, "bias_variance_levers.png")

    return dict(
        bag_bias_first=bag_b2[0], bag_bias_last=bag_b2[-1],
        bag_var_first=bag_v[0], bag_var_last=bag_v[-1],
        bst_bias_first=bst_b2[0], bst_bias_last=bst_b2[-1],
        bst_var_first=bst_v[0], bst_var_last=bst_v[-1],
        bst_best_M=m_star, bst_best_err=tot[m_star - 1], bst_last_err=tot[-1],
        bag_rho=rho_bag, bag_cov=cov_bag,
    )


# ==========================================================================
# 2. Корреляция деревьев: почему одного усреднения мало
# ==========================================================================


def run_correlation(R=80, B=60, n=200, n_test=150, seed=1):
    """Var ансамбля = c + (sigma^2 - c)/B; c и sigma^2 меряются по прогонам."""
    rng = np.random.default_rng(seed)
    X_test, f_test = make_friedman1(n_samples=n_test, noise=0.0, random_state=999)

    settings = [
        ("max_features = 10 (все признаки)", 1.0, C_ORANGE),
        ("max_features = 3", 3, C_BLUE),
        ("max_features = 1", 1, C_GREEN),
    ]
    out = {}
    for label, max_features, color in settings:
        preds = np.zeros((R, B, n_test))
        for r in range(R):
            X, y = make_friedman1(n_samples=n, noise=1.0,
                                  random_state=int(rng.integers(0, 10**6)))
            rf = RandomForestRegressor(
                n_estimators=B, max_features=max_features,
                random_state=int(rng.integers(0, 10**6)),
            ).fit(X, y)
            preds[r] = np.array([est.predict(X_test) for est in rf.estimators_])

        # дисперсия одного дерева и ковариация двух разных деревьев — по R выборкам
        centred = preds - preds.mean(axis=0, keepdims=True)
        sigma2 = (centred**2).sum(axis=0).mean() / (R - 1)
        gram = np.einsum("rbx,rcx->bcx", centred, centred) / (R - 1)
        off = (gram.sum(axis=(0, 1)) - np.einsum("bbx->x", gram)) / (B * (B - 1))
        cov = off.mean()
        rho = cov / sigma2

        Bs = np.arange(1, B + 1)
        measured = np.array(
            [preds[:, :b].mean(axis=1).var(axis=0, ddof=1).mean() for b in Bs]
        )
        theory = cov + (sigma2 - cov) / Bs
        rel = np.abs(measured - theory).max() / sigma2
        assert rel < 0.02, (label, rel)

        # чем платим за декорреляцию: смещение полного ансамбля
        ens = preds.mean(axis=1)                       # (R, n_test)
        bias2 = float(((ens.mean(axis=0) - f_test) ** 2).mean())
        var_ens = float(ens.var(axis=0).mean())
        out[label] = dict(sigma2=sigma2, cov=cov, rho=rho, Bs=Bs, color=color,
                          measured=measured, theory=theory,
                          bias2=bias2, var=var_ens, err=bias2 + var_ens)
    return out


def draw_correlation(res):
    """Предел усреднения задаётся корреляцией деревьев, а не их числом."""
    _apply_style()
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.6, 4.5),
                                   gridspec_kw={"width_ratios": [1.5, 1]})

    for i, (label, d) in enumerate(res.items()):
        c = d["color"]
        axL.plot(d["Bs"], d["measured"], color=c, lw=2.2,
                 label=f"{label}: ρ = {d['rho']:.2f}")
        axL.plot(d["Bs"], d["theory"], color=C_INK, lw=0.9, ls=":", alpha=0.8)
        axL.axhline(d["cov"], color=c, ls="--", lw=1.1, alpha=0.85)
        axL.text(1.05 + 2.6 * i, d["cov"] * 1.07, f"$\\rho\\sigma^2$ = {d['cov']:.2f}",
                 fontsize=9, color=c, va="bottom")

    axL.set_xscale("log")
    axL.set_yscale("log")
    axL.set_xlabel("число деревьев $B$ (лог)")
    axL.set_ylabel("дисперсия предсказания ансамбля")
    axL.set_title(
        "Var$(\\bar{f}) = \\rho\\sigma^2 + \\dfrac{1-\\rho}{B}\\sigma^2$: "
        "точками — формула, линией — измерение",
        fontsize=11.5,
    )
    axL.legend(fontsize=9.5, loc="upper right")
    axL.grid(alpha=0.25, color=C_GRAY, lw=0.6, which="both")
    _despine(axL)

    # справа — цена декорреляции: bias^2 против variance у полного ансамбля
    labels = list(res)
    xs = np.arange(len(labels))
    b2 = [res[k]["bias2"] for k in labels]
    vr = [res[k]["var"] for k in labels]
    axR.bar(xs, b2, width=0.6, color=C_ORANGE, label="bias²")
    axR.bar(xs, vr, width=0.6, bottom=b2, color=C_BLUE, label="variance")
    for x, (a, b) in enumerate(zip(b2, vr)):
        axR.text(x, a + b + 0.03, f"{a + b:.2f}", ha="center", fontsize=9.5)
    axR.set_xticks(xs, [k.replace("max_features = ", "").replace(" (все признаки)", "\n(все)")
                        for k in labels])
    axR.set_xlabel("max_features")
    axR.set_title("ошибка ансамбля из 60 деревьев", fontsize=11.5)
    axR.legend(fontsize=9.5)
    axR.grid(alpha=0.25, color=C_GRAY, lw=0.6, axis="y")
    _despine(axR)

    fig.suptitle(
        "Random Forest ослабляет корреляцию деревьев — и платит за это смещением",
        fontsize=13, y=1.02,
    )
    fig.tight_layout()
    _save(fig, "ensemble_correlation.png")
    return {k: (v["rho"], v["sigma2"], v["cov"], v["bias2"], v["var"], v["err"])
            for k, v in res.items()}


# ==========================================================================
# 3. Бустинг как пошаговый спуск: как собирается ответ
# ==========================================================================


def draw_stagewise(seed=3):
    """Аддитивная модель по шагам и роль темпа обучения."""
    _apply_style()
    rng = np.random.default_rng(seed)
    X, y = sample(rng)
    Xg, f_true = _grid()
    Xt, ft = _grid(400)
    rng_t = np.random.default_rng(seed + 1)
    yt = ft + rng_t.normal(0, NOISE, size=len(ft))

    stages = [1, 5, 25, 200]
    gbr = GradientBoostingRegressor(
        n_estimators=max(stages), max_depth=2, learning_rate=0.3, random_state=0
    ).fit(X, y)
    preds = list(gbr.staged_predict(Xg))

    fig = plt.figure(figsize=(12.6, 6.4))
    gs = fig.add_gridspec(2, 4, height_ratios=[1, 1.05], hspace=0.42, wspace=0.28)

    for k, m in enumerate(stages):
        ax = fig.add_subplot(gs[0, k])
        ax.scatter(X.ravel(), y, s=8, color=C_GRAY, alpha=0.7, linewidths=0)
        ax.plot(Xg.ravel(), f_true, color=C_INK, lw=1.4, ls="--", alpha=0.8)
        ax.plot(Xg.ravel(), preds[m - 1], color=C_ORANGE, lw=2.2)
        mse = float(np.mean((preds[m - 1] - f_true) ** 2))
        ax.set_title(f"$M$ = {m},  MSE к правде = {mse:.3f}", fontsize=10.5)
        ax.set_xticks([])
        ax.set_yticks([])
        _despine(ax, keep=())
        ax.set_facecolor(C_BG)

    ax2 = fig.add_subplot(gs[1, :])
    curves = {}
    for nu, color in [(1.0, C_GREEN), (0.3, C_ORANGE), (0.1, C_BLUE)]:
        g = GradientBoostingRegressor(
            n_estimators=600, max_depth=2, learning_rate=nu, random_state=0
        ).fit(X, y)
        test_mse = np.array([np.mean((p - yt) ** 2) for p in g.staged_predict(Xt)])
        m_star = int(np.argmin(test_mse)) + 1
        curves[nu] = (test_mse, m_star)
        ax2.plot(np.arange(1, 601), test_mse, color=color, lw=2.0,
                 label=f"$\\nu$ = {nu}: минимум {test_mse[m_star-1]:.3f} при $M$ = {m_star}")
        ax2.scatter([m_star], [test_mse[m_star - 1]], color=color, s=30, zorder=5)

    ax2.axhline(NOISE**2, color=C_GRAY, ls="--", lw=1.2)
    ax2.text(620, NOISE**2, "неустранимый шум $\\sigma^2$", fontsize=9.5,
             color=C_GRAY, va="center")
    ax2.set_xscale("log")
    ax2.set_xlabel("число итераций $M$ (лог)")
    ax2.set_ylabel("MSE на отложенной выборке")
    ax2.set_ylim(NOISE**2 * 0.75, 0.55)
    ax2.set_xlim(1, 900)
    ax2.set_title("темп обучения ν и число итераций — один рычаг, а не два",
                  fontsize=11.5)
    ax2.legend(fontsize=9.5)
    ax2.grid(alpha=0.25, color=C_GRAY, lw=0.6)
    _despine(ax2)

    fig.suptitle("Boosting строит ответ по шагам: каждое дерево чинит остаток предыдущих",
                 fontsize=13, y=0.98)
    _save(fig, "boosting_stagewise.png")
    return {nu: (float(v[0][v[1] - 1]), v[1]) for nu, v in curves.items()}


# ==========================================================================
# 4. Асимметрия: лишние деревья в лесу безвредны, в бустинге — нет
# ==========================================================================


def draw_overfitting(seed=5):
    """Test-ошибка против числа базовых моделей: RF выходит на полку, GBM разворачивается."""
    _apply_style()
    X, y = make_friedman1(n_samples=200, noise=3.0, random_state=seed)
    Xt, yt = make_friedman1(n_samples=4000, noise=3.0, random_state=seed + 1)

    B = 500
    rf = RandomForestRegressor(n_estimators=B, random_state=0).fit(X, y)
    cum_tr = np.cumsum([e.predict(X) for e in rf.estimators_], axis=0) / np.arange(1, B + 1)[:, None]
    cum_te = np.cumsum([e.predict(Xt) for e in rf.estimators_], axis=0) / np.arange(1, B + 1)[:, None]
    rf_tr = ((cum_tr - y) ** 2).mean(axis=1)
    rf_te = ((cum_te - yt) ** 2).mean(axis=1)

    gbms = {}
    for depth in (2, 8):
        g = GradientBoostingRegressor(
            n_estimators=B, max_depth=depth, learning_rate=0.1, random_state=0
        ).fit(X, y)
        tr = np.array([np.mean((p - y) ** 2) for p in g.staged_predict(X)])
        te = np.array([np.mean((p - yt) ** 2) for p in g.staged_predict(Xt)])
        gbms[depth] = (tr, te)

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.4, 4.5), sharey=True)
    xs = np.arange(1, B + 1)
    top = max(rf_te[0], gbms[2][1][0]) * 1.05

    axL.plot(xs, rf_te, color=C_ORANGE, lw=2.2, label="тест")
    axL.plot(xs, rf_tr, color=C_ORANGE, lw=1.4, ls="--", alpha=0.75, label="обучение")
    axL.axhline(rf_te[-1], color=C_GRAY, ls=":", lw=1.2)
    axL.annotate(f"полка {rf_te[-1]:.1f}", xy=(B, rf_te[-1]), xytext=(2.5, rf_te[-1] + 1.6),
                 fontsize=9.5, color=C_GRAY)
    axL.set_title(
        f"Random Forest, {B} деревьев: {rf_te[0]:.1f} → {rf_te[-1]:.1f}, дальше ничего",
        fontsize=11.5)
    axL.set_ylabel("MSE")

    for depth, color in [(2, C_BLUE), (8, C_GREEN)]:
        tr, te = gbms[depth]
        m_star = int(np.argmin(te)) + 1
        rise = (te[-1] / te[m_star - 1] - 1) * 100
        axR.plot(xs, te, color=color, lw=2.2,
                 label=f"глубина {depth}: мин. {te[m_star-1]:.1f} при $M$={m_star}, "
                       f"к {B} итерациям +{rise:.0f}%")
        axR.plot(xs, tr, color=color, lw=1.4, ls="--", alpha=0.6)
        axR.scatter([m_star], [te[m_star - 1]], color=color, s=34, zorder=5)
        axR.axvline(m_star, color=color, ls=":", lw=1.0, alpha=0.7)
    axR.set_title("Gradient Boosting, ν = 0.1: минимум, затем рост", fontsize=11.5)

    for ax in (axL, axR):
        ax.set_xscale("log")
        ax.set_xlabel("число базовых моделей (лог)")
        ax.set_ylim(0, top)
        ax.legend(fontsize=9.5)
        ax.grid(alpha=0.25, color=C_GRAY, lw=0.6)
        _despine(ax)

    fig.suptitle(
        "Штриховая — обучение, сплошная — тест: «добавить ещё деревьев» безопасно "
        "только слева",
        fontsize=12.5, y=1.02,
    )
    fig.tight_layout()
    _save(fig, "ensemble_overfitting.png")
    return dict(
        rf_first=rf_te[0], rf_min=rf_te.min(), rf_argmin=int(rf_te.argmin()) + 1,
        rf_last=rf_te[-1], rf_train_last=rf_tr[-1],
        gbm={d: (float(te.min()), int(np.argmin(te)) + 1, float(te[-1]), float(tr[-1]))
             for d, (tr, te) in gbms.items()},
    )


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    print("Генерация схем «Bagging и Boosting»:")
    bv = draw_bias_variance(run_bias_variance())
    corr = draw_correlation(run_correlation())
    stage = draw_stagewise()
    over = draw_overfitting()

    print("\nЧисла для текста лекции:")
    print(f"  bagging  : bias² {bv['bag_bias_first']:.3f} → {bv['bag_bias_last']:.3f}, "
          f"variance {bv['bag_var_first']:.3f} → {bv['bag_var_last']:.3f}, "
          f"ρ = {bv['bag_rho']:.2f}, полка {bv['bag_cov']:.3f}")
    print(f"  boosting : bias² {bv['bst_bias_first']:.3f} → {bv['bst_bias_last']:.3f}, "
          f"variance {bv['bst_var_first']:.3f} → {bv['bst_var_last']:.3f}")
    print(f"  boosting : минимум ошибки {bv['bst_best_err']:.3f} при M = {bv['bst_best_M']}, "
          f"в конце {bv['bst_last_err']:.3f}")
    for k, (rho, s2, cov, b2, vr, err) in corr.items():
        print(f"  {k}: ρ = {rho:.3f}, σ² = {s2:.2f}, предел ρσ² = {cov:.3f}, "
              f"bias² = {b2:.2f}, var = {vr:.2f}, MSE = {err:.2f}")
    for nu, (mse, m) in stage.items():
        print(f"  ν = {nu}: минимум MSE {mse:.3f} при M = {m}")
    print(f"  RF   : тест {over['rf_first']:.2f} → {over['rf_last']:.2f} "
          f"(минимум {over['rf_min']:.2f} при B={over['rf_argmin']}), "
          f"обучение {over['rf_train_last']:.2f}")
    for d, (mn, m, last, tr) in over["gbm"].items():
        print(f"  GBM depth={d}: минимум {mn:.2f} при M={m}, в конце {last:.2f} "
              f"(+{(last/mn-1)*100:.0f}%), обучение {tr:.3f}")


if __name__ == "__main__":
    main()
