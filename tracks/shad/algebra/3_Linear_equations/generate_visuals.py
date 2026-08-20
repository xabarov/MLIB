"""Иллюстрации для лекции про системы линейных уравнений."""

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


def _setup_axis(ax: plt.Axes) -> None:
    ax.set_facecolor(C_BG)
    ax.grid(True, alpha=0.28)
    ax.axhline(0, color=C_GRAY, lw=0.9)
    ax.axvline(0, color=C_GRAY, lw=0.9)
    for spine in ax.spines.values():
        spine.set_color(C_GRAY)


def draw_augmented_matrix_example(out_name: str = "augmented_matrix_example.png") -> None:
    """Аккуратная схема расширенной матрицы с выделенной правой частью."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(7.5, 2.9))
    ax.axis("off")

    data = [["1", "2", "-1", "3"], ["2", "1", "1", "4"]]
    col_labels = [r"$x$", r"$y$", r"$z$", r"$b$"]
    tbl = ax.table(
        cellText=data,
        colLabels=col_labels,
        loc="center",
        cellLoc="center",
        colColours=[C_PANEL, C_PANEL, C_PANEL, "#f0d9cf"],
    )
    tbl.scale(1.18, 2.25)

    for (row, col), cell in tbl.get_celld().items():
        cell.set_edgecolor(C_INK)
        cell.set_linewidth(1.0)
        if row == 0:
            cell.set_facecolor(C_BLUE if col < 3 else C_ORANGE)
            cell.get_text().set_color(C_BG)
            cell.get_text().set_weight("bold")
        else:
            cell.set_facecolor(C_BG if col < 3 else "#fbefe8")
            cell.get_text().set_color(C_INK)
            cell.get_text().set_fontsize(13)

    ax.text(0.15, 0.1, "матрица коэффициентов", transform=ax.transAxes, fontsize=10, color=C_BLUE)
    ax.text(0.76, 0.1, "правая часть", transform=ax.transAxes, fontsize=10, color=C_ORANGE)
    ax.set_title(r"Расширенная матрица $[A \mid b]$", fontsize=12, weight="bold", pad=14)
    fig.tight_layout()
    _save(fig, out_name)


def draw_two_lines_intersection(out_name: str = "two_lines_intersection.png") -> None:
    """Геометрия 2x2 системы через пересечение двух прямых."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(6.2, 5.7))
    _setup_axis(ax)

    t = np.linspace(-0.4, 1.4, 300)
    ax.plot(t, 1 - t, color=C_BLUE, lw=2.5, label=r"$x+y=1$")
    ax.plot(t, t, color=C_ORANGE, lw=2.5, label=r"$x-y=0$")
    sol_x, sol_y = 0.5, 0.5
    ax.scatter([sol_x], [sol_y], s=120, color=C_GREEN, edgecolors=C_INK, linewidths=1.2, zorder=5)
    ax.annotate(
        "решение системы",
        (sol_x, sol_y),
        xytext=(0.72, 0.72),
        textcoords="data",
        fontsize=10,
        color=C_GREEN,
        arrowprops=dict(arrowstyle="->", color=C_GREEN, lw=1.1),
    )

    ax.set_xlim(-0.15, 1.15)
    ax.set_ylim(-0.15, 1.15)
    ax.set_aspect("equal")
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.set_title(r"Пересечение прямых соответствует решению системы", fontsize=12, weight="bold")
    ax.legend(loc="upper right", fontsize=9, framealpha=0.95)
    fig.tight_layout()
    _save(fig, out_name)


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


def draw_iterative_methods_intro(
    out_name: str = "iterative_methods_metaphor.png", n_iter: int = 7
) -> None:
    """Содержательная схема последовательных приближений к решению."""
    _apply_style()
    A = np.array([[4.0, 1.0], [2.0, 3.0]], dtype=float)
    b = np.array([9.0, 13.0], dtype=float)
    x_star = np.linalg.solve(A, b)

    xj = np.array([0.0, 0.0])
    xg = np.array([0.0, 0.0])
    traj_j = [xj.copy()]
    traj_g = [xg.copy()]
    for _ in range(n_iter):
        xj = _jacobi_step(A, b, xj)
        xg = _gs_step(A, b, xg)
        traj_j.append(xj.copy())
        traj_g.append(xg.copy())

    traj_j = np.array(traj_j)
    traj_g = np.array(traj_g)

    x = np.linspace(-0.1, 2.7, 400)
    fig, ax = plt.subplots(figsize=(7.4, 5.8))
    _setup_axis(ax)

    ax.plot(x, 9 - 4 * x, color=C_BLUE, lw=2.2, label=r"$4x_1+x_2=9$")
    ax.plot(x, (13 - 2 * x) / 3, color=C_ORANGE, lw=2.2, label=r"$2x_1+3x_2=13$")
    ax.plot(traj_j[:, 0], traj_j[:, 1], "o-", color=C_PURPLE, lw=1.9, ms=4.5, label="траектория Якоби")
    ax.plot(traj_g[:, 0], traj_g[:, 1], "s-", color=C_GREEN, lw=1.9, ms=4.2, label="траектория Гаусса-Зейделя")
    ax.scatter([x_star[0]], [x_star[1]], s=130, color=C_INK, zorder=6)
    ax.text(x_star[0] + 0.07, x_star[1] - 0.18, r"$x^*$", fontsize=11, color=C_INK)
    ax.text(0.14, 0.22, r"$x^{(0)}$", fontsize=10, color=C_PURPLE)

    ax.set_xlim(-0.05, 2.55)
    ax.set_ylim(-0.2, 4.1)
    ax.set_xlabel(r"$x_1$")
    ax.set_ylabel(r"$x_2$")
    ax.set_title("Итерационные методы строят цепочку приближений к решению", fontsize=12, weight="bold")
    ax.legend(loc="upper right", fontsize=8.8, framealpha=0.95)
    fig.tight_layout()
    _save(fig, out_name)


def draw_jacobi_gs_errors(
    out_name: str = "jacobi_gs_error_compare.png", n_iter: int = 22
) -> None:
    """Сравнение скорости сходимости Якоби и Гаусса-Зейделя."""
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
    fig, ax = plt.subplots(figsize=(8.1, 4.8))
    ax.set_facecolor(C_BG)
    ax.semilogy(k, err_j, "o-", color=C_ORANGE, lw=2.0, ms=4.8, label="Якоби")
    ax.semilogy(k, err_g, "s-", color=C_BLUE, lw=2.0, ms=4.2, label="Гаусса-Зейделя")
    ax.set_xlabel(r"номер итерации $k$")
    ax.set_ylabel(r"$\|x^{(k)}-x^*\|_{\infty}$")
    ax.set_title("Скорость сходимости на одном и том же примере", fontsize=12, weight="bold")
    ax.text(
        0.03,
        0.08,
        r"$10x_1-x_2+2x_3=6,\; -x_1+11x_2-x_3=25,\; 2x_1-x_2+10x_3=-11$",
        transform=ax.transAxes,
        fontsize=8.8,
        color=C_INK,
    )
    ax.legend(loc="upper right", fontsize=9.5, framealpha=0.95)
    ax.grid(True, which="both", alpha=0.28)
    for spine in ax.spines.values():
        spine.set_color(C_GRAY)
    fig.tight_layout()
    _save(fig, out_name)


def gif_jacobi_components(
    out_name: str = "gif_jacobi_components.gif", duration: float = 0.25
) -> None:
    """GIF: как компоненты Якоби стабилизируются к точному решению."""
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
            fig, ax = plt.subplots(figsize=(7.6, 4.5))
            ax.set_facecolor(C_BG)
            ax.plot(xs, arr[:, 0], "o-", color=C_ORANGE, lw=1.9, ms=4.5, label=r"$x_1^{(k)}$")
            ax.plot(xs, arr[:, 1], "s-", color=C_BLUE, lw=1.9, ms=4.0, label=r"$x_2^{(k)}$")
            ax.plot(xs, arr[:, 2], "^-", color=C_GREEN, lw=1.9, ms=4.0, label=r"$x_3^{(k)}$")
            ax.axhline(x_star[0], color=C_ORANGE, ls=":", lw=1.0, alpha=0.8)
            ax.axhline(x_star[1], color=C_BLUE, ls=":", lw=1.0, alpha=0.8)
            ax.axhline(x_star[2], color=C_GREEN, ls=":", lw=1.0, alpha=0.8)
            ax.set_xlim(-0.2, len(traj) - 0.2)
            ax.set_xlabel(r"$k$")
            ax.set_ylabel("значение компоненты")
            ax.set_title(fr"Метод Якоби: первые {m} итераций", fontsize=12, weight="bold")
            ax.legend(loc="lower right", fontsize=9, ncol=3, framealpha=0.95)
            ax.grid(True, alpha=0.28)
            for spine in ax.spines.values():
                spine.set_color(C_GRAY)
            fig.tight_layout()
            fp = tmp_path / f"j_{m:03d}.png"
            fig.savefig(fp, dpi=130, bbox_inches="tight", facecolor=C_BG)
            plt.close(fig)
            frames.append(imageio.imread(fp))

        for _ in range(5):
            frames.append(frames[-1])

    imageio.mimsave(ASSETS / out_name, frames, duration=duration, loop=0)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_augmented_matrix_example()
    draw_two_lines_intersection()
    draw_iterative_methods_intro()
    draw_jacobi_gs_errors()
    gif_jacobi_components()
    print(f"Generated visuals in {ASSETS}")


if __name__ == "__main__":
    main()
