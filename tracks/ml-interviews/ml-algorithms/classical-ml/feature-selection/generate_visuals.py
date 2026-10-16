"""Точные схемы для темы «Выбор признаков».

Все числа на картинках — результат прогона, а не подобранные вручную значения:
утечка при отборе меряется на данных без сигнала вообще, одномерные оценки
считаются настоящими F-статистикой и взаимной информацией, устойчивость Lasso —
по бутстрэп-повторам, важности — MDI против permutation importance на отложенной части.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import f_classif, mutual_info_classif
from sklearn.inspection import permutation_importance
from sklearn.linear_model import ElasticNet, Lasso, LogisticRegression
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.neighbors import KNeighborsClassifier
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


def _abs_corr(X, y):
    """|корреляция| каждого столбца с целевой переменной, векторно."""
    Xc = X - X.mean(axis=0)
    yc = y - y.mean()
    denom = np.sqrt((Xc**2).sum(axis=0) * (yc**2).sum()) + 1e-12
    return np.abs(Xc.T @ yc) / denom


# ==========================================================================
# 1. Отбор до валидации: как получить 90% точности на чистом шуме
# ==========================================================================


def run_leakage(R=20, n=100, p=5000, k=100, seed=0):
    """ESL 7.10.2: отбор по всем данным против отбора внутри фолда."""
    rng = np.random.default_rng(seed)
    wrong, right = [], []

    for _ in range(R):
        X = rng.normal(size=(n, p))
        y = rng.integers(0, 2, size=n)

        # НЕПРАВИЛЬНО: экран по всем данным, потом кросс-валидация
        top = np.argsort(_abs_corr(X, y))[-k:]
        Xs = X[:, top]
        cv = StratifiedKFold(5, shuffle=True, random_state=0)
        acc = [
            KNeighborsClassifier(1).fit(Xs[tr], y[tr]).score(Xs[te], y[te])
            for tr, te in cv.split(Xs, y)
        ]
        wrong.append(np.mean(acc))

        # ПРАВИЛЬНО: экран заново внутри каждого фолда
        acc = []
        for tr, te in cv.split(X, y):
            top_tr = np.argsort(_abs_corr(X[tr], y[tr]))[-k:]
            acc.append(
                KNeighborsClassifier(1)
                .fit(X[tr][:, top_tr], y[tr])
                .score(X[te][:, top_tr], y[te])
            )
        right.append(np.mean(acc))

    return np.array(wrong), np.array(right)


def run_leakage_with_signal(R=12, n=200, p=2000, k=50, n_inf=10, seed=1):
    """То же, но сигнал есть: сравниваем обе оценки с честным тестом."""
    rng = np.random.default_rng(seed)
    wrong, right, honest = [], [], []

    for r in range(R):
        X, y = make_classification(
            n_samples=n + 2000, n_features=p, n_informative=n_inf, n_redundant=0,
            n_repeated=0, class_sep=1.0, shuffle=False,
            random_state=int(rng.integers(0, 10**6)),
        )
        X, Xt, y, yt = train_test_split(X, y, train_size=n, stratify=y, random_state=r)
        cv = StratifiedKFold(5, shuffle=True, random_state=0)

        top = np.argsort(_abs_corr(X, y))[-k:]
        Xs = X[:, top]
        wrong.append(np.mean([
            KNeighborsClassifier(5).fit(Xs[tr], y[tr]).score(Xs[te], y[te])
            for tr, te in cv.split(Xs, y)
        ]))

        acc = []
        for tr, te in cv.split(X, y):
            top_tr = np.argsort(_abs_corr(X[tr], y[tr]))[-k:]
            acc.append(KNeighborsClassifier(5).fit(X[tr][:, top_tr], y[tr])
                       .score(X[te][:, top_tr], y[te]))
        right.append(np.mean(acc))

        # честная оценка: отбор по всей обучающей части, проверка на отложенной
        honest.append(KNeighborsClassifier(5).fit(X[:, top], y).score(Xt[:, top], yt))

    return np.array(wrong), np.array(right), np.array(honest)


def draw_leakage(noise_res, signal_res):
    _apply_style()
    wrong, right = noise_res
    w2, r2, h2 = signal_res

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.4, 4.4))

    bins = np.linspace(0.35, 1.0, 27)
    axL.hist(wrong, bins=bins, color=C_ORANGE, alpha=0.85,
             label=f"отбор по всем данным: {wrong.mean():.3f}")
    axL.hist(right, bins=bins, color=C_BLUE, alpha=0.85,
             label=f"отбор внутри фолда: {right.mean():.3f}")
    axL.axvline(0.5, color=C_INK, ls="--", lw=1.4)
    axL.text(0.505, axL.get_ylim()[1] * 0.55, "правда: 0.5", fontsize=9.5, color=C_INK)
    axL.set_xlabel("оценка accuracy по 5-фолдовой кросс-валидации")
    axL.set_ylabel("число прогонов")
    axL.set_title("данные без сигнала: n = 100, p = 5000, метки случайны", fontsize=11.5)
    axL.legend(fontsize=9.5, loc="upper left")

    xs = np.arange(3)
    vals = [w2.mean(), r2.mean(), h2.mean()]
    errs = [w2.std(), r2.std(), h2.std()]
    axR.bar(xs, vals, yerr=errs, capsize=4, width=0.6,
            color=[C_ORANGE, C_BLUE, C_GREEN])
    for x, v, e in zip(xs, vals, errs):
        axR.text(x, v + e + 0.025, f"{v:.3f}", ha="center", fontsize=10)
    axR.set_xticks(xs, ["отбор по всем\nданным (CV)", "отбор внутри\nфолда (CV)",
                        "честный\nотложенный тест"])
    axR.set_ylim(0, 1.05)
    axR.axhline(h2.mean(), color=C_GREEN, ls=":", lw=1.2)
    axR.set_ylabel("accuracy")
    axR.set_title("сигнал есть (10 информативных из 2000): кто говорит правду",
                  fontsize=11.5)

    for ax in (axL, axR):
        ax.grid(alpha=0.25, color=C_GRAY, lw=0.6, axis="y")
        _despine(ax)

    fig.suptitle("Отбор признаков — часть модели: сделанный до валидации, он её ломает",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "selection_leakage.png")
    return dict(noise_wrong=wrong.mean(), noise_right=right.mean(),
                sig_wrong=w2.mean(), sig_right=r2.mean(), sig_honest=h2.mean())


# ==========================================================================
# 2. Слепая зона одномерного отбора: взаимодействие признаков
# ==========================================================================


def draw_univariate_blindspot(seed=0):
    """Пара признаков, каждый из которых по отдельности бесполезен."""
    _apply_style()
    rng = np.random.default_rng(seed)
    n = 600

    x1 = rng.normal(size=n)
    x2 = rng.normal(size=n)
    y = ((x1 > 0) ^ (x2 > 0)).astype(int)          # XOR: вместе решают, порознь нет
    decoy = np.where(y == 1, 0.45, -0.45) + rng.normal(0, 1.0, size=n)  # слабый, но одномерный
    noise = rng.normal(size=(n, 6))
    X = np.column_stack([x1, x2, decoy, noise])
    names = ["x₁ (XOR)", "x₂ (XOR)", "приманка"] + [f"шум {i+1}" for i in range(6)]

    F, _ = f_classif(X, y)
    MI = mutual_info_classif(X, y, random_state=0)

    tr, te = train_test_split(np.arange(n), test_size=0.4, stratify=y, random_state=1)

    def acc(cols):
        Xs = X[:, cols]
        return RandomForestClassifier(n_estimators=300, random_state=0).fit(
            Xs[tr], y[tr]).score(Xs[te], y[te])

    top2_F = list(np.argsort(F)[-2:])
    acc_top2 = acc(top2_F)
    acc_true = acc([0, 1])
    acc_all = acc(list(range(X.shape[1])))

    fig, (ax1, ax2, ax3) = plt.subplots(
        1, 3, figsize=(13.2, 4.2), gridspec_kw={"width_ratios": [1, 1.35, 0.9]})

    ax1.scatter(x1, x2, c=[C_BLUE if t else C_ORANGE for t in y], s=9,
                linewidths=0, alpha=0.75)
    ax1.axhline(0, color=C_INK, lw=1.0)
    ax1.axvline(0, color=C_INK, lw=1.0)
    ax1.set_xlabel("x₁")
    ax1.set_ylabel("x₂")
    ax1.set_title("вместе — идеальное правило", fontsize=11.5)
    _despine(ax1)

    ys = np.arange(len(names))[::-1]
    ax2.barh(ys - 0.19, F / F.max(), height=0.36, color=C_ORANGE, label="F-статистика")
    ax2.barh(ys + 0.19, MI / max(MI.max(), 1e-9), height=0.36, color=C_BLUE,
             label="взаимная информация")
    ax2.set_yticks(ys, names, fontsize=9.5)
    ax2.set_xlabel("оценка, нормированная на максимум")
    ax2.set_title("одномерные оценки: XOR-пара на дне", fontsize=11.5)
    ax2.legend(fontsize=9.5, loc="lower right")
    _despine(ax2)

    bars = [acc_top2, acc_true, acc_all]
    labels = ["топ-2 по\nF-статистике", "настоящая\nпара x₁, x₂", "все 9 признаков,\nбез отбора"]
    ax3.bar(np.arange(3), bars, color=[C_ORANGE, C_GREEN, C_GRAY], width=0.62)
    for x, v in enumerate(bars):
        ax3.text(x, v + 0.015, f"{v:.2f}", ha="center", fontsize=10)
    ax3.set_xticks(np.arange(3), labels, fontsize=9)
    ax3.set_ylim(0, 1.12)
    ax3.axhline(0.5, color=C_INK, ls="--", lw=1.2)
    ax3.set_ylabel("accuracy на отложенной части")
    ax3.set_title("случайный лес на разных наборах", fontsize=11.5)
    ax3.grid(alpha=0.25, color=C_GRAY, lw=0.6, axis="y")
    _despine(ax3)

    fig.suptitle(
        "Одномерный отбор оценивает признак в одиночку — и не видит того, что работает в паре",
        fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "univariate_blindspot.png")
    return dict(F_xor=F[:2].tolist(), F_decoy=float(F[2]), MI_xor=MI[:2].tolist(),
                MI_decoy=float(MI[2]), acc_top2=acc_top2, acc_true=acc_true,
                acc_all=acc_all, top2=[names[i] for i in top2_F])


# ==========================================================================
# 3. Сколько признаков оставлять
# ==========================================================================


def run_how_many(R=12, n=300, p=200, n_inf=10, n_red=10, seed=3):
    """Кривая качества против числа отобранных признаков для четырёх методов."""
    rng = np.random.default_rng(seed)
    ks = np.array([1, 2, 3, 5, 8, 12, 20, 30, 50, 80, 120, 200])
    methods = ["F-статистика", "взаимная информация", "L1-логрегрессия", "важности леса"]
    curves = {m: np.zeros((R, len(ks))) for m in methods}
    baseline = np.zeros(R)

    for r in range(R):
        X, y = make_classification(
            n_samples=n + 3000, n_features=p, n_informative=n_inf, n_redundant=n_red,
            class_sep=0.8, flip_y=0.02,
            random_state=int(rng.integers(0, 10**6)),
        )
        X, Xt, y, yt = train_test_split(X, y, train_size=n, stratify=y, random_state=r)
        sc = StandardScaler().fit(X)
        X, Xt = sc.transform(X), sc.transform(Xt)

        ranks = {
            "F-статистика": f_classif(X, y)[0],
            "взаимная информация": mutual_info_classif(X, y, random_state=0),
            "L1-логрегрессия": np.abs(
                LogisticRegression(penalty="l1", C=0.1, solver="liblinear",
                                   max_iter=2000).fit(X, y).coef_[0]),
            "важности леса": RandomForestClassifier(
                n_estimators=200, random_state=0).fit(X, y).feature_importances_,
        }
        base = LogisticRegression(max_iter=2000).fit(X, y)
        baseline[r] = base.score(Xt, yt)

        for m, score in ranks.items():
            order = np.argsort(score)[::-1]
            for j, k in enumerate(ks):
                cols = order[:k]
                curves[m][r, j] = LogisticRegression(max_iter=2000).fit(
                    X[:, cols], y).score(Xt[:, cols], yt)

    return ks, {m: c.mean(axis=0) for m, c in curves.items()}, baseline.mean()


def draw_how_many(res):
    _apply_style()
    ks, curves, baseline = res
    fig, ax = plt.subplots(figsize=(9.2, 4.6))

    colors = [C_ORANGE, C_BLUE, C_GREEN, C_INK]
    best = {}
    for (m, c), color in zip(curves.items(), colors):
        j = int(np.argmax(c))
        best[m] = (int(ks[j]), float(c[j]))
        ax.plot(ks, c, color=color, lw=2.2, marker="o", ms=4,
                label=f"{m}: максимум {c[j]:.3f} при k = {ks[j]}")
        ax.scatter([ks[j]], [c[j]], color=color, s=46, zorder=5)

    ax.axhline(baseline, color=C_GRAY, ls="--", lw=1.4)
    ax.text(1.05, baseline - 0.008, f"без отбора, все 200 признаков: {baseline:.3f}",
            fontsize=9.5, color=C_GRAY, va="top")
    ax.set_xscale("log")
    ax.set_ylim(top=max(c.max() for c in curves.values()) + 0.055)
    ax.set_xlabel("сколько признаков оставили, k (лог)")
    ax.set_ylabel("accuracy на отложенной выборке")
    ax.set_title("n = 300, p = 200 (10 информативных + 10 их линейных комбинаций)",
                 fontsize=11.5)
    ax.legend(fontsize=9.5, loc="upper left")
    ax.grid(alpha=0.25, color=C_GRAY, lw=0.6)
    _despine(ax)
    fig.suptitle("Кривая отбора: слишком мало — недобор сигнала, слишком много — шум",
                 fontsize=13, y=0.99)
    fig.tight_layout()
    _save(fig, "how_many_features.png")
    return best, baseline


# ==========================================================================
# 4. Коррелированные признаки: Lasso выбирает произвольного представителя
# ==========================================================================


def run_stability(R=200, n=120, alpha=1.0, l1_ratio=0.5, seed=4):
    """Группа из 5 почти одинаковых информативных признаков + шум."""
    rng = np.random.default_rng(seed)
    p_noise = 8
    base = rng.normal(size=n)
    group = base[:, None] + rng.normal(0, 0.10, size=(n, 5))     # взаимная корр. ~0.99
    solo = rng.normal(size=(n, 2))
    noise = rng.normal(size=(n, p_noise))
    X = np.column_stack([group, solo, noise])
    beta = np.zeros(X.shape[1])
    beta[:5] = 1.0          # вклад группы
    beta[5] = 2.5           # одиночный сильный признак
    y = X @ beta + rng.normal(0, 1.0, size=n)

    corr_in_group = np.corrcoef(group.T)[np.triu_indices(5, 1)].mean()

    sel_lasso = np.zeros(X.shape[1])
    sel_enet = np.zeros(X.shape[1])
    for _ in range(R):
        idx = rng.integers(0, n, n)                 # бутстрэп
        Xb, yb = X[idx], y[idx]
        Xb = StandardScaler().fit_transform(Xb)
        sel_lasso += np.abs(Lasso(alpha=alpha, max_iter=5000).fit(Xb, yb).coef_) > 1e-8
        # у Elastic Net берём alpha так, чтобы L1-часть штрафа была той же силы
        sel_enet += np.abs(ElasticNet(alpha=alpha / l1_ratio, l1_ratio=l1_ratio,
                                      max_iter=5000).fit(Xb, yb).coef_) > 1e-8
    return sel_lasso / R, sel_enet / R, corr_in_group, alpha, l1_ratio


def draw_stability(res):
    _apply_style()
    lasso, enet, corr, alpha, l1_ratio = res
    p = len(lasso)
    names = [f"группа {i+1}" for i in range(5)] + ["сильный", "лишний"] + \
            [f"шум {i+1}" for i in range(p - 7)]

    fig, ax = plt.subplots(figsize=(11.6, 4.4))
    xs = np.arange(p)
    ax.bar(xs - 0.2, lasso, width=0.4, color=C_ORANGE, label=f"Lasso (α = {alpha})")
    ax.bar(xs + 0.2, enet, width=0.4, color=C_BLUE,
           label=f"Elastic Net (l1_ratio = {l1_ratio}, та же сила L1-штрафа)")
    ax.axvspan(-0.6, 4.6, color=C_PANEL, alpha=0.6, zorder=0)
    ax.text(2.0, 1.10, f"группа взаимозаменяемых признаков,\nсредняя корреляция {corr:.2f}",
            ha="center", va="top", fontsize=9.5, color=C_INK)
    ax.set_xticks(xs, names, rotation=45, ha="right", fontsize=8.5)
    ax.set_ylim(0, 1.28)
    ax.set_ylabel("доля бутстрэп-повторов")
    ax.set_title(
        f"частота отбора внутри группы: Lasso {lasso[:5].min():.2f}…{lasso[:5].max():.2f}, "
        f"Elastic Net {enet[:5].min():.2f}…{enet[:5].max():.2f}",
        fontsize=11.5)
    ax.legend(fontsize=9.5, loc="upper right")
    ax.grid(alpha=0.25, color=C_GRAY, lw=0.6, axis="y")
    _despine(ax)
    fig.suptitle("«Признак не выбран» не значит «признак не нужен»",
                 fontsize=13, y=1.0)
    fig.tight_layout()
    _save(fig, "selection_stability.png")
    return dict(lasso_group=lasso[:5], enet_group=enet[:5],
                lasso_strong=lasso[5], corr=corr,
                lasso_noise_max=lasso[7:].max(), enet_noise_max=enet[7:].max())


# ==========================================================================
# 5. Важности: MDI против permutation importance
# ==========================================================================


def draw_importance_bias(seed=5):
    """Ловушка кардинальности: случайный непрерывный признак в топе MDI."""
    _apply_style()
    rng = np.random.default_rng(seed)
    n = 800

    X_inf, y = make_classification(n_samples=n, n_features=3, n_informative=3,
                                   n_redundant=0, n_repeated=0, class_sep=1.4,
                                   random_state=seed)
    # информативные признаки огрубляем до трёх категорий — как в реальных табличных данных
    X_cat = np.stack(
        [np.digitize(X_inf[:, j], np.quantile(X_inf[:, j], [0.33, 0.66])) for j in range(3)],
        axis=1).astype(float)
    uid = rng.normal(size=n)                       # непрерывный шум, все значения разные
    binary = rng.integers(0, 2, size=n).astype(float)   # бинарный шум
    X = np.column_stack([X_cat, uid, binary])
    names = ["инф. 1 (3 кат.)", "инф. 2 (3 кат.)", "инф. 3 (3 кат.)",
             "шум непрерывный", "шум бинарный"]

    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.4, stratify=y,
                                          random_state=0)
    rf = RandomForestClassifier(n_estimators=300, random_state=0).fit(Xtr, ytr)
    mdi = rf.feature_importances_
    perm_tr = permutation_importance(rf, Xtr, ytr, n_repeats=20, random_state=0)
    perm_te = permutation_importance(rf, Xte, yte, n_repeats=20, random_state=0)

    fig, ax = plt.subplots(figsize=(10.4, 4.4))
    xs = np.arange(len(names))
    ax.bar(xs - 0.27, mdi / mdi.sum(), width=0.27, color=C_ORANGE,
           label="MDI (impurity, на обучении)")
    ax.bar(xs, perm_tr.importances_mean / max(perm_tr.importances_mean.sum(), 1e-9),
           width=0.27, color=C_GRAY, label="permutation, на обучении")
    ax.bar(xs + 0.27,
           np.clip(perm_te.importances_mean, 0, None) /
           max(np.clip(perm_te.importances_mean, 0, None).sum(), 1e-9),
           width=0.27, color=C_BLUE, label="permutation, на отложенной части")
    ax.set_xticks(xs, names, fontsize=9.5)
    ax.set_ylabel("важность, доля от суммы")
    ax.axhline(0, color=C_INK, lw=0.8)
    ax.set_title(
        f"MDI отдаёт чистому шуму {100 * mdi[3] / mdi.sum():.0f}% — больше, чем двум "
        f"настоящим признакам; permutation на тесте: {perm_te.importances_mean[3]:+.3f}",
        fontsize=11.5)
    ax.legend(fontsize=9.5)
    ax.grid(alpha=0.25, color=C_GRAY, lw=0.6, axis="y")
    _despine(ax)
    fig.suptitle("Важность признака — это ответ на вопрос «по какой метрике и на каких данных»",
                 fontsize=13, y=1.0)
    fig.tight_layout()
    _save(fig, "importance_bias.png")
    return dict(mdi=mdi / mdi.sum(), perm_tr=perm_tr.importances_mean,
                perm_te=perm_te.importances_mean, names=names)


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    print("Генерация схем «Выбор признаков»:")
    leak = draw_leakage(run_leakage(), run_leakage_with_signal())
    blind = draw_univariate_blindspot()
    how = draw_how_many(run_how_many())
    stab = draw_stability(run_stability())
    imp = draw_importance_bias()

    print("\nЧисла для текста лекции:")
    print(f"  шум, отбор по всем данным : accuracy {leak['noise_wrong']:.3f}")
    print(f"  шум, отбор внутри фолда   : accuracy {leak['noise_right']:.3f}")
    print(f"  сигнал: по всем {leak['sig_wrong']:.3f} / внутри фолда "
          f"{leak['sig_right']:.3f} / честный тест {leak['sig_honest']:.3f}")
    print(f"  XOR: F = {blind['F_xor'][0]:.2f}, {blind['F_xor'][1]:.2f}; "
          f"приманка F = {blind['F_decoy']:.1f}")
    print(f"  XOR: MI = {blind['MI_xor'][0]:.3f}, {blind['MI_xor'][1]:.3f}; "
          f"приманка MI = {blind['MI_decoy']:.3f}")
    print(f"  топ-2 по F = {blind['top2']}, accuracy {blind['acc_top2']:.3f}; "
          f"настоящая пара {blind['acc_true']:.3f}; все признаки {blind['acc_all']:.3f}")
    best, baseline = how
    for m, (k, v) in best.items():
        print(f"  {m}: максимум {v:.3f} при k = {k}")
    print(f"  без отбора: {baseline:.3f}")
    print(f"  Lasso в группе (корр. {stab['corr']:.2f}): "
          f"{np.round(stab['lasso_group'], 2).tolist()}")
    print(f"  Elastic Net в группе: {np.round(stab['enet_group'], 2).tolist()}")
    print(f"  максимум по шуму: Lasso {stab['lasso_noise_max']:.2f}, "
          f"Elastic Net {stab['enet_noise_max']:.2f}")
    print("  важности (MDI): " +
          ", ".join(f"{n} {v:.3f}" for n, v in zip(imp['names'], imp['mdi'])))
    print("  permutation на тесте: " +
          ", ".join(f"{n} {v:.3f}" for n, v in zip(imp['names'], imp['perm_te'])))


if __name__ == "__main__":
    main()
