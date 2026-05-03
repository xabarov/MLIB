"""
Иллюстрации для лекции SHAD/algebra/3_Linear_equations (СЛАУ, Гаусс, Якоби, Гаусса–Зейделя).

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


def draw_augmented_matrix_example(out_name: str = "augmented_matrix_example.png"):
    """Пример из §3: $[A\\mid b]$ для $2\\times 3$ системы."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(7.2, 2.8))
    ax.axis("off")
    fig.patch.set_facecolor(C_BG)
    data = [["1", "2", "-1", "3"], ["2", "1", "1", "4"]]
    col_labels = [r"$x$", r"$y$", r"$z$", r"$b$"]
    tbl = ax.table(
        cellText=data,
        colLabels=col_labels,
        loc="center",
        cellLoc="center",
        colColours=[C_PANEL] * 4,
    )
    tbl.scale(1.15, 2.2)
    for (row, col), cell in tbl.get_celld().items():
        cell.set_edgecolor(C_INK)
        cell.set_linewidth(1.0)
        if row == 0:
            cell.set_facecolor(C_BLUE)
            cell.get_text().set_color(C_BG)
            cell.get_text().set_weight("bold")
        else:
            cell.set_facecolor(C_BG if row % 2 else C_PANEL)
            cell.get_text().set_color(C_INK)
            cell.get_text().set_fontsize(13)
    ax.set_title(r"Расширенная матрица $[A \mid b]$ (пример из лекции)", fontsize=12, weight="bold", pad=14, color=C_INK)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def draw_two_lines_intersection(out_name: str = "two_lines_intersection.png"):
    """Геометрия $2\\times 2$: $x+y=1$, $x-y=0$ (из §11)."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(6.2, 6.2))
    ax.set_facecolor(C_BG)
    fig.patch.set_facecolor(C_BG)
    t = np.linspace(-0.6, 1.6, 200)
    ax.plot(t, 1 - t, color=C_BLUE, lw=2.4, label=r"$x+y=1$")
    ax.plot(t, t, color=C_ORANGE, lw=2.4, label=r"$x-y=0$")
    sol_x, sol_y = 0.5, 0.5
    ax.scatter(
        [sol_x],
        [sol_y],
        s=140,
        c=C_GREEN,
        edgecolors=C_INK,
        linewidths=1.3,
        zorder=5,
        label=r"точка $(\frac{1}{2},\frac{1}{2})$",
    )
    ax.set_xlim(-0.2, 1.2)
    ax.set_ylim(-0.2, 1.2)
    ax.set_aspect("equal")
    ax.set_xlabel(r"$x$", fontsize=12, color=C_INK)
    ax.set_ylabel(r"$y$", fontsize=12, color=C_INK)
    ax.set_title(r"Пересечение двух прямых — решение $2\times 2$ системы", fontsize=12, weight="bold", color=C_INK)
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(True, alpha=0.4)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def _jacobi_step(A: np.ndarray, b: np.ndarray, x: np.ndarray) -> np.ndarray:
    n = len(b)
    x_new = np.zeros_like(x)
    for i in range(n):
        s = sum(A[i, j] * x[j] for j in range(n) if j != i)
        x_new[i] = (b[i] - s) / A[i, i]
    return x_new


def _gs_step(A: np.ndarray, b: np.ndarray, x: np.ndarray) -> np.ndarray:
    n = len(b)
    x_new = x.copy()
    for i in range(n):
        s = sum(A[i, j] * x_new[j] for j in range(n) if j != i)
        x_new[i] = (b[i] - s) / A[i, i]
    return x_new


def draw_jacobi_gs_errors(out_name: str = "jacobi_gs_error_compare.png", n_iter: int = 22):
    """Система из §16: сравнение нормы ошибки Якоби и Гаусса–Зейделя."""
    _apply_style()
    A = np.array([[10.0, -1.0, 2.0], [-1.0, 11.0, -1.0], [2.0, -1.0, 10.0]], dtype=float)
    b = np.array([6.0, 25.0, -11.0], dtype=float)
    x_star = np.linalg.solve(A, b)

    xj = np.zeros(3)
    xg = np.zeros(3)
    err_j = [np.linalg.norm(xj - x_star, ord=np.inf)]
    err_g = [np.linalg.norm(xg - x_star, ord=np.inf)]
    for _ in range(n_iter):
        xj = _jacobi_step(A, b, xj)
        xg = _gs_step(A, b, xg)
        err_j.append(np.linalg.norm(xj - x_star, ord=np.inf))
        err_g.append(np.linalg.norm(xg - x_star, ord=np.inf))

    k = np.arange(len(err_j))
    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    ax.set_facecolor(C_BG)
    fig.patch.set_facecolor(C_BG)
    ax.semilogy(k, err_j, "o-", color=C_ORANGE, lw=2.0, ms=5, label="Якоби")
    ax.semilogy(k, err_g, "s-", color=C_BLUE, lw=2.0, ms=4, label="Гаусс–Зейдель")
    ax.set_xlabel(r"номер итерации $k$", fontsize=11, color=C_INK)
    ax.set_ylabel(r"$\|x^{(k)} - x^*\|_\infty$", fontsize=11, color=C_INK)
    ax.set_title(
        r"Сходимость на примере $10x_1-x_2+2x_3=6$, $-x_1+11x_2-x_3=25$, $2x_1-x_2+10x_3=-11$",
        fontsize=11,
        weight="bold",
        color=C_INK,
    )
    ax.legend(loc="upper right", fontsize=10)
    ax.grid(True, which="both", alpha=0.35)
    fig.tight_layout()
    fig.savefig(ASSETS / out_name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def gif_jacobi_components(out_name: str = "gif_jacobi_components.gif", duration: float = 0.25):
    """Компоненты $x^{(k)}$ при методе Якоби (та же система)."""
    _apply_style()
    A = np.array([[10.0, -1.0, 2.0], [-1.0, 11.0, -1.0], [2.0, -1.0, 10.0]], dtype=float)
    b = np.array([6.0, 25.0, -11.0], dtype=float)
    x_star = np.linalg.solve(A, b)
    x = np.zeros(3)
    traj = [x.copy()]
    for _ in range(18):
        x = _jacobi_step(A, b, x)
        traj.append(x.copy())

    frames = []
    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for m in range(1, len(traj) + 1):
            xs = np.arange(m)
            arr = np.array(traj[:m])
            fig, ax = plt.subplots(figsize=(7.4, 4.2))
            ax.set_facecolor(C_BG)
            fig.patch.set_facecolor(C_BG)
            ax.plot(xs, arr[:, 0], "o-", color=C_ORANGE, lw=1.8, ms=5, label=r"$x_1^{(k)}$")
            ax.plot(xs, arr[:, 1], "s-", color=C_BLUE, lw=1.8, ms=4, label=r"$x_2^{(k)}$")
            ax.plot(xs, arr[:, 2], "^-", color=C_GREEN, lw=1.8, ms=4, label=r"$x_3^{(k)}$")
            ax.axhline(x_star[0], color=C_ORANGE, ls=":", lw=1.0, alpha=0.7)
            ax.axhline(x_star[1], color=C_BLUE, ls=":", lw=1.0, alpha=0.7)
            ax.axhline(x_star[2], color=C_GREEN, ls=":", lw=1.0, alpha=0.7)
            ax.set_xlim(-0.2, len(traj) + 0.2)
            ax.set_xlabel(r"$k$", fontsize=11, color=C_INK)
            ax.set_ylabel(r"значение компонент", fontsize=10, color=C_INK)
            ax.set_title(
                fr"Метод Якоби: первые {m} векторов $x^{{(k)}}$",
                fontsize=11,
                weight="bold",
                color=C_INK,
            )
            ax.legend(loc="lower right", fontsize=9, ncol=3)
            ax.grid(True, alpha=0.35)
            fig.subplots_adjust(left=0.1, right=0.97, top=0.86, bottom=0.14)
            fp = tmp_path / f"j_{m:03d}.png"
            fig.savefig(fp, dpi=130, facecolor=C_BG)
            plt.close(fig)
            frames.append(imageio.imread(fp))
        for _ in range(5):
            frames.append(frames[-1])
    imageio.mimsave(ASSETS / out_name, frames, duration=duration, loop=0)


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_augmented_matrix_example()
    draw_two_lines_intersection()
    draw_jacobi_gs_errors()
    gif_jacobi_components()
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
