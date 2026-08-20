"""Точные схемы для лекции про основные задачи машинного обучения."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

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
    plt.rcParams.update({
        "figure.facecolor": C_BG,
        "axes.facecolor": C_BG,
        "axes.edgecolor": C_GRAY,
        "text.color": C_INK,
        "font.size": 11,
        "font.family": "sans-serif",
        "axes.spines.top": False,
        "axes.spines.right": False,
    })


def _save(fig, name):
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS / f"{name}.png", dpi=150, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)
    print(f"Saved: assets/{name}.png")


def draw_ml_tasks_overview():
    """2x2 grid: classification, regression, ranking, clustering."""
    _apply_style()
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    fig.patch.set_facecolor(C_BG)
    fig.suptitle("Основные задачи машинного обучения", fontsize=15,
                 color=C_INK, fontweight="bold", y=1.01)

    rng = np.random.default_rng(42)

    # ── Panel 1: Classification ──────────────────────────────────────────
    ax = axes[0][0]
    ax.set_facecolor(C_BG)
    n = 60
    x0 = rng.normal(loc=[2.5, 2.5], scale=0.6, size=(n, 2))
    x1 = rng.normal(loc=[4.5, 4.5], scale=0.6, size=(n, 2))
    ax.scatter(x0[:, 0], x0[:, 1], color=C_BLUE, s=40, alpha=0.8,
               label="Класс 0", zorder=3)
    ax.scatter(x1[:, 0], x1[:, 1], color=C_ORANGE, s=40, marker="^", alpha=0.8,
               label="Класс 1", zorder=3)
    # decision boundary approximation
    boundary_x = np.linspace(1, 6, 100)
    ax.plot(boundary_x, boundary_x, color=C_INK, lw=2, linestyle="--",
            label="граница решения", zorder=2)
    ax.set_xlim(1, 6)
    ax.set_ylim(1, 6)
    ax.set_title("Классификация", fontsize=13, color=C_INK, fontweight="bold")
    ax.set_xlabel("$x_1$", color=C_INK)
    ax.set_ylabel("$x_2$", color=C_INK)
    ax.legend(fontsize=9, facecolor=C_PANEL, edgecolor=C_GRAY)

    # ── Panel 2: Regression ──────────────────────────────────────────────
    ax = axes[0][1]
    ax.set_facecolor(C_BG)
    x_reg = rng.uniform(0, 10, 80)
    y_reg = 1.5 * x_reg + 3 + rng.normal(0, 2, 80)
    ax.scatter(x_reg, y_reg, color=C_BLUE, s=30, alpha=0.7, label="Наблюдения")
    xs = np.linspace(0, 10, 200)
    ax.plot(xs, 1.5 * xs + 3, color=C_ORANGE, lw=2.5, label="$a(x) = wx + b$")
    # residual lines for 5 points
    sample_idx = [5, 20, 35, 50, 65]
    for i in sample_idx:
        y_hat = 1.5 * x_reg[i] + 3
        ax.plot([x_reg[i], x_reg[i]], [y_reg[i], y_hat],
                color=C_GREEN, lw=1.2, linestyle=":")
    ax.set_title("Регрессия", fontsize=13, color=C_INK, fontweight="bold")
    ax.set_xlabel("$x$", color=C_INK)
    ax.set_ylabel("$y$", color=C_INK)
    ax.legend(fontsize=9, facecolor=C_PANEL, edgecolor=C_GRAY)

    # ── Panel 3: Ranking ─────────────────────────────────────────────────
    ax = axes[1][0]
    ax.set_facecolor(C_BG)
    ax.axis("off")
    ax.set_title("Ранжирование", fontsize=13, color=C_INK, fontweight="bold")

    docs = ["Документ A", "Документ B", "Документ C", "Документ D", "Документ E"]
    relevance = [0.92, 0.71, 0.65, 0.38, 0.12]
    colors = [C_ORANGE, C_ORANGE, C_BLUE, C_BLUE, C_GRAY]
    bar_x = 0.18
    bar_y_start = 0.82
    step = 0.16

    for i, (doc, rel, col) in enumerate(zip(docs, relevance, colors)):
        y = bar_y_start - i * step
        # rank badge
        badge = mpatches.FancyBboxPatch(
            (bar_x - 0.14, y - 0.055), 0.11, 0.10,
            boxstyle="round,pad=0.01",
            facecolor=col, edgecolor="none", transform=ax.transAxes, zorder=3
        )
        ax.add_patch(badge)
        ax.text(bar_x - 0.085, y, f"#{i+1}", ha="center", va="center",
                fontsize=11, color="white", fontweight="bold",
                transform=ax.transAxes)
        # bar
        bar = mpatches.FancyBboxPatch(
            (bar_x, y - 0.04), rel * 0.6, 0.08,
            boxstyle="round,pad=0.005",
            facecolor=col, edgecolor="none", alpha=0.8,
            transform=ax.transAxes, zorder=2
        )
        ax.add_patch(bar)
        ax.text(bar_x + rel * 0.6 + 0.02, y, f"{doc}  ({rel:.2f})",
                ha="left", va="center", fontsize=9.5, color=C_INK,
                transform=ax.transAxes)

    ax.text(0.5, 0.06, "Запрос: «ML курс» — отсортировано по релевантности",
            ha="center", va="center", fontsize=9, color=C_GRAY,
            transform=ax.transAxes, style="italic")

    # ── Panel 4: Clustering ──────────────────────────────────────────────
    ax = axes[1][1]
    ax.set_facecolor(C_BG)
    centers = [[2, 2], [5, 5], [2, 6]]
    cluster_colors = [C_BLUE, C_ORANGE, C_GREEN]
    for center, col in zip(centers, cluster_colors):
        pts = rng.normal(loc=center, scale=0.7, size=(50, 2))
        ax.scatter(pts[:, 0], pts[:, 1], color=col, s=35, alpha=0.75, zorder=2)
        # centroid
        ax.scatter(*center, color=col, s=140, marker="*",
                   edgecolors=C_INK, linewidths=1, zorder=4)

    ax.set_title("Кластеризация (без учителя)", fontsize=13, color=C_INK, fontweight="bold")
    ax.set_xlabel("$x_1$", color=C_INK)
    ax.set_ylabel("$x_2$", color=C_INK)

    legend_patches = [
        mpatches.Patch(color=C_BLUE,   label="Кластер 1"),
        mpatches.Patch(color=C_ORANGE, label="Кластер 2"),
        mpatches.Patch(color=C_GREEN,  label="Кластер 3"),
    ]
    ax.legend(handles=legend_patches, fontsize=9,
              facecolor=C_PANEL, edgecolor=C_GRAY)

    plt.tight_layout()
    _save(fig, "ml_tasks_overview")


def draw_supervised_unsupervised():
    """Two-panel: labeled data (supervised) vs unlabeled (unsupervised)."""
    _apply_style()
    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(13, 5.5))
    fig.patch.set_facecolor(C_BG)

    rng = np.random.default_rng(7)

    for ax in (ax_l, ax_r):
        ax.set_facecolor(C_BG)
        ax.set_xlim(0, 8)
        ax.set_ylim(0, 8)
        ax.set_aspect("equal")
        ax.axis("off")

    pts_a = rng.normal(loc=[2.5, 5.5], scale=0.8, size=(18, 2))
    pts_b = rng.normal(loc=[5.5, 2.5], scale=0.8, size=(18, 2))

    # LEFT: supervised — colored and labeled
    ax_l.set_title("С учителем (Supervised)\n$\\{(x_i, y_i)\\}$ — есть метки",
                   fontsize=12, color=C_INK, fontweight="bold", pad=10)
    ax_l.scatter(pts_a[:, 0], pts_a[:, 1], color=C_BLUE, s=70,
                 zorder=3, label="Класс A (y=0)")
    ax_l.scatter(pts_b[:, 0], pts_b[:, 1], color=C_ORANGE, s=70, marker="^",
                 zorder=3, label="Класс B (y=1)")
    # labels next to a few points
    for i in range(0, 18, 5):
        ax_l.text(pts_a[i, 0] + 0.2, pts_a[i, 1], "A",
                  fontsize=8, color=C_BLUE, fontweight="bold")
        ax_l.text(pts_b[i, 0] + 0.2, pts_b[i, 1], "B",
                  fontsize=8, color=C_ORANGE, fontweight="bold")
    ax_l.legend(fontsize=9, facecolor=C_PANEL, edgecolor=C_GRAY)

    # Decision boundary
    bx = np.linspace(0, 8, 100)
    ax_l.plot(bx, bx, color=C_INK, lw=2, linestyle="--", alpha=0.5,
              label="граница решения")
    ax_l.text(6.5, 7.2, "Задача:\nнайти $a(x)$", fontsize=9,
              color=C_INK, ha="center",
              bbox=dict(facecolor=C_PANEL, edgecolor=C_GRAY,
                        boxstyle="round,pad=0.3"))

    # RIGHT: unsupervised — all gray, no labels
    ax_r.set_title("Без учителя (Unsupervised)\n$\\{x_i\\}$ — меток нет",
                   fontsize=12, color=C_INK, fontweight="bold", pad=10)
    all_pts = np.vstack([pts_a, pts_b])
    ax_r.scatter(all_pts[:, 0], all_pts[:, 1], color=C_GRAY, s=70,
                 zorder=3, alpha=0.85)

    # Cluster circles (what unsupervised discovers)
    circle_a = mpatches.Circle((2.5, 5.5), 1.4, fill=False,
                                edgecolor=C_BLUE, lw=2, linestyle="--", zorder=2)
    circle_b = mpatches.Circle((5.5, 2.5), 1.4, fill=False,
                                edgecolor=C_ORANGE, lw=2, linestyle="--", zorder=2)
    ax_r.add_patch(circle_a)
    ax_r.add_patch(circle_b)
    ax_r.text(2.5, 7.2, "Кластер ?", fontsize=9, ha="center",
              color=C_BLUE, fontweight="bold")
    ax_r.text(5.5, 0.8, "Кластер ?", fontsize=9, ha="center",
              color=C_ORANGE, fontweight="bold")
    ax_r.text(6.5, 7.2, "Задача:\nнайти структуру", fontsize=9,
              color=C_INK, ha="center",
              bbox=dict(facecolor=C_PANEL, edgecolor=C_GRAY,
                        boxstyle="round,pad=0.3"))

    fig.suptitle("Обучение с учителем vs. без учителя",
                 fontsize=14, color=C_INK, fontweight="bold", y=1.02)
    plt.tight_layout()
    _save(fig, "supervised_unsupervised")


def draw_generalization_gap():
    """Train/test error vs model complexity — bias-variance tradeoff."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.set_facecolor(C_BG)
    fig.patch.set_facecolor(C_BG)

    complexity = np.linspace(1, 10, 200)

    # Train error: decreases then plateaus near 0
    train_err = 0.5 / complexity + 0.02

    # Test error: U-shaped — high bias then high variance
    test_err = 0.5 / complexity + 0.04 * (complexity - 3) ** 2 + 0.05

    ax.plot(complexity, train_err, color=C_BLUE, lw=2.5, label="Ошибка на train")
    ax.plot(complexity, test_err, color=C_ORANGE, lw=2.5, label="Ошибка на test")

    # Optimal point
    opt_idx = int(np.argmin(test_err))
    opt_c = complexity[opt_idx]
    opt_e = test_err[opt_idx]
    ax.scatter([opt_c], [opt_e], color=C_GREEN, s=120, zorder=5)
    ax.annotate("Оптимальная\nсложность", xy=(opt_c, opt_e),
                xytext=(opt_c + 1.5, opt_e + 0.15),
                fontsize=10, color=C_GREEN, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C_GREEN, lw=1.5))

    # Regions
    ax.axvspan(1, opt_c, alpha=0.07, color=C_BLUE, label="Недообучение (high bias)")
    ax.axvspan(opt_c, 10, alpha=0.07, color=C_ORANGE, label="Переобучение (high variance)")

    ax.text(2.0, 0.75, "Недообучение\n(underfitting)", fontsize=9.5,
            color=C_BLUE, ha="center", style="italic")
    ax.text(7.5, 0.75, "Переобучение\n(overfitting)", fontsize=9.5,
            color=C_ORANGE, ha="center", style="italic")

    # Gap annotation
    gap_c = 7.0
    gap_train = float(np.interp(gap_c, complexity, train_err))
    gap_test = float(np.interp(gap_c, complexity, test_err))
    ax.annotate("", xy=(gap_c, gap_test), xytext=(gap_c, gap_train),
                arrowprops=dict(arrowstyle="<->", color=C_INK, lw=1.5))
    ax.text(gap_c + 0.2, (gap_train + gap_test) / 2, "generalization\ngap",
            fontsize=8.5, color=C_INK, va="center")

    ax.set_xlabel("Сложность модели", fontsize=12, color=C_INK)
    ax.set_ylabel("Ошибка", fontsize=12, color=C_INK)
    ax.set_title("Обобщающая способность: компромисс смещение–дисперсия",
                 fontsize=13, color=C_INK, fontweight="bold")
    ax.legend(fontsize=10, facecolor=C_PANEL, edgecolor=C_GRAY)
    ax.set_xlim(1, 10)
    ax.set_ylim(0, 1.0)
    ax.tick_params(colors=C_INK)

    plt.tight_layout()
    _save(fig, "generalization_gap")


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_ml_tasks_overview()
    draw_supervised_unsupervised()
    draw_generalization_gap()
    print("All visuals generated.")


if __name__ == "__main__":
    main()
