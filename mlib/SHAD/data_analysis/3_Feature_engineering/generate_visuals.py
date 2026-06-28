import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

C_BG = '#faf9f5'
C_INK = '#141413'
C_GRAY = '#b0aea5'
C_PANEL = '#e8e6dc'
C_ORANGE = '#d97757'
C_BLUE = '#6a9bcc'
C_GREEN = '#788c5d'

ASSETS = os.path.join(os.path.dirname(__file__), 'assets')
os.makedirs(ASSETS, exist_ok=True)


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
    fig.savefig(os.path.join(ASSETS, name + '.png'), dpi=150, bbox_inches='tight',
                facecolor=C_BG)
    plt.close(fig)


def draw_encoding_comparison():
    """
    Table-style comparison: raw category -> OHE / Ordinal / Target encoding
    for a small toy example (City: Moscow, SPb, Kazan).
    """
    _apply_style()

    categories = ['Moscow', 'SPb', 'Kazan']
    ordinal = [0, 1, 2]
    target = [4.2, 3.8, 2.9]   # mock mean target per category
    ohe_headers = ['is_Moscow', 'is_SPb', 'is_Kazan']
    ohe_values = [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
    ]

    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    fig.patch.set_facecolor(C_BG)
    fig.suptitle('Сравнение методов кодирования категорий', fontsize=14,
                 color=C_INK, fontweight='bold', y=1.02)

    # --- OHE ---
    ax = axes[0]
    ax.set_facecolor(C_PANEL)
    ax.set_title('One-Hot Encoding', color=C_BLUE, fontweight='bold')
    col_labels = ['Город'] + ohe_headers
    table_data = [[categories[i]] + ohe_values[i] for i in range(3)]
    table = ax.table(
        cellText=table_data,
        colLabels=col_labels,
        loc='center',
        cellLoc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.8)
    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor(C_GRAY)
        if r == 0:
            cell.set_facecolor(C_BLUE)
            cell.set_text_props(color='white', fontweight='bold')
        else:
            val = table_data[r - 1][c] if c > 0 else None
            if val == 1:
                cell.set_facecolor(C_GREEN + 'aa')
            else:
                cell.set_facecolor(C_BG)
    ax.axis('off')

    # --- Ordinal ---
    ax = axes[1]
    ax.set_facecolor(C_PANEL)
    ax.set_title('Ordinal Encoding', color=C_ORANGE, fontweight='bold')
    ord_data = [[categories[i], ordinal[i]] for i in range(3)]
    table2 = ax.table(
        cellText=ord_data,
        colLabels=['Город', 'Код'],
        loc='center',
        cellLoc='center'
    )
    table2.auto_set_font_size(False)
    table2.set_fontsize(11)
    table2.scale(1.4, 2.2)
    for (r, c), cell in table2.get_celld().items():
        cell.set_edgecolor(C_GRAY)
        if r == 0:
            cell.set_facecolor(C_ORANGE)
            cell.set_text_props(color='white', fontweight='bold')
        else:
            cell.set_facecolor(C_BG)
    ax.axis('off')

    # --- Target ---
    ax = axes[2]
    ax.set_facecolor(C_PANEL)
    ax.set_title('Target Encoding  E[y | cat]', color=C_GREEN, fontweight='bold')
    tgt_data = [[categories[i], f'{target[i]:.1f}'] for i in range(3)]
    table3 = ax.table(
        cellText=tgt_data,
        colLabels=['Город', 'E[y|город]'],
        loc='center',
        cellLoc='center'
    )
    table3.auto_set_font_size(False)
    table3.set_fontsize(11)
    table3.scale(1.4, 2.2)
    for (r, c), cell in table3.get_celld().items():
        cell.set_edgecolor(C_GRAY)
        if r == 0:
            cell.set_facecolor(C_GREEN)
            cell.set_text_props(color='white', fontweight='bold')
        else:
            cell.set_facecolor(C_BG)
    ax.axis('off')

    fig.tight_layout()
    _save(fig, 'encoding_comparison')
    print('Saved: encoding_comparison.png')


def draw_feature_importance():
    """
    Horizontal bar chart of mock feature importances from a Random Forest.
    """
    _apply_style()

    features = [
        'log(price)',
        'city_target_enc',
        'age * income',
        'sqrt(distance)',
        'hour_of_day',
        'city_freq_enc',
        'weekday',
        'is_weekend',
        'log(population)',
        'income^2',
    ]
    importances = [0.187, 0.154, 0.121, 0.098, 0.085,
                   0.072, 0.065, 0.058, 0.044, 0.038]

    colors = [C_ORANGE if imp > 0.1 else C_BLUE if imp > 0.06 else C_GRAY
              for imp in importances]

    fig, ax = plt.subplots(figsize=(9, 6))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_PANEL)

    y_pos = np.arange(len(features))
    bars = ax.barh(y_pos, importances, color=colors, edgecolor=C_BG, height=0.65)

    for bar, imp in zip(bars, importances):
        ax.text(imp + 0.003, bar.get_y() + bar.get_height() / 2,
                f'{imp:.3f}', va='center', fontsize=9.5, color=C_INK)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(features, fontsize=10.5)
    ax.invert_yaxis()
    ax.set_xlabel('Feature Importance (MDI)', color=C_INK)
    ax.set_title('Feature Importances — Random Forest\n(mock example)', color=C_INK,
                 fontweight='bold', fontsize=13)
    ax.set_xlim(0, 0.23)
    ax.grid(axis='x', linestyle='--', alpha=0.6)

    legend_patches = [
        mpatches.Patch(color=C_ORANGE, label='Высокая важность (>0.10)'),
        mpatches.Patch(color=C_BLUE, label='Средняя важность (0.06–0.10)'),
        mpatches.Patch(color=C_GRAY, label='Низкая важность (<0.06)'),
    ]
    ax.legend(handles=legend_patches, loc='lower right', fontsize=9,
              framealpha=0.85, facecolor=C_BG, edgecolor=C_GRAY)

    fig.tight_layout()
    _save(fig, 'feature_importance')
    print('Saved: feature_importance.png')


def draw_cardinality_tradeoff():
    """
    Line plot: number of unique categories vs resulting OHE column count,
    illustrating the dimensionality explosion problem.
    Annotates with memory footprint (uint8 sparse vs dense).
    """
    _apply_style()

    n_categories = np.array([2, 5, 10, 20, 50, 100, 200, 500, 1000, 5000, 10000])
    ohe_cols = n_categories  # OHE produces exactly #categories columns
    # mock dataset with 100k rows: memory in MB (float64 dense)
    mb_dense = n_categories * 100_000 * 8 / 1024**2
    # uint8 sparse stores only 1 byte per non-zero (1 per row)
    mb_sparse = n_categories * 1 * 100_000 / 1024**2  # sparse: just non-zeros

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.patch.set_facecolor(C_BG)

    # Left: columns explosion
    ax1.set_facecolor(C_PANEL)
    ax1.plot(n_categories, ohe_cols, color=C_ORANGE, lw=2.5, marker='o',
             markersize=5, label='OHE columns')
    ax1.axvline(x=50, color=C_GRAY, linestyle='--', lw=1.5, label='~50 uniq: border zone')
    ax1.axvline(x=200, color=C_INK, linestyle=':', lw=1.5, label='>200 uniq: high-cardinality')
    ax1.fill_betweenx([0, 10000], 0, 50, alpha=0.12, color=C_GREEN, label='Safe OHE zone')
    ax1.fill_betweenx([0, 10000], 200, 10000, alpha=0.10, color=C_ORANGE, label='Danger zone')
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_xlabel('Уникальных категорий (log)', color=C_INK)
    ax1.set_ylabel('Новых признаков (OHE, log)', color=C_INK)
    ax1.set_title('Взрыв размерности при OHE', color=C_INK, fontweight='bold', fontsize=12)
    ax1.legend(fontsize=8.5, facecolor=C_BG, edgecolor=C_GRAY)
    ax1.grid(True, linestyle='--', alpha=0.5)

    # Right: memory comparison dense vs sparse
    ax2.set_facecolor(C_PANEL)
    ax2.plot(n_categories, mb_dense, color=C_ORANGE, lw=2.5, marker='s',
             markersize=5, label='Dense float64 (MB)')
    ax2.plot(n_categories, mb_sparse, color=C_BLUE, lw=2.5, marker='^',
             markersize=5, label='Sparse uint8 (MB)')
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_xlabel('Уникальных категорий (log)', color=C_INK)
    ax2.set_ylabel('Память (MB, log scale)', color=C_INK)
    ax2.set_title('Память: Dense vs Sparse OHE\n(100 000 строк)', color=C_INK,
                  fontweight='bold', fontsize=12)
    ax2.legend(fontsize=9.5, facecolor=C_BG, edgecolor=C_GRAY)
    ax2.grid(True, linestyle='--', alpha=0.5)

    fig.tight_layout()
    _save(fig, 'cardinality_tradeoff')
    print('Saved: cardinality_tradeoff.png')


def main():
    draw_encoding_comparison()
    draw_feature_importance()
    draw_cardinality_tradeoff()
    print('All visuals generated in assets/')


if __name__ == '__main__':
    main()
