"""
Иллюстрации для лекции SHAD/algebra/4_Rank (линейная зависимость, ранг, Кронекер-Капелли, ФСР).

Палитра: SHAD/lecture_visual_generation/lecture_visual_design_system.md
"""

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


def _apply_style():
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
            "grid.alpha": 0.35,
            "font.size": 11,
        }
    )


def draw_rank_rows_and_columns(out_name: str = "rank_rows_and_columns.png"):
    """Матрица из лекции и подсветка базисных строк/столбцов."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(8.2, 3.4))
    fig.patch.set_facecolor(C_BG)
    ax.axis("off")

    data = [
        ["1", "2", "1", "3"],
        ["2", "4", "0", "6"],
        ["1", "2", "2", "3"],
    ]
    tbl = ax.table(cellText=data, loc="center", cellLoc="center")
    tbl.scale(1.2, 2.0)

    for (row, col), cell in tbl.get_celld().items():
        cell.set_edgecolor(C_INK)
        cell.set_linewidth(1.0)
        if row in (0, 2) and col >= 0:
            cell.set_facecolor(C_BLUE if col in (0, 2) else C_PANEL)
        elif row == 1 and col >= 0:
            cell.set_facecolor(C_BG)
        cell.get_text().set_color(C_INK)
        cell.get_text().set_fontsize(13)

    ax.set_title(
        "Ранг матрицы: ведущие строки и столбцы (пример, rank = 2)",
        fontsize=12,
        weight="bold",
        color=C_INK,
        pad=12,
    )
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def draw_kronecker_capelli_bars(out_name: str = "kronecker_capelli_bars.png"):
    """Иллюстрация случаев rank(A)=rank([A|b]) и rank(A)<rank([A|b])."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)

    labels = ["Совместна", "Несовместна"]
    rank_a = [2, 1]
    rank_aug = [2, 2]
    x = np.arange(len(labels))
    w = 0.35

    ax.bar(x - w / 2, rank_a, width=w, color=C_BLUE, edgecolor=C_INK, linewidth=1.0, label=r"$\mathrm{rank}(A)$")
    ax.bar(
        x + w / 2,
        rank_aug,
        width=w,
        color=C_ORANGE,
        edgecolor=C_INK,
        linewidth=1.0,
        label=r"$\mathrm{rank}([A\mid b])$",
    )
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 3)
    ax.set_ylabel("значение ранга", color=C_INK)
    ax.set_title("Критерий Кронекера-Капелли", fontsize=13, weight="bold", color=C_INK)
    ax.grid(True, axis="y", linestyle="--", alpha=0.35)
    ax.legend(loc="upper right", fontsize=10)

    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def draw_nullspace_basis_vectors(out_name: str = "nullspace_basis_vectors.png"):
    """ФСР из лекции как две базисные стрелки в R^2."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(6.6, 6.2))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.axhline(0, color=C_GRAY, lw=1.2)
    ax.axvline(0, color=C_GRAY, lw=1.2)

    v1 = np.array([-3, 2], dtype=float)
    v2 = np.array([1, -1], dtype=float)

    ax.quiver(0, 0, v1[0], v1[1], angles="xy", scale_units="xy", scale=1, color=C_BLUE, width=0.008)
    ax.quiver(0, 0, v2[0], v2[1], angles="xy", scale_units="xy", scale=1, color=C_ORANGE, width=0.008)
    ax.text(v1[0] - 0.2, v1[1] + 0.2, r"$X^{(1)}$", color=C_INK, fontsize=12)
    ax.text(v2[0] + 0.15, v2[1] - 0.25, r"$X^{(2)}$", color=C_INK, fontsize=12)

    ax.set_xlim(-4.2, 2.4)
    ax.set_ylim(-2.6, 3.0)
    ax.set_aspect("equal")
    ax.grid(True, linestyle="--", alpha=0.35)
    ax.set_title("ФСР однородной системы: базис пространства решений", fontsize=12, weight="bold", color=C_INK)

    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def gif_row_reduction_rank(out_name: str = "gif_row_reduction_rank.gif", duration: float = 0.5):
    """Анимация шагов приведения к ступенчатому виду и подсчета ранга."""
    _apply_style()
    frames = []

    matrices = [
        np.array([[1, 2, 1, 3], [2, 4, 0, 6], [1, 2, 2, 3]], dtype=int),
        np.array([[1, 2, 1, 3], [0, 0, -2, 0], [0, 0, 1, 0]], dtype=int),
        np.array([[1, 2, 1, 3], [0, 0, 1, 0], [0, 0, 0, 0]], dtype=int),
    ]
    titles = [
        "Исходная матрица A",
        "После R2 <- R2 - 2R1, R3 <- R3 - R1",
        "Ступенчатый вид: две ненулевые строки => rank(A)=2",
    ]

    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        idx = 0
        for mat, title in zip(matrices, titles):
            for _ in range(3):
                fig, ax = plt.subplots(figsize=(8.2, 3.1))
                fig.patch.set_facecolor(C_BG)
                ax.axis("off")
                tbl = ax.table(
                    cellText=[[str(v) for v in row] for row in mat],
                    loc="center",
                    cellLoc="center",
                )
                tbl.scale(1.2, 2.0)
                for (row, col), cell in tbl.get_celld().items():
                    cell.set_edgecolor(C_INK)
                    cell.set_linewidth(1.0)
                    if np.all(mat[row] == 0):
                        cell.set_facecolor(C_PANEL)
                    else:
                        cell.set_facecolor(C_BG)
                    cell.get_text().set_fontsize(13)
                    cell.get_text().set_color(C_INK)
                ax.set_title(title, fontsize=12, weight="bold", color=C_INK)
                fig.tight_layout()
                fp = tmp_path / f"rr_{idx:03d}.png"
                fig.savefig(fp, dpi=130, facecolor=C_BG)
                plt.close(fig)
                frames.append(imageio.imread(fp))
                idx += 1

    imageio.mimsave(ASSETS / out_name, frames, duration=duration, loop=0)


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_rank_rows_and_columns()
    draw_kronecker_capelli_bars()
    draw_nullspace_basis_vectors()
    gif_row_reduction_rank()
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
