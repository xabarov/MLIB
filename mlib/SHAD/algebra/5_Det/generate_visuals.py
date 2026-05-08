"""Иллюстрации для лекции про определители."""

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


def _setup_axes(ax: plt.Axes, xlim: tuple[float, float], ylim: tuple[float, float]) -> None:
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axhline(0, color=C_GRAY, lw=0.9)
    ax.axvline(0, color=C_GRAY, lw=0.9)
    ax.grid(True, alpha=0.28)
    for spine in ax.spines.values():
        spine.set_color(C_GRAY)


def draw_det_area_parallelogram(out_name: str = "det_area_parallelogram.png") -> None:
    _apply_style()
    v1 = np.array([2.2, 0.7])
    v2 = np.array([0.8, 1.8])
    poly = np.array([[0, 0], v1, v1 + v2, v2, [0, 0]])
    area = abs(np.linalg.det(np.column_stack([v1, v2])))

    fig, ax = plt.subplots(figsize=(7.0, 5.6))
    _setup_axes(ax, (-0.2, 3.6), (-0.2, 3.1))
    ax.fill(poly[:, 0], poly[:, 1], color=C_BLUE, alpha=0.28)
    ax.plot(poly[:, 0], poly[:, 1], color=C_BLUE, lw=2.0)
    ax.arrow(0, 0, v1[0], v1[1], width=0.02, head_width=0.12, head_length=0.15, color=C_ORANGE, length_includes_head=True)
    ax.arrow(0, 0, v2[0], v2[1], width=0.02, head_width=0.12, head_length=0.15, color=C_GREEN, length_includes_head=True)
    ax.text(v1[0] + 0.06, v1[1] - 0.05, r"$a_1$", color=C_ORANGE, fontsize=11)
    ax.text(v2[0] - 0.15, v2[1] + 0.06, r"$a_2$", color=C_GREEN, fontsize=11)
    ax.text(1.1, 1.15, fr"$|\det A| = {area:.1f}$", color=C_INK, fontsize=12)
    ax.set_aspect("equal")
    ax.set_title("Модуль определителя как площадь параллелограмма", fontsize=12, weight="bold")
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    fig.tight_layout()
    _save(fig, out_name)


def draw_sarrus_rule(out_name: str = "sarrus_rule_diagonals.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(9.0, 3.5))
    ax.axis("off")

    values = [
        ["$a_{11}$", "$a_{12}$", "$a_{13}$", "$a_{11}$", "$a_{12}$"],
        ["$a_{21}$", "$a_{22}$", "$a_{23}$", "$a_{21}$", "$a_{22}$"],
        ["$a_{31}$", "$a_{32}$", "$a_{33}$", "$a_{31}$", "$a_{32}$"],
    ]
    tbl = ax.table(cellText=values, loc="center", cellLoc="center")
    tbl.scale(1.2, 2.0)
    for (_, col), cell in tbl.get_celld().items():
        cell.set_edgecolor(C_INK)
        cell.set_linewidth(1.0)
        cell.set_facecolor("#eef3f9" if col < 3 else "#f6f1e8")
        cell.get_text().set_color(C_INK)
        cell.get_text().set_fontsize(13)

    ax.plot([0.14, 0.48], [0.73, 0.32], color=C_GREEN, lw=2.5, transform=ax.transAxes)
    ax.plot([0.30, 0.64], [0.73, 0.32], color=C_GREEN, lw=2.5, transform=ax.transAxes)
    ax.plot([0.46, 0.80], [0.73, 0.32], color=C_GREEN, lw=2.5, transform=ax.transAxes)

    ax.plot([0.14, 0.48], [0.32, 0.73], color=C_ORANGE, lw=2.5, transform=ax.transAxes)
    ax.plot([0.30, 0.64], [0.32, 0.73], color=C_ORANGE, lw=2.5, transform=ax.transAxes)
    ax.plot([0.46, 0.80], [0.32, 0.73], color=C_ORANGE, lw=2.5, transform=ax.transAxes)

    ax.text(0.18, 0.15, "сумма \"нисходящих\" диагоналей", color=C_GREEN, transform=ax.transAxes, fontsize=10)
    ax.text(0.54, 0.15, "минус сумма \"восходящих\" диагоналей", color=C_ORANGE, transform=ax.transAxes, fontsize=10)
    ax.set_title("Правило Саррюса для матрицы $3\\times 3$", fontsize=12, weight="bold", color=C_INK, pad=10)
    fig.tight_layout()
    _save(fig, out_name)


def draw_cofactor_checkerboard(out_name: str = "cofactor_checkerboard.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(5.2, 4.8))
    ax.axis("off")

    values = [
        ["+", "-", "+"],
        ["-", "+", "-"],
        ["+", "-", "+"],
    ]
    tbl = ax.table(cellText=values, loc="center", cellLoc="center")
    tbl.scale(1.4, 2.4)
    for (row, col), cell in tbl.get_celld().items():
        cell.set_edgecolor(C_INK)
        cell.set_linewidth(1.0)
        cell.set_facecolor("#eef3f9" if (row + col) % 2 == 0 else "#fbefe8")
        cell.get_text().set_color(C_INK)
        cell.get_text().set_fontsize(20)
        cell.get_text().set_weight("bold")

    ax.set_title("Шахматная таблица знаков для алгебраических дополнений", fontsize=12, weight="bold", pad=10)
    ax.text(0.5, 0.08, r"$A_{ij}=(-1)^{i+j}M_{ij}$", ha="center", transform=ax.transAxes, fontsize=13, color=C_PURPLE)
    fig.tight_layout()
    _save(fig, out_name)


def draw_zero_det_dependence(out_name: str = "zero_det_degenerate_parallelogram.png") -> None:
    _apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.8))

    v1 = np.array([2.1, 0.8])
    v2 = np.array([0.9, 1.7])
    poly = np.array([[0, 0], v1, v1 + v2, v2, [0, 0]])

    ax = axes[0]
    _setup_axes(ax, (-0.2, 3.5), (-0.2, 2.9))
    ax.fill(poly[:, 0], poly[:, 1], color=C_BLUE, alpha=0.25)
    ax.plot(poly[:, 0], poly[:, 1], color=C_BLUE, lw=2.0)
    ax.arrow(0, 0, v1[0], v1[1], width=0.02, head_width=0.12, head_length=0.15, color=C_ORANGE, length_includes_head=True)
    ax.arrow(0, 0, v2[0], v2[1], width=0.02, head_width=0.12, head_length=0.15, color=C_GREEN, length_includes_head=True)
    ax.set_title(r"$\det A \neq 0$: ненулевая площадь", fontsize=11, weight="bold")
    ax.set_aspect("equal")

    ax = axes[1]
    _setup_axes(ax, (-0.2, 3.5), (-0.2, 2.9))
    v1 = np.array([2.0, 0.9])
    v2 = 1.6 * v1
    ax.arrow(0, 0, v1[0], v1[1], width=0.02, head_width=0.12, head_length=0.15, color=C_ORANGE, length_includes_head=True)
    ax.arrow(0, 0, v2[0], v2[1], width=0.02, head_width=0.12, head_length=0.15, color=C_GREEN, length_includes_head=True)
    ax.plot([0, v2[0]], [0, v2[1]], color=C_GRAY, ls="--", lw=1.2)
    ax.text(1.75, 1.1, "векторы коллинеарны", color=C_INK, fontsize=10)
    ax.set_title(r"$\det A = 0$: параллелограмм вырождается в отрезок", fontsize=11, weight="bold")
    ax.set_aspect("equal")

    fig.suptitle("Нулевой определитель и линейная зависимость столбцов", fontsize=13, weight="bold")
    fig.tight_layout()
    _save(fig, out_name)


def gif_det_row_reduction(out_name: str = "gif_det_row_reduction.gif", duration: float = 0.65) -> None:
    _apply_style()
    frames = []
    matrices = [
        np.array([[1, 2, 1], [2, 5, 3], [1, 0, 8]], dtype=int),
        np.array([[1, 2, 1], [0, 1, 1], [0, -2, 7]], dtype=int),
        np.array([[1, 2, 1], [0, 1, 1], [0, 0, 9]], dtype=int),
    ]
    titles = [
        "Исходная матрица",
        r"После $R_2 \leftarrow R_2-2R_1,\; R_3 \leftarrow R_3-R_1$",
        r"После $R_3 \leftarrow R_3+2R_2$: треугольный вид",
    ]

    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        idx = 0
        for step, (mat, title) in enumerate(zip(matrices, titles), start=1):
            for _ in range(3):
                fig, ax = plt.subplots(figsize=(7.6, 3.6))
                ax.axis("off")
                tbl = ax.table(cellText=[[str(v) for v in row] for row in mat], loc="center", cellLoc="center")
                tbl.scale(1.2, 2.0)
                for (row, col), cell in tbl.get_celld().items():
                    cell.set_edgecolor(C_INK)
                    cell.set_linewidth(1.0)
                    cell.set_facecolor("#eef3f9" if row == col else C_BG)
                    cell.get_text().set_fontsize(13)
                    cell.get_text().set_color(C_INK)
                ax.set_title(title, fontsize=12, weight="bold")
                if step == 3:
                    ax.text(0.5, 0.08, r"Разрешённые преобразования не меняли det, поэтому $\det A = 1\cdot 1\cdot 9 = 9$", ha="center", transform=ax.transAxes, fontsize=10.5, color=C_GREEN)
                fp = tmp_path / f"det_{idx:03d}.png"
                fig.savefig(fp, dpi=130, facecolor=C_BG)
                plt.close(fig)
                frames.append(imageio.imread(fp))
                idx += 1
    ASSETS.mkdir(parents=True, exist_ok=True)
    imageio.mimsave(ASSETS / out_name, frames, duration=duration, loop=0)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_det_area_parallelogram()
    draw_sarrus_rule()
    draw_cofactor_checkerboard()
    draw_zero_det_dependence()
    gif_det_row_reduction()
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
