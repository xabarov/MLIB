"""Иллюстрации для лекции про линейную зависимость, ранг и ФСР."""

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


def draw_linear_dependence_basis_selection(
    out_name: str = "linear_dependence_basis_selection.png",
) -> None:
    """Две фазы: зависимость и выделение базиса."""
    _apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.9))

    v1 = np.array([1.6, 0.8])
    v2 = np.array([0.7, 1.6])
    v3 = v1 + v2

    ax = axes[0]
    _setup_axes(ax, (-0.2, 2.8), (-0.2, 2.8))
    ax.arrow(0, 0, v1[0], v1[1], width=0.025, head_width=0.14, head_length=0.18, color=C_BLUE, length_includes_head=True)
    ax.arrow(0, 0, v2[0], v2[1], width=0.025, head_width=0.14, head_length=0.18, color=C_GREEN, length_includes_head=True)
    ax.arrow(0, 0, v3[0], v3[1], width=0.025, head_width=0.14, head_length=0.18, color=C_ORANGE, length_includes_head=True)
    ax.plot([v1[0], v3[0]], [v1[1], v3[1]], ls="--", lw=1.2, color=C_GRAY)
    ax.plot([v2[0], v3[0]], [v2[1], v3[1]], ls="--", lw=1.2, color=C_GRAY)
    ax.text(v1[0] + 0.05, v1[1] - 0.08, r"$v_1$", color=C_BLUE, fontsize=11)
    ax.text(v2[0] - 0.03, v2[1] + 0.06, r"$v_2$", color=C_GREEN, fontsize=11)
    ax.text(v3[0] + 0.05, v3[1] + 0.02, r"$v_3=v_1+v_2$", color=C_ORANGE, fontsize=11)
    ax.set_title("Зависимость: один вектор выражается через другие", fontsize=11, weight="bold")
    ax.set_aspect("equal")

    ax = axes[1]
    _setup_axes(ax, (-0.2, 2.8), (-0.2, 2.8))
    ax.arrow(0, 0, v1[0], v1[1], width=0.025, head_width=0.14, head_length=0.18, color=C_BLUE, length_includes_head=True)
    ax.arrow(0, 0, v2[0], v2[1], width=0.025, head_width=0.14, head_length=0.18, color=C_GREEN, length_includes_head=True)
    ax.arrow(0, 0, v3[0], v3[1], width=0.016, head_width=0.12, head_length=0.14, color=C_ORANGE, alpha=0.45, length_includes_head=True)
    ax.text(v1[0] + 0.05, v1[1] - 0.08, r"$v_1$", color=C_BLUE, fontsize=11)
    ax.text(v2[0] - 0.03, v2[1] + 0.06, r"$v_2$", color=C_GREEN, fontsize=11)
    ax.text(1.62, 2.42, "базис", color=C_INK, fontsize=10)
    ax.text(v3[0] - 0.8, v3[1] - 0.38, "лишний вектор", color=C_ORANGE, fontsize=10)
    ax.set_title("Базис: достаточно оставить независимые направления", fontsize=11, weight="bold")
    ax.set_aspect("equal")

    fig.suptitle("Линейная зависимость и выбор базиса", fontsize=13, weight="bold")
    fig.tight_layout()
    _save(fig, out_name)


def draw_rank_rows_and_columns(out_name: str = "rank_rows_and_columns.png") -> None:
    """Подсветка базисных строк и ведущих столбцов."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(8.8, 3.8))
    ax.axis("off")

    data = [
        ["1", "2", "1", "3"],
        ["2", "4", "0", "6"],
        ["1", "2", "2", "3"],
    ]
    tbl = ax.table(cellText=data, loc="center", cellLoc="center")
    tbl.scale(1.18, 2.0)

    for (row, col), cell in tbl.get_celld().items():
        cell.set_edgecolor(C_INK)
        cell.set_linewidth(1.0)
        base_color = C_BG
        if row in (0, 2):
            base_color = "#eef3f9"
        if col in (0, 2):
            base_color = "#faefe9" if row == 1 else "#dbe8f5"
        if row in (0, 2) and col in (0, 2):
            base_color = "#c7d8ec"
        cell.set_facecolor(base_color)
        cell.get_text().set_color(C_INK)
        cell.get_text().set_fontsize(13)

    ax.text(0.06, 0.18, "базисные строки", transform=ax.transAxes, fontsize=10, color=C_BLUE)
    ax.text(0.42, 0.08, "ведущие столбцы", transform=ax.transAxes, fontsize=10, color=C_ORANGE)
    ax.set_title("Ранг 2: строки и столбцы, которые несут независимую информацию", fontsize=12, weight="bold", pad=12)
    fig.tight_layout()
    _save(fig, out_name)


def draw_kronecker_capelli_geometry(
    out_name: str = "kronecker_capelli_metaphor.png",
) -> None:
    """Геометрия: b лежит или не лежит в линейной оболочке столбцов."""
    _apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 5.0))

    a1 = np.array([1.8, 0.9])
    a2 = np.array([1.2, 0.6])
    b_good = np.array([2.5, 1.25])
    b_bad = np.array([1.8, 1.8])

    for ax in axes:
        _setup_axes(ax, (-0.2, 3.2), (-0.2, 2.5))
        ax.set_aspect("equal")
        ax.set_xlabel(r"$x$")
        ax.set_ylabel(r"$y$")

    ax = axes[0]
    span_line_x = np.linspace(0, 3.0, 100)
    ax.plot(span_line_x, 0.5 * span_line_x, color=C_GRAY, lw=1.6, ls="--", label=r"$\operatorname{span}(a_1,a_2)$")
    ax.arrow(0, 0, a1[0], a1[1], width=0.02, head_width=0.12, head_length=0.15, color=C_BLUE, length_includes_head=True)
    ax.arrow(0, 0, a2[0], a2[1], width=0.02, head_width=0.12, head_length=0.15, color=C_GREEN, length_includes_head=True)
    ax.arrow(0, 0, b_good[0], b_good[1], width=0.02, head_width=0.12, head_length=0.15, color=C_ORANGE, length_includes_head=True)
    ax.text(a1[0] + 0.05, a1[1] - 0.03, r"$a_1$", color=C_BLUE, fontsize=11)
    ax.text(a2[0] + 0.05, a2[1] - 0.16, r"$a_2$", color=C_GREEN, fontsize=11)
    ax.text(b_good[0] + 0.03, b_good[1] + 0.06, r"$b$", color=C_ORANGE, fontsize=11)
    ax.set_title("Совместная система:\n$b$ лежит в оболочке столбцов $A$", fontsize=11, weight="bold")

    ax = axes[1]
    ax.plot(span_line_x, 0.5 * span_line_x, color=C_GRAY, lw=1.6, ls="--", label=r"$\operatorname{span}(a_1,a_2)$")
    ax.arrow(0, 0, a1[0], a1[1], width=0.02, head_width=0.12, head_length=0.15, color=C_BLUE, length_includes_head=True)
    ax.arrow(0, 0, a2[0], a2[1], width=0.02, head_width=0.12, head_length=0.15, color=C_GREEN, length_includes_head=True)
    ax.arrow(0, 0, b_bad[0], b_bad[1], width=0.02, head_width=0.12, head_length=0.15, color=C_ORANGE, length_includes_head=True)
    ax.text(a1[0] + 0.05, a1[1] - 0.03, r"$a_1$", color=C_BLUE, fontsize=11)
    ax.text(a2[0] + 0.05, a2[1] - 0.16, r"$a_2$", color=C_GREEN, fontsize=11)
    ax.text(b_bad[0] + 0.04, b_bad[1] + 0.05, r"$b$", color=C_ORANGE, fontsize=11)
    ax.set_title("Несовместная система:\n$b$ выходит из оболочки столбцов $A$", fontsize=11, weight="bold")

    fig.suptitle("Геометрический смысл критерия Кронекера-Капелли", fontsize=13, weight="bold")
    fig.tight_layout()
    _save(fig, out_name)


def draw_kronecker_capelli_bars(out_name: str = "kronecker_capelli_bars.png") -> None:
    """Сравнение рангов в двух ключевых случаях."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(8.2, 4.8))

    labels = ["Совместна", "Несовместна"]
    rank_a = [2, 1]
    rank_aug = [2, 2]
    x = np.arange(len(labels))
    w = 0.35

    ax.bar(x - w / 2, rank_a, width=w, color=C_BLUE, edgecolor=C_INK, linewidth=1.0, label=r"$\mathrm{rank}(A)$")
    ax.bar(x + w / 2, rank_aug, width=w, color=C_ORANGE, edgecolor=C_INK, linewidth=1.0, label=r"$\mathrm{rank}([A\mid b])$")
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 3)
    ax.set_ylabel("значение ранга")
    ax.set_title("Сравнение рангов в критерии Кронекера-Капелли", fontsize=12, weight="bold")
    ax.grid(True, axis="y", linestyle="--", alpha=0.28)
    ax.legend(loc="upper right", fontsize=10, framealpha=0.95)
    for spine in ax.spines.values():
        spine.set_color(C_GRAY)
    fig.tight_layout()
    _save(fig, out_name)


def draw_nullspace_basis_vectors(out_name: str = "nullspace_basis_vectors.png") -> None:
    """ФСР как набор базисных векторов и формула общего решения."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    ax.axis("off")

    ax.text(0.08, 0.82, "ФСР для примера из лекции", fontsize=12, weight="bold", color=C_INK, transform=ax.transAxes)
    ax.text(
        0.08,
        0.62,
        r"$X^{(1)} = (-3,\;2,\;1,\;0)^T$",
        fontsize=17,
        color=C_BLUE,
        transform=ax.transAxes,
        bbox=dict(boxstyle="round,pad=0.35", facecolor="#edf4fb", edgecolor=C_BLUE),
    )
    ax.text(
        0.08,
        0.38,
        r"$X^{(2)} = (1,\;-1,\;0,\;1)^T$",
        fontsize=17,
        color=C_ORANGE,
        transform=ax.transAxes,
        bbox=dict(boxstyle="round,pad=0.35", facecolor="#fbefe8", edgecolor=C_ORANGE),
    )
    ax.text(
        0.08,
        0.14,
        r"Любое решение имеет вид  $x = sX^{(1)} + tX^{(2)}$",
        fontsize=16,
        color=C_GREEN,
        transform=ax.transAxes,
    )
    ax.text(0.77, 0.5, "2\nсвободные\nпеременные", fontsize=12, color=C_GREEN, ha="center", va="center", transform=ax.transAxes)
    _save(fig, out_name)


def gif_row_reduction_rank(out_name: str = "gif_row_reduction_rank.gif", duration: float = 0.55) -> None:
    """Анимация приведения к ступенчатому виду и чтения ранга."""
    _apply_style()
    frames = []

    matrices = [
        np.array([[1, 2, 1, 3], [2, 4, 0, 6], [1, 2, 2, 3]], dtype=int),
        np.array([[1, 2, 1, 3], [0, 0, -2, 0], [0, 0, 1, 0]], dtype=int),
        np.array([[1, 2, 1, 3], [0, 0, 1, 0], [0, 0, 0, 0]], dtype=int),
    ]
    titles = [
        "Исходная матрица",
        r"После $R_2 \leftarrow R_2-2R_1,\; R_3 \leftarrow R_3-R_1$",
        "Ступенчатый вид: две ненулевые строки",
    ]

    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        idx = 0
        for step, (mat, title) in enumerate(zip(matrices, titles), start=1):
            for _ in range(3):
                fig, ax = plt.subplots(figsize=(8.4, 3.5))
                ax.axis("off")
                tbl = ax.table(cellText=[[str(v) for v in row] for row in mat], loc="center", cellLoc="center")
                tbl.scale(1.18, 2.0)
                for (row, col), cell in tbl.get_celld().items():
                    cell.set_edgecolor(C_INK)
                    cell.set_linewidth(1.0)
                    if np.all(mat[row] == 0):
                        cell.set_facecolor(C_PANEL)
                    elif row < 2 and col in (0, 2):
                        cell.set_facecolor("#edf4fb")
                    else:
                        cell.set_facecolor(C_BG)
                    cell.get_text().set_color(C_INK)
                    cell.get_text().set_fontsize(13)
                ax.set_title(title, fontsize=12, weight="bold")
                if step == 3:
                    ax.text(0.5, 0.08, r"Число ненулевых строк $= 2$, значит $\operatorname{rank}(A)=2$", transform=ax.transAxes, ha="center", fontsize=11, color=C_GREEN)
                fig.tight_layout()
                fp = tmp_path / f"rr_{idx:03d}.png"
                fig.savefig(fp, dpi=130, facecolor=C_BG)
                plt.close(fig)
                frames.append(imageio.imread(fp))
                idx += 1

    imageio.mimsave(ASSETS / out_name, frames, duration=duration, loop=0)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_linear_dependence_basis_selection()
    draw_rank_rows_and_columns()
    draw_kronecker_capelli_geometry()
    draw_kronecker_capelli_bars()
    draw_nullspace_basis_vectors()
    gif_row_reduction_rank()
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
