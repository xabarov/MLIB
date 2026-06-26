"""
Иллюстрации для лекции «Комплексные векторные пространства».

Запуск:
    python3 generate_visuals.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, FancyArrowPatch, Rectangle, Wedge

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

C_BG = "#ffffff"
C_INK = "#141413"
C_GRAY = "#b0aea5"
C_ORANGE = "#d97757"
C_BLUE = "#6a9bcc"
C_GREEN = "#788c5d"
C_PURPLE = "#7c6ccf"
C_RED = "#c45c4a"


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
            "grid.alpha": 0.22,
            "font.size": 11,
        }
    )


def _save(fig: plt.Figure, name: str) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS / name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)


def _setup_2d(ax: plt.Axes, lim: float = 3.0, origin: bool = True) -> None:
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    if origin:
        ax.axhline(0, color=C_GRAY, lw=0.8)
        ax.axvline(0, color=C_GRAY, lw=0.8)
    ax.grid(True, alpha=0.22)
    for spine in ax.spines.values():
        spine.set_color(C_GRAY)


def _quad_contours(ax: plt.Axes, A: np.ndarray, levels: np.ndarray, color: str, lw: float = 1.6) -> None:
    """Линии уровня Q(x)=x^T A x."""
    w, h = 320, 320
    xs = np.linspace(ax.get_xlim()[0], ax.get_xlim()[1], w)
    ys = np.linspace(ax.get_ylim()[0], ax.get_ylim()[1], h)
    X, Y = np.meshgrid(xs, ys)
    Z = A[0, 0] * X**2 + 2 * A[0, 1] * X * Y + A[1, 1] * Y**2
    ax.contour(X, Y, Z, levels=levels, colors=color, linewidths=lw)


def draw_complex_plane_vector(out_name: str = "complex_plane_vector.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(6.4, 6.0))
    _setup_2d(ax, lim=2.6)

    z = 1.45 + 1.05j
    ax.annotate("", xy=(z.real, z.imag), xytext=(0, 0), arrowprops=dict(arrowstyle="->", lw=2.8, color=C_BLUE))
    ax.plot([0, z.real], [0, 0], color=C_ORANGE, lw=1.8, ls="--")
    ax.plot([z.real, z.real], [0, z.imag], color=C_ORANGE, lw=1.8, ls="--")

    r = abs(z)
    theta = np.angle(z)
    arc = Arc((0, 0), 0.9, 0.9, angle=0, theta1=0, theta2=np.degrees(theta), color=C_GREEN, lw=2.0)
    ax.add_patch(arc)

    ax.text(z.real * 0.55, -0.22, r"$\mathrm{Re}\,z$", color=C_ORANGE, fontsize=11)
    ax.text(z.real + 0.12, z.imag * 0.45, r"$\mathrm{Im}\,z$", color=C_ORANGE, fontsize=11)
    ax.text(z.real + 0.1, z.imag + 0.12, r"$z$", color=C_BLUE, fontsize=13)
    ax.text(0.55, 0.38, r"$\arg z$", color=C_GREEN, fontsize=11)
    ax.text(-2.35, 2.15, r"$|z|=\sqrt{x^2+y^2}$", fontsize=10, color=C_INK)
    ax.set_xlabel(r"$\mathrm{Re}$")
    ax.set_ylabel(r"$\mathrm{Im}$")
    ax.set_title(r"Комплексное число $z=x+iy$ на плоскости", fontsize=12, weight="bold")
    _save(fig, out_name)


def draw_hermitian_inner_product_scheme(out_name: str = "hermitian_inner_product_scheme.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(9.2, 3.8))
    ax.axis("off")
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 4)

    left = Rectangle((0.6, 1.0), 1.9, 1.6, facecolor="#eef3f9", edgecolor=C_BLUE, linewidth=2.0)
    mid = Rectangle((3.0, 1.0), 1.9, 1.6, facecolor="#f9efe8", edgecolor=C_ORANGE, linewidth=2.0)
    right = Rectangle((7.4, 1.15), 2.4, 1.3, facecolor="#edf5e8", edgecolor=C_GREEN, linewidth=2.0)
    ax.add_patch(left)
    ax.add_patch(mid)
    ax.add_patch(right)
    ax.text(1.55, 1.8, r"$x$", fontsize=22, color=C_BLUE, ha="center", va="center")
    ax.text(3.95, 1.8, r"$\overline{y}$", fontsize=20, color=C_ORANGE, ha="center", va="center")
    ax.text(8.6, 1.8, r"$\langle x,y\rangle$", fontsize=16, color=C_GREEN, ha="center", va="center")

    ax.annotate("", xy=(6.9, 1.8), xytext=(5.1, 1.8), arrowprops=dict(arrowstyle="->", lw=2.4, color=C_INK))
    ax.annotate("", xy=(6.9, 1.45), xytext=(2.6, 1.45), arrowprops=dict(arrowstyle="->", lw=2.4, color=C_INK))
    ax.text(5.8, 2.35, "линейно по $x$", fontsize=10, ha="center", color=C_INK)
    ax.text(4.0, 0.75, "сопряжение во втором аргументе", fontsize=10, ha="center", color=C_INK)
    ax.text(0.6, 3.2, "Эрмитово скалярное произведение", fontsize=14, weight="bold", color=C_INK)
    _save(fig, out_name)


def draw_quadratic_forms_level_sets(out_name: str = "quadratic_forms_level_sets.png") -> None:
    _apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.8))

    # Положительно определённая: x^2 + 2xy + 3y^2  (из лекции)
    A_pos = np.array([[1.0, 1.0], [1.0, 3.0]])
    # Неопределённая: x^2 - y^2
    A_ind = np.array([[1.0, 0.0], [0.0, -1.0]])

    specs = [
        (A_pos, [1, 2, 4, 7], "положительно определённая", C_BLUE),
        (A_ind, [-2, -1, 1, 2], "неопределённая", C_PURPLE),
    ]
    for ax, (A, levels, title, color) in zip(axes, specs):
        _setup_2d(ax, lim=2.8)
        _quad_contours(ax, A, np.array(levels, dtype=float), color)
        ax.set_title(title, fontsize=11, weight="bold")
        ax.text(-2.55, -2.45, r"$Q(x)=x^TAx$", fontsize=9, color=C_INK)

    fig.suptitle("Линии уровня квадратичной формы в $\mathbb{R}^2$", fontsize=13, weight="bold", y=1.02)
    fig.tight_layout()
    _save(fig, out_name)


def draw_positive_vs_indefinite_form(out_name: str = "positive_vs_indefinite_form.png") -> None:
    _apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.8))

    A_pos = np.array([[2.0, 0.0], [0.0, 1.0]])
    A_ind = np.array([[1.0, 0.0], [0.0, -1.0]])

    for ax, A, title, color in zip(
        axes,
        [A_pos, A_ind],
        [r"$\Delta_k>0$: вложенные эллипсы", r"знаки разные: гиперболы"],
        [C_GREEN, C_ORANGE],
    ):
        _setup_2d(ax, lim=2.6)
        if A[0, 1] == 0 and A[0, 0] > 0 and A[1, 1] > 0:
            levels = np.array([0.6, 1.2, 1.8, 2.4])
        else:
            levels = np.array([-2.0, -1.0, 1.0, 2.0])
        _quad_contours(ax, A, levels, color, lw=2.0)
        ax.set_title(title, fontsize=11, weight="bold")

    fig.suptitle("Критерий Сильвестра: геометрия знаков формы", fontsize=13, weight="bold", y=1.02)
    fig.tight_layout()
    _save(fig, out_name)


def draw_jacobi_diagonalization(out_name: str = "jacobi_diagonalization.png") -> None:
    _apply_style()
    # Q = x^2 + 4xy + 3y^2, после замены u=x+2y, v=y  =>  u^2 - v^2 (неопределённая)
    # Для «выровненных эллипсов» возьмём положительно определённую форму и её диагонализацию.
    A = np.array([[2.0, 1.0], [1.0, 3.0]])
    w, Q = np.linalg.eigh(A)
    C = Q.T  # x = C u  =>  Q_old(x) = sum w_i u_i^2

    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.8))
    levels = np.array([2.0, 4.0, 6.0, 9.0])

    _setup_2d(axes[0], lim=2.8)
    _quad_contours(axes[0], A, levels, C_BLUE)
    axes[0].set_title("до замены координат", fontsize=11, weight="bold")
    v1, v2 = Q[:, 0], Q[:, 1]
    axes[0].annotate("", xy=v1 * 1.6, xytext=(0, 0), arrowprops=dict(arrowstyle="->", lw=2.2, color=C_GREEN))
    axes[0].annotate("", xy=v2 * 1.6, xytext=(0, 0), arrowprops=dict(arrowstyle="->", lw=2.2, color=C_GREEN))
    axes[0].text(1.05 * v1[0], 1.05 * v1[1], r"$e_1$", color=C_GREEN, fontsize=11)
    axes[0].text(1.05 * v2[0], 1.05 * v2[1], r"$e_2$", color=C_GREEN, fontsize=11)

    A_diag = np.diag(w)
    _setup_2d(axes[1], lim=2.8)
    _quad_contours(axes[1], A_diag, levels, C_RED)
    axes[1].set_title("после метода Якоби / диагонализации", fontsize=11, weight="bold")
    axes[1].text(-2.4, -2.35, r"$Q=\lambda_1 u_1^2+\lambda_2 u_2^2$", fontsize=9, color=C_INK)

    fig.suptitle("Метод Якоби: наклонённые эллипсы выравниваются по осям", fontsize=13, weight="bold", y=1.02)
    fig.tight_layout()
    _save(fig, out_name)


def draw_self_adjoint_operator(out_name: str = "self_adjoint_operator.png") -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(6.4, 6.0))
    _setup_2d(ax, lim=2.6)

    A = np.array([[2.0, 1.0], [1.0, 2.0]])
    w, Q = np.linalg.eigh(A)

    t = np.linspace(0, 2 * np.pi, 200)
    circle = np.stack([np.cos(t), np.sin(t)], axis=0)
    ellipse = A @ circle

    ax.plot(circle[0], circle[1], color=C_BLUE, lw=2.4, label="единичная окружность")
    ax.plot(ellipse[0], ellipse[1], color=C_RED, lw=2.4, label=r"образ $Ax$")

    for i, lam in enumerate(w):
        v = Q[:, i] / np.linalg.norm(Q[:, i]) * (1.35 + 0.15 * i)
        ax.annotate("", xy=v, xytext=(0, 0), arrowprops=dict(arrowstyle="->", lw=2.4, color=C_GREEN))
        ax.text(v[0] * 1.08, v[1] * 1.08, rf"$v_{i+1}$", color=C_GREEN, fontsize=11)

    ax.text(-2.45, 2.1, r"$A=A^T$, $\lambda\in\mathbb{R}$", fontsize=10, color=C_INK)
    ax.set_title("Самосопряжённый оператор: собственные направления и эллипс", fontsize=11, weight="bold")
    ax.legend(loc="lower right", fontsize=9, framealpha=0.95)
    _save(fig, out_name)


def draw_svd_geometry(out_name: str = "svd_geometry.png") -> None:
    _apply_style()
    A = np.array([[3.0, 1.0], [1.0, 2.0]])
    U, s, Vt = np.linalg.svd(A)
    Sigma = np.diag(s)

    t = np.linspace(0, 2 * np.pi, 160)
    circle = np.stack([np.cos(t), np.sin(t)], axis=0)

    stages = [
        (circle, "исходный круг", C_BLUE),
        (Vt @ circle, r"$V^*$", C_PURPLE),
        (Sigma @ (Vt @ circle), r"$\Sigma$", C_ORANGE),
        (U @ Sigma @ Vt @ circle, r"$U$", C_RED),
    ]

    fig, axes = plt.subplots(1, 4, figsize=(13.6, 3.8))
    lim = 3.6
    for ax, (pts, title, color) in zip(axes, stages):
        _setup_2d(ax, lim=lim)
        ax.plot(pts[0], pts[1], color=color, lw=2.5)
        ax.set_title(title, fontsize=11, weight="bold")

    fig.suptitle(r"$A=U\Sigma V^*$: поворот — растяжение — поворот", fontsize=13, weight="bold", y=1.05)
    fig.tight_layout()
    _save(fig, out_name)


def main() -> None:
    jobs = [
        draw_complex_plane_vector,
        draw_hermitian_inner_product_scheme,
        draw_quadratic_forms_level_sets,
        draw_jacobi_diagonalization,
        draw_positive_vs_indefinite_form,
        draw_self_adjoint_operator,
        draw_svd_geometry,
    ]
    ASSETS.mkdir(parents=True, exist_ok=True)
    for fn in jobs:
        fn()
    print("Созданы файлы в assets/:")
    for path in sorted(ASSETS.glob("*.png"), key=lambda p: p.name):
        print(f"  - {path.name}")


if __name__ == "__main__":
    main()
