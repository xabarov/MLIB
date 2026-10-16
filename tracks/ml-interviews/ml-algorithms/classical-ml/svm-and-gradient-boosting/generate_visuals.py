"""Точные схемы для темы «SVM и градиентный бустинг».

Все числа на картинках — результат прогона, а не подобранные вручную значения:
ширина полосы и опорные векторы берутся из обученных SVC, сравнение с персептроном
и эффект выброса усреднены по сотням независимых выборок, отступы AdaBoost
считаются вручную из весов и предсказаний слабых учеников, время обучения
меряется в один поток, чтобы сравнивать алгоритмы, а не число ядер.
"""

import math
import time
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import make_circles, make_classification, make_moons
from sklearn.ensemble import AdaBoostClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import Perceptron
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer, StandardScaler
from sklearn.svm import SVC, LinearSVC
from sklearn.tree import DecisionTreeClassifier
from threadpoolctl import threadpool_limits

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


def _clean(ax):
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


# ==========================================================================
# Данные: два класса по разные стороны прямой с гарантированным зазором
# ==========================================================================

W_TRUE = np.array([1.0, 0.6]) / np.linalg.norm([1.0, 0.6])
LIM = 3.0


def separable(n, rng, gap=1.2):
    X, y = [], []
    while len(X) < n:
        p = rng.uniform(-LIM, LIM, 2)
        s = p @ W_TRUE
        if abs(s) > gap / 2:
            X.append(p)
            y.append(int(s > 0))
    return np.array(X), np.array(y)


def geo_margin(w, b, X, y):
    return float(((2 * y - 1) * (X @ w + b) / np.linalg.norm(w)).min())


def _line(ax, w, b, offset=0.0, **kw):
    """Прямая w·x + b = offset в границах картинки."""
    xs = np.linspace(-LIM, LIM, 2)
    if abs(w[1]) > 1e-9:
        ax.plot(xs, (offset - b - w[0] * xs) / w[1], **kw)
    else:
        ax.axvline((offset - b) / w[0], **kw)


def _scatter(ax, X, y, s=16):
    ax.scatter(X[y == 0, 0], X[y == 0, 1], s=s, color=C_BLUE, linewidths=0, alpha=0.8)
    ax.scatter(X[y == 1, 0], X[y == 1, 1], s=s, color=C_ORANGE, linewidths=0, alpha=0.8)


# ==========================================================================
# 1. Разделяющих прямых бесконечно много; SVM выбирает одну
# ==========================================================================


def run_perceptron_vs_svm(runs=200, n=20, seed=0):
    rng = np.random.default_rng(seed)
    acc_p, acc_s, m_p, m_s = [], [], [], []
    for r in range(runs):
        X, y = separable(n, rng, gap=0.6)
        Xt, yt = separable(3000, rng, gap=0.0)
        p = Perceptron(max_iter=1000, tol=None, random_state=r).fit(X, y)
        s = SVC(kernel="linear", C=1e6).fit(X, y)
        if (p.predict(X) != y).any():
            continue
        acc_p.append(p.score(Xt, yt))
        acc_s.append(s.score(Xt, yt))
        m_p.append(geo_margin(p.coef_[0], p.intercept_[0], X, y))
        m_s.append(geo_margin(s.coef_[0], s.intercept_[0], X, y))
    return dict(acc_p=np.array(acc_p), acc_s=np.array(acc_s),
                m_p=np.array(m_p), m_s=np.array(m_s))


def draw_max_margin(stats, seed=7):
    _apply_style()
    rng = np.random.default_rng(seed)
    X, y = separable(40, rng, gap=1.0)

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.6, 5.0),
                                   gridspec_kw={"width_ratios": [1, 1.05]})

    for r in range(8):
        p = Perceptron(max_iter=1000, tol=None, random_state=r, shuffle=True).fit(X, y)
        _line(axL, p.coef_[0], p.intercept_[0], color=C_GRAY, lw=1.0, alpha=0.8)
    svm = SVC(kernel="linear", C=1e6).fit(X, y)
    w, b = svm.coef_[0], svm.intercept_[0]
    width = 2 / np.linalg.norm(w)
    xs = np.linspace(-LIM, LIM, 2)
    axL.fill_between(xs, (-1 - b - w[0] * xs) / w[1], (1 - b - w[0] * xs) / w[1],
                     color=C_PANEL, alpha=0.9, zorder=0)
    _line(axL, w, b, color=C_INK, lw=2.4)
    _line(axL, w, b, offset=1, color=C_INK, lw=1.0, ls="--")
    _line(axL, w, b, offset=-1, color=C_INK, lw=1.0, ls="--")
    _scatter(axL, X, y, s=26)
    sv = svm.support_vectors_
    axL.scatter(sv[:, 0], sv[:, 1], s=150, facecolors="none", edgecolors=C_INK, lw=1.6)
    axL.set_xlim(-LIM, LIM)
    axL.set_ylim(-LIM, LIM)
    axL.set_aspect("equal")
    axL.set_title(f"серые — 8 решений персептрона; чёрная — SVM\n"
                  f"ширина полосы {width:.2f}, опорных векторов {len(sv)} из {len(X)}",
                  fontsize=11)
    _clean(axL)

    lo = min(stats["acc_p"].min(), stats["acc_s"].min())
    bins = np.linspace(np.floor(lo * 50) / 50, 1.0, 33)
    axR.hist(stats["acc_p"], bins=bins, color=C_GRAY, alpha=0.85, histtype="stepfilled",
             label=f"персептрон: среднее {stats['acc_p'].mean():.4f}")
    axR.hist(stats["acc_s"], bins=bins, color=C_INK, lw=2.2, histtype="step",
             label=f"SVM (максимальный отступ): {stats['acc_s'].mean():.4f}")
    axR.set_xlabel("точность на тесте")
    axR.set_ylabel("число прогонов")
    axR.set_title(f"{len(stats['acc_p'])} выборок по 20 точек; отступ на обучении: "
                  f"{stats['m_p'].mean():.2f} против {stats['m_s'].mean():.2f}",
                  fontsize=11)
    axR.legend(fontsize=9.5, loc="upper left")
    axR.grid(alpha=0.25, color=C_GRAY, lw=0.6, axis="y")
    _despine(axR)

    fig.suptitle("Линейная разделимость даёт бесконечно много ответов; "
                 "максимальный отступ выбирает один", fontsize=13, y=1.01)
    fig.tight_layout()
    _save(fig, "max_margin.png")
    return dict(width=width, n_sv=len(sv), n=len(X))


# ==========================================================================
# 1a. Расстояние от точки до гиперплоскости и ширина полосы SVM
# ==========================================================================


def draw_distance_to_hyperplane():
    """Схема для вывода формулы расстояния и геометрического отступа."""
    _apply_style()
    w = np.array([1.0, 0.6])
    b = 0.0
    norm_w = np.linalg.norm(w)
    x0 = np.array([1.7, 1.8])
    projection = x0 - (x0 @ w + b) / (norm_w**2) * w

    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(11.5, 4.7))

    _line(ax_left, w, b, color=C_INK, lw=2.2)
    ax_left.plot(
        [x0[0], projection[0]],
        [x0[1], projection[1]],
        color=C_ORANGE,
        lw=2.0,
        ls="--",
    )
    ax_left.scatter([x0[0]], [x0[1]], s=80, color=C_ORANGE, zorder=3)
    ax_left.scatter([projection[0]], [projection[1]], s=55, color=C_BLUE, zorder=3)
    ax_left.annotate(
        "$x_0$",
        xy=x0,
        xytext=(8, 8),
        textcoords="offset points",
        color=C_ORANGE,
        fontsize=12,
    )
    ax_left.annotate(
        "$x_\\perp$",
        xy=projection,
        xytext=(8, -16),
        textcoords="offset points",
        color=C_BLUE,
        fontsize=12,
    )
    ax_left.annotate(
        "",
        xy=projection,
        xytext=x0,
        arrowprops={"arrowstyle": "<->", "color": C_ORANGE, "lw": 1.4},
    )
    ax_left.text(
        -2.8,
        2.25,
        r"$d=\frac{|w\cdot x_0+b|}{\|w\|}$",
        fontsize=13,
        bbox={"facecolor": C_BG, "edgecolor": "none", "pad": 2},
    )
    ax_left.set_title("расстояние до границы — по нормали $w$", fontsize=11.5)

    for offset, color, ls in [(-1, C_BLUE, "--"), (0, C_INK, "-"), (1, C_ORANGE, "--")]:
        _line(ax_right, w, b, offset=offset, color=color, lw=2.0 if offset == 0 else 1.3, ls=ls)
    p0 = np.zeros(2)
    p1 = w / (norm_w**2)
    ax_right.annotate(
        "",
        xy=p1,
        xytext=p0,
        arrowprops={"arrowstyle": "<->", "color": C_INK, "lw": 1.4},
    )
    ax_right.text(
        0.35,
        0.18,
        r"$\frac{1}{\|w\|}$",
        fontsize=12,
        bbox={"facecolor": C_BG, "edgecolor": "none", "pad": 1},
    )
    ax_right.text(
        -2.8,
        2.25,
        r"$\text{ширина полосы}=\frac{2}{\|w\|}$",
        fontsize=12.5,
        bbox={"facecolor": C_BG, "edgecolor": "none", "pad": 2},
    )
    ax_right.set_title("у SVM две границы: $w\\cdot x+b=\\pm1$", fontsize=11.5)

    for ax in (ax_left, ax_right):
        ax.set_xlim(-3, 3)
        ax.set_ylim(-3, 3)
        ax.set_aspect("equal")
        _clean(ax)

    fig.suptitle("От расстояния от точки до линии к геометрическому отступу", fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "distance_to_hyperplane.png")


# ==========================================================================
# 2. Один выброс и мягкий отступ
# ==========================================================================


def with_outlier(X, y, rng):
    """Точка класса 1 в зазоре со стороны класса 0: данные остаются разделимыми."""
    along = rng.uniform(1.5, 2.5) * np.array([-W_TRUE[1], W_TRUE[0]])
    out = along - 0.45 * W_TRUE
    return np.vstack([X, out]), np.append(y, 1), out


def run_outlier(runs=150, soft_c=0.5, seed=0):
    rng = np.random.default_rng(seed)
    acc = {k: [] for k in ("clean", "hard", "soft")}
    width = {k: [] for k in acc}
    tilt = {k: [] for k in acc}
    for _ in range(runs):
        X, y = separable(60, rng)
        Xt, yt = separable(4000, rng, gap=0.0)
        Xo, yo, _ = with_outlier(X, y, rng)
        for k, (XX, yy, C) in {"clean": (X, y, 1e6), "hard": (Xo, yo, 1e6),
                               "soft": (Xo, yo, soft_c)}.items():
            m = SVC(kernel="linear", C=C).fit(XX, yy)
            w = m.coef_[0]
            acc[k].append(m.score(Xt, yt))
            width[k].append(2 / np.linalg.norm(w))
            tilt[k].append(np.degrees(np.arccos(np.clip(abs(w @ W_TRUE) / np.linalg.norm(w),
                                                        0, 1))))
    return {k: dict(acc=np.mean(acc[k]), worst=np.min(acc[k]), width=np.mean(width[k]),
                    tilt=np.mean(tilt[k])) for k in acc}, soft_c


def draw_soft_margin(outlier_stats, seed=3):
    _apply_style()
    stats, soft_c = outlier_stats
    rng = np.random.default_rng(seed)
    X, y = separable(60, rng)
    Xo, yo, out = with_outlier(X, y, rng)
    Xt, yt = separable(4000, np.random.default_rng(99), gap=0.0)

    fig = plt.figure(figsize=(13.4, 4.6))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.05, 0.9, 1.1], wspace=0.32)

    ax1 = fig.add_subplot(gs[0, 0])
    _scatter(ax1, Xo, yo, s=20)
    ax1.scatter([out[0]], [out[1]], s=210, facecolors="none", edgecolors=C_ORANGE, lw=2.0)
    for XX, yy, C, color, ls, label in [
        (X, y, 1e6, C_GRAY, "-", "жёсткий, без выброса"),
        (Xo, yo, 1e6, C_ORANGE, "-", "жёсткий, с выбросом"),
        (Xo, yo, soft_c, C_INK, "--", f"мягкий $C$ = {soft_c}, с выбросом"),
    ]:
        m = SVC(kernel="linear", C=C).fit(XX, yy)
        _line(ax1, m.coef_[0], m.intercept_[0], color=color, lw=2.2, ls=ls, label=label)
    ax1.set_xlim(-LIM, LIM)
    ax1.set_ylim(-LIM, LIM)
    ax1.set_aspect("equal")
    ax1.legend(fontsize=8.8, loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=1)
    ax1.set_title("одна точка в зазоре", fontsize=11)
    _clean(ax1)

    ax2 = fig.add_subplot(gs[0, 1])
    keys = ["clean", "hard", "soft"]
    labels = ["жёсткий\nбез выброса", "жёсткий\nс выбросом", "мягкий\nс выбросом"]
    colors = [C_GRAY, C_ORANGE, C_INK]
    xs = np.arange(3)
    ax2.bar(xs, [stats[k]["width"] for k in keys], color=colors, width=0.62)
    for x, k in zip(xs, keys):
        ax2.text(x, stats[k]["width"] + 0.04,
                 f"{stats[k]['width']:.2f}\nточн. {stats[k]['acc']:.3f}",
                 ha="center", fontsize=9.3)
    ax2.set_xticks(xs, labels, fontsize=9)
    ax2.set_ylim(0, max(stats[k]["width"] for k in keys) * 1.35)
    ax2.set_ylabel("ширина полосы $2/\\|w\\|$")
    ax2.set_title("среднее по 150 выборкам", fontsize=11)
    ax2.grid(alpha=0.25, color=C_GRAY, lw=0.6, axis="y")
    _despine(ax2)

    ax3 = fig.add_subplot(gs[0, 2])
    Cs = np.logspace(-3, 4, 22)
    widths, n_sv, accs = [], [], []
    for C in Cs:
        m = SVC(kernel="linear", C=C).fit(Xo, yo)
        widths.append(2 / np.linalg.norm(m.coef_[0]))
        n_sv.append(m.n_support_.sum())
        accs.append(m.score(Xt, yt))
    ax3.plot(Cs, widths, color=C_INK, lw=2.2, marker="o", ms=3.5, label="ширина полосы")
    ax3.set_xscale("log")
    ax3.set_yscale("log")
    ax3.set_xlabel("$C$ (лог)")
    ax3.set_ylabel("ширина полосы (лог)")
    ax3b = ax3.twinx()
    ax3b.plot(Cs, accs, color=C_ORANGE, lw=2.2, marker="s", ms=3.5, label="точность на тесте")
    ax3b.set_ylabel("точность на тесте", color=C_ORANGE)
    ax3b.tick_params(colors=C_ORANGE)
    for s in ax3b.spines.values():
        s.set_visible(False)
    ax3.set_title(f"$C$ решает, сколько стоит нарушение:\n"
                  f"опорных векторов {n_sv[0]} при $C$=0.001 и {n_sv[-1]} при $C$=10⁴",
                  fontsize=10.5)
    lines = ax3.get_lines() + ax3b.get_lines()
    ax3.legend(lines, [ln.get_label() for ln in lines], fontsize=9, loc="lower left")
    ax3.grid(alpha=0.25, color=C_GRAY, lw=0.6, which="both")
    _despine(ax3, keep=("left", "bottom"))

    fig.suptitle("Жёсткий отступ подчиняется одной точке; мягкий платит за нарушение "
                 "и сохраняет границу", fontsize=13, y=1.03)
    _save(fig, "soft_margin_outlier.png")
    return dict(Cs=Cs, widths=widths, n_sv=n_sv, accs=accs)


# ==========================================================================
# 3. Как vanilla SVM справится с этим набором данных
# ==========================================================================


def four_datasets(seed=11):
    rng = np.random.default_rng(seed)
    X1, y1 = separable(300, rng)
    X2, y2 = separable(300, rng)
    X2, y2, _ = with_outlier(X2, y2, rng)
    X3, y3 = make_circles(400, noise=0.08, factor=0.45, random_state=1)
    X3 = X3 * 2.6
    X4, y4 = make_moons(400, noise=0.18, random_state=2)
    X4 = (X4 - X4.mean(0)) * 1.9
    return {"разделимые": (X1, y1), "разделимые + выброс": (X2, y2),
            "концентрические окружности": (X3, y3), "полумесяцы": (X4, y4)}


def draw_vanilla(seed=0):
    _apply_style()
    data = four_datasets()
    fig, axes = plt.subplots(2, 4, figsize=(14.0, 7.2))
    gx, gy = np.meshgrid(np.linspace(-LIM, LIM, 260), np.linspace(-LIM, LIM, 260))
    grid = np.column_stack([gx.ravel(), gy.ravel()])
    rows = []

    for col, (name, (X, y)) in enumerate(data.items()):
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.4, random_state=seed,
                                              stratify=y)
        models = [
            ("линейный SVM, $C$ = 1", SVC(kernel="linear", C=1.0)),
            ("SVM с RBF-ядром, $C$ = 1", SVC(kernel="rbf", C=1.0, gamma="scale")),
        ]
        accs = []
        for row, (label, m) in enumerate(models):
            m.fit(Xtr, ytr)
            acc = m.score(Xte, yte)
            accs.append(acc)
            ax = axes[row, col]
            Z = m.decision_function(grid).reshape(gx.shape)
            ax.contourf(gx, gy, Z > 0, levels=[-0.5, 0.5, 1.5],
                        colors=["#dfe8f1", "#f5ddd3"], alpha=0.9)
            ax.contour(gx, gy, Z, levels=[0], colors=[C_INK], linewidths=1.8)
            _scatter(ax, X, y, s=9)
            if name == "разделимые + выброс":
                ax.scatter([X[-1, 0]], [X[-1, 1]], s=120, facecolors="none",
                           edgecolors=C_ORANGE, lw=1.8)
            ax.set_xlim(-LIM, LIM)
            ax.set_ylim(-LIM, LIM)
            ax.set_aspect("equal")
            ax.set_title(f"точность {acc:.3f}", fontsize=11,
                         color=C_ORANGE if acc < 0.9 else C_INK)
            _clean(ax)
            if col == 0:
                ax.text(-LIM - 0.35, 0, label, rotation=90, va="center", ha="right",
                        fontsize=10.5)
        axes[0, col].text(0, LIM + 0.9, name, ha="center", fontsize=11.5)
        rows.append((name, accs[0], accs[1]))

    fig.suptitle("«Как vanilla SVM справится с этим набором?» — прямой ответ прогоном",
                 fontsize=13.5, y=1.02)
    fig.tight_layout()
    _save(fig, "vanilla_svm_datasets.png")
    return rows


# ==========================================================================
# 4. Ядерный трюк: подъём в пространство, где граница — плоскость
# ==========================================================================


def draw_kernel_trick(seed=0):
    _apply_style()
    X, y = make_circles(400, noise=0.08, factor=0.45, random_state=1)
    z = (X**2).sum(1)
    lift = np.column_stack([X, z])
    lin3 = SVC(kernel="linear", C=10.0).fit(lift, y)
    acc_lift = lin3.score(lift, y)
    acc_flat = SVC(kernel="linear", C=10.0).fit(X, y).score(X, y)
    w, b = lin3.coef_[0], lin3.intercept_[0]

    fig = plt.figure(figsize=(13.6, 4.6))
    ax1 = fig.add_subplot(1, 3, 1, projection="3d")
    ax1.scatter(lift[y == 0, 0], lift[y == 0, 1], lift[y == 0, 2], s=7, color=C_BLUE,
                alpha=0.8, depthshade=False)
    ax1.scatter(lift[y == 1, 0], lift[y == 1, 1], lift[y == 1, 2], s=7, color=C_ORANGE,
                alpha=0.8, depthshade=False)
    gx, gy = np.meshgrid(np.linspace(-1.2, 1.2, 12), np.linspace(-1.2, 1.2, 12))
    gz = -(w[0] * gx + w[1] * gy + b) / w[2]
    ax1.plot_surface(gx, gy, gz, color=C_GRAY, alpha=0.25, linewidth=0)
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.set_zticks([])
    ax1.set_xlabel("$x_1$", labelpad=-10)
    ax1.set_ylabel("$x_2$", labelpad=-10)
    ax1.set_zlabel("$x_1^2 + x_2^2$", labelpad=-8)
    ax1.set_facecolor(C_BG)
    for pane in (ax1.xaxis.pane, ax1.yaxis.pane, ax1.zaxis.pane):
        pane.set_facecolor(C_BG)
        pane.set_edgecolor(C_PANEL)
    ax1.view_init(elev=16, azim=-58)
    ax1.set_title(f"плоскость в 3D: точность {acc_lift:.3f}\n(прямая в 2D: {acc_flat:.3f})",
                  fontsize=11)

    # RBF: ширина ядра управляет сложностью
    Xm, ym = make_moons(500, noise=0.25, random_state=3)
    Xtr, Xte, ytr, yte = train_test_split(Xm, ym, test_size=0.5, random_state=0,
                                          stratify=ym)
    gammas = np.logspace(-3, 3, 25)
    tr, te, nsv = [], [], []
    for g in gammas:
        m = SVC(kernel="rbf", C=1.0, gamma=g).fit(Xtr, ytr)
        tr.append(m.score(Xtr, ytr))
        te.append(m.score(Xte, yte))
        nsv.append(m.n_support_.sum() / len(ytr))
    g_best = gammas[int(np.argmax(te))]

    ax2 = fig.add_subplot(1, 3, 2)
    ax2.plot(gammas, tr, color=C_INK, lw=1.6, ls="--", label="обучение")
    ax2.plot(gammas, te, color=C_ORANGE, lw=2.4, label="тест")
    ax2.plot(gammas, nsv, color=C_BLUE, lw=1.8, label="доля опорных векторов")
    ax2.axvline(g_best, color=C_GREEN, ls=":", lw=1.4)
    ax2.text(g_best * 1.3, 0.12, f"лучшее $\\gamma$ ≈ {g_best:.2g}\nтест {max(te):.3f}",
             fontsize=9.5, color=C_GREEN)
    ax2.set_xscale("log")
    ax2.set_ylim(0, 1.05)
    ax2.set_xlabel("$\\gamma$ в $K(x, z) = e^{-\\gamma\\|x - z\\|^2}$ (лог)")
    ax2.set_title("RBF: узкое ядро запоминает,\nширокое усредняет", fontsize=11)
    ax2.legend(fontsize=9, loc="center left")
    ax2.grid(alpha=0.25, color=C_GRAY, lw=0.6)
    _despine(ax2)

    # размерность явного отображения против стоимости ядра
    ax3 = fig.add_subplot(1, 3, 3)
    degrees = np.arange(1, 11)
    for d, color in ((10, C_GREEN), (100, C_BLUE), (1000, C_ORANGE)):
        dims = [math.comb(d + p, p) for p in degrees]
        ax3.plot(degrees, dims, color=color, lw=2.2, marker="o", ms=4,
                 label=f"$d$ = {d}: при $p$ = 5 → {math.comb(d + 5, 5):.2g}")
    ax3.set_yscale("log")
    ax3.set_xlabel("степень полинома $p$")
    ax3.set_ylabel("признаков в явном $\\phi(x)$ (лог)")
    ax3.set_title("$K(x, z) = (x\\cdot z + 1)^p$ стоит $O(d)$,\n"
                  "а явное $\\phi(x)$ — $\\binom{d+p}{p}$ координат", fontsize=11)
    ax3.legend(fontsize=9)
    ax3.grid(alpha=0.25, color=C_GRAY, lw=0.6, which="both")
    _despine(ax3)

    fig.suptitle("Ядро считает скалярное произведение в пространстве, "
                 "которое никто не строит", fontsize=13, y=1.03)
    fig.tight_layout()
    _save(fig, "kernel_trick.png")
    return dict(acc_lift=acc_lift, acc_flat=acc_flat, g_best=g_best, best_te=max(te),
                tr_hi=tr[-1], te_hi=te[-1], nsv_hi=nsv[-1], tr_lo=tr[0], te_lo=te[0])


# ==========================================================================
# 5. Бустинг тоже растит отступы
# ==========================================================================


def run_boosting_margins(T=600, seed=3):
    X, y = make_classification(n_samples=1500, n_features=10, n_informative=6,
                               n_redundant=2, class_sep=1.0, flip_y=0.0,
                               random_state=seed)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.5, random_state=0)
    ada = AdaBoostClassifier(DecisionTreeClassifier(max_depth=2), n_estimators=T,
                             learning_rate=0.5, random_state=0).fit(Xtr, ytr)
    a = ada.estimator_weights_[: len(ada.estimators_)]
    H_tr = np.array([2 * e.predict(Xtr) - 1 for e in ada.estimators_])
    H_te = np.array([2 * e.predict(Xte) - 1 for e in ada.estimators_])
    cum_a = np.cumsum(a)
    F_tr = np.cumsum(a[:, None] * H_tr, axis=0) / cum_a[:, None]
    F_te = np.cumsum(a[:, None] * H_te, axis=0) / cum_a[:, None]
    ys, yts = 2 * ytr - 1, 2 * yte - 1
    margins = ys[None, :] * F_tr                     # (T, n) нормированные отступы
    train_err = np.mean(margins <= 0, axis=1)
    test_err = np.mean(yts[None, :] * F_te <= 0, axis=1)
    return dict(margins=margins, train_err=train_err, test_err=test_err)


def draw_boosting_margins(r):
    _apply_style()
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.6, 4.5))
    T_all = len(r["train_err"])
    for T, color in ((5, C_GRAY), (50, C_BLUE), (200, C_GREEN), (T_all, C_INK)):
        m = np.sort(r["margins"][T - 1])
        axL.plot(m, np.arange(1, len(m) + 1) / len(m), color=color, lw=2.2,
                 label=f"T = {T}: мин. отступ {m[0]:+.3f}")
    axL.axvline(0, color=C_ORANGE, ls="--", lw=1.2)
    axL.set_xlim(-0.8, 1.0)
    axL.set_xlabel("нормированный отступ $y\\,\\sum_t \\alpha_t h_t(x) / \\sum_t \\alpha_t$")
    axL.set_ylabel("доля обучающих объектов с отступом не больше")
    axL.set_title("хвост слабых отступов уезжает вправо", fontsize=11.5)
    axL.legend(fontsize=9.5, loc="center left", bbox_to_anchor=(0.0, 0.62))

    Ts = np.arange(1, T_all + 1)
    axR.plot(Ts, r["train_err"], color=C_INK, lw=1.8, ls="--", label="ошибка на обучении")
    axR.plot(Ts, r["test_err"], color=C_ORANGE, lw=2.4, label="ошибка на тесте")
    zero = int(np.argmax(r["train_err"] == 0)) + 1 if (r["train_err"] == 0).any() else None
    if zero:
        axR.axvline(zero, color=C_GRAY, ls=":", lw=1.3)
        axR.annotate(f"ошибка на обучении = 0 с T = {zero},\nа тест продолжает падать",
                     xy=(zero, 0.0), xytext=(1.15, 0.008), fontsize=9.5, color=C_INK,
                     arrowprops=dict(arrowstyle="->", color=C_GRAY, lw=1.1))
    axR.set_xscale("log")
    axR.set_xlabel("число слабых учеников T (лог)")
    axR.set_ylabel("доля ошибок")
    axR.set_title(f"тест: {r['test_err'][4]:.3f} при T=5 → {r['test_err'][-1]:.3f} "
                  f"при T={T_all}", fontsize=11.5)
    axR.legend(fontsize=9.5, loc="upper right")

    for ax in (axL, axR):
        ax.grid(alpha=0.25, color=C_GRAY, lw=0.6)
        _despine(ax)

    fig.suptitle("AdaBoost продолжает раздвигать отступы и после нулевой ошибки "
                 "на обучении", fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "boosting_margins.png")
    ms = r["margins"]
    return dict(zero=zero, test_first=r["test_err"][4], test_last=r["test_err"][-1],
                test_at_zero=r["test_err"][zero - 1] if zero else None,
                snapshots={T: (float(ms[T - 1].min()), float(np.quantile(ms[T - 1], 0.05)),
                               float(np.median(ms[T - 1])))
                           for T in (5, 50, 200, T_all)})


# ==========================================================================
# 6. Где что выигрывает
# ==========================================================================


def regime_tabular(rng, n=3000):
    """Разнородная таблица: категории-коды, тяжёлые хвосты, пороги, взаимодействия."""
    X = np.column_stack([
        rng.integers(0, 12, n),
        np.exp(rng.normal(3, 1.5, n)),
        rng.normal(0, 1, n),
        rng.integers(0, 2, n),
        *[rng.normal(0, 1, n) for _ in range(6)],
    ])
    logit = (np.isin(X[:, 0], [2, 5, 7]) * 2.0 + (X[:, 1] > 60) * 1.5
             - 1.2 * X[:, 3] * (X[:, 2] > 0) - 1.0)
    y = (rng.random(n) < 1 / (1 + np.exp(-3 * logit))).astype(int)
    return X, y


def regime_oblique(rng, n=600):
    """Гладкая косая граница в двух признаках."""
    X = rng.normal(size=(n, 2))
    y = ((X[:, 0] + X[:, 1]) + 0.15 * rng.normal(size=n) > 0).astype(int)
    return X, y


def regime_text(rng, n=600, p=4000):
    """Мешок слов: мало объектов, тысячи редких признаков, слабый сигнал в каждом."""
    base = np.full(p, 0.004)
    p1, p0 = base.copy(), base.copy()
    p1[:120] = 0.02
    p0[120:240] = 0.02
    y = rng.integers(0, 2, n)
    probs = np.where(y[:, None] == 1, p1, p0)
    X = (rng.random((n, p)) < probs).astype(float)
    return X, y


def run_regimes(seed=4):
    rows = []
    # у каждого типа данных своя стандартная предобработка для SVM:
    # плотные признаки стандартизуют, мешок слов нормируют по строкам (как tf-idf)
    for name, gen, prep in (("разнородная таблица", regime_tabular, StandardScaler),
                            ("гладкая косая граница", regime_oblique, StandardScaler),
                            ("мешок слов, $p \\gg n$", regime_text, Normalizer)):
        X, y = gen(np.random.default_rng(seed))
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.4, random_state=0,
                                              stratify=y)
        with threadpool_limits(1):
            gbm = HistGradientBoostingClassifier(random_state=0).fit(Xtr, ytr)
            rbf = make_pipeline(prep(), SVC(kernel="rbf")).fit(Xtr, ytr)
            lin = make_pipeline(prep(), LinearSVC(C=1.0)).fit(Xtr, ytr)
        rows.append((name, gbm.score(Xte, yte), rbf.score(Xte, yte), lin.score(Xte, yte)))

    timing = []
    for n in (1000, 2000, 4000, 8000, 16000, 32000):
        X, y = make_classification(n_samples=n, n_features=20, random_state=0)
        with threadpool_limits(1):
            t = time.perf_counter()
            SVC(kernel="rbf").fit(X, y)
            ts = time.perf_counter() - t
            t = time.perf_counter()
            HistGradientBoostingClassifier(max_iter=100, early_stopping=False).fit(X, y)
            tg = time.perf_counter() - t
        timing.append((n, ts, tg))
    return rows, timing


def draw_regimes(res):
    _apply_style()
    rows, timing = res
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.8, 4.6),
                                   gridspec_kw={"width_ratios": [1.2, 1]})

    xs = np.arange(len(rows))
    wbar = 0.26
    for k, (label, color) in enumerate((("градиентный бустинг", C_ORANGE),
                                        ("SVM с RBF-ядром", C_BLUE),
                                        ("линейный SVM", C_INK))):
        vals = [r[k + 1] for r in rows]
        axL.bar(xs + (k - 1) * wbar, vals, width=wbar, color=color, label=label)
        for x, v in zip(xs, vals):
            axL.text(x + (k - 1) * wbar, v + 0.012, f"{v:.2f}", ha="center", fontsize=8.8)
    axL.set_xticks(xs, [r[0] for r in rows], fontsize=10)
    axL.set_ylim(0.4, 1.06)
    axL.axhline(0.5, color=C_GRAY, ls=":", lw=1.2)
    axL.set_ylabel("точность на тесте")
    axL.set_title("у каждой модели есть свой режим", fontsize=11.5)
    axL.legend(fontsize=9.5, loc="upper right", ncol=3, bbox_to_anchor=(1.0, 1.0))
    axL.grid(alpha=0.25, color=C_GRAY, lw=0.6, axis="y")
    _despine(axL)

    ns = np.array([t[0] for t in timing])
    ts = np.array([t[1] for t in timing])
    tg = np.array([t[2] for t in timing])
    slope_s = np.polyfit(np.log(ns[2:]), np.log(ts[2:]), 1)[0]
    slope_g = np.polyfit(np.log(ns[2:]), np.log(tg[2:]), 1)[0]
    axR.plot(ns, ts, color=C_BLUE, lw=2.4, marker="o", ms=5,
             label=f"SVM с RBF-ядром: время ∝ $n^{{{slope_s:.1f}}}$")
    axR.plot(ns, tg, color=C_ORANGE, lw=2.4, marker="s", ms=5,
             label=f"гистограммный бустинг: ∝ $n^{{{slope_g:.1f}}}$")
    axR.set_xscale("log")
    axR.set_yscale("log")
    axR.set_xlabel("объектов в обучении (лог)")
    axR.set_ylabel("время обучения, с (лог)")
    axR.set_title("один поток, 20 признаков", fontsize=11.5)
    axR.legend(fontsize=9.5, loc="upper left")
    axR.grid(alpha=0.25, color=C_GRAY, lw=0.6, which="both")
    _despine(axR)

    fig.suptitle("Бустинг строит признаки из данных, SVM сравнивает объекты "
                 "по заданной похожести", fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "where_each_wins.png")
    return rows, timing, slope_s, slope_g


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    print("Генерация схем «SVM и градиентный бустинг»:")
    pv = run_perceptron_vs_svm()
    mm = draw_max_margin(pv)
    draw_distance_to_hyperplane()
    out_stats = run_outlier()
    sm = draw_soft_margin(out_stats)
    vanilla = draw_vanilla()
    kt = draw_kernel_trick()
    bm = draw_boosting_margins(run_boosting_margins())
    rows, timing, slope_s, slope_g = draw_regimes(run_regimes())

    print("\nЧисла для текста лекции:")
    print(f"  пример: ширина полосы {mm['width']:.2f}, опорных векторов {mm['n_sv']} из {mm['n']}")
    print(f"  персептрон против SVM ({len(pv['acc_p'])} прогонов): точность "
          f"{pv['acc_p'].mean():.4f} ± {pv['acc_p'].std():.4f} против "
          f"{pv['acc_s'].mean():.4f} ± {pv['acc_s'].std():.4f}; отступ "
          f"{pv['m_p'].mean():.3f} против {pv['m_s'].mean():.3f}; SVM не хуже в "
          f"{np.mean(pv['acc_s'] >= pv['acc_p']):.0%}")
    stats, soft_c = out_stats
    for k, lab in (("clean", "жёсткий без выброса"), ("hard", "жёсткий с выбросом"),
                   ("soft", f"мягкий C={soft_c} с выбросом")):
        s = stats[k]
        print(f"  {lab:24s}: точность {s['acc']:.4f} (худшая {s['worst']:.3f}), "
              f"ширина {s['width']:.3f}, наклон {s['tilt']:.1f}°")
    print(f"  C-свип: опорных {sm['n_sv'][0]} → {sm['n_sv'][-1]}, ширина "
          f"{sm['widths'][0]:.2f} → {sm['widths'][-1]:.3f}, точность "
          f"{sm['accs'][0]:.3f} → {max(sm['accs']):.3f} (макс) → {sm['accs'][-1]:.3f}")
    for name, a_lin, a_rbf in vanilla:
        print(f"  {name:28s}: линейный {a_lin:.3f}, RBF {a_rbf:.3f}")
    print(f"  подъём окружностей: плоскость в 3D {kt['acc_lift']:.3f}, прямая в 2D "
          f"{kt['acc_flat']:.3f}")
    print(f"  RBF γ: лучшее {kt['g_best']:.2g} (тест {kt['best_te']:.3f}); при γ=1e-3 "
          f"train {kt['tr_lo']:.3f} test {kt['te_lo']:.3f}; при γ=1e3 train {kt['tr_hi']:.3f} "
          f"test {kt['te_hi']:.3f}, опорных {kt['nsv_hi']:.0%}")
    for d in (10, 100, 1000):
        print(f"  явный полином p=5 при d={d}: {math.comb(d + 5, 5)} признаков")
    print(f"  AdaBoost: ошибка на обучении 0 с T={bm['zero']}, тест {bm['test_first']:.3f} "
          f"(T=5) → {bm['test_at_zero']:.3f} (T={bm['zero']}) → {bm['test_last']:.3f} (конец)")
    for T, (mn, p5, med) in bm["snapshots"].items():
        print(f"    T={T:4d}: минимальный отступ {mn:+.3f}, 5-й перцентиль {p5:+.3f}, "
              f"медиана {med:+.3f}")
    for name, g, r, lin in rows:
        print(f"  {name:24s}: бустинг {g:.3f}, SVM RBF {r:.3f}, линейный SVM {lin:.3f}")
    for n, ts, tg in timing:
        print(f"  n={n:6d}: SVM RBF {ts:6.2f} с, HistGBM {tg:5.2f} с")
    print(f"  наклоны: SVM {slope_s:.2f}, бустинг {slope_g:.2f}")


if __name__ == "__main__":
    main()
