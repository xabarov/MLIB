"""Иллюстрации для лекции про операции над матрицами."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import imageio.v2 as imageio
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
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
C_PURPLE = "#7c6ccf"


def _apply_style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": C_BG,
            "axes.facecolor": C_BG,
            "axes.edgecolor": C_GRAY,
            "axes.labelcolor": C_INK,
            "text.color": C_INK,
            "xtick.color": C_INK,
            "ytick.color": C_INK,
            "grid.color": C_GRAY,
            "grid.alpha": 0.28,
            "font.size": 11,
        }
    )


def _save(fig: plt.Figure, out_name: str) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def _table(ax: plt.Axes, data: list[list[str]], bbox: list[float], header_rows: set[int] | None = None) -> None:
    header_rows = header_rows or set()
    tbl = ax.table(cellText=data, cellLoc="center", bbox=bbox)
    for (row, _), cell in tbl.get_celld().items():
        cell.set_edgecolor(C_INK)
        cell.set_linewidth(1.0)
        cell.set_facecolor("#edf4fb" if row in header_rows else C_BG)
        cell.get_text().set_color(C_INK)
        cell.get_text().set_fontsize(12)
        if row in header_rows:
            cell.get_text().set_weight("bold")


def draw_matrix_product_scheme(out_name: str = "matrix_product_row_column.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(10.0, 4.2))
    ax.axis("off")

    _table(ax, [["1", "2"], ["3", "4"]], [0.05, 0.32, 0.18, 0.38])
    _table(ax, [["5", "6"], ["7", "8"]], [0.40, 0.32, 0.18, 0.38])
    _table(ax, [["19", "22"], ["43", "50"]], [0.76, 0.32, 0.18, 0.38])

    ax.text(0.14, 0.74, r"$A$", fontsize=16, weight="bold", transform=ax.transAxes)
    ax.text(0.49, 0.74, r"$B$", fontsize=16, weight="bold", transform=ax.transAxes)
    ax.text(0.84, 0.74, r"$AB$", fontsize=16, weight="bold", transform=ax.transAxes)
    ax.text(0.30, 0.5, r"$\times$", fontsize=18, transform=ax.transAxes)
    ax.text(0.67, 0.5, r"$=$", fontsize=18, transform=ax.transAxes)

    ax.annotate("", xy=(0.43, 0.61), xytext=(0.23, 0.61), xycoords=ax.transAxes, textcoords=ax.transAxes,
                arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=2))
    ax.annotate("", xy=(0.49, 0.67), xytext=(0.49, 0.31), xycoords=ax.transAxes, textcoords=ax.transAxes,
                arrowprops=dict(arrowstyle="->", color=C_GREEN, lw=2))
    ax.text(0.18, 0.68, "строка A", color=C_ORANGE, transform=ax.transAxes, fontsize=10)
    ax.text(0.51, 0.70, "столбец B", color=C_GREEN, transform=ax.transAxes, fontsize=10)
    ax.text(0.78, 0.22, r"$(AB)_{11}=1\cdot5+2\cdot7=19$", color=C_PURPLE, transform=ax.transAxes, fontsize=11)
    ax.set_title("Произведение матриц: строка первой матрицы на столбец второй", fontsize=13, weight="bold", color=C_INK)
    fig.tight_layout()
    _save(fig, out_name)


def draw_noncommutative_example(out_name: str = "matrix_noncommutativity.png") -> None:
    _apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.3))
    titles = ["AB = [[2, 0], [0, 0]]", "BA = [[1, 1], [1, 1]]"]
    matrices = [
        [["2", "0"], ["0", "0"]],
        [["1", "1"], ["1", "1"]],
    ]
    colors = [C_BLUE, C_ORANGE]

    for ax, title, data, color in zip(axes, titles, matrices, colors):
        ax.axis("off")
        tbl = ax.table(cellText=data, cellLoc="center", loc="center")
        for _, cell in tbl.get_celld().items():
            cell.set_edgecolor(C_INK)
            cell.set_linewidth(1.0)
            cell.set_facecolor(C_BG)
            cell.get_text().set_color(C_INK)
            cell.get_text().set_fontsize(18)
        tbl.scale(1.3, 2.3)
        ax.set_title(title, fontsize=15, weight="bold", color=color)

    fig.suptitle("В общем случае порядок множителей важен: $AB \\ne BA$", fontsize=13, weight="bold")
    fig.tight_layout()
    _save(fig, out_name)


def draw_rank_product_columns(out_name: str = "rank_product_columns.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(7.2, 5.6))
    ax.set_xlim(-0.2, 3.6)
    ax.set_ylim(-0.2, 2.7)
    ax.axhline(0, color=C_GRAY, lw=0.9)
    ax.axvline(0, color=C_GRAY, lw=0.9)
    ax.grid(True, alpha=0.28)
    for spine in ax.spines.values():
        spine.set_color(C_GRAY)

    a1 = np.array([1.7, 0.8])
    a2 = np.array([3.0, 1.4])
    ax.plot([0, 3.3], [0, 1.54], ls="--", color=C_GRAY, lw=1.4)
    ax.arrow(0, 0, a1[0], a1[1], width=0.02, head_width=0.12, head_length=0.15, color=C_BLUE, length_includes_head=True)
    ax.arrow(0, 0, a2[0], a2[1], width=0.02, head_width=0.12, head_length=0.15, color=C_GREEN, length_includes_head=True)

    cols = [np.array([0.9, 0.42]), np.array([2.2, 1.03]), np.array([2.9, 1.35])]
    for idx, col in enumerate(cols, start=1):
        ax.arrow(0, 0, col[0], col[1], width=0.013, head_width=0.10, head_length=0.12, color=C_ORANGE, alpha=0.8, length_includes_head=True)
        ax.text(col[0] + 0.03, col[1] + 0.04, fr"$Ab_{idx}$", color=C_ORANGE, fontsize=10)

    ax.text(1.8, 1.95, "все столбцы $AB$\nлежат в оболочке\nстолбцов $A$", color=C_INK, fontsize=11)
    ax.text(a1[0] + 0.06, a1[1] - 0.08, r"$a_1$", color=C_BLUE, fontsize=11)
    ax.text(a2[0] + 0.04, a2[1] - 0.08, r"$a_2$", color=C_GREEN, fontsize=11)
    ax.set_title(r"Почему $\operatorname{rank}(AB)\leq \operatorname{rank}(A)$", fontsize=12, weight="bold")
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    fig.tight_layout()
    _save(fig, out_name)


def draw_adjugate_transpose_scheme(out_name: str = "adjugate_transpose_scheme.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(10.2, 4.3))
    ax.axis("off")

    _table(ax, [["$A_{11}$", "$A_{12}$", "$A_{13}$"], ["$A_{21}$", "$A_{22}$", "$A_{23}$"], ["$A_{31}$", "$A_{32}$", "$A_{33}$"]], [0.05, 0.25, 0.28, 0.5])
    _table(ax, [["$A_{11}$", "$A_{21}$", "$A_{31}$"], ["$A_{12}$", "$A_{22}$", "$A_{32}$"], ["$A_{13}$", "$A_{23}$", "$A_{33}$"]], [0.63, 0.25, 0.28, 0.5])

    ax.text(0.11, 0.80, "матрица\nалгебраических\nдополнений", ha="center", transform=ax.transAxes, fontsize=11, color=C_BLUE)
    ax.text(0.69, 0.80, r"$\operatorname{adj}(A)$", transform=ax.transAxes, fontsize=16, weight="bold", color=C_ORANGE)
    ax.annotate("", xy=(0.60, 0.50), xytext=(0.37, 0.50), xycoords=ax.transAxes, textcoords=ax.transAxes,
                arrowprops=dict(arrowstyle="->", color=C_PURPLE, lw=2))
    ax.text(0.43, 0.57, "транспонируем", color=C_PURPLE, transform=ax.transAxes, fontsize=11)
    ax.text(0.56, 0.12, r"$A^{-1}=\dfrac{1}{\det A}\operatorname{adj}(A)$", color=C_GREEN, transform=ax.transAxes, fontsize=15)

    ax.set_title("Присоединенная матрица получается транспонированием матрицы дополнений", fontsize=12, weight="bold")
    fig.tight_layout()
    _save(fig, out_name)


def gif_inverse_gauss(out_name: str = "gif_inverse_gauss_steps.gif", duration: float = 0.6) -> None:
    _apply_style()
    frames = []
    states = [
        (
            [["1", "2", "1", "0"], ["3", "4", "0", "1"]],
            r"Исходная расширенная матрица $[A\mid I]$",
        ),
        (
            [["1", "2", "1", "0"], ["0", "-2", "-3", "1"]],
            r"После $R_2 \leftarrow R_2-3R_1$",
        ),
        (
            [["1", "2", "1", "0"], ["0", "1", "3/2", "-1/2"]],
            r"После $R_2 \leftarrow -\frac{1}{2} R_2$",
        ),
        (
            [["1", "0", "-2", "1"], ["0", "1", "3/2", "-1/2"]],
            r"После $R_1 \leftarrow R_1-2R_2$: получаем $[I\mid A^{-1}]$",
        ),
    ]

    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        idx = 0
        for step, (data, title) in enumerate(states, start=1):
            for _ in range(3):
                fig, ax = plt.subplots(figsize=(8.4, 3.6))
                ax.axis("off")
                tbl = ax.table(cellText=data, cellLoc="center", loc="center")
                for (_, col), cell in tbl.get_celld().items():
                    cell.set_edgecolor(C_INK)
                    cell.set_linewidth(1.0)
                    if col < 2:
                        cell.set_facecolor("#eef3f9")
                    else:
                        cell.set_facecolor("#fbefe8")
                    cell.get_text().set_color(C_INK)
                    cell.get_text().set_fontsize(14)
                tbl.scale(1.25, 2.15)
                ax.set_title(title, fontsize=12, weight="bold")
                ax.text(0.30, 0.14, "левая часть", transform=ax.transAxes, fontsize=10, color=C_BLUE)
                ax.text(0.69, 0.14, "правая часть", transform=ax.transAxes, fontsize=10, color=C_ORANGE)
                if step == 4:
                    ax.text(0.50, 0.05, r"$A^{-1}$ = [[-2, 1], [3/2, -1/2]]", transform=ax.transAxes, ha="center", fontsize=12, color=C_GREEN)
                fp = tmp_path / f"inverse_{idx:03d}.png"
                fig.savefig(fp, dpi=130, facecolor=C_BG)
                plt.close(fig)
                frames.append(imageio.imread(fp))
                idx += 1

    ASSETS.mkdir(parents=True, exist_ok=True)
    imageio.mimsave(ASSETS / out_name, frames, duration=duration, loop=0)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_matrix_product_scheme()
    draw_noncommutative_example()
    draw_rank_product_columns()
    draw_adjugate_transpose_scheme()
    gif_inverse_gauss()
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
