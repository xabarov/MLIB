"""Точные диаграммы к лекции о предположениях линейной регрессии."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
C_BG, C_INK, C_GRAY = "#faf9f5", "#141413", "#b0aea5"
C_PANEL, C_ORANGE, C_BLUE, C_GREEN = "#e8e6dc", "#d97757", "#6a9bcc", "#788c5d"


def style():
    plt.rcParams.update({
        "figure.facecolor": C_BG, "axes.facecolor": C_BG,
        "axes.edgecolor": C_GRAY, "axes.labelcolor": C_INK,
        "text.color": C_INK, "xtick.color": C_INK, "ytick.color": C_INK,
        "font.size": 10, "axes.titlesize": 11, "legend.frameon": False,
    })


def save(fig, name):
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS / name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)
    print(name)


def residual_patterns(seed=0):
    rng = np.random.default_rng(seed)
    x = np.linspace(0, 10, 300)
    y_linear = 1.0 + 0.7 * x + rng.normal(0, 1.0, len(x))
    y_nonlinear = 1.0 + 0.7 * x + 0.07 * (x - 5) ** 2 + rng.normal(0, 0.65, len(x))
    y_hetero = 1.0 + 0.7 * x + rng.normal(0, 0.16 + 0.15 * x, len(x))
    datasets = [(y_linear, "линейность + постоянный разброс"),
                (y_nonlinear, "нелинейность"),
                (y_hetero, "непостоянный разброс")]
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.3), sharex=True)
    for ax, (y, title) in zip(axes, datasets):
        coef = np.polyfit(x, y, 1)
        fitted = np.polyval(coef, x)
        residual = y - fitted
        ax.scatter(fitted, residual, s=10, color=C_BLUE, alpha=0.55, linewidths=0)
        ax.axhline(0, color=C_INK, lw=1)
        ax.set_title(title)
        ax.set_xlabel("предсказание $\\hat y$")
        ax.set_ylabel("остаток $y - \\hat y$")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    fig.suptitle("Остатки: форма облака показывает, какое предположение нарушено", y=1.04, fontsize=13)
    fig.tight_layout()
    save(fig, "residual_patterns.png")


def multicollinearity(seed=1):
    rng = np.random.default_rng(seed)
    n, reps = 120, 220
    beta_true = np.array([2.0, 2.0])
    estimates = []
    for _ in range(reps):
        x1 = rng.normal(size=n)
        x2 = 0.97 * x1 + np.sqrt(1 - 0.97**2) * rng.normal(size=n)
        X = np.column_stack([np.ones(n), x1, x2])
        y = X @ np.r_[0.5, beta_true] + rng.normal(0, 1.0, n)
        estimates.append(np.linalg.lstsq(X, y, rcond=None)[0][1:])
    est = np.array(estimates)
    fig, ax = plt.subplots(figsize=(5.5, 4.4))
    ax.scatter(est[:, 0], est[:, 1], s=18, color=C_ORANGE, alpha=0.55, linewidths=0)
    ax.axvline(beta_true[0], color=C_GRAY, lw=1, ls="--")
    ax.axhline(beta_true[1], color=C_GRAY, lw=1, ls="--")
    ax.scatter(*beta_true, color=C_INK, s=75, zorder=3, label="истинные коэффициенты")
    ax.set_xlabel("оценка $\\hat\\beta_1$")
    ax.set_ylabel("оценка $\\hat\\beta_2$")
    ax.set_title("При коррелированных признаках коэффициенты гуляют")
    ax.legend(loc="upper left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    save(fig, "multicollinearity_instability.png")


def endogeneity(seed=2):
    rng = np.random.default_rng(seed)
    n, reps = 180, 180
    slopes = []
    true = 2.0
    for _ in range(reps):
        z = rng.normal(size=n)
        x = z + rng.normal(0, 0.7, n)
        u = 1.4 * z + rng.normal(0, 0.7, n)  # общая причина X и ошибки
        y = 1.0 + true * x + u
        slopes.append(np.polyfit(x, y, 1)[0])
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    ax.hist(slopes, bins=22, color=C_ORANGE, alpha=0.78, edgecolor=C_BG)
    ax.axvline(true, color=C_INK, lw=2, label="истинный эффект = 2")
    ax.axvline(np.mean(slopes), color=C_BLUE, lw=2, ls="--", label=f"средняя оценка = {np.mean(slopes):.2f}")
    ax.set_xlabel("оценка наклона $\\hat\\beta$")
    ax.set_ylabel("число прогонов")
    ax.set_title("Эндогенность: OLS систематически видит лишний эффект")
    ax.legend()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    save(fig, "endogeneity_bias.png")


def main():
    style()
    residual_patterns()
    multicollinearity()
    endogeneity()


if __name__ == "__main__":
    main()
