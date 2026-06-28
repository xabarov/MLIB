from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
import numpy as np

ASSETS = Path(__file__).resolve().parent / 'assets'

C_BG = '#faf9f5'
C_INK = '#141413'
C_GRAY = '#b0aea5'
C_PANEL = '#e8e6dc'
C_ORANGE = '#d97757'
C_BLUE = '#6a9bcc'
C_GREEN = '#788c5d'


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
        'font.family': 'DejaVu Sans',
        'font.size': 11,
    })


def _save(fig, name):
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(ASSETS / (name + '.png')), dpi=150, bbox_inches='tight',
                facecolor=C_BG)
    plt.close(fig)
    print('Saved:', name + '.png')


def _kde(data, x_range, bw_factor=0.35):
    n = len(data)
    h = bw_factor * float(data.std()) * n ** (-0.2)
    diff = (x_range[:, np.newaxis] - data[np.newaxis, :]) / h
    ys = np.exp(-0.5 * diff * diff).sum(axis=1)
    ys /= n * h * np.sqrt(2.0 * np.pi)
    return ys


def draw_missing_patterns():
    rng = np.random.default_rng(42)
    n_rows, n_cols = 22, 6

    # MCAR: uniformly random missing
    mcar_mask = rng.random((n_rows, n_cols)) < 0.28

    # MAR: missingness in cols 3-5 depends on observed col 0
    col0_vals = rng.uniform(0, 1, n_rows)
    mar_mask = np.zeros((n_rows, n_cols), dtype=bool)
    for r in range(n_rows):
        if col0_vals[r] > 0.52:
            mar_mask[r, 3] = rng.random() < 0.88
            mar_mask[r, 4] = rng.random() < 0.72
            mar_mask[r, 5] = rng.random() < 0.55

    # MNAR: high values of the variable itself go missing
    true_vals = rng.uniform(0, 10, (n_rows, n_cols))
    mnar_mask = true_vals > 6.5

    cmap = ListedColormap([C_PANEL, C_ORANGE])
    titles = [
        'MCAR\n(Случайное)',
        'MAR\n(Зависит от наблюдаемых)',
        'MNAR\n(Зависит от себя)',
    ]
    masks = [mcar_mask, mar_mask, mnar_mask]
    col_labels = ['X' + str(i + 1) for i in range(n_cols)]

    fig, axes = plt.subplots(1, 3, figsize=(12, 5))
    fig.patch.set_facecolor(C_BG)

    for ax, mask, title in zip(axes, masks, titles):
        ax.set_facecolor(C_BG)
        ax.imshow(mask.astype(float), aspect='auto', cmap=cmap, vmin=0, vmax=1,
                  interpolation='nearest')
        ax.set_title(title, color=C_INK, fontsize=11, pad=8)
        ax.set_xlabel('Признак', color=C_INK, fontsize=10)
        ax.set_ylabel('Наблюдение', color=C_INK, fontsize=10)
        ax.set_xticks(range(n_cols))
        ax.set_xticklabels(col_labels, fontsize=9)
        ax.tick_params(colors=C_INK)
        for spine in ax.spines.values():
            spine.set_edgecolor(C_GRAY)

    present_patch = mpatches.Patch(facecolor=C_PANEL, edgecolor=C_GRAY,
                                   label='Присутствует')
    missing_patch = mpatches.Patch(facecolor=C_ORANGE, label='Пропущено')
    fig.legend(handles=[present_patch, missing_patch], loc='lower center',
               ncol=2, framealpha=0, labelcolor=C_INK, fontsize=11,
               bbox_to_anchor=(0.5, -0.05))

    fig.suptitle('Типы механизмов пропуска данных', color=C_INK,
                 fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, 'hero_missing_patterns')


def draw_imputation_comparison():
    rng = np.random.default_rng(1)
    original = rng.gamma(2.0, 3.0, 500)

    missing_mask = rng.random(500) < 0.3
    with_missing = original.copy()
    with_missing[missing_mask] = np.nan

    mean_val = float(np.nanmean(with_missing))
    median_val = float(np.nanmedian(with_missing))

    mean_imp = np.where(np.isnan(with_missing), mean_val, with_missing)
    median_imp = np.where(np.isnan(with_missing), median_val, with_missing)

    x_max = float(np.percentile(original, 99)) + 2.0
    x_range = np.linspace(0.0, x_max, 400)

    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    fig.patch.set_facecolor(C_BG)

    datasets = [
        (original, 'Оригинал', C_GREEN),
        (mean_imp, 'Импутация средним', C_BLUE),
        (median_imp, 'Импутация медианой', C_ORANGE),
    ]

    for ax, (data, label, color) in zip(axes, datasets):
        ax.set_facecolor(C_PANEL)
        for spine in ax.spines.values():
            spine.set_edgecolor(C_GRAY)
        ys = _kde(data, x_range)
        ax.fill_between(x_range, ys, alpha=0.35, color=color)
        ax.plot(x_range, ys, color=color, linewidth=2)
        ax.axvline(float(np.mean(data)), color=C_INK, linestyle='--',
                   linewidth=1.2, alpha=0.7, label='Среднее')
        ax.axvline(float(np.median(data)), color=C_GRAY, linestyle=':',
                   linewidth=1.5, alpha=0.9, label='Медиана')
        ax.set_title(label, color=C_INK, fontsize=11)
        ax.set_xlabel('Значение', color=C_INK, fontsize=10)
        ax.set_ylabel('Плотность', color=C_INK, fontsize=10)
        ax.tick_params(colors=C_INK)

    axes[0].legend(framealpha=0.5, facecolor=C_BG, edgecolor=C_GRAY,
                   labelcolor=C_INK, fontsize=9)
    fig.suptitle('Влияние стратегии импутации на распределение',
                 color=C_INK, fontsize=13)
    fig.tight_layout()
    _save(fig, 'imputation_comparison')


def draw_outlier_detection():
    rng = np.random.default_rng(7)
    n = 90
    x = rng.uniform(0, 10, n)
    y = 2.0 * x + rng.normal(0, 2.0, n)

    x_out = np.array([1.5, 4.0, 7.5, 9.2])
    y_out = np.array([28.0, -8.0, 36.0, -4.0])
    x_all = np.concatenate([x, x_out])
    y_all = np.concatenate([y, y_out])

    q1 = float(np.percentile(y_all, 25))
    q3 = float(np.percentile(y_all, 75))
    iqr = q3 - q1
    lower_iqr = q1 - 1.5 * iqr
    upper_iqr = q3 + 1.5 * iqr
    iqr_mask = (y_all < lower_iqr) | (y_all > upper_iqr)

    y_z = np.abs((y_all - y_all.mean()) / y_all.std())
    z_mask = y_z > 2.5

    both = iqr_mask & z_mask
    iqr_only = iqr_mask & ~z_mask
    z_only = z_mask & ~iqr_mask
    normal = ~iqr_mask & ~z_mask

    fig, ax = plt.subplots(figsize=(9, 5))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_PANEL)
    for spine in ax.spines.values():
        spine.set_edgecolor(C_GRAY)

    ax.scatter(x_all[normal], y_all[normal], color=C_BLUE, s=35,
               alpha=0.65, label='Норма', zorder=2)
    if iqr_only.any():
        ax.scatter(x_all[iqr_only], y_all[iqr_only], color=C_GREEN, s=80,
                   marker='D', alpha=0.9, label='Только IQR', zorder=3)
    if z_only.any():
        ax.scatter(x_all[z_only], y_all[z_only], color=C_ORANGE, s=80,
                   marker='^', alpha=0.9, label='Только Z-score', zorder=3)
    if both.any():
        ax.scatter(x_all[both], y_all[both], color='#c0392b', s=110,
                   marker='X', zorder=5, label='Оба метода')

    ax.axhline(upper_iqr, color=C_ORANGE, linestyle='--', linewidth=1.8,
               label='Q3 + 1.5 IQR = ' + str(round(upper_iqr, 1)))
    ax.axhline(lower_iqr, color=C_ORANGE, linestyle=':', linewidth=1.8,
               label='Q1 - 1.5 IQR = ' + str(round(lower_iqr, 1)))

    ax.set_xlabel('X', color=C_INK, fontsize=11)
    ax.set_ylabel('Y', color=C_INK, fontsize=11)
    ax.set_title('Обнаружение выбросов: IQR и Z-score', color=C_INK, fontsize=13)
    ax.tick_params(colors=C_INK)
    ax.legend(framealpha=0.5, facecolor=C_BG, edgecolor=C_GRAY,
              labelcolor=C_INK, fontsize=9, loc='upper left')

    fig.tight_layout()
    _save(fig, 'outlier_detection')


def main():
    _apply_style()
    draw_missing_patterns()
    draw_imputation_comparison()
    draw_outlier_detection()


if __name__ == '__main__':
    main()
