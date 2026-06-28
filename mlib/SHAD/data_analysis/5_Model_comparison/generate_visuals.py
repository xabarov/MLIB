"""Точные схемы для лекции про сравнение моделей и метрики."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

C_BG    = "#faf9f5"
C_INK   = "#141413"
C_GRAY  = "#b0aea5"
C_PANEL = "#e8e6dc"
C_ORANGE = "#d97757"
C_BLUE  = "#6a9bcc"
C_GREEN = "#788c5d"


def _apply_style():
    plt.rcParams.update({
        "figure.facecolor": C_BG,
        "axes.facecolor":   C_BG,
        "axes.edgecolor":   C_GRAY,
        "text.color":       C_INK,
        "font.size":        11,
        "font.family":      "sans-serif",
        "axes.spines.top":   False,
        "axes.spines.right": False,
    })


def _save(fig, name):
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS / f"{name}.png", dpi=150, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)
    print(f"Saved: assets/{name}.png")


# ─────────────────────────────────────────────────────────────────────────────
# 1. Confusion matrix with TP/FP/TN/FN and precision/recall arrows
# ─────────────────────────────────────────────────────────────────────────────
def draw_confusion_matrix():
    """Annotated 2×2 confusion matrix with TP/FP/TN/FN, precision/recall arrows."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(8, 7))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    fig.suptitle("Матрица ошибок (Confusion Matrix)", fontsize=14,
                 color=C_INK, fontweight="bold", y=0.97)

    # --- Cell definitions: [x, y, w, h, color, label, count, sublabel]
    # Grid origin: bottom-left at (1, 1), each cell 3.5×3.5
    cell_x = [1.5, 5.0]   # col positions
    cell_y = [1.5, 5.0]   # row positions (bottom row first)
    cell_w, cell_h = 3.3, 3.3

    cells = [
        # (row, col, label, count, face_color, text_color)
        (0, 0, "TN", 820, C_PANEL,  C_INK),    # bottom-left
        (0, 1, "FP", 30,  C_ORANGE, "white"),   # bottom-right
        (1, 0, "FN", 50,  C_BLUE,   "white"),   # top-left
        (1, 1, "TP", 100, C_GREEN,  "white"),   # top-right
    ]

    for row, col, label, count, fc, tc in cells:
        x = cell_x[col]
        y = cell_y[row]
        patch = mpatches.FancyBboxPatch(
            (x, y), cell_w, cell_h,
            boxstyle="round,pad=0.12",
            facecolor=fc, edgecolor=C_GRAY, linewidth=1.5,
            transform=ax.transData, zorder=2
        )
        ax.add_patch(patch)
        cx = x + cell_w / 2
        cy = y + cell_h / 2
        ax.text(cx, cy + 0.45, label, ha="center", va="center",
                fontsize=20, fontweight="bold", color=tc, zorder=3)
        ax.text(cx, cy - 0.35, str(count), ha="center", va="center",
                fontsize=15, color=tc, alpha=0.85, zorder=3)

    # --- Axis labels
    ax.text(3.15, 9.4, "Истинный класс", ha="center", va="center",
            fontsize=12, fontweight="bold", color=C_INK)
    ax.text(3.15, 9.0, "Negative", ha="center", va="center",
            fontsize=10, color=C_GRAY)
    ax.text(6.65, 9.0, "Positive", ha="center", va="center",
            fontsize=10, color=C_GRAY)

    ax.text(0.5, 6.65, "Predicted\nPositive", ha="center", va="center",
            fontsize=10, color=C_GRAY, rotation=90)
    ax.text(0.5, 3.15, "Predicted\nNegative", ha="center", va="center",
            fontsize=10, color=C_GRAY, rotation=90)
    ax.text(0.1, 5.0, "Предсказание", ha="center", va="center",
            fontsize=12, fontweight="bold", color=C_INK, rotation=90)

    # --- Precision arrow: over top row (TP / (TP+FP))
    prec_x0, prec_x1 = 5.0, 8.3
    prec_y = 9.0
    ax.annotate("", xy=(prec_x1, prec_y), xytext=(prec_x0, prec_y),
                arrowprops=dict(arrowstyle="<->", color=C_GREEN, lw=2.0))
    ax.text((prec_x0 + prec_x1) / 2, prec_y + 0.35,
            r"Precision = TP / (TP + FP) = 100/130 ≈ 0.77",
            ha="center", va="bottom", fontsize=9, color=C_GREEN, fontweight="bold")

    # --- Recall arrow: right column (TP / (TP+FN))
    rec_x = 9.3
    rec_y0, rec_y1 = 5.0, 8.3
    ax.annotate("", xy=(rec_x, rec_y1), xytext=(rec_x, rec_y0),
                arrowprops=dict(arrowstyle="<->", color=C_BLUE, lw=2.0))
    ax.text(rec_x + 0.2, (rec_y0 + rec_y1) / 2,
            "Recall\n= TP/(TP+FN)\n= 100/150\n≈ 0.67",
            ha="left", va="center", fontsize=9, color=C_BLUE, fontweight="bold")

    # --- Derived metrics box
    tp, fp, fn, tn = 100, 30, 50, 820
    acc = (tp + tn) / (tp + fp + fn + tn)
    prec = tp / (tp + fp)
    rec = tp / (tp + fn)
    f1 = 2 * prec * rec / (prec + rec)

    box_text = (
        f"Accuracy  = (TP+TN)/N = {acc:.3f}\n"
        f"Precision = TP/(TP+FP) = {prec:.3f}\n"
        f"Recall    = TP/(TP+FN) = {rec:.3f}\n"
        f"F1        = 2·P·R/(P+R) = {f1:.3f}"
    )
    ax.text(5.0, 0.7, box_text, ha="left", va="center", fontsize=9,
            color=C_INK, fontfamily="monospace",
            bbox=dict(facecolor=C_PANEL, edgecolor=C_GRAY,
                      boxstyle="round,pad=0.4"))

    plt.tight_layout()
    _save(fig, "confusion_matrix")


# ─────────────────────────────────────────────────────────────────────────────
# 2. ROC curve + PR curve, side by side
# ─────────────────────────────────────────────────────────────────────────────
def draw_roc_pr_curves():
    """Side by side: ROC curve with AUC shaded, PR curve with AUC shaded."""
    _apply_style()
    fig, (ax_roc, ax_pr) = plt.subplots(1, 2, figsize=(13, 5.5))
    fig.patch.set_facecolor(C_BG)
    fig.suptitle("ROC-кривая и PR-кривая", fontsize=14,
                 color=C_INK, fontweight="bold", y=1.01)

    rng = np.random.default_rng(17)

    # Synthetic predictions: 200 samples, 30% positive
    n = 300
    n_pos = 90
    y_true = np.array([1] * n_pos + [0] * (n - n_pos))
    # Good classifier: positives get higher scores
    scores_pos = rng.beta(5, 2, n_pos)
    scores_neg = rng.beta(2, 5, n - n_pos)
    scores = np.concatenate([scores_pos, scores_neg])

    # Sort by descending score to compute ROC/PR
    order = np.argsort(-scores)
    # ROC: FPR vs TPR at each threshold
    thresholds = np.concatenate([[2.0], scores[order], [0.0]])
    tprs = np.zeros(len(thresholds))
    fprs = np.zeros(len(thresholds))
    for i, thr in enumerate(thresholds):
        pred = (scores >= thr).astype(int)
        tp = ((pred == 1) & (y_true == 1)).sum()
        fp = ((pred == 1) & (y_true == 0)).sum()
        fn = ((pred == 0) & (y_true == 1)).sum()
        tn = ((pred == 0) & (y_true == 0)).sum()
        tprs[i] = tp / (tp + fn) if (tp + fn) > 0 else 0
        fprs[i] = fp / (fp + tn) if (fp + tn) > 0 else 0

    auc_roc = float(np.trapezoid(tprs, fprs))
    if auc_roc < 0:
        auc_roc = -auc_roc

    # PR: Precision vs Recall at each threshold
    precs = np.zeros(len(thresholds))
    recs  = np.zeros(len(thresholds))
    for i, thr in enumerate(thresholds):
        pred = (scores >= thr).astype(int)
        tp = ((pred == 1) & (y_true == 1)).sum()
        fp = ((pred == 1) & (y_true == 0)).sum()
        fn = ((pred == 0) & (y_true == 1)).sum()
        precs[i] = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        recs[i]  = tp / (tp + fn) if (tp + fn) > 0 else 0.0

    # Sort PR by recall for proper plotting
    pr_order = np.argsort(recs)
    pr_recs  = recs[pr_order]
    pr_precs = precs[pr_order]
    auc_pr = float(np.trapezoid(pr_precs, pr_recs))

    # ── ROC panel ──────────────────────────────────────────────────────────
    ax_roc.set_facecolor(C_BG)
    fpr_sorted_idx = np.argsort(fprs)
    fpr_plot = fprs[fpr_sorted_idx]
    tpr_plot = tprs[fpr_sorted_idx]

    ax_roc.fill_between(fpr_plot, tpr_plot, alpha=0.18, color=C_BLUE, label="AUC")
    ax_roc.plot(fpr_plot, tpr_plot, color=C_BLUE, lw=2.5, label=f"ROC (AUC={auc_roc:.2f})")
    ax_roc.plot([0, 1], [0, 1], color=C_GRAY, lw=1.5, linestyle="--", label="Random (AUC=0.50)")

    # Optimal threshold point (Youden J = TPR - FPR max)
    j_scores = tprs - fprs
    best_i = int(np.argmax(j_scores))
    ax_roc.scatter([fprs[best_i]], [tprs[best_i]], color=C_ORANGE, s=100, zorder=5)
    ax_roc.annotate(f"Оптимальный порог\nFPR={fprs[best_i]:.2f}, TPR={tprs[best_i]:.2f}",
                    xy=(fprs[best_i], tprs[best_i]),
                    xytext=(fprs[best_i] + 0.12, tprs[best_i] - 0.15),
                    fontsize=8.5, color=C_ORANGE,
                    arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=1.2))

    ax_roc.set_xlabel("FPR (False Positive Rate)", color=C_INK)
    ax_roc.set_ylabel("TPR (True Positive Rate / Recall)", color=C_INK)
    ax_roc.set_title("ROC-кривая", fontsize=13, color=C_INK, fontweight="bold")
    ax_roc.legend(fontsize=9, facecolor=C_PANEL, edgecolor=C_GRAY)
    ax_roc.set_xlim(-0.02, 1.02)
    ax_roc.set_ylim(-0.02, 1.05)
    ax_roc.tick_params(colors=C_INK)
    ax_roc.text(0.55, 0.12,
                "ROC использовать когда\nклассы сбалансированы",
                fontsize=8, color=C_GRAY, style="italic",
                bbox=dict(facecolor=C_PANEL, edgecolor=C_GRAY, boxstyle="round,pad=0.3"))

    # ── PR panel ───────────────────────────────────────────────────────────
    ax_pr.set_facecolor(C_BG)
    ax_pr.fill_between(pr_recs, pr_precs, alpha=0.18, color=C_ORANGE, label="AUC-PR")
    ax_pr.plot(pr_recs, pr_precs, color=C_ORANGE, lw=2.5, label=f"PR (AUC={auc_pr:.2f})")

    # Baseline: random classifier = prevalence
    prevalence = n_pos / n
    ax_pr.axhline(prevalence, color=C_GRAY, lw=1.5, linestyle="--",
                  label=f"Random (P={prevalence:.2f})")

    ax_pr.set_xlabel("Recall", color=C_INK)
    ax_pr.set_ylabel("Precision", color=C_INK)
    ax_pr.set_title("PR-кривая", fontsize=13, color=C_INK, fontweight="bold")
    ax_pr.legend(fontsize=9, facecolor=C_PANEL, edgecolor=C_GRAY)
    ax_pr.set_xlim(-0.02, 1.02)
    ax_pr.set_ylim(-0.02, 1.05)
    ax_pr.tick_params(colors=C_INK)
    ax_pr.text(0.02, 0.12,
               "PR использовать при\nсильном дисбалансе классов",
               fontsize=8, color=C_GRAY, style="italic",
               bbox=dict(facecolor=C_PANEL, edgecolor=C_GRAY, boxstyle="round,pad=0.3"))

    plt.tight_layout()
    _save(fig, "roc_pr_curves")


# ─────────────────────────────────────────────────────────────────────────────
# 3. GridSearch accuracy heatmap over 2 hyperparameters
# ─────────────────────────────────────────────────────────────────────────────
def draw_hyperparam_search():
    """Heatmap of GridSearch accuracy over 2 hyperparameters."""
    _apply_style()
    fig, (ax_grid, ax_rand) = plt.subplots(1, 2, figsize=(13, 5.5))
    fig.patch.set_facecolor(C_BG)
    fig.suptitle("Подбор гиперпараметров: GridSearch vs RandomizedSearch",
                 fontsize=13, color=C_INK, fontweight="bold", y=1.01)

    rng = np.random.default_rng(99)

    C_vals = [0.001, 0.01, 0.1, 1, 10, 100]
    gamma_vals = [0.001, 0.01, 0.1, 1, 10, 100]
    n_c = len(C_vals)
    n_g = len(gamma_vals)

    # Synthetic accuracy: peaks around C=1, gamma=0.1
    acc_grid = np.zeros((n_c, n_g))
    for i, c in enumerate(C_vals):
        for j, g in enumerate(gamma_vals):
            log_c = np.log10(c)
            log_g = np.log10(g)
            # Peak at log_c=0, log_g=-1
            val = 0.98 * np.exp(-0.25 * ((log_c - 0) ** 2 + (log_g + 1) ** 2))
            val = max(0.50, min(0.98, val + 0.52 + rng.normal(0, 0.015)))
            acc_grid[i, j] = val

    # ── GridSearch heatmap ─────────────────────────────────────────────────
    ax_grid.set_facecolor(C_BG)
    im = ax_grid.imshow(acc_grid, cmap="YlOrRd", aspect="auto",
                        vmin=0.50, vmax=0.98, origin="lower")
    fig.colorbar(im, ax=ax_grid, label="Accuracy (CV)", shrink=0.85)

    ax_grid.set_xticks(range(n_g))
    ax_grid.set_xticklabels([str(g) for g in gamma_vals], fontsize=8, color=C_INK)
    ax_grid.set_yticks(range(n_c))
    ax_grid.set_yticklabels([str(c) for c in C_vals], fontsize=8, color=C_INK)
    ax_grid.set_xlabel("gamma", color=C_INK, fontsize=11)
    ax_grid.set_ylabel("C", color=C_INK, fontsize=11)
    ax_grid.set_title("GridSearchCV\n(все 36 точек)", fontsize=12,
                      color=C_INK, fontweight="bold")

    # Annotate cells with accuracy value
    for i in range(n_c):
        for j in range(n_g):
            val = acc_grid[i, j]
            txt_color = "white" if val > 0.80 else C_INK
            ax_grid.text(j, i, f"{val:.2f}", ha="center", va="center",
                         fontsize=7.5, color=txt_color, fontweight="bold")

    # Mark best cell
    best_i, best_j = divmod(int(np.argmax(acc_grid)), n_g)
    ax_grid.add_patch(mpatches.Rectangle(
        (best_j - 0.5, best_i - 0.5), 1, 1,
        fill=False, edgecolor=C_INK, lw=2.5, zorder=5
    ))

    # ── RandomizedSearch scatter ───────────────────────────────────────────
    ax_rand.set_facecolor(C_BG)

    # Generate 12 random (log-uniform) sample points
    n_rand = 12
    rand_c     = 10 ** rng.uniform(-3, 2, n_rand)
    rand_gamma = 10 ** rng.uniform(-3, 2, n_rand)

    # Compute their accuracy using same formula
    rand_acc = []
    for rc, rg in zip(rand_c, rand_gamma):
        log_c = np.log10(rc)
        log_g = np.log10(rg)
        val = 0.98 * np.exp(-0.25 * ((log_c - 0) ** 2 + (log_g + 1) ** 2))
        val = max(0.50, min(0.98, val + 0.52 + rng.normal(0, 0.015)))
        rand_acc.append(val)
    rand_acc = np.array(rand_acc)

    sc = ax_rand.scatter(rand_gamma, rand_c,
                         c=rand_acc, cmap="YlOrRd", vmin=0.50, vmax=0.98,
                         s=200, zorder=4, edgecolors=C_INK, linewidths=0.8)
    fig.colorbar(sc, ax=ax_rand, label="Accuracy (CV)", shrink=0.85)

    # Background heatmap (faint)
    g_fine = np.logspace(-3, 2, 80)
    c_fine = np.logspace(-3, 2, 80)
    GG, CC = np.meshgrid(g_fine, c_fine)
    ZZ = 0.98 * np.exp(-0.25 * ((np.log10(CC) - 0) ** 2 + (np.log10(GG) + 1) ** 2)) + 0.52
    ZZ = np.clip(ZZ, 0.50, 0.98)
    ax_rand.contourf(GG, CC, ZZ, levels=10, cmap="YlOrRd", alpha=0.18)
    ax_rand.contour(GG, CC, ZZ, levels=[0.80, 0.90, 0.95],
                    colors=[C_GRAY], linewidths=0.8, linestyles="--")

    # Best point annotation
    best_rand_i = int(np.argmax(rand_acc))
    ax_rand.annotate(f"Best: {rand_acc[best_rand_i]:.2f}",
                     xy=(rand_gamma[best_rand_i], rand_c[best_rand_i]),
                     xytext=(rand_gamma[best_rand_i] * 5, rand_c[best_rand_i] * 5),
                     fontsize=9, color=C_ORANGE, fontweight="bold",
                     arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=1.2))

    ax_rand.set_xscale("log")
    ax_rand.set_yscale("log")
    ax_rand.set_xlabel("gamma", color=C_INK, fontsize=11)
    ax_rand.set_ylabel("C", color=C_INK, fontsize=11)
    ax_rand.set_title(f"RandomizedSearchCV\n({n_rand} случайных точек)", fontsize=12,
                      color=C_INK, fontweight="bold")
    ax_rand.tick_params(colors=C_INK)

    plt.tight_layout()
    _save(fig, "hyperparam_search")


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_confusion_matrix()
    draw_roc_pr_curves()
    draw_hyperparam_search()
    print("All visuals generated.")


if __name__ == "__main__":
    main()
