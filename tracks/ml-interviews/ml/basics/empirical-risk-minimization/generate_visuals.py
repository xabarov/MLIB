"""Точные схемы для темы «Минимизация эмпирического риска».

Все числа на картинках — результат прогона, а не подобранные вручную значения:
разброс эмпирического риска меряется по сотням подвыборок и сверяется с
sqrt(R(1-R)/n), оптимистичность победителя — честным перебором K моделей на
данных без сигнала, ступеньки 0-1 риска считаются вдоль среза параметров,
двойной спуск — решением минимальной нормы на случайных признаках, а неявная
регуляризация — настоящим градиентным спуском на миллионы шагов.
"""

import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures

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
# 1. Эмпирический риск как оценка истинного
# ==========================================================================


def run_concentration(ns=(10, 30, 100, 300, 1000, 3000, 10000), reps=400, seed=0):
    """Для ОДНОЙ фиксированной модели: R̂ несмещена, разброс падает как 1/sqrt(n)."""
    rng = np.random.default_rng(seed)
    d, N = 5, 300_000
    X = rng.normal(size=(N, d))
    y = (X @ rng.normal(size=d) + 0.8 * rng.normal(size=N) > 0).astype(int)
    w = rng.normal(size=d)
    err = (X @ w > 0).astype(int) != y          # ошибка на каждом объекте
    R_true = float(err.mean())

    rows = []
    for n in ns:
        dev = np.array([err[rng.integers(0, N, n)].mean() - R_true for _ in range(reps)])
        rows.append((n, dev.std(), dev.mean(), np.sqrt(R_true * (1 - R_true) / n)))
    return R_true, rows


def run_winners_curse(Ks=(1, 10, 100, 1000, 10000), n=50, d=10, reps=60, seed=1):
    """Данных без сигнала: чем больше моделей перебрали, тем оптимистичнее победитель."""
    rng = np.random.default_rng(seed)
    rows = []
    for K in Ks:
        emp, tru = [], []
        for _ in range(reps):
            X = rng.normal(size=(n, d))
            y = rng.integers(0, 2, n)
            W = rng.normal(size=(K, d))
            risks = np.mean((X @ W.T > 0).astype(int) != y[:, None], axis=0)
            k = int(np.argmin(risks))
            emp.append(risks[k])
            Xt, yt = rng.normal(size=(4000, d)), rng.integers(0, 2, 4000)
            tru.append(np.mean((Xt @ W[k] > 0).astype(int) != yt))
        rows.append((K, float(np.mean(emp)), float(np.mean(tru)),
                     float(np.sqrt(np.log(max(K, 2)) / (2 * n)))))
    return rows, n


def draw_empirical_vs_true(conc, curse):
    _apply_style()
    R_true, rows = conc
    curse_rows, n_curse = curse

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.6, 4.5))

    ns = np.array([r[0] for r in rows])
    sd = np.array([r[1] for r in rows])
    th = np.array([r[3] for r in rows])
    bias = np.array([r[2] for r in rows])
    axL.plot(ns, sd, color=C_ORANGE, lw=2.4, marker="o", ms=6,
             label="измеренный разброс $R̂ - R$")
    axL.plot(ns, th, color=C_INK, lw=1.3, ls="--",
             label="$\\sqrt{R(1-R)/n}$")
    axL.plot(ns, np.abs(bias), color=C_BLUE, lw=1.8, marker="s", ms=4,
             label="|среднее смещение| — колеблется около нуля")
    axL.set_xscale("log")
    axL.set_yscale("log")
    axL.set_xlabel("размер выборки $n$ (лог)")
    axL.set_ylabel("отклонение эмпирического риска (лог)")
    axL.set_title(f"одна фиксированная модель, истинный риск $R$ = {R_true:.3f}",
                  fontsize=11.5)
    axL.legend(fontsize=9.5, loc="lower left")

    Ks = np.array([r[0] for r in curse_rows])
    emp = np.array([r[1] for r in curse_rows])
    tru = np.array([r[2] for r in curse_rows])
    bound = np.array([r[3] for r in curse_rows])
    axR.plot(Ks, emp, color=C_ORANGE, lw=2.4, marker="o", ms=6,
             label="эмпирический риск победителя")
    axR.plot(Ks, tru, color=C_INK, lw=2.4, marker="s", ms=6,
             label="его же истинный риск")
    axR.fill_between(Ks, emp, tru, color=C_ORANGE, alpha=0.15)
    axR.plot(Ks, 0.5 - bound, color=C_GRAY, lw=1.3, ls="--",
             label="ниже этой границы (Хёфдинг + union bound)\nне должна опускаться ни одна из $K$ моделей")
    axR.axhline(0.5, color=C_GRAY, ls=":", lw=1.2)
    axR.annotate(f"разрыв {tru[-1] - emp[-1]:.2f} при $K$ = {Ks[-1]}",
                 xy=(Ks[-1], (emp[-1] + tru[-1]) / 2), xytext=(Ks[-1] / 8, 0.33),
                 fontsize=9.5, color=C_ORANGE,
                 arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=1.1))
    axR.set_xscale("log")
    axR.set_xlabel("сколько моделей перебрали, $K$ (лог)")
    axR.set_ylabel("доля ошибок")
    axR.set_ylim(0.2, 0.56)
    axR.set_title(f"данные без сигнала: $n$ = {n_curse}, метки — монетка", fontsize=11.5)
    axR.legend(fontsize=9.5, loc="lower left")

    for ax in (axL, axR):
        ax.grid(alpha=0.25, color=C_GRAY, lw=0.6, which="both")
        _despine(ax)

    fig.suptitle("Эмпирический риск честен для одной модели и лжёт про выбранную из многих",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "empirical_vs_true.png")
    return dict(R_true=R_true, rows=rows, curse=curse_rows, n_curse=n_curse)


# ==========================================================================
# 2. Вторая подмена: суррогатные потери
# ==========================================================================


def run_slice(n=60, seed=0, grid=4000):
    """Эмпирический 0-1 риск вдоль одномерного среза параметров: лестница."""
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, 2))
    y = (X[:, 0] + 0.7 * X[:, 1] + 0.5 * rng.normal(size=n) > 0).astype(int)
    th = np.linspace(0, np.pi, grid)
    r01, rlog, rhinge = [], [], []
    for t in th:
        w = np.array([np.cos(t), np.sin(t)])
        m = (2 * y - 1) * (X @ w)
        r01.append(np.mean(m <= 0))
        rlog.append(np.mean(np.log1p(np.exp(-m))))
        rhinge.append(np.mean(np.maximum(0, 1 - m)))
    r01 = np.array(r01)
    n_loc = sum(1 for i in range(1, len(r01) - 1)
                if r01[i] < r01[i - 1] and r01[i] <= r01[i + 1])
    return th, r01, np.array(rlog), np.array(rhinge), n_loc, len(np.unique(r01))


def draw_surrogates(slice_res):
    _apply_style()
    th, r01, rlog, rhinge, n_loc, n_levels = slice_res

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.6, 4.5))

    m = np.linspace(-3, 3, 600)
    curves = [
        ("0-1: $\\mathbf{1}[m \\leq 0]$", (m <= 0).astype(float), C_INK, "-", 2.6),
        ("hinge: $\\max(0, 1-m)$", np.maximum(0, 1 - m), C_ORANGE, "-", 2.0),
        ("логистическая: $\\log(1+e^{-m})$", np.log1p(np.exp(-m)), C_BLUE, "-", 2.0),
        ("экспоненциальная: $e^{-m}$", np.exp(-m), C_GREEN, "-", 2.0),
        ("квадратичная: $(1-m)^2$", (1 - m) ** 2, C_GRAY, "--", 1.8),
    ]
    for label, v, color, ls, lw in curves:
        axL.plot(m, v, color=color, lw=lw, ls=ls, label=label)
    axL.set_ylim(0, 4)
    axL.set_xlabel("отступ $m = y\\,f(x)$")
    axL.set_ylabel("потеря на объекте")
    axL.set_title("все суррогаты — выпуклые мажоранты 0-1", fontsize=11.5)
    axL.legend(fontsize=9.5)
    axL.axvline(0, color=C_GRAY, ls=":", lw=1.2)

    deg = np.degrees(th)
    axR.step(deg, r01, color=C_INK, lw=2.2, where="mid",
             label=f"эмпирический 0-1 риск: {n_loc} локальных минимумов")
    axR.set_xlabel("направление $w = (\\cos\\theta, \\sin\\theta)$, градусы")
    axR.set_ylabel("доля ошибок", color=C_INK)
    ax2 = axR.twinx()
    ax2.plot(deg, rlog, color=C_BLUE, lw=2.2, label="логистический риск: 1 минимум")
    ax2.set_ylabel("логистический риск", color=C_BLUE)
    ax2.tick_params(colors=C_BLUE)
    for s in ax2.spines.values():
        s.set_visible(False)
    best01 = deg[int(np.argmin(r01))]
    bestlog = deg[int(np.argmin(rlog))]
    axR.axvline(best01, color=C_INK, ls=":", lw=1.2)
    ax2.axvline(bestlog, color=C_BLUE, ls=":", lw=1.2)
    axR.set_title(f"срез по одному параметру: {n_levels} ступенек,\n"
                  f"минимумы в {best01:.0f}° и {bestlog:.0f}°", fontsize=11)
    lines = axR.get_lines()[:1] + ax2.get_lines()[:1]
    axR.legend(lines, [ln.get_label() for ln in lines], fontsize=9.5, loc="upper center")
    _despine(axR)
    axR.grid(alpha=0.25, color=C_GRAY, lw=0.6)
    _despine(axL)
    axL.grid(alpha=0.25, color=C_GRAY, lw=0.6)

    fig.suptitle("0-1 потерю не минимизируют напрямую: у неё нет градиента и полно "
                 "локальных минимумов", fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "surrogate_losses.png")
    return dict(n_loc=n_loc, n_levels=n_levels, best01=best01, bestlog=bestlog)


# ==========================================================================
# 3. Сложность класса: классическая U и двойной спуск
# ==========================================================================


def run_classic_u(n=30, degrees=range(0, 16), reps=60, seed=2):
    rng = np.random.default_rng(seed)
    tr_all, te_all = [], []
    for _ in range(reps):
        x = rng.uniform(-1, 1, n)
        y = np.sin(3 * x) + 0.3 * rng.normal(size=n)
        xt = rng.uniform(-1, 1, 2000)
        yt = np.sin(3 * xt) + 0.3 * rng.normal(size=2000)
        tr, te = [], []
        for p in degrees:
            F = PolynomialFeatures(p).fit_transform(x[:, None])
            Ft = PolynomialFeatures(p).fit_transform(xt[:, None])
            m = Ridge(alpha=1e-10, fit_intercept=False).fit(F, y)
            tr.append(np.mean((m.predict(F) - y) ** 2))
            te.append(np.mean((m.predict(Ft) - yt) ** 2))
        tr_all.append(tr)
        te_all.append(te)
    return np.array(list(degrees)), np.mean(tr_all, 0), np.median(te_all, 0)


def run_double_descent(n_tr=100, d0=20, reps=12, seed=3):
    rng = np.random.default_rng(seed)
    ps = np.unique(np.concatenate([
        np.round(np.logspace(np.log10(5), np.log10(3000), 34)).astype(int),
        [n_tr - 10, n_tr, n_tr + 10],          # точка интерполяции p = n обязательна
    ]))
    tr_all, te_all = [], []
    for _ in range(reps):
        beta = rng.normal(size=d0)
        Xtr = rng.normal(size=(n_tr, d0))
        Xte = rng.normal(size=(2000, d0))
        ytr = Xtr @ beta + 0.5 * rng.normal(size=n_tr)
        yte = Xte @ beta + 0.5 * rng.normal(size=2000)
        tr, te = [], []
        for p in ps:
            W = rng.normal(size=(d0, p)) / np.sqrt(d0)
            Ftr = np.maximum(Xtr @ W, 0)
            Fte = np.maximum(Xte @ W, 0)
            coef = np.linalg.pinv(Ftr) @ ytr          # решение минимальной нормы
            tr.append(np.mean((Ftr @ coef - ytr) ** 2))
            te.append(np.mean((Fte @ coef - yte) ** 2))
        tr_all.append(tr)
        te_all.append(te)
    return ps, np.mean(tr_all, 0), np.median(te_all, 0), n_tr


def draw_complexity(classic, dd):
    _apply_style()
    degrees, tr_c, te_c = classic
    ps, tr_d, te_d, n_tr = dd

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.6, 4.5))

    axL.plot(degrees, tr_c, color=C_BLUE, lw=2.2, marker="o", ms=4,
             label="эмпирический риск (обучение)")
    axL.plot(degrees, te_c, color=C_ORANGE, lw=2.4, marker="s", ms=4,
             label="истинный риск (оценка по тесту)")
    k = int(np.argmin(te_c))
    axL.scatter([degrees[k]], [te_c[k]], color=C_GREEN, s=60, zorder=5)
    axL.annotate(f"минимум при степени {degrees[k]}",
                 xy=(degrees[k], te_c[k]), xytext=(degrees[k] + 1.2, te_c[k] * 6),
                 fontsize=9.5, color=C_GREEN,
                 arrowprops=dict(arrowstyle="->", color=C_GREEN, lw=1.1))
    axL.set_yscale("log")
    axL.set_xlabel("степень полинома")
    axL.set_ylabel("MSE (лог)")
    axL.set_title("классическая картина: $n$ = 30 точек, $\\sin 3x$ + шум", fontsize=11.5)
    axL.legend(fontsize=9.5, loc="upper center")

    floor = 1e-4
    axR.plot(ps, np.maximum(tr_d, floor), color=C_BLUE, lw=2.2,
             label="эмпирический риск (ниже $10^{-4}$ — машинный ноль)")
    axR.plot(ps, te_d, color=C_ORANGE, lw=2.4, label="истинный риск (оценка по тесту)")
    axR.axvline(n_tr, color=C_INK, ls="--", lw=1.4)
    peak = int(np.argmax(te_d))
    axR.annotate(f"пик {te_d[peak]:.0f} при $p$ = {ps[peak]} = $n$",
                 xy=(ps[peak], te_d[peak]), xytext=(ps[peak] / 9, te_d[peak] / 3),
                 fontsize=9.5, color=C_INK,
                 arrowprops=dict(arrowstyle="->", color=C_INK, lw=1.1))
    axR.annotate(f"при $p$ = {ps[-1]}: {te_d[-1]:.2f}\n(лучше любой модели слева)",
                 xy=(ps[-1], te_d[-1]), xytext=(ps[-1] / 14, te_d[-1] / 9),
                 fontsize=9.5, color=C_ORANGE,
                 arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=1.1))
    axR.set_ylim(floor / 2, te_d[peak] * 6)
    axR.set_xscale("log")
    axR.set_yscale("log")
    axR.set_xlabel("число случайных признаков $p$ (лог)")
    axR.set_ylabel("MSE (лог)")
    axR.set_title(f"двойной спуск: решение минимальной нормы, $n$ = {n_tr}", fontsize=11.5)
    axR.legend(fontsize=9.5, loc="lower left")

    for ax in (axL, axR):
        ax.grid(alpha=0.25, color=C_GRAY, lw=0.6, which="both")
        _despine(ax)

    fig.suptitle("«Чем богаче класс, тем хуже обобщение» — верно слева и неверно справа",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "complexity_double_descent.png")
    return dict(best_degree=int(degrees[k]), best_test=float(te_c[k]),
                dd_peak_p=int(ps[peak]), dd_peak=float(te_d[peak]),
                dd_last_p=int(ps[-1]), dd_last=float(te_d[-1]),
                dd_before=float(te_d[np.argmin(np.abs(ps - 50))]))


# ==========================================================================
# 4. Третья подмена: «минимизировать» не значит «получить минимум»
# ==========================================================================


def run_implicit_bias(steps=3_000_000, lr=4.0, seed=1):
    rng = np.random.default_rng(seed)
    far = rng.normal(loc=[2.2, 2.0], scale=0.5, size=(60, 2))
    neg = rng.normal(loc=[-2.0, -2.2], scale=0.5, size=(60, 2))
    near_pos = np.array([[0.75, 0.15], [0.6, 0.45]])
    near_neg = np.array([[-0.5, -0.6], [-0.7, -0.25]])
    X = np.vstack([far, near_pos, neg, near_neg])
    y = np.array([1] * 62 + [-1] * 62)

    r = minimize(lambda w: 0.5 * w @ w, np.zeros(2), jac=lambda w: w,
                 constraints=[{"type": "ineq", "fun": lambda w: y * (X @ w) - 1,
                               "jac": lambda w: y[:, None] * X}],
                 method="SLSQP", options={"maxiter": 800, "ftol": 1e-14})
    w_mm = r.x / np.linalg.norm(r.x)
    w_mean = X[y == 1].mean(0) - X[y == -1].mean(0)
    w_mean /= np.linalg.norm(w_mean)

    ts, cos_mm, cos_mean, margins, norms, risks = [], [], [], [], [], []
    w = np.zeros(2)
    checkpoints = set(np.unique(np.round(np.logspace(0, np.log10(steps), 60)).astype(int)))
    for t in range(1, steps + 1):
        m = y * (X @ w)
        w -= lr * (-(y[:, None] * X * (1 / (1 + np.exp(m)))[:, None]).mean(0))
        if t in checkpoints:
            wn = w / np.linalg.norm(w)
            ts.append(t)
            cos_mm.append(float(wn @ w_mm))
            cos_mean.append(float(wn @ w_mean))
            margins.append(float((y * (X @ wn)).min()))
            norms.append(float(np.linalg.norm(w)))
            risks.append(float(np.mean(y * (X @ w) <= 0)))
    return dict(ts=np.array(ts), cos_mm=np.array(cos_mm), cos_mean=np.array(cos_mean),
                margins=np.array(margins), norms=np.array(norms), risks=np.array(risks),
                mm_margin=float((y * (X @ w_mm)).min()),
                mean_margin=float((y * (X @ w_mean)).min()),
                cos_mm_mean=float(w_mm @ w_mean))


def run_regularization(n=60, p=40, reps=200, seed=5):
    """Регуляризованный ERM: минимум истинного риска достигается при lambda > 0."""
    rng = np.random.default_rng(seed)
    lams = np.logspace(-4, 3, 30)
    tr_all, te_all = [], []
    for _ in range(reps):
        beta = rng.normal(size=p) / np.sqrt(p)
        X = rng.normal(size=(n, p))
        y = X @ beta + 0.7 * rng.normal(size=n)
        Xt = rng.normal(size=(4000, p))
        yt = Xt @ beta + 0.7 * rng.normal(size=4000)
        tr, te = [], []
        for lam in lams:
            m = Ridge(alpha=lam, fit_intercept=False).fit(X, y)
            tr.append(np.mean((m.predict(X) - y) ** 2))
            te.append(np.mean((m.predict(Xt) - yt) ** 2))
        tr_all.append(tr)
        te_all.append(te)
    return lams, np.mean(tr_all, 0), np.mean(te_all, 0)


def draw_minimize(imp, reg):
    _apply_style()
    lams, tr, te = reg
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.6, 4.5))

    axL.plot(imp["ts"], imp["cos_mm"], color=C_ORANGE, lw=2.4,
             label="косинус с максимальным отступом")
    axL.plot(imp["ts"], imp["cos_mean"], color=C_BLUE, lw=2.0,
             label="косинус с разностью средних")
    axL.set_xscale("log")
    axL.set_xlabel("шаг градиентного спуска (лог)")
    axL.set_ylabel("косинус между направлениями")
    axL.set_ylim(0.95, 1.003)
    ax2 = axL.twinx()
    ax2.plot(imp["ts"], imp["margins"], color=C_GREEN, lw=2.0, ls="--",
             label="нормированный отступ")
    ax2.axhline(imp["mm_margin"], color=C_GREEN, ls=":", lw=1.2)
    ax2.set_ylabel("нормированный отступ", color=C_GREEN)
    ax2.tick_params(colors=C_GREEN)
    for s in ax2.spines.values():
        s.set_visible(False)
    axL.set_title(f"эмпирический 0-1 риск равен нулю с первого шага,\n"
                  f"но модель меняется ещё {imp['ts'][-1]:.0e} шагов", fontsize=11)
    lines = axL.get_lines() + ax2.get_lines()[:1]
    axL.legend(lines, [ln.get_label() for ln in lines], fontsize=9, loc="center left")

    axR.plot(lams, tr, color=C_BLUE, lw=2.2, label="эмпирический риск (обучение)")
    axR.plot(lams, te, color=C_ORANGE, lw=2.4, label="истинный риск (оценка по тесту)")
    k = int(np.argmin(te))
    axR.scatter([lams[k]], [te[k]], color=C_GREEN, s=60, zorder=5)
    axR.annotate(f"минимум при $\\lambda$ = {lams[k]:.2g}\n"
                 f"{te[k]:.2f} против {te[0]:.2f} при $\\lambda \\to 0$",
                 xy=(lams[k], te[k]), xytext=(lams[k] / 900, te[k] * 1.35),
                 fontsize=9.5, color=C_GREEN,
                 arrowprops=dict(arrowstyle="->", color=C_GREEN, lw=1.1))
    axR.set_xscale("log")
    axR.set_yscale("log")
    axR.set_xlabel("сила регуляризации $\\lambda$ (лог)")
    axR.set_ylabel("MSE (лог)")
    axR.set_title("чистый ERM — это $\\lambda = 0$, и он не оптимален", fontsize=11.5)
    axR.legend(fontsize=9.5, loc="center left")

    for ax in (axL, axR):
        ax.grid(alpha=0.25, color=C_GRAY, lw=0.6, which="both")
        _despine(ax)

    fig.suptitle("«Минимизировать эмпирический риск» не определяет ответ: "
                 "решают алгоритм и регуляризатор", fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "what_minimize_means.png")
    return dict(lam_best=float(lams[k]), te_best=float(te[k]), te_erm=float(te[0]),
                tr_erm=float(tr[0]))


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    print("Генерация схем «Минимизация эмпирического риска»:")
    conc = run_concentration()
    curse = run_winners_curse()
    a = draw_empirical_vs_true(conc, curse)
    b = draw_surrogates(run_slice())
    c = draw_complexity(run_classic_u(), run_double_descent())
    imp = run_implicit_bias()
    d = draw_minimize(imp, run_regularization())

    print("\nЧисла для текста лекции:")
    print(f"  истинный риск фиксированной модели: {a['R_true']:.4f}")
    for n, sd, bias, th in a["rows"]:
        print(f"    n={n:6d}: std(R̂−R) = {sd:.4f}, теория {th:.4f}, смещение {bias:+.4f}")
    for K, emp, tru, bound in a["curse"]:
        print(f"    K={K:6d}: риск победителя {emp:.3f} против истинного {tru:.3f}, "
              f"разрыв {tru - emp:+.3f}, граница {bound:.3f}")
    print(f"  0-1 риск на срезе: {b['n_loc']} локальных минимумов, {b['n_levels']} ступенек; "
          f"минимум 0-1 в {b['best01']:.0f}°, логистической — в {b['bestlog']:.0f}°")
    print(f"  классическая U: минимум теста {c['best_test']:.4f} при степени {c['best_degree']}")
    print(f"  двойной спуск: пик {c['dd_peak']:.1f} при p={c['dd_peak_p']}, "
          f"при p=50 было {c['dd_before']:.2f}, при p={c['dd_last_p']} стало {c['dd_last']:.2f}")
    print(f"  неявная регуляризация: cos(max-margin, разность средних) = "
          f"{imp['cos_mm_mean']:.4f}")
    for i in (0, len(imp["ts"]) // 3, 2 * len(imp["ts"]) // 3, -1):
        print(f"    t={imp['ts'][i]:>9}: ||w|| = {imp['norms'][i]:6.2f}, "
              f"cos с max-margin {imp['cos_mm'][i]:.5f}, отступ {imp['margins'][i]:.4f}, "
              f"0-1 риск {imp['risks'][i]:.3f}")
    print(f"    предел: отступ max-margin {imp['mm_margin']:.4f}, "
          f"у разности средних {imp['mean_margin']:.4f}")
    print(f"  регуляризация: минимум теста {d['te_best']:.3f} при λ = {d['lam_best']:.3g}, "
          f"при λ→0 тест {d['te_erm']:.3f} при обучении {d['tr_erm']:.3f}")


if __name__ == "__main__":
    main()
