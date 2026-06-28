"""Точные схемы для лекции про переобучение и регуляризацию."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

C_BG = '#faf9f5'
C_INK = '#141413'
C_GRAY = '#b0aea5'
C_PANEL = '#e8e6dc'
C_ORANGE = '#d97757'
C_BLUE = '#6a9bcc'
C_GREEN = '#788c5d'

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'assets'


def _apply_style():
    plt.rcParams.update({
        'figure.facecolor': C_BG,
        'axes.facecolor': C_PANEL,
        'axes.edgecolor': C_GRAY,
        'axes.labelcolor': C_INK,
        'text.color': C_INK,
        'xtick.color': C_INK,
        'ytick.color': C_INK,
        'grid.color': C_BG,
        'grid.linewidth': 0.8,
        'font.family': 'DejaVu Sans',
        'font.size': 11,
    })


def _save(fig, name):
    fig.savefig(ASSETS / (name + '.png'), dpi=150, bbox_inches='tight', facecolor=C_BG)
    plt.close(fig)


def draw_learning_curves():
    """
    Three panels: underfitting / just right / overfitting.
    Each panel shows train and val error vs number of training samples.
    """
    _apply_style()

    rng = np.random.default_rng(42)
    n_pts = np.linspace(20, 500, 40, dtype=int)

    def _noise(size, scale):
        return rng.normal(0, scale, size)

    # --- underfit: both errors high, close together ---
    train_uf = 0.55 - 0.04 * np.log(n_pts / 20) + _noise(len(n_pts), 0.01)
    val_uf   = 0.60 - 0.04 * np.log(n_pts / 20) + _noise(len(n_pts), 0.01)

    # --- good fit: train slightly below val, both converge low ---
    train_gf = 0.30 - 0.18 * np.log(n_pts / 20) / np.log(500 / 20) + _noise(len(n_pts), 0.008)
    val_gf   = 0.38 - 0.14 * np.log(n_pts / 20) / np.log(500 / 20) + _noise(len(n_pts), 0.010)
    train_gf = np.clip(train_gf, 0.11, 1.0)
    val_gf   = np.clip(val_gf,   0.22, 1.0)

    # --- overfit: train → 0, val stays high ---
    train_of = 0.40 * np.exp(-n_pts / 80) + 0.02 + _noise(len(n_pts), 0.005)
    val_of   = 0.22 + 0.30 * np.exp(-n_pts / 600) + _noise(len(n_pts), 0.012)
    train_of = np.clip(train_of, 0.02, 1.0)
    val_of   = np.clip(val_of,   0.20, 1.0)

    titles = ['Недообучение\n(Underfitting)', 'Хорошая модель', 'Переобучение\n(Overfitting)']
    trains = [train_uf, train_gf, train_of]
    vals   = [val_uf,   val_gf,   val_of]
    annotations = [
        'Train ≈ Val\nОба высоки → bias',
        'Train < Val\nОба низки → ok',
        'Train << Val\nVal высок → variance',
    ]

    fig, axes = plt.subplots(1, 3, figsize=(14, 5), sharey=False)
    fig.patch.set_facecolor(C_BG)
    fig.suptitle('Кривые обучения: три режима модели', fontsize=14,
                 color=C_INK, fontweight='bold', y=1.01)

    for ax, title, tr, vl, ann in zip(axes, titles, trains, vals, annotations):
        ax.set_facecolor(C_PANEL)
        ax.plot(n_pts, tr, color=C_BLUE,   lw=2.2, label='Train error')
        ax.plot(n_pts, vl, color=C_ORANGE, lw=2.2, label='Val error',  linestyle='--')
        ax.fill_between(n_pts, tr, vl, alpha=0.15, color=C_ORANGE)
        ax.set_xlabel('Число обучающих примеров', fontsize=10)
        ax.set_ylabel('Ошибка', fontsize=10)
        ax.set_title(title, color=C_INK, fontweight='bold', fontsize=11)
        ax.set_ylim(0, 0.80)
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend(fontsize=9, facecolor=C_BG, edgecolor=C_GRAY, loc='upper right')
        ax.text(0.05, 0.08, ann, transform=ax.transAxes,
                fontsize=8.5, color=C_INK,
                bbox=dict(boxstyle='round,pad=0.3', facecolor=C_BG, edgecolor=C_GRAY, alpha=0.85))

    fig.tight_layout()
    _save(fig, 'learning_curves')
    print('Saved: learning_curves.png')


def _ridge_path(X, y, alphas):
    """Analytic Ridge path: w(alpha) = (X'X + alpha*I)^{-1} X'y."""
    XtX = X.T @ X
    Xty = X.T @ y
    d = XtX.shape[0]
    coefs = []
    for a in alphas:
        w = np.linalg.solve(XtX + a * np.eye(d), Xty)
        coefs.append(w)
    return np.array(coefs)  # shape (n_alphas, n_features)


def _lasso_cd(X, y, alpha, max_iter=2000, tol=1e-7):
    """Coordinate descent for Lasso."""
    n, p = X.shape
    w = np.zeros(p)
    xj_sq = (X ** 2).sum(axis=0) / n
    for _ in range(max_iter):
        w_old = w.copy()
        for j in range(p):
            rho = X[:, j] @ (y - X @ w + X[:, j] * w[j]) / n
            if rho > alpha:
                w[j] = (rho - alpha) / xj_sq[j]
            elif rho < -alpha:
                w[j] = (rho + alpha) / xj_sq[j]
            else:
                w[j] = 0.0
        if np.max(np.abs(w - w_old)) < tol:
            break
    return w


def _lasso_path_numpy(X, y, alphas):
    """Lasso path via coordinate descent, warm starts."""
    p = X.shape[1]
    coefs = np.zeros((len(alphas), p))
    w = np.zeros(p)
    for k, a in enumerate(alphas):
        w = _lasso_cd(X, y, a)
        coefs[k] = w
    return coefs  # shape (n_alphas, n_features)


def draw_regularization_paths():
    """
    L1 (Lasso) vs L2 (Ridge): coefficient paths as 1/lambda increases.
    Left panel: L1 — coefficients hit zero (sparsity).
    Right panel: L2 — coefficients shrink smoothly toward zero.
    """
    _apply_style()

    rng = np.random.default_rng(0)
    n, p = 200, 8
    X = rng.standard_normal((n, p))
    true_w = np.array([3.0, -2.5, 1.8, -1.2, 0.0, 0.0, 0.0, 0.0])
    y = X @ true_w + rng.normal(0, 1.5, n)
    X = X / X.std(axis=0)   # normalise

    # --- L1 path ---
    alphas_l1 = np.logspace(-2, 1, 80)[::-1]   # decreasing = increasing complexity
    coefs_l1 = _lasso_path_numpy(X, y, alphas_l1).T  # shape (p, n_alphas)
    log_alpha_l1 = np.log10(alphas_l1)

    # --- L2 path ---
    alphas_l2 = np.logspace(-2, 4, 60)
    coefs_l2 = _ridge_path(X, y, alphas_l2)    # shape (n_alphas, p)

    colors8 = [C_ORANGE, C_BLUE, C_GREEN, C_GRAY,
               '#c07850', '#8ab4cc', '#a0b07e', '#888880']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    fig.patch.set_facecolor(C_BG)

    # L1
    ax1.set_facecolor(C_PANEL)
    for i in range(coefs_l1.shape[0]):
        ax1.plot(-log_alpha_l1, coefs_l1[i], lw=1.8, color=colors8[i],
                 label=f'w{i+1}')
    ax1.axhline(0, color=C_INK, lw=0.8, linestyle=':')
    ax1.set_xlabel(r'$-\log_{10}(\lambda)$  (→ меньше регуляризации)', fontsize=10)
    ax1.set_ylabel('Значение коэффициента', fontsize=10)
    ax1.set_title('L1-регуляризация (Lasso)\nКоэффициенты обнуляются', color=C_INK,
                  fontweight='bold', fontsize=11)
    ax1.legend(ncol=2, fontsize=8, facecolor=C_BG, edgecolor=C_GRAY, loc='upper left')
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.text(0.55, 0.08, 'Разреженность весов\n(feature selection)', transform=ax1.transAxes,
             fontsize=9, color=C_INK,
             bbox=dict(boxstyle='round,pad=0.3', facecolor=C_BG, edgecolor=C_ORANGE, alpha=0.9))

    # L2
    ax2.set_facecolor(C_PANEL)
    for i in range(coefs_l2.shape[1]):
        ax2.plot(np.log10(alphas_l2), coefs_l2[:, i], lw=1.8, color=colors8[i],
                 label=f'w{i+1}')
    ax2.axhline(0, color=C_INK, lw=0.8, linestyle=':')
    ax2.set_xlabel(r'$\log_{10}(\lambda)$  (→ больше регуляризации)', fontsize=10)
    ax2.set_ylabel('Значение коэффициента', fontsize=10)
    ax2.set_title('L2-регуляризация (Ridge)\nКоэффициенты сжимаются плавно', color=C_INK,
                  fontweight='bold', fontsize=11)
    ax2.legend(ncol=2, fontsize=8, facecolor=C_BG, edgecolor=C_GRAY, loc='upper right')
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.text(0.03, 0.08, 'Shrinkage: ни один вес\nне обнуляется точно', transform=ax2.transAxes,
             fontsize=9, color=C_INK,
             bbox=dict(boxstyle='round,pad=0.3', facecolor=C_BG, edgecolor=C_BLUE, alpha=0.9))

    fig.tight_layout()
    _save(fig, 'regularization_paths')
    print('Saved: regularization_paths.png')


def draw_cv_scheme():
    """
    Visual of 5-fold cross-validation split.
    Rows = folds, columns = sample blocks, colored train/val.
    Plus a small panel showing train/val/test outer split.
    """
    _apply_style()

    fig, (ax_outer, ax_kfold) = plt.subplots(1, 2, figsize=(14, 5),
                                              gridspec_kw={'width_ratios': [1, 2]})
    fig.patch.set_facecolor(C_BG)

    # --- Left: train / val / test outer split ---
    ax_outer.set_facecolor(C_BG)
    ax_outer.set_xlim(0, 10)
    ax_outer.set_ylim(-0.5, 3.5)
    ax_outer.axis('off')
    ax_outer.set_title('Hold-out: train / val / test', color=C_INK,
                        fontweight='bold', fontsize=11)

    split_data = [
        (0, 6, C_BLUE,   'Train (60%)'),
        (6, 8, C_GREEN,  'Val (20%)'),
        (8, 10, C_ORANGE, 'Test (20%)'),
    ]
    for x0, x1, color, label in split_data:
        rect = mpatches.FancyBboxPatch((x0 + 0.05, 1.2), x1 - x0 - 0.10, 1.0,
                                       boxstyle='round,pad=0.05',
                                       facecolor=color, edgecolor=C_INK, linewidth=1.2,
                                       alpha=0.85)
        ax_outer.add_patch(rect)
        ax_outer.text((x0 + x1) / 2, 1.70, label, ha='center', va='center',
                      fontsize=9.5, color='white', fontweight='bold')

    ax_outer.text(5, 0.5, 'Простой Hold-out: быстро, но зависит\nот случайного разбиения',
                  ha='center', va='center', fontsize=9, color=C_INK,
                  bbox=dict(boxstyle='round,pad=0.3', facecolor=C_PANEL, edgecolor=C_GRAY))

    # --- Right: 5-fold CV ---
    ax_kfold.set_facecolor(C_BG)
    n_folds = 5
    n_blocks = 10
    ax_kfold.set_xlim(-0.5, n_blocks + 0.5)
    ax_kfold.set_ylim(-0.8, n_folds + 0.5)
    ax_kfold.axis('off')
    ax_kfold.set_title('5-Fold Cross-Validation', color=C_INK,
                        fontweight='bold', fontsize=11)

    for fold in range(n_folds):
        val_start = fold * 2
        val_end = val_start + 2
        y_pos = n_folds - 1 - fold
        for b in range(n_blocks):
            color = C_ORANGE if val_start <= b < val_end else C_BLUE
            alpha = 0.90
            rect = mpatches.FancyBboxPatch((b + 0.05, y_pos + 0.08), 0.90, 0.75,
                                           boxstyle='round,pad=0.03',
                                           facecolor=color, edgecolor=C_BG,
                                           linewidth=0.8, alpha=alpha)
            ax_kfold.add_patch(rect)
        ax_kfold.text(-0.3, y_pos + 0.46, f'Fold {fold+1}',
                      ha='right', va='center', fontsize=9, color=C_INK)

    legend_patches = [
        mpatches.Patch(facecolor=C_BLUE,   edgecolor=C_INK, label='Train'),
        mpatches.Patch(facecolor=C_ORANGE, edgecolor=C_INK, label='Validation'),
    ]
    ax_kfold.legend(handles=legend_patches, loc='lower center',
                    fontsize=10, facecolor=C_BG, edgecolor=C_GRAY,
                    framealpha=0.9, ncol=2)
    ax_kfold.text(4.75, -0.65,
                  'Каждый пример ровно 1 раз попадает в val → честная оценка',
                  ha='center', va='center', fontsize=9, color=C_INK,
                  bbox=dict(boxstyle='round,pad=0.3', facecolor=C_PANEL, edgecolor=C_GRAY))

    fig.tight_layout()
    _save(fig, 'cv_scheme')
    print('Saved: cv_scheme.png')


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_learning_curves()
    draw_regularization_paths()
    draw_cv_scheme()
    print('All visuals generated in assets/')


if __name__ == '__main__':
    main()
