"""Точные схемы для лекции про основные модели классификации и регрессии."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
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


def draw_decision_tree():
    """3-level decision tree: internal nodes show feature/threshold/Gini, leaves show class."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("Решающее дерево — структура узлов и критерий Джини",
                 fontsize=14, color=C_INK, fontweight="bold", pad=14)

    BOX_W = 0.17
    BOX_H = 0.15

    # (x_center, y_center, [text_lines], is_leaf, fill_color)
    nodes = [
        (0.50, 0.82, ["$x_1 \\leq 2.5$", "Gini = 0.48", "n = 100"], False, C_PANEL),
        (0.25, 0.52, ["$x_2 \\leq 1.0$", "Gini = 0.35", "n = 45"],  False, C_PANEL),
        (0.75, 0.52, ["$x_3 \\leq 3.2$", "Gini = 0.40", "n = 55"],  False, C_PANEL),
        (0.10, 0.16, ["Класс A", "Gini = 0.00", "n = 30"], True, C_BLUE),
        (0.38, 0.16, ["Класс B", "Gini = 0.08", "n = 15"], True, C_ORANGE),
        (0.62, 0.16, ["Класс A", "Gini = 0.10", "n = 28"], True, C_BLUE),
        (0.90, 0.16, ["Класс B", "Gini = 0.00", "n = 27"], True, C_ORANGE),
    ]

    for xc, yc, lines, is_leaf, col in nodes:
        xl = xc - BOX_W / 2
        yl = yc - BOX_H / 2
        box = mpatches.FancyBboxPatch(
            (xl, yl), BOX_W, BOX_H,
            boxstyle="round,pad=0.01",
            facecolor=col,
            edgecolor=C_INK,
            linewidth=2.0 if not is_leaf else 1.5,
            zorder=3,
            alpha=0.9 if not is_leaf else 0.85,
        )
        ax.add_patch(box)
        fc = "white" if is_leaf else C_INK
        for i, line in enumerate(lines):
            dy = BOX_H * (0.5 - (i + 0.5) / len(lines))
            ax.text(xc, yc + dy, line,
                    ha="center", va="center",
                    fontsize=8.5, color=fc,
                    fontweight="bold" if i == 0 else "normal",
                    zorder=4)

    # (parent_xc, parent_yc, child_xc, child_yc, edge_label)
    edges = [
        (0.50, 0.82, 0.25, 0.52, "Да"),
        (0.50, 0.82, 0.75, 0.52, "Нет"),
        (0.25, 0.52, 0.10, 0.16, "Да"),
        (0.25, 0.52, 0.38, 0.16, "Нет"),
        (0.75, 0.52, 0.62, 0.16, "Да"),
        (0.75, 0.52, 0.90, 0.16, "Нет"),
    ]

    for x1c, y1c, x2c, y2c, label in edges:
        y_start = y1c - BOX_H / 2
        y_end = y2c + BOX_H / 2
        ax.annotate("", xy=(x2c, y_end), xytext=(x1c, y_start),
                    arrowprops=dict(arrowstyle="-|>", color=C_INK, lw=1.5),
                    zorder=2)
        mx = (x1c + x2c) / 2 + 0.01
        my = (y_start + y_end) / 2
        ax.text(mx, my, label, ha="left", va="center",
                fontsize=8, color=C_GREEN, fontweight="bold", zorder=5,
                bbox=dict(facecolor=C_BG, edgecolor="none", pad=1.5))

    node_patch = mpatches.Patch(facecolor=C_PANEL, edgecolor=C_INK, label="Внутренний узел")
    leaf_a = mpatches.Patch(facecolor=C_BLUE, label="Лист: Класс A")
    leaf_b = mpatches.Patch(facecolor=C_ORANGE, label="Лист: Класс B")
    ax.legend(handles=[node_patch, leaf_a, leaf_b], fontsize=9,
              facecolor=C_BG, edgecolor=C_GRAY, loc="lower right")

    _save(fig, "decision_tree")


def draw_decision_boundaries():
    """2×2: illustrative boundaries for four classifier types on XOR-pattern data."""
    _apply_style()
    rng = np.random.default_rng(42)

    cov = [[0.25, 0.0], [0.0, 0.25]]
    c0 = np.vstack([
        rng.multivariate_normal([1.0, 1.0], cov, 50),
        rng.multivariate_normal([4.0, 4.0], cov, 50),
    ])
    c1 = np.vstack([
        rng.multivariate_normal([1.0, 4.0], cov, 50),
        rng.multivariate_normal([4.0, 1.0], cov, 50),
    ])

    xx, yy = np.meshgrid(np.linspace(0, 5, 250), np.linspace(0, 5, 250))

    # Logistic regression: linear boundary — cannot separate XOR pattern
    Z_lr = ((xx + yy) > 5.0).astype(float)

    # Decision tree: axis-aligned XOR split at x=2.5 and y=2.5
    Z_tree = ((xx > 2.5) != (yy > 2.5)).astype(float)

    # Random forest: smooth approximation via sigmoid XOR
    sx = 1.0 / (1.0 + np.exp(-5.0 * (xx - 2.5)))
    sy = 1.0 / (1.0 + np.exp(-5.0 * (yy - 2.5)))
    Z_rf = (sx * (1.0 - sy) + (1.0 - sx) * sy > 0.5).astype(float)

    # SVM RBF: nearest-centroid assignment mimics kernel boundary
    d0 = np.minimum((xx - 1.0)**2 + (yy - 1.0)**2,
                    (xx - 4.0)**2 + (yy - 4.0)**2)
    d1 = np.minimum((xx - 1.0)**2 + (yy - 4.0)**2,
                    (xx - 4.0)**2 + (yy - 1.0)**2)
    Z_svm = (d1 < d0).astype(float)

    titles_Z = [
        ("Лог. регрессия (линейная граница)", Z_lr),
        ("Решающее дерево (глубина 2)",       Z_tree),
        ("Случайный лес",                      Z_rf),
        ("SVM (ядро RBF)",                     Z_svm),
    ]

    cmap_bg = ListedColormap([C_BLUE, C_ORANGE])

    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    fig.patch.set_facecolor(C_BG)
    fig.suptitle("Границы решений: четыре классификатора на XOR-данных",
                 fontsize=14, color=C_INK, fontweight="bold", y=1.01)

    for ax, (title, Z) in zip(axes.ravel(), titles_Z):
        ax.set_facecolor(C_BG)
        ax.contourf(xx, yy, Z, levels=[-0.5, 0.5, 1.5], cmap=cmap_bg, alpha=0.25)
        ax.contour(xx, yy, Z, levels=[0.5], colors=[C_INK], linewidths=1.8)
        ax.scatter(c0[:, 0], c0[:, 1], c=C_BLUE, s=30, alpha=0.85,
                   edgecolors="white", linewidths=0.4, zorder=3)
        ax.scatter(c1[:, 0], c1[:, 1], c=C_ORANGE, s=30, alpha=0.85,
                   marker="^", edgecolors="white", linewidths=0.4, zorder=3)
        ax.set_title(title, fontsize=11, color=C_INK, fontweight="bold")
        ax.tick_params(colors=C_INK, labelsize=8)
        ax.set_xlim(0, 5)
        ax.set_ylim(0, 5)

    leg_c0 = mpatches.Patch(color=C_BLUE, label="Класс 0")
    leg_c1 = mpatches.Patch(color=C_ORANGE, label="Класс 1")
    axes[0, 0].legend(handles=[leg_c0, leg_c1], fontsize=8,
                      facecolor=C_PANEL, edgecolor=C_GRAY, loc="upper left")

    plt.tight_layout()
    _save(fig, "decision_boundaries")


def draw_model_comparison_table():
    """Heatmap: models (rows) × properties (cols), scores 1=low to 5=high."""
    _apply_style()

    models = [
        "Лин. регрессия",
        "Лог. регрессия",
        "Реш. дерево",
        "SVM (RBF)",
        "Случ. лес",
        "GBM / XGBoost",
    ]
    props = [
        "Интерпрет-ть",
        "Скорость обуч.",
        "Точность",
        "Устойч. к выбр.",
        "Без масштаб-я",
        "Без переобуч-я",
        "Раб. с пропуск.",
    ]

    # rows = models, cols = props; 1 = слабо/плохо, 5 = сильно/хорошо
    data = np.array([
        [5, 5, 2, 2, 1, 5, 1],   # Лин. регрессия
        [5, 5, 3, 2, 1, 4, 1],   # Лог. регрессия
        [4, 4, 3, 4, 5, 1, 3],   # Реш. дерево
        [1, 2, 4, 3, 1, 3, 1],   # SVM
        [2, 3, 5, 4, 5, 4, 3],   # Случ. лес
        [2, 2, 5, 4, 5, 3, 4],   # GBM
    ], dtype=float)

    cmap = LinearSegmentedColormap.from_list(
        "model_cmp", [C_ORANGE, C_PANEL, C_GREEN], N=256
    )

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)

    im = ax.imshow(data, cmap=cmap, vmin=1, vmax=5, aspect="auto")

    ax.set_xticks(range(len(props)))
    ax.set_xticklabels(props, fontsize=10, color=C_INK, rotation=35, ha="right")
    ax.set_yticks(range(len(models)))
    ax.set_yticklabels(models, fontsize=11, color=C_INK)
    ax.tick_params(length=0)

    for i in range(len(models)):
        for j in range(len(props)):
            val = int(data[i, j])
            tc = "white" if val <= 1 or val >= 5 else C_INK
            ax.text(j, i, str(val), ha="center", va="center",
                    fontsize=12, color=tc, fontweight="bold")

    ax.set_title("Сравнение моделей: 1 = слабо, 5 = сильно",
                 fontsize=12, color=C_INK, fontweight="bold", pad=12)

    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.04)
    cbar.ax.tick_params(colors=C_INK)

    plt.tight_layout()
    _save(fig, "model_comparison_table")


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_decision_tree()
    draw_decision_boundaries()
    draw_model_comparison_table()
    print("All visuals generated.")


if __name__ == "__main__":
    main()
