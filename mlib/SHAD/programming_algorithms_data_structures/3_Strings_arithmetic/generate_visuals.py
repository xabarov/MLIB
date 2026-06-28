"""Точные схемы для лекции 3: Строки и длинная арифметика."""
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

ROOT   = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

C_BG     = "#faf9f5"
C_INK    = "#141413"
C_GRAY   = "#b0aea5"
C_PANEL  = "#e8e6dc"
C_ORANGE = "#d97757"
C_BLUE   = "#6a9bcc"
C_GREEN  = "#788c5d"


def _apply_style():
    plt.rcParams.update({
        "figure.facecolor":  C_BG,
        "axes.facecolor":    C_BG,
        "axes.edgecolor":    C_GRAY,
        "axes.labelcolor":   C_INK,
        "xtick.color":       C_INK,
        "ytick.color":       C_INK,
        "text.color":        C_INK,
        "font.size":         11,
        "font.family":       "sans-serif",
        "axes.spines.top":   False,
        "axes.spines.right": False,
    })


def _save(fig, name: str):
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS / name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)
    print("Saved: assets/" + name)


# ---------------------------------------------------------------------------
# Диаграмма 1: Расположение char-массива "hello\0" в памяти
# ---------------------------------------------------------------------------

def draw_string_layout():
    _apply_style()

    chars = ['h', 'e', 'l', 'l', 'o', '\\0']
    labels_bottom = ['0', '1', '2', '3', '4', '5']
    n = len(chars)

    fig, ax = plt.subplots(figsize=(9, 2.8))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.axis("off")

    cell_w = 1.1
    cell_h = 0.7
    x0 = 0.5
    y0 = 0.9

    for i, ch in enumerate(chars):
        x = x0 + i * (cell_w + 0.08)
        is_null = (ch == '\\0')
        face = C_ORANGE if is_null else C_PANEL
        edge = C_ORANGE if is_null else C_BLUE

        rect = mpatches.Rectangle(
            (x, y0), cell_w, cell_h,
            facecolor=face, edgecolor=edge, linewidth=2.0
        )
        ax.add_patch(rect)

        # Символ внутри ячейки
        ax.text(
            x + cell_w / 2, y0 + cell_h / 2,
            ch,
            ha="center", va="center",
            fontsize=14, color=C_INK,
            fontweight="bold" if is_null else "normal",
            fontfamily="monospace"
        )

        # Индекс под ячейкой
        ax.text(
            x + cell_w / 2, y0 - 0.25,
            labels_bottom[i],
            ha="center", va="top",
            fontsize=9.5, color=C_GRAY
        )

    # Стрелка к '\0' с подписью
    null_x = x0 + 5 * (cell_w + 0.08) + cell_w / 2
    ax.annotate(
        "нуль-терминатор",
        xy=(null_x, y0 + cell_h),
        xytext=(null_x + 0.4, y0 + cell_h + 0.55),
        fontsize=9.5, color=C_ORANGE,
        arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=1.4),
        ha="left"
    )

    # Скобка длины
    arr_end = x0 + 5 * (cell_w + 0.08)
    y_brace = y0 - 0.65
    ax.annotate(
        "", xy=(x0, y_brace), xytext=(arr_end, y_brace),
        arrowprops=dict(arrowstyle="<->", color=C_GRAY, lw=1.3)
    )
    ax.text(
        (x0 + arr_end) / 2, y_brace - 0.22,
        'strlen("hello") = 5',
        ha="center", va="top", fontsize=9.5, color=C_GRAY
    )

    ax.set_xlim(0, x0 + n * (cell_w + 0.08) + 2.0)
    ax.set_ylim(y0 - 1.1, y0 + cell_h + 1.1)
    ax.set_title('char s[] = "hello";   // размер массива = 6', fontsize=12,
                 color=C_INK, pad=10, fontfamily="monospace")

    fig.tight_layout()
    _save(fig, "string_layout.png")


# ---------------------------------------------------------------------------
# Диаграмма 2: Сложение BigInt с переносами (123456789 + 987654321)
# ---------------------------------------------------------------------------

def draw_bigint_addition():
    _apply_style()

    # Числа (цифры от старшего к младшему, для отображения)
    a_digits = list("123456789")  # старший слева
    b_digits = list("987654321")
    n = len(a_digits)

    # Результат: 123456789 + 987654321 = 1111111110
    result   = list("1111111110")  # 10 цифр
    fig, ax = plt.subplots(figsize=(11, 3.8))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.axis("off")

    cell_w = 0.8
    cell_h = 0.55
    gap    = 0.06
    x0     = 0.6

    row_a   = 2.5
    row_b   = 1.8
    row_res = 0.8
    row_car = 3.25

    def draw_row(digits, y, color_face, color_edge, label, label_color=C_INK, font_size=13):
        # label справа
        ax.text(x0 - 0.3, y + cell_h / 2, label,
                ha="right", va="center", fontsize=10, color=label_color)
        for k, ch in enumerate(digits):
            x = x0 + k * (cell_w + gap)
            rect = mpatches.Rectangle(
                (x, y), cell_w, cell_h,
                facecolor=color_face, edgecolor=color_edge, linewidth=1.5
            )
            ax.add_patch(rect)
            ax.text(x + cell_w / 2, y + cell_h / 2, ch,
                    ha="center", va="center", fontsize=font_size,
                    color=C_INK, fontfamily="monospace")

    # Строка A
    draw_row(a_digits, row_a, C_PANEL, C_BLUE, "a =", font_size=12)
    # Строка B
    draw_row(b_digits, row_b, C_PANEL, C_BLUE, "b =", font_size=12)
    # Строка результата (на одну цифру длиннее)
    draw_row(result, row_res, C_GREEN + "55", C_GREEN, "=", label_color=C_GREEN, font_size=12)

    # Линия-разделитель перед результатом
    line_x_start = x0 - 0.05
    line_x_end   = x0 + len(result) * (cell_w + gap) + 0.1
    ax.plot([line_x_start, line_x_end], [row_res + cell_h + 0.08, row_res + cell_h + 0.08],
            color=C_INK, lw=1.5, linestyle="--")
    ax.text(line_x_start - 0.05, row_res + cell_h + 0.08, "+",
            ha="right", va="center", fontsize=16, color=C_INK)

    # Переносы carry над строкой A (справа налево: переносы появляются из правых позиций)
    # Перенос возникает когда a[i]+b[i] >= 10, рисуем над следующей позицией (слева)
    # Для отображения: carry[k] над позицией k (0 = самый левый = старший)
    carry_display = [1, 1, 1, 1, 1, 1, 1, 1, 0]  # переносы над каждой позицией (для 9 позиций)
    # Над самой левой — нет (она сама становится старшим разрядом)
    for k in range(n):
        c_val = carry_display[k]
        if c_val:
            x = x0 + k * (cell_w + gap) + cell_w / 2
            ax.text(x, row_car - 0.05, str(c_val),
                    ha="center", va="bottom", fontsize=9, color=C_ORANGE, fontweight="bold")
            # Маленькая стрелка вниз к строке a
            ax.annotate("", xy=(x, row_a + cell_h),
                        xytext=(x, row_car - 0.05),
                        arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=0.9))

    ax.text(x0 + n * (cell_w + gap) / 2, row_car + 0.28,
            "переносы (carry)",
            ha="center", va="bottom", fontsize=9.5, color=C_ORANGE)

    # Заголовок результата
    res_str = "123456789 + 987654321 = 1111111110"
    ax.text(x0 + len(result) * (cell_w + gap) / 2, row_res - 0.35,
            res_str, ha="center", va="top", fontsize=9, color=C_GRAY)

    ax.set_xlim(0, x0 + len(result) * (cell_w + gap) + 0.5)
    ax.set_ylim(row_res - 0.7, row_car + 0.7)
    ax.set_title("Сложение длинных чисел: поразрядно с переносом", fontsize=12,
                 color=C_INK, pad=8)

    fig.tight_layout()
    _save(fig, "bigint_addition.png")


# ---------------------------------------------------------------------------
# Диаграмма 3: Умножение BigInt столбиком (123 × 45)
# ---------------------------------------------------------------------------

def draw_bigint_multiplication():
    _apply_style()

    # a = 123 = [3, 2, 1] (младший в [0]), b = 45 = [5, 4]
    # Для отображения сетки: a по строкам (i), b по столбцам (j)
    # a_disp = [1, 2, 3] (старший слева), b_disp = [4, 5]
    a_disp   = [1, 2, 3]   # разряды a от старшего к младшему
    b_disp   = [4, 5]      # разряды b от старшего к младшему
    n_a, n_b = len(a_disp), len(b_disp)

    # Частичные произведения (i-я строка a, j-й столбец b)
    # В нотации алгоритма: a[i] индексируется от младшего; для сетки отобразим
    # частичные произведения grid[i][j] = a_disp[i] * b_disp[j]
    grid = [[a_disp[i] * b_disp[j] for j in range(n_b)] for i in range(n_a)]

    fig, ax = plt.subplots(figsize=(8, 5.5))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.axis("off")

    cell_w = 1.0
    cell_h = 0.65
    gap_x  = 0.08
    gap_y  = 0.08

    # Заголовки столбцов (цифры b)
    header_y = 4.2
    ax.text(0.4, header_y + cell_h / 2, "×", ha="center", va="center",
            fontsize=16, color=C_INK)
    for j, bj in enumerate(b_disp):
        x = 1.3 + j * (cell_w + gap_x)
        ax.text(x + cell_w / 2, header_y + cell_h / 2, str(bj),
                ha="center", va="center", fontsize=14, color=C_BLUE,
                fontweight="bold", fontfamily="monospace")
        rect = mpatches.Rectangle((x, header_y), cell_w, cell_h,
                                   facecolor=C_PANEL, edgecolor=C_BLUE, linewidth=1.8)
        ax.add_patch(rect)

    # Заголовки строк (цифры a) и сетка произведений
    colors_row = [C_ORANGE, C_GREEN, C_BLUE]
    for i, ai in enumerate(a_disp):
        y = header_y - (i + 1) * (cell_h + gap_y)
        c = colors_row[i % len(colors_row)]
        # Цифра a слева
        rect_a = mpatches.Rectangle((0.0, y), cell_w, cell_h,
                                     facecolor=C_PANEL, edgecolor=c, linewidth=1.8)
        ax.add_patch(rect_a)
        ax.text(0.0 + cell_w / 2, y + cell_h / 2, str(ai),
                ha="center", va="center", fontsize=14, color=c,
                fontweight="bold", fontfamily="monospace")

        for j in range(n_b):
            x = 1.3 + j * (cell_w + gap_x)
            val = grid[i][j]
            rect = mpatches.Rectangle((x, y), cell_w, cell_h,
                                       facecolor=C_BG, edgecolor=c, linewidth=1.2,
                                       linestyle="--")
            ax.add_patch(rect)
            ax.text(x + cell_w / 2, y + cell_h / 2, str(val),
                    ha="center", va="center", fontsize=12, color=c,
                    fontfamily="monospace")

    # Формула результата
    y_form = header_y - (n_a + 1) * (cell_h + gap_y) - 0.1
    ax.plot([0, 1.3 + n_b * (cell_w + gap_x)], [y_form + cell_h + 0.05] * 2,
            color=C_INK, lw=1.5, linestyle="--")

    # Объяснение: res[i+j] += a[i]*b[j]
    ax.text(0.0, y_form + cell_h / 2,
            "res[i+j] += a[i] × b[j]",
            ha="left", va="center", fontsize=10, color=C_GRAY,
            fontfamily="monospace")

    # Итог
    ax.text(1.3 + n_b * (cell_w + gap_x) / 2, y_form - 0.2,
            "123 × 45 = 5535",
            ha="center", va="top", fontsize=12, color=C_INK, fontweight="bold")

    # Таблица частичных произведений (res до нормализации)
    y_table = y_form - 0.85
    ax.text(0.0, y_table + 0.1,
            "До нормализации:  res = [15, 22, 13, 4]",
            ha="left", va="bottom", fontsize=9.5, color=C_GRAY,
            fontfamily="monospace")
    ax.text(0.0, y_table - 0.2,
            "После нормализации: res = [ 5,  3,  5, 5]  →  5535",
            ha="left", va="bottom", fontsize=9.5, color=C_GREEN,
            fontfamily="monospace")

    ax.set_xlim(-0.2, 4.5)
    ax.set_ylim(y_table - 0.5, header_y + cell_h + 0.6)
    ax.set_title("Умножение BigInt столбиком: 123 × 45", fontsize=12,
                 color=C_INK, pad=8)

    fig.tight_layout()
    _save(fig, "bigint_multiplication.png")


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_string_layout()
    draw_bigint_addition()
    draw_bigint_multiplication()
    print("Все диаграммы сгенерированы.")


if __name__ == "__main__":
    main()
