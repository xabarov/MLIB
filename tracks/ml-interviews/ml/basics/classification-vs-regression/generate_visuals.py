"""Точные схемы для темы «Классификация и регрессия».

Все кривые считаются на синтетических данных прямо здесь, ничего не рисуется
«на глаз»: числа на осях — результат реального прогона.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import precision_recall_curve
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import SplineTransformer

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

# уровень шума в синтетических данных — нижняя граница достижимого RMSE
NOISE_SIGMA = 0.8


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
            "axes.grid": False,
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


# --------------------------------------------------------------------------
# 1. Геометрия пространства меток: что функция потерь считает «близким»
# --------------------------------------------------------------------------
def draw_label_space_loss():
    nominal = ["кошка", "собака", "птица", "рыба"]
    ordinal = ["1★", "2★", "3★", "4★"]

    zero_one = 1.0 - np.eye(4)
    idx = np.arange(4)
    squared = (idx[:, None] - idx[None, :]) ** 2 / 9.0

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.6))

    for ax, matrix, labels, title, sub in (
        (axes[0], zero_one, nominal, "Номинальные метки → 0-1 потеря",
         "все ошибки стоят одинаково"),
        (axes[1], squared, ordinal, "Порядковые метки → квадратичная потеря",
         "ошибка растёт с расстоянием"),
    ):
        ax.imshow(matrix, cmap=CMAP_WARM, vmin=0, vmax=1)
        ax.set_xticks(idx, labels)
        ax.set_yticks(idx, labels)
        ax.set_xlabel("предсказано")
        ax.set_ylabel("истина")
        ax.set_title(title, pad=14)
        ax.text(0.5, -0.22, sub, transform=ax.transAxes, ha="center",
                color=C_GRAY, fontsize=10)
        for i in idx:
            for j in idx:
                v = matrix[i, j]
                ax.text(j, i, f"{v:.2f}".rstrip("0").rstrip("."),
                        ha="center", va="center", fontsize=10,
                        color=C_BG if v > 0.55 else C_INK)
        _despine(ax, keep=())
        ax.tick_params(length=0)

    fig.suptitle("Разницу задаёт не тип выхода, а метрика на пространстве меток",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "label_space_loss.png")


# --------------------------------------------------------------------------
# 2. Ловушка условного среднего: MSE-регрессия на бимодальной цели
# --------------------------------------------------------------------------
def draw_conditional_mean_trap():
    rng = np.random.default_rng(7)
    n = 600
    x = rng.uniform(0, 10, n)
    branch = rng.random(n) < 0.5
    y = np.where(branch, 1.6 * x + 4.0, -1.6 * x + 26.0) + rng.normal(0, 1.1, n)

    fit = LinearRegression().fit(x[:, None], y)
    grid = np.linspace(0, 10, 100)
    pred = fit.predict(grid[:, None])

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4),
                             gridspec_kw={"width_ratios": [1.55, 1]})

    ax = axes[0]
    ax.scatter(x, y, s=12, color=C_GRAY, alpha=0.75, linewidths=0)
    ax.plot(grid, pred, color=C_ORANGE, lw=2.6, label="регрессия с MSE")
    ax.axvline(5.0, color=C_INK, lw=1.0, ls=":", alpha=0.7)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("MSE предсказывает $E[y \\mid x]$", pad=10)
    ax.legend(loc="upper center")
    _despine(ax)

    # срез при x = 5: два режима, среднее между ними
    slice_mask = np.abs(x - 5.0) < 0.5
    ys = y[slice_mask]
    ax = axes[1]
    ax.hist(ys, bins=14, color=C_PANEL, edgecolor=C_GRAY, orientation="horizontal")
    mean_at_5 = float(fit.predict([[5.0]])[0])
    ax.axhline(mean_at_5, color=C_ORANGE, lw=2.4)
    ax.text(0.97, mean_at_5, f"  $E[y\\mid x{{=}}5] \\approx {mean_at_5:.1f}$",
            transform=ax.get_yaxis_transform(), ha="right", va="bottom",
            color=C_ORANGE, fontsize=10)
    ax.set_xlabel("частота")
    ax.set_title("срез при $x = 5$", pad=10)
    ax.set_yticks([])
    _despine(ax, keep=("bottom",))

    fig.suptitle("Условное среднее попадает туда, где данных нет",
                 fontsize=13, y=1.03)
    fig.tight_layout()
    _save(fig, "conditional_mean_trap.png")


# --------------------------------------------------------------------------
# 3. Биннинг: разрешение против дисперсии оценки
# --------------------------------------------------------------------------
def _make_wave(n, seed):
    """Нелинейная зависимость с постоянным шумом sigma=0.8."""
    rng = np.random.default_rng(seed)
    x = rng.uniform(-3, 3, (n, 1))
    y = np.sin(x.ravel() * 1.4) * 4 + x.ravel() + rng.normal(0, NOISE_SIGMA, n)
    return x, y


def _spline_clf():
    return make_pipeline(
        SplineTransformer(n_knots=12, degree=3),
        LogisticRegression(max_iter=4000, C=5.0),
    )


def _binned_rmse(n_bins, x_tr, y_tr, x_te, y_te):
    """Обучить классификатор по бинам и декодировать обратно в число через E[y]."""
    edges = np.quantile(y_tr, np.linspace(0, 1, n_bins + 1))
    edges[0] -= 1e-9
    edges[-1] += 1e-9
    cls_tr = np.clip(np.digitize(y_tr, edges[1:-1]), 0, n_bins - 1)
    if len(np.unique(cls_tr)) < 2:
        return np.nan
    centers = np.array([
        y_tr[cls_tr == k].mean() if np.any(cls_tr == k) else 0.0
        for k in range(n_bins)
    ])
    clf = _spline_clf().fit(x_tr, cls_tr)
    decoded = clf.predict_proba(x_te) @ centers[clf.classes_]
    return float(np.sqrt(np.mean((decoded - y_te) ** 2)))


def draw_binning_tradeoff():
    bins = np.array([2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64])
    n_test = 400
    curves = {}
    for n_train in (150, 2000):
        x, y = _make_wave(n_train + n_test, seed=3)
        x_tr, y_tr = x[:n_train], y[:n_train]
        x_te, y_te = x[n_train:], y[n_train:]
        curves[n_train] = np.array([
            _binned_rmse(int(k), x_tr, y_tr, x_te, y_te) for k in bins
        ])

    # честный ориентир: прямая регрессия на тех же признаках, 150 объектов
    x, y = _make_wave(150 + n_test, seed=3)
    reg = make_pipeline(SplineTransformer(n_knots=12, degree=3), LinearRegression())
    reg.fit(x[:150], y[:150])
    reg_rmse = float(np.sqrt(np.mean((reg.predict(x[150:]) - y[150:]) ** 2)))

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.3),
                             gridspec_kw={"width_ratios": [1, 1.3]})

    # слева — как выглядит сам биннинг
    ax = axes[0]
    x_show, y_show = _make_wave(500, seed=3)
    ax.scatter(x_show.ravel(), y_show, s=11, color=C_GRAY, alpha=0.7, linewidths=0)
    for e in np.quantile(y_show, np.linspace(0, 1, 7)):
        ax.axhline(e, color=C_BLUE, lw=0.9, alpha=0.85)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("цель нарезана на 6 бинов по квантилям", pad=10)
    _despine(ax)

    # справа — реальный прогон
    ax = axes[1]
    for n_train, color in ((150, C_ORANGE), (2000, C_BLUE)):
        vals = curves[n_train]
        best = int(bins[np.nanargmin(vals)])
        ax.plot(bins, vals, color=color, lw=2.4, marker="o", ms=4,
                label=f"{n_train} объектов обучения (минимум при K={best})")
    ax.axhline(reg_rmse, color=C_GREEN, lw=1.8, ls="--")
    ax.text(bins[-1], reg_rmse, f"прямая регрессия, 150 объектов: {reg_rmse:.2f} ",
            ha="right", va="bottom", fontsize=9.5, color=C_GREEN)
    ax.axhline(NOISE_SIGMA, color=C_GRAY, lw=1.4, ls=":")
    ax.text(bins[-1], NOISE_SIGMA, f"неустранимый шум: {NOISE_SIGMA} ",
            ha="right", va="bottom", fontsize=9.5, color=C_GRAY)
    ax.set_xscale("log", base=2)
    ax.set_xticks(bins, [str(b) for b in bins])
    ax.set_xlabel("число бинов $K$")
    ax.set_ylabel("RMSE на тесте")
    ax.set_title("Цена дробного биннинга — нехватка данных на бин", pad=10)
    ax.legend(loc="upper center", fontsize=9.5)
    _despine(ax)

    fig.suptitle("Регрессия → классификация: сколько бинов брать, решают данные",
                 fontsize=13, y=1.03)
    fig.tight_layout()
    _save(fig, "binning_tradeoff.png")


# --------------------------------------------------------------------------
# 4. Какая потеря какую статистику восстанавливает
# --------------------------------------------------------------------------
def draw_loss_targets():
    rng = np.random.default_rng(11)
    sample = rng.lognormal(mean=0.0, sigma=0.75, size=200_000) * 3.0

    mean = sample.mean()
    median = np.median(sample)
    q90 = np.quantile(sample, 0.9)

    fig, ax = plt.subplots(figsize=(9.5, 4.2))
    ax.hist(sample, bins=160, range=(0, 18), color=C_PANEL,
            edgecolor=C_PANEL, density=True)
    top = ax.get_ylim()[1]

    # подписи разнесены по высоте: median и mean стоят близко по оси x
    for value, color, height, label in (
        (median, C_BLUE, 0.95, f"MAE → медиана = {median:.1f}"),
        (mean, C_ORANGE, 0.78, f"MSE → среднее = {mean:.1f}"),
        (q90, C_GREEN, 0.61, f"pinball(0.9) → квантиль = {q90:.1f}"),
    ):
        ax.axvline(value, color=color, lw=2.4)
        ax.annotate(
            label,
            xy=(value, top * height),
            xytext=(value + 0.45, top * height),
            color=color, fontsize=10.5, va="center", ha="left",
            bbox=dict(facecolor=C_BG, edgecolor="none", pad=1.5),
        )

    ax.set_xlim(0, 18)
    ax.set_xlabel("y при фиксированном x")
    ax.set_ylabel("плотность")
    ax.set_title("Функция потерь выбирает, какую статистику $p(y \\mid x)$ вы получите",
                 pad=12)
    ax.set_yticks([])
    _despine(ax, keep=("bottom",))
    fig.tight_layout()
    _save(fig, "loss_targets.png")


# --------------------------------------------------------------------------
# 5. Вероятность — это регрессия; класс появляется только на пороге
# --------------------------------------------------------------------------
def draw_probability_to_class():
    rng = np.random.default_rng(5)
    n = 900
    y = (rng.random(n) < 0.35).astype(int)
    x = np.where(y == 1, rng.normal(1.4, 1.0, n), rng.normal(-0.4, 1.0, n))[:, None]

    clf = LogisticRegression().fit(x, y)
    proba = clf.predict_proba(x)[:, 1]
    prec, rec, thr = precision_recall_curve(y, proba)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))

    ax = axes[0]
    ax.hist(proba[y == 0], bins=30, range=(0, 1), color=C_PANEL,
            edgecolor=C_GRAY, label="класс 0", alpha=0.95)
    ax.hist(proba[y == 1], bins=30, range=(0, 1), color=C_BLUE,
            edgecolor=C_BLUE, label="класс 1", alpha=0.6)
    ax.axvline(0.5, color=C_ORANGE, lw=2.4)
    ax.text(0.52, ax.get_ylim()[1] * 0.95, "порог 0.5", color=C_ORANGE,
            fontsize=10, va="top")
    ax.set_xlabel("предсказанная $P(y{=}1 \\mid x)$ — непрерывный выход")
    ax.set_ylabel("объектов")
    ax.set_title("Модель выдаёт число, а не класс", pad=10)
    ax.legend(loc="upper right", fontsize=9.5)
    _despine(ax)

    ax = axes[1]
    ax.plot(thr, prec[:-1], color=C_ORANGE, lw=2.4, label="precision")
    ax.plot(thr, rec[:-1], color=C_GREEN, lw=2.4, label="recall")
    ax.axvline(0.5, color=C_INK, lw=1.0, ls=":", alpha=0.8)
    ax.set_xlabel("порог")
    ax.set_ylabel("значение метрики")
    ax.set_title("Класс — отдельное решение поверх числа", pad=10)
    ax.legend(loc="center right", fontsize=9.5)
    _despine(ax)

    fig.suptitle("Классификация = регрессия вероятности + правило принятия решения",
                 fontsize=13, y=1.03)
    fig.tight_layout()
    _save(fig, "probability_to_class.png")


def main():
    _apply_style()
    ASSETS.mkdir(parents=True, exist_ok=True)
    print(f"Generating visuals in {ASSETS}")
    draw_label_space_loss()
    draw_conditional_mean_trap()
    draw_binning_tradeoff()
    draw_loss_targets()
    draw_probability_to_class()


if __name__ == "__main__":
    main()
